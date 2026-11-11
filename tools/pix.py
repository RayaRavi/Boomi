import json
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
import numpy as np
D=json.load(open('/tmp/w/diag/diagrams.json')); res=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    for d in D:
        o=Image.open(f'/tmp/w/diag/crops/{d["id"]}.png').convert('L'); W,H=o.size
        pg.set_viewport_size({'width':W,'height':H})
        svg=d['svg'].replace('<animateMotion','<animateMotion').replace('<g class="dots">','<g class="dots" display="none">')
        pg.set_content(f'<body style="margin:0">{svg.replace("<svg ",f"<svg width={W} height={H} ")}')
        pg.wait_for_timeout(150); pg.screenshot(path='/tmp/w/diag/_r.png',clip={'x':0,'y':0,'width':W,'height':H})
        r=Image.open('/tmp/w/diag/_r.png').convert('L')
        # tolerate small antialias/text-shift: blur-compare via downscale
        a=np.asarray(o.resize((W//4,H//4)),dtype=float); c=np.asarray(r.resize((W//4,H//4)),dtype=float)
        res.append((d['id'],round(float(np.abs(a-c).mean()),2),round(float((np.abs(a-c)>60).mean()*100),2)))
    b.close()
for r in res: print(r)
json.dump(res,open('/tmp/w/diag/pixel_diff.json','w'))
