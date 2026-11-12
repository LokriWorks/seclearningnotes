#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <pthread.h>
#include <semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { MAX_CAPACITY=32 };
static char *slots[MAX_CAPACITY];
static size_t capacity=3, in, out, occupied, peak, produced, consumed, full_waits, empty_waits;
static unsigned delay_ms;
static int input_failed;
static sem_t empty_slots, full_slots, mutex;
static void check(int rc,const char *op) {
    if (rc<0) { perror(op); exit(1); }
}
static void thread_check(int rc,const char *op) {
    if(rc) { fprintf(stderr,"%s: %s\n",op,strerror(rc)); exit(1); }
}
static void acquire(sem_t *s) {
    int rc;
    do { rc=sem_wait(s); } while(rc<0 && errno==EINTR);
    check(rc,"sem_wait");
}
static void await_slot(sem_t *s,size_t *counter,const char *event) {
    int rc;
    do { rc=sem_trywait(s); } while(rc<0 && errno==EINTR);
    if (rc==0) return;
    if (errno!=EAGAIN) check(rc,"sem_trywait");
    ++*counter;
    puts(event);
    acquire(s);
}
static void release(sem_t *s) { check(sem_post(s),"sem_post"); }
static void put(char *line) {
    await_slot(&empty_slots,&full_waits,"producer waiting: buffer full");
    acquire(&mutex);
    slots[in]=line; in=(in+1)%capacity;
    ++occupied;
    if (occupied>peak) peak=occupied;
    if (line) printf("produce %zu occupied=%zu: %s\n",++produced,occupied,line);
    else printf("produce EOF occupied=%zu\n",occupied);
    release(&mutex);
    release(&full_slots);
}
static void *producer(void *arg) {
    (void)arg;
    char *line=NULL;
    size_t len=0;
    ssize_t n;
    while ((n=getline(&line,&len,stdin))>=0) {
        if (n>0 && line[n-1]=='\n') line[n-1]='\0';
        put(line); line=NULL; len=0;
    }
    input_failed=ferror(stdin);
    free(line);
    put(NULL);
    return NULL;
}
static void *consumer(void *arg) {
    (void)arg;
    for (;;) {
        struct timespec delay={.tv_sec=delay_ms/1000,.tv_nsec=(long)(delay_ms%1000)*1000000};
        while(nanosleep(&delay,&delay)<0 && errno==EINTR) {}
        await_slot(&full_slots,&empty_waits,"consumer waiting: buffer empty");
        acquire(&mutex);
        char *line=slots[out]; slots[out]=NULL; out=(out+1)%capacity; --occupied;
        if (line) printf("consume %zu occupied=%zu: %s\n",++consumed,occupied,line);
        else printf("consume EOF occupied=%zu\n",occupied);
        release(&mutex);
        release(&empty_slots);
        if (!line) break;
        free(line);
    }
    return NULL;
}
static unsigned parse(const char *s,unsigned min,unsigned max) {
    char *end;
    errno=0;
    unsigned long n=strtoul(s,&end,10);
    if(errno || end==s || *end || n<min || n>max) {
        fprintf(stderr,"invalid numeric argument: %s\n",s); exit(2);
    }
    return (unsigned)n;
}
int main(int argc,char **argv) {
    if(argc>3) { fprintf(stderr,"usage: %s [capacity] [consumer_delay_ms]\n",argv[0]); return 2; }
    if(argc>1) capacity=parse(argv[1],1,MAX_CAPACITY);
    if(argc>2) delay_ms=parse(argv[2],0,1000);
    setvbuf(stdout,NULL,_IOLBF,0);
    check(sem_init(&empty_slots,0,(unsigned)capacity),"sem_init empty");
    check(sem_init(&full_slots,0,0),"sem_init full");
    check(sem_init(&mutex,0,1),"sem_init mutex");
    printf("capacity=%zu; enter one product per line, EOF to finish\n",capacity);
    pthread_t p,c;
    thread_check(pthread_create(&c,NULL,consumer,NULL),"pthread_create consumer");
    thread_check(pthread_create(&p,NULL,producer,NULL),"pthread_create producer");
    thread_check(pthread_join(p,NULL),"pthread_join producer");
    thread_check(pthread_join(c,NULL),"pthread_join consumer");
    check(sem_destroy(&mutex),"sem_destroy mutex");
    check(sem_destroy(&full_slots),"sem_destroy full");
    check(sem_destroy(&empty_slots),"sem_destroy empty");
    printf("produced=%zu consumed=%zu peak=%zu remaining=%zu full_waits=%zu empty_waits=%zu\n",
           produced,consumed,peak,occupied,full_waits,empty_waits);
    return input_failed || produced!=consumed || occupied!=0 || peak>capacity;
}
