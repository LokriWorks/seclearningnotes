# TCP Reno 拥塞控制教学模拟器

[返回计算机网络目录](../../readme.md) · [阅读课程设计报告](REPORT.md) · [模型与复现说明](docs/模型与复现.md)

这里包含报告对应的完整教学模拟器。它用 Python 和 Tkinter 展示拥塞窗口 `cwnd`、慢开始阈值 `ssthresh` 与阶段变化，不发送真实 TCP 数据包。

## 下载与启动

在仓库页面选择 **Code → Download ZIP** 并完整解压；需要保留 `reno_core.py` 和 `reno_gui.py` 在同一文件夹。

进入 `network/course-design/tcp-reno/程序`，Windows 可双击 **启动模拟器.bat**。

也可在终端执行：

```shell
cd network/course-design/tcp-reno/程序
python reno_gui.py
```

需要 Python 3.10 或更新版本和 Tkinter。正常运行无需安装第三方库。部分 Linux Python 发行版需要另外提供 Tkinter；GUI 需要桌面显示环境。

Windows 上只有 `py` 启动器时，可使用 `py -3 reno_gui.py`。

## 功能

- 单步推进或自动推进正常 RTT。
- 单个重复 ACK、连续三个重复 ACK，以及额外重复 ACK。
- 手动触发超时，观察窗口回到 1。
- 无丢包、轻度丢包和重度丢包预设。
- 设置随机事件概率与种子。
- 课程简化规则与标准 Reno 快恢复入口的对照。
- 显示双曲线与事件表；可导出本地 CSV。

## 复现与测试

在 `程序` 目录运行：

```shell
python -m unittest -v test_reno.py
python test_gui.py
python run_experiments.py
```

第一个命令不需要桌面，第二个检查真实 Tk 按钮并需要显示环境。实验脚本会在本机创建 `测试记录` 文件夹。

可选：生成不同事件概率的窗口对比图：

```shell
python -m pip install -r requirements-plot.txt
python run_experiments.py
python plot_comparison.py
```

输出为本机 `截图/07_cwnd_probability_comparison.svg`。保存窗口截图是另一项可选功能，需要 Windows 和 Pillow：

```shell
python -m pip install -r requirements-capture.txt
python reno_gui.py --capture ../截图
```

## 文件说明

| 文件 | 用途 |
| --- | --- |
| [REPORT.md](REPORT.md) | 脱敏课程设计报告 |
| [程序/reno_core.py](程序/reno_core.py) | 状态机、场景生成与 CSV 导出 |
| [程序/reno_gui.py](程序/reno_gui.py) | 桌面界面、曲线与手动事件 |
| [程序/test_reno.py](程序/test_reno.py) | 核心逻辑与边界测试 |
| [程序/test_gui.py](程序/test_gui.py) | 界面按钮集成检查 |
| [程序/run_experiments.py](程序/run_experiments.py) | 在本机生成实验数据与汇总 |
| [程序/plot_comparison.py](程序/plot_comparison.py) | 读取生成的数据并绘图 |

## 公开范围

本目录已补充源码、运行说明和原报告中的 6 张运行图。带个人信息的 Word、学校 PDF、原始 ZIP 和独立的原 CSV/JSON 逐步记录未上传。
`.gitignore` 已排除本地生成的记录、截图和缓存；它不替代上传前检查，也不会移除已经提交过的文件。

模型只表示教学状态变化。随机参数是每个决策轮的故障事件概率，不是逐包丢包率；估算指标不是网卡吞吐测速。详细假设见报告和模型说明。

本项目为课程学习材料，借助资料和 AI 辅助实现与整理。

## 原报告截图

原报告中的运行界面和窗口对比图已恢复，见[报告的运行截图章节](REPORT.md#36-运行截图与分析)。图中 RTT 为模拟轮次。
