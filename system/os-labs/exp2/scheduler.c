#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum { N=4, QUANTUM=2 };
enum State { NEW, READY, RUNNING, DONE };
typedef struct PCB {
    char id;
    int arrival, burst, priority, remaining, first, end;
    enum State state;
    struct PCB *next;
} PCB;
static const PCB input[N] = {
    {.id='A', .arrival=0, .burst=5, .priority=3},
    {.id='B', .arrival=1, .burst=3, .priority=1},
    {.id='C', .arrival=2, .burst=1, .priority=0},
    {.id='D', .arrival=12, .burst=2, .priority=1}
};
static void append(PCB **q, PCB *p) {
    while (*q) q = &(*q)->next;
    p->state=READY; p->next=NULL; *q=p;
}
static void admit(PCB p[], PCB **q, int *next, int t) {
    while (*next < N && p[*next].arrival <= t) { append(q, &p[*next]); ++*next; }
}
static PCB *take(PCB **q, int priority) {
    PCB **pick=q;
    if (priority)
        for (PCB **s=q; *s; s=&(*s)->next)
            if ((*s)->priority < (*pick)->priority) pick=s;
    PCB *p=*pick; *pick=p->next; p->next=NULL; p->state=RUNNING; return p;
}
static void simulate(const char *mode) {
    PCB p[N]; memcpy(p,input,sizeof p);
    for (int i=0;i<N;i++) { p[i].remaining=p[i].burst; p[i].first=-1; }
    int time=0, done=0, next=0, sumw=0, sumt=0;
    int rr=strcmp(mode,"RR")==0;
    PCB *queue=NULL;
    printf("\n%s (lower priority number first; RR quantum=%d)\n",mode,QUANTUM);
    while (done<N) {
        admit(p,&queue,&next,time);
        if (!queue) { printf("[%d,%d) idle\n",time,p[next].arrival); time=p[next].arrival; continue; }
        PCB *run=take(&queue,strcmp(mode,"PR")==0);
        if (run->first<0) run->first=time;
        int len=rr && run->remaining>QUANTUM ? QUANTUM : run->remaining;
        printf("[%d,%d) %c\n",time,time+len,run->id);
        time+=len; run->remaining-=len;
        admit(p,&queue,&next,time);
        if (run->remaining) append(&queue,run);
        else { run->end=time; run->state=DONE; ++done; }
    }
    puts("ID arrival burst priority first finish turnaround waiting");
    for (int i=0;i<N;i++) {
        int turn=p[i].end-p[i].arrival, wait=turn-p[i].burst;
        sumt+=turn; sumw+=wait;
        printf("%c %d %d %d %d %d %d %d\n",p[i].id,p[i].arrival,p[i].burst,p[i].priority,p[i].first,p[i].end,turn,wait);
    }
    printf("mean turnaround=%.2f mean waiting=%.2f\n",(double)sumt/N,(double)sumw/N);
}
int main(int argc,char **argv) {
    if (argc==1) { simulate("FCFS"); simulate("PR"); simulate("RR"); }
    else if (argc==2 && (!strcmp(argv[1],"FCFS") || !strcmp(argv[1],"PR") || !strcmp(argv[1],"RR"))) simulate(argv[1]);
    else { fprintf(stderr,"usage: %s [FCFS|PR|RR]\n",argv[0]); return 2; }
    return 0;
}
