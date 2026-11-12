#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

enum { ROUNDS=100, DEADLINE_MS=1500, REQUEST=1, MOVE=2, RESULT=3 };
typedef struct { int kind, round, own, opponent, winner; } Packet;
typedef struct { long type; Packet data; } Message;
static int qid=-1, to[2][2], from[2][2];
static int timeout_demo;
static long long now_ms(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC,&t)<0) { perror("clock_gettime"); exit(1); }
    return (long long)t.tv_sec*1000+t.tv_nsec/1000000;
}
static int win(int a,int b) {
    if (a==b) return 0;
    if (a<0) return 2;
    if (b<0) return 1;
    return (a+1)%3==b ? 1 : 2;
}
static int send_packet(int player,int referee,Packet p) {
#ifdef USE_QUEUE
    Message m={.type=1+2*player+!referee,.data=p};
    int rc;
    do { rc=msgsnd(qid,&m,sizeof m.data,0); } while (rc<0 && errno==EINTR);
    return rc==0;
#else
    int fd=referee ? to[player][1] : from[player][1];
    ssize_t n;
    do { n=write(fd,&p,sizeof p); } while(n<0 && errno==EINTR);
    return n==(ssize_t)sizeof p;
#endif
}
/* 1 = packet, 0 = deadline, -1 = transport failure */
static int receive(int player,int referee,Packet *p,long long end) {
#ifdef USE_QUEUE
    Message m;
    long type=1+2*player+referee;
    for (;;) {
        ssize_t n=msgrcv(qid,&m,sizeof m.data,type,IPC_NOWAIT);
        if (n>=0) { if (n!=(ssize_t)sizeof *p) return -1; *p=m.data; return 1; }
        if (errno==EINTR) continue;
        if (errno!=ENOMSG) return -1;
        if (now_ms()>=end) return 0;
        struct timespec pause={.tv_nsec=1000000}; nanosleep(&pause,NULL);
    }
#else
    struct pollfd f={.fd=referee ? from[player][0] : to[player][0],.events=POLLIN};
    for (;;) {
        long long left=end-now_ms();
        int n=poll(&f,1,left>0 ? (int)left : 0);
        if (n<0 && errno==EINTR) continue;
        if (n<=0) return n;
        if (!(f.revents&POLLIN)) return -1;
        ssize_t count;
        do { count=read(f.fd,p,sizeof *p); } while(count<0 && errno==EINTR);
        return count==(ssize_t)sizeof *p ? 1 : -1;
    }
#endif
}
static void close_pipes(int player) {
#ifndef USE_QUEUE
    for(int i=0;i<2;i++) for(int j=0;j<2;j++) {
        if (player<0 ? j==0 : (i!=player || j==1)) close(to[i][j]);
        if (player<0 ? j==1 : (i!=player || j==0)) close(from[i][j]);
    }
#else
    (void)player;
#endif
}
static int play(int p) {
    close_pipes(p);
    unsigned state=p==0 ? 42u : 73u;
    for(int round=1;round<=ROUNDS;round++) {
        Packet data;
        if (receive(p,0,&data,now_ms()+5000)!=1 || data.kind!=REQUEST || data.round!=round) return 1;
        state=1664525u*state+1013904223u;
        int hand=(int)((state>>16)%3u);
        if (timeout_demo && p==0 && round==2) hand=-1;
        if (hand>=0 && !send_packet(p,0,(Packet){MOVE,round,hand,0,0})) return 1;
        if (receive(p,0,&data,now_ms()+5000)!=1 || data.kind!=RESULT || data.round!=round ||
            data.own!=hand || data.opponent< -1 || data.opponent>2 ||
            data.winner!=(p==0 ? win(hand,data.opponent) : win(data.opponent,hand))) return 1;
    }
    return 0;
}
int main(int argc,char **argv) {
    if (argc>2 || (argc==2 && strcmp(argv[1],"--timeout-demo"))) return 2;
    timeout_demo=argc==2;
    signal(SIGPIPE,SIG_IGN);
#ifdef USE_QUEUE
    (void)to; (void)from;
    qid=msgget(IPC_PRIVATE,IPC_CREAT|0600);
    if(qid<0) { perror("msgget"); return 1; }
    printf("transport=System V message queue qid=%d\n",qid);
#else
    for(int i=0;i<2;i++) if(pipe(to[i])<0 || pipe(from[i])<0) { perror("pipe"); return 1; }
    puts("transport=two bidirectional channels using four anonymous pipes");
#endif
    pid_t children[2]={0,0};
    int ok=1, score[3]={0,0,0}, timeouts=0;
    for(int p=0;p<2;p++) {
        children[p]=fork();
        if (children[p]<0) { perror("fork"); ok=0; break; }
        if (children[p]==0) _exit(play(p));
    }
    close_pipes(-1);
    static const char *names[]={"timeout","rock","scissors","paper"};
    for(int round=1;ok && round<=ROUNDS;round++) {
        long long end=now_ms()+DEADLINE_MS;
        int hands[2]={-1,-1};
        for(int p=0;p<2;p++) if (!send_packet(p,1,(Packet){REQUEST,round,0,0,0})) ok=0;
        for(int p=0;ok && p<2;p++) {
            Packet data;
            int rc=receive(p,1,&data,end);
            if (rc<0 || (rc==1 && (data.kind!=MOVE || data.round!=round || data.own<0 || data.own>2))) ok=0;
            else if (rc==0) ++timeouts;
            else hands[p]=data.own;
        }
        if (!ok) break;
        int winner=win(hands[0],hands[1]); ++score[winner];
        printf("round %03d P1=%s P2=%s winner=%d\n",round,names[hands[0]+1],names[hands[1]+1],winner);
        for(int p=0;p<2;p++) if (!send_packet(p,1,(Packet){RESULT,round,hands[p],hands[1-p],winner})) ok=0;
    }
    if (!ok) for(int p=0;p<2;p++) if(children[p]>0) kill(children[p],SIGTERM);
    for(int p=0;p<2;p++) if(children[p]>0) {
        int status;
        pid_t w;
        do { w=waitpid(children[p],&status,0); } while(w<0 && errno==EINTR);
        if(w<0 || !WIFEXITED(status) || WEXITSTATUS(status)!=0) ok=0;
    }
    if(qid>=0) {
        if(msgctl(qid,IPC_RMID,NULL)<0) { perror("msgctl IPC_RMID"); ok=0; }
        else puts("message queue removed");
    }
    int total=score[0]+score[1]+score[2];
    printf("score: P1=%d P2=%d draw=%d total=%d timeouts=%d\n",score[1],score[2],score[0],total,timeouts);
    printf("match winner=%s\n",score[1]>score[2] ? "P1" : score[1]<score[2] ? "P2" : "draw");
    if(!ok) fprintf(stderr,"transport or child failure\n");
    return ok && total==ROUNDS ? 0 : 1;
}
