from playwright.sync_api import sync_playwright
import json
D=json.load(open('/tmp/w/diag/diagrams.json'))
lessons=sorted(set(d['lesson'] for d in D if d['lesson']))
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,w,h in (('desktop',1280,900),('tablet',820,1100),('android',390,844)):
        pg=b.new_page(viewport={'width':w,'height':h}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.goto('file:///tmp/w/build/index.html'); pg.wait_for_timeout(1800)
        for l in lessons:
            pg.evaluate(f"location.hash='#/l/{l}'"); pg.wait_for_timeout(1000)
            r=pg.evaluate("""()=>{const v=document.querySelector('#view');const w=v.querySelector('.dgx-wrap');const src=v.querySelector('details.lesson-source-final');
             return {n:v.querySelectorAll('.dgx').length,order:w&&src?!!(w.compareDocumentPosition(src)&4):null,ox:document.documentElement.scrollWidth>innerWidth+1,
             svgW:[...v.querySelectorAll('.dgx svg')].every(s=>s.getBoundingClientRect().right<=innerWidth+1)}}""")
            exp=len([d for d in D if d['lesson']==l])
            if r['n']!=exp or r['order'] is not True or r['ox'] or not r['svgW']: bad.append((name,l,r,exp))
        if errs: bad.append((name,'errs',errs[:3]))
        pg.close()
    # interaction
    pg=b.new_page(viewport={'width':1100,'height':900}); pg.goto('file:///tmp/w/build/index.html'); pg.wait_for_timeout(1500)
    pg.evaluate("location.hash='#/l/ch02'"); pg.wait_for_timeout(1200)
    pg.click('.dgx [data-a=next]'); print(pg.inner_text('.dgx-step')[:100])
    pg.click('.dgx [data-a=play]'); pg.wait_for_timeout(3300); print(pg.inner_text('.dgx-cnt'))
    pg.click('.dgx [data-v=img]'); print('img visible',pg.is_visible('.dgx-img img'),'svg hidden',not pg.is_visible('.dgx-svg'))
    pg.click('.dgx [data-v=svg]'); pg.click('.dgx [data-a=dots]'); print(pg.inner_text('.dgx [data-a=dots]'))
    pg.query_selector('.dgx').screenshot(path='/tmp/w/shots/dgx.png')
    pg.evaluate("location.hash='#/l/ch19'"); pg.wait_for_timeout(1500)
    pg.query_selector_all('.dgx')[0].scroll_into_view_if_needed(); pg.query_selector_all('.dgx')[3].screenshot(path='/tmp/w/shots/dgx19.png')
    b.close()
print('problems',bad)
