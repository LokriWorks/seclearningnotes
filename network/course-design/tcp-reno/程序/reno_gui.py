"""运行 python reno_gui.py。界面只使用标准库tkinter。"""
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from reno_core import Reno, preset, random_run, SS, CA, FR

class App:
    def __init__(self, root):
        self.root = root
        root.title('题目9  TCP Reno 网络拥塞控制机制模拟器')
        root.geometry('1160x790+70+40')
        root.minsize(1000, 720)
        root.configure(bg='#f2f5f9')
        self.model = Reno()
        self.timer = None
        self.mode = tk.StringVar(value='课程简化规则')
        self.threshold = tk.StringVar(value='64')
        self.scenario = tk.StringVar(value='无丢包')
        self.probability = tk.StringVar(value='0.05')
        self.seed = tk.StringVar(value='42')
        self.buttons = {}
        self.status = tk.StringVar()
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Microsoft YaHei',10), padding=(8,7))
        style.configure('TLabel', font=('Microsoft YaHei',10))
        style.configure('Treeview', font=('Microsoft YaHei',9), rowheight=24)
        style.configure('Treeview.Heading', font=('Microsoft YaHei',9,'bold'))
        tk.Label(root,text='TCP Reno  拥塞控制实验',font=('Microsoft YaHei',21,'bold'),
                 bg='#1d3451',fg='white',anchor='w',padx=22,pady=13).pack(fill='x')
        top=ttk.Frame(root,padding=(16,10));top.pack(fill='x')
        ttk.Label(top,text='规则').pack(side='left')
        ttk.Combobox(top,textvariable=self.mode,values=['课程简化规则','标准Reno对照'],state='readonly',width=15).pack(side='left',padx=6)
        ttk.Label(top,text='初始ssthresh').pack(side='left',padx=(12,3))
        ttk.Entry(top,textvariable=self.threshold,width=7).pack(side='left')
        ttk.Button(top,text='重置并应用',command=self.reset).pack(side='left',padx=8)
        ttk.Combobox(top,textvariable=self.scenario,values=['无丢包','轻度丢包','重度丢包'],state='readonly',width=12).pack(side='left',padx=(15,5))
        ttk.Button(top,text='运行预设场景',command=self.load_preset).pack(side='left')
        ttk.Button(top,text='导出CSV',command=self.export).pack(side='right')
        self.card=tk.Label(root,textvariable=self.status,font=('Microsoft YaHei',12,'bold'),
            bg='white',fg='#1c3959',anchor='w',padx=18,pady=11)
        self.card.pack(fill='x',padx=16,pady=(0,8))
        controls=ttk.Frame(root);controls.pack(fill='x',padx=16,pady=(0,8))
        buttons=[('正常推进1 RTT / 新ACK',lambda:self.act('normal')),
            ('重复ACK +1',lambda:self.act('dup')),
            ('连续3个重复ACK',lambda:self.act('triple')),
            ('触发超时',lambda:self.act('timeout')),
            ('自动运行 / 暂停',self.toggle)]
        for text,fn in buttons:
            button=ttk.Button(controls,text=text,command=fn)
            button.pack(side='left',padx=(0,7));self.buttons[text]=button
        ttk.Label(controls,text='p').pack(side='left')
        ttk.Entry(controls,textvariable=self.probability,width=5).pack(side='left',padx=3)
        ttk.Label(controls,text='种子').pack(side='left')
        ttk.Entry(controls,textvariable=self.seed,width=5).pack(side='left',padx=3)
        ttk.Button(controls,text='随机200轮',command=self.random_scene).pack(side='left',padx=4)
        self.canvas=tk.Canvas(root,bg='white',height=350,highlightthickness=0)
        self.canvas.pack(fill='both',expand=True,padx=16)
        self.canvas.bind('<Configure>',lambda e:self.draw())
        tk.Label(root,text='蓝色实线 cwnd  |  橙色虚线 ssthresh  |  红点 快重传/超时  |  同一RTT可有多个ACK事件',
            font=('Microsoft YaHei',10),bg='#f2f5f9',fg='#3a485a').pack(anchor='w',padx=20,pady=5)
        frame=ttk.Frame(root);frame.pack(fill='x',padx=16,pady=(0,10))
        columns=('step','rtt','event','cwnd','ssthresh','state','dup','retrans')
        self.tree=ttk.Treeview(frame,columns=columns,show='headings',height=7)
        for col,title,width in zip(columns,['事件步','RTT','事件','cwnd','ssthresh','阶段','重复ACK','重传数'],[65,60,375,80,90,100,85,75]):
            self.tree.heading(col,text=title);self.tree.column(col,width=width,anchor='center' if col!='event' else 'w')
        sb=ttk.Scrollbar(frame,orient='vertical',command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set);self.tree.pack(side='left',fill='x',expand=True);sb.pack(side='right',fill='y')
        self.refresh()

    def mode_key(self):return 'course' if self.mode.get()=='课程简化规则' else 'standard'
    def pause(self):
        if self.timer is not None:self.root.after_cancel(self.timer);self.timer=None
    def reset(self):
        try:model=Reno(int(self.threshold.get()),self.mode_key())
        except ValueError as e:messagebox.showerror('参数错误',str(e));return
        self.pause();self.model=model;self.refresh()
    def load_preset(self):
        self.pause();self.threshold.set('64')
        self.model=preset(self.scenario.get(),self.mode_key());self.refresh()
    def act(self,kind):
        if kind=='normal':self.model.normal_rtt()
        elif kind=='dup':self.model.duplicate_ack()
        elif kind=='triple':
            for _ in range(3):self.model.duplicate_ack()
        else:self.model.timeout()
        self.refresh()
    def random_scene(self):
        try:
            model,_=random_run(float(self.probability.get()),int(self.seed.get()),mode=self.mode_key())
        except ValueError as e:messagebox.showerror('参数错误',str(e));return
        self.pause();self.threshold.set('64');self.model=model;self.refresh()
    def toggle(self):
        if self.timer is not None:self.pause()
        else:self.tick()
    def tick(self):
        self.act('normal');self.timer=self.root.after(600,self.tick)
    def export(self):
        path=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV文件','*.csv')])
        if path:self.model.export_csv(path)
    def refresh(self):
        m=self.model
        label='课程简化' if m.mode=='course' else '标准对照'
        self.status.set(f'{label}    cwnd = {m.cwnd} MSS    ssthresh = {m.ssthresh} MSS    {m.state}    RTT = {m.rtt}    重传 = {m.retransmissions}')
        self.tree.delete(*self.tree.get_children())
        for row in m.history:
            self.tree.insert('', 'end',values=(row.step,row.rtt,row.event,row.cwnd,row.ssthresh,row.state,row.dupacks,row.retransmissions))
        children=self.tree.get_children()
        if children:self.tree.see(children[-1])
        self.draw()
    def draw(self):
        c=self.canvas;c.delete('all');w=max(c.winfo_width(),1000);h=max(c.winfo_height(),310)
        left,top,right,bottom=66,32,w-28,h-42
        hist=self.model.history
        xmax=max(10,hist[-1].rtt);ymax=max(10,max(max(x.cwnd,x.ssthresh) for x in hist)*1.15)
        def point(row,key):return (left+(right-left)*row.rtt/xmax,bottom-(bottom-top)*getattr(row,key)/ymax)
        for i in range(6):
            y=bottom-(bottom-top)*i/5
            c.create_line(left,y,right,y,fill='#e4eaf1')
            c.create_text(left-12,y,text=f'{ymax*i/5:.0f}',anchor='e',fill='#536176',font=('Arial',10))
            x=left+(right-left)*i/5
            c.create_text(x,bottom+17,text=f'{xmax*i/5:.0f}',fill='#536176',font=('Arial',10))
        c.create_line(left,top,left,bottom,right,bottom,fill='#96a4b7')
        c.create_text(left,14,text='窗口 / MSS',anchor='w',font=('Microsoft YaHei',10))
        c.create_text(right,bottom+32,text='仿真时间 / RTT',anchor='e',font=('Microsoft YaHei',10))
        for key,color,dash in [('ssthresh','#d48522',(7,4)),('cwnd','#2468ad',None)]:
            if key=='ssthresh':
                # 阈值只在故障事件瞬间改变，使用阶梯线避免暗示缓慢下降。
                pts=list(point(hist[0],key))
                for prev,row in zip(hist,hist[1:]):
                    x,y=point(row,key);_,old_y=point(prev,key)
                    pts.extend([x,old_y,x,y])
            else:pts=[v for row in hist for v in point(row,key)]
            if len(hist)>1:c.create_line(*pts,fill=color,width=2.5,dash=dash)
        for row in hist:
            if '快重传' in row.event or '超时：' in row.event:
                x,y=point(row,'cwnd');c.create_oval(x-4,y-4,x+4,y+4,fill='#be3c3c',outline='white')
        x,y=point(hist[-1],'cwnd');c.create_oval(x-3,y-3,x+3,y+3,fill='#2468ad',outline='')

def capture_scenarios(folder):
    """对真实运行的Tk窗口调用Windows PrintWindow截图。"""
    import ctypes
    from PIL import ImageGrab
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    root=tk.Tk();app=App(root)
    tasks=[('01_no_loss.png','无丢包'),('02_fast_recovery.png','fast'),
           ('03_timeout.png','timeout'),('04_standard.png','standard'),
           ('05_recovery_exit.png','exit'),('06_heavy_loss.png','heavy')]
    def next_task(i=0):
        if i==len(tasks):root.destroy();return
        filename,scene=tasks[i]
        if scene=='无丢包':app.model=preset(scene)
        elif scene=='heavy':app.model=preset('重度丢包')
        else:
            app.model=Reno(mode='standard' if scene=='standard' else 'course')
            for _ in range(10):app.model.normal_rtt()
            if scene=='timeout':app.model.timeout()
            else:
                for _ in range(3):app.model.duplicate_ack()
                if scene=='exit':
                    for _ in range(2):app.model.duplicate_ack()
                    app.model.normal_rtt()
                    for _ in range(5):app.model.normal_rtt()
        app.mode.set('标准Reno对照' if scene=='standard' else '课程简化规则')
        app.scenario.set('重度丢包' if scene in ('timeout','heavy') else '轻度丢包' if scene!='无丢包' else scene)
        app.refresh();root.update_idletasks()
        def shot():
            hwnd=ctypes.windll.user32.GetParent(root.winfo_id())
            ImageGrab.grab(window=hwnd).save(folder/filename)
            root.after(100,lambda:next_task(i+1))
        root.after(650,shot)
    root.after(300,next_task);root.mainloop()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--capture')
    args=parser.parse_args()
    if args.capture:capture_scenarios(args.capture)
    else:
        window=tk.Tk();App(window);window.mainloop()
