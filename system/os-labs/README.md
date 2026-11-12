# 计算机操作系统实验

在 Ubuntu 上用 GCC 和 GNU Make 复现四个实验。目录中保留 C 源码、Makefile 和验证脚本，编译出的程序在本机生成。

| 目录 | 内容 | 验证命令 |
|---|---|---|
| [exp1](exp1/) | Shell、GCC 编译阶段和 Makefile | `bash run_lab.sh` |
| [exp2](exp2/) | fork、waitpid、exec 以及 FCFS、优先级、时间片轮转 | `bash verify.sh` |
| [exp3](exp3/) | System V 消息队列与匿名管道的石头剪子布 | `bash verify.sh` |
| [exp4](exp4/) | pthread 与 POSIX 信号量的生产者和消费者 | `bash verify.sh` |

进入对应子目录再运行命令。实验一会在 `records/` 下新建运行记录；其他实验会在各自目录生成日志。可在目录副本里复现，便于保留历史记录。

实验在 Ubuntu 虚拟机中运行验证，源码与实验记录整理使用了 AI 辅助。

[返回系统基础](../readme.md)
