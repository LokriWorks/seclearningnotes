"""TCP Reno教学状态机。单位为MSS，默认遵循课程简化规则。"""
from dataclasses import dataclass, asdict
import csv
import random

SS = '慢开始'
CA = '拥塞避免'
FR = '快恢复'

@dataclass(frozen=True)
class Record:
    step: int
    rtt: int
    event: str
    cwnd: int
    ssthresh: int
    state: str
    dupacks: int
    retransmissions: int

class Reno:
    def __init__(self, threshold=64, mode='course'):
        if not isinstance(threshold, int) or threshold < 2:
            raise ValueError('初始阈值必须是大于等于2的整数')
        if mode not in ('course', 'standard'):
            raise ValueError('未知规则模式')
        self.initial_threshold, self.mode = threshold, mode
        self.cwnd, self.ssthresh, self.state = 1, threshold, SS
        self.rtt = self.dupacks = self.retransmissions = 0
        self.fast_count = self.timeout_count = 0
        self.history = []
        self.record('初始化')

    def record(self, event):
        self.history.append(Record(len(self.history), self.rtt, event,
            self.cwnd, self.ssthresh, self.state, self.dupacks,
            self.retransmissions))

    def normal_rtt(self):
        """一个无丢失RTT，或快恢复后收到推进累计确认的新ACK。"""
        self.rtt += 1
        self.dupacks = 0
        if self.state == FR:
            self.cwnd = self.ssthresh
            self.state = CA
            self.record('新ACK：退出快恢复')
        elif self.cwnd < self.ssthresh:
            self.cwnd = min(2 * self.cwnd, self.ssthresh)
            self.state = CA if self.cwnd >= self.ssthresh else SS
            self.record('正常RTT：慢开始增长')
        else:
            self.cwnd += 1
            self.state = CA
            self.record('正常RTT：拥塞避免增长')

    def duplicate_ack(self):
        """单个重复ACK；同一RTT内的事件保留相同横坐标。"""
        self.dupacks += 1
        if self.state == FR:
            self.cwnd += 1
            self.record('额外重复ACK：窗口加1')
        elif self.dupacks == 3:
            # 满窗口在途假设下，FlightSize用当前cwnd近似。
            self.ssthresh = max(self.cwnd // 2, 2)
            self.cwnd = self.ssthresh + (3 if self.mode == 'standard' else 0)
            self.state = FR
            self.retransmissions += 1
            self.fast_count += 1
            self.record('第3个重复ACK：快重传')
        else:
            self.record(f'第{self.dupacks}个重复ACK：继续等待')

    def timeout(self):
        """将RTO等待抽象为2个RTT，不实现操作系统TCP重传定时器。"""
        self.rtt += 2
        self.ssthresh = max(self.cwnd // 2, 2)
        self.cwnd, self.state, self.dupacks = 1, SS, 0
        self.retransmissions += 1
        self.timeout_count += 1
        self.record('超时：重传并重新慢开始')

    def export_csv(self, path):
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=list(asdict(self.history[0])))
            writer.writeheader()
            writer.writerows(asdict(row) for row in self.history)

    def summary(self):
        return dict(mode=self.mode, rtt=self.rtt, events=len(self.history)-1,
            cwnd=self.cwnd, ssthresh=self.ssthresh, state=self.state,
            fast_retransmits=self.fast_count, timeouts=self.timeout_count,
            retransmissions=self.retransmissions,
            mean_cwnd=round(sum(x.cwnd for x in self.history[1:]) /
                            max(1, len(self.history)-1), 3))

def preset(name, mode='course'):
    r = Reno(mode=mode)
    if name == '无丢包':
        for _ in range(20): r.normal_rtt()
    elif name == '轻度丢包':
        for _ in range(10): r.normal_rtt()
        for _ in range(5): r.duplicate_ack()
        r.normal_rtt()
        for _ in range(12): r.normal_rtt()
    elif name == '重度丢包':
        for _ in range(10): r.normal_rtt()
        r.timeout()
        for _ in range(9): r.normal_rtt()
        r.timeout()
        for _ in range(8): r.normal_rtt()
    else:
        raise ValueError('未知场景')
    return r

def random_run(probability, seed=42, rounds=200, mode='course'):
    """概率为每个决策轮的丢包事件概率，非逐包丢失率。"""
    if not 0 <= probability <= 1 or rounds < 1:
        raise ValueError('概率须在0和1之间，轮数须大于零')
    rng = random.Random(seed)
    r = Reno(mode=mode)
    goodput_proxy = 0
    for _ in range(rounds):
        if rng.random() < probability:
            # 小窗口不足以形成3个重复ACK；较大窗口也可能超时。
            if r.cwnd >= 4 and rng.random() < .7:
                for _ in range(3): r.duplicate_ack()
                r.normal_rtt()
            else:
                r.timeout()
        else:
            goodput_proxy += r.cwnd
            r.normal_rtt()
    summary = r.summary()
    summary.update(probability=probability, seed=seed, rounds=rounds,
        goodput_proxy=round(goodput_proxy / r.rtt, 3))
    return r, summary
