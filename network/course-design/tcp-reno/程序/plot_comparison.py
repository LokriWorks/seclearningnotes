"""从现有CSV生成窗口对比SVG，需报告制作环境中的reportlab。"""
import csv, math, json
from pathlib import Path
from reportlab.graphics.shapes import Drawing, String, Line
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderSVG
from reportlab.lib import colors

root=Path(__file__).resolve().parent.parent
series=[]
for prob in [0,.05,.2]:
    path=root/'测试记录'/f'随机事件概率{prob:.2f}_seed42.csv'
    with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    points=[(int(x['rtt']),int(x['cwnd'])) for x in rows]
    series.append((prob,points))
palette=['#2468ad','#d57b16','#24854e']
draw=Drawing(900,710)
draw.add(String(450,681,'Congestion-window comparison',fontName='Times-Bold',fontSize=20,textAnchor='middle'))
draw.add(String(450,657,'Course mode | initial cwnd = 1 MSS | initial ssthresh = 64 MSS | seed = 42 | 200 decision rounds',fontName='Times-Roman',fontSize=11,textAnchor='middle'))
maxx=math.ceil(max(points[-1][0] for _,points in series)/50)*50
def panel(y,items,ymax,ystep,title):
    plot=LinePlot();plot.x=83;plot.y=y;plot.width=735;plot.height=216
    plot.data=[points for _,points in items]
    plot.xValueAxis.valueMin=0;plot.xValueAxis.valueMax=maxx;plot.xValueAxis.valueStep=50
    plot.yValueAxis.valueMin=0;plot.yValueAxis.valueMax=ymax;plot.yValueAxis.valueStep=ystep
    for axis in [plot.xValueAxis,plot.yValueAxis]:
        axis.labels.fontName='Times-Roman';axis.labels.fontSize=11
        axis.strokeColor=colors.HexColor('#87919d');axis.visibleGrid=True
        axis.gridStrokeColor=colors.HexColor('#e2e7ed');axis.gridStrokeWidth=.5
    for i,(p,_) in enumerate(items):
        color=palette[[v for v,_ in series].index(p)]
        plot.lines[i].strokeColor=colors.HexColor(color);plot.lines[i].strokeWidth=1.8
        plot.lines[i].symbol=None
    draw.add(plot)
    draw.add(String(83,y+235,title,fontName='Times-Bold',fontSize=13))
    draw.add(String(18,y+110,'cwnd',fontName='Times-Roman',fontSize=11))
    draw.add(String(18,y+96,'(MSS)',fontName='Times-Roman',fontSize=11))
    draw.add(String(450,y-37,'Simulation time (RTT)',fontName='Times-Roman',fontSize=12,textAnchor='middle'))
panel(382,series,math.ceil(max(p[1] for _,pts in series for p in pts)/50)*50,50,'(a) All three probabilities')
panel(87,series[1:],math.ceil(max(p[1] for _,pts in series[1:] for p in pts)/10)*10,10,'(b) Detail of the two lossy scenarios')
for i,((prob,_),color) in enumerate(zip(series,palette)):
    x=185+i*210;draw.add(Line(x,30,x+30,30,strokeColor=colors.HexColor(color),strokeWidth=2))
    draw.add(String(x+40,25,f'p = {prob:.2f}',fontName='Times-Roman',fontSize=12))
out=root/'截图'/'07_cwnd_probability_comparison.svg'
out.parent.mkdir(parents=True, exist_ok=True)
renderSVG.drawToFile(draw,str(out))
summary=[dict(probability=p,final_rtt=pts[-1][0],final_cwnd=pts[-1][1]) for p,pts in series]
(root/'测试记录'/'曲线对比设置.json').write_text(json.dumps(dict(seed=42,rounds=200,series=summary),indent=2),encoding='utf-8')
print(out);print(summary)
