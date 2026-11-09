from pathlib import Path
import json, statistics
from reno_core import preset, random_run

root=Path(__file__).resolve().parent.parent
output=root/'测试记录';output.mkdir(exist_ok=True)
data={'presets':{},'comparisons':[],'random_runs':[]}
for scene in ['无丢包','轻度丢包','重度丢包']:
    r=preset(scene);r.export_csv(output/f'{scene}.csv')
    data['presets'][scene]=r.summary()
for p in [0,.05,.2]:
    rows=[]
    for seed in range(50):
        r,s=random_run(p,seed=seed,rounds=200)
        rows.append(s);data['random_runs'].append(s)
        if seed==42:r.export_csv(output/f'随机事件概率{p:.2f}_seed42.csv')
    proxies=[r['goodput_proxy'] for r in rows]
    data['comparisons'].append(dict(probability=p,seeds=50,rounds=200,
        mean_goodput_proxy=round(statistics.mean(proxies),3),
        sd_goodput_proxy=round(statistics.stdev(proxies),3),
        mean_retransmissions=round(statistics.mean(x['retransmissions'] for x in rows),3),
        mean_timeouts=round(statistics.mean(x['timeouts'] for x in rows),3)))
(output/'实测结果.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in data.items() if k!='random_runs'},ensure_ascii=False,indent=2))
