"""对实际Tk按钮和状态刷新进行集成检查。"""
from pathlib import Path
import tkinter as tk
from reno_gui import App
from reno_core import FR,CA,SS

root=tk.Tk();app=App(root);root.update()
for _ in range(10):app.buttons['正常推进1 RTT / 新ACK'].invoke()
assert app.model.cwnd==68
app.buttons['重复ACK +1'].invoke()
app.buttons['重复ACK +1'].invoke()
assert app.model.cwnd==68 and app.model.retransmissions==0
app.buttons['重复ACK +1'].invoke()
assert app.model.cwnd==34 and app.model.state==FR
app.buttons['重复ACK +1'].invoke()
assert app.model.cwnd==35
app.buttons['正常推进1 RTT / 新ACK'].invoke()
assert app.model.cwnd==34 and app.model.state==CA
app.buttons['触发超时'].invoke()
assert app.model.cwnd==1 and app.model.state==SS
app.mode.set('标准Reno对照');app.reset()
for _ in range(10):app.buttons['正常推进1 RTT / 新ACK'].invoke()
app.buttons['连续3个重复ACK'].invoke()
assert app.model.cwnd==37
app.probability.set('0.2');app.random_scene()
assert app.model.retransmissions>0
output = Path(__file__).resolve().parent.parent / '测试记录'
output.mkdir(parents=True, exist_ok=True)
app.model.export_csv(output / 'GUI按钮测试导出.csv')
assert len(app.tree.get_children())==len(app.model.history)
root.destroy()
print('GUI集成检查通过：逐次重复ACK、第三次快重传、恢复退出、超时、模式切换、随机场景、CSV导出和日志刷新。')
