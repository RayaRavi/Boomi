from playwright.sync_api import sync_playwright
import json,sys
ids=['appA']+['cert%02d'%i for i in range(1,17)]
res={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,w,h in (('desktop',1280,900),('tablet',820,1100),('android',390,844)):
        pg=b.new_page(viewport={'width':w,'height':h}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.goto('file:///tmp/w/build/index.html'); pg.wait_for_timeout(2000)
        for i in ids:
            pg.evaluate(f"location.hash='#/l/{i}'"); pg.wait_for_timeout(900)
            r=pg.evaluate("""()=>{const v=document.querySelector('#view');const s=v.querySelector('[data-supp]');
              const src=v.querySelector('details.lesson-source-final');
              const order = s&&src ? !!(s.compareDocumentPosition(src)&Node.DOCUMENT_POSITION_FOLLOWING) : null;
              const last=[...v.children].filter(x=>x.tagName!=='SCRIPT').pop();
              return {has:!!s,textLen:s?s.innerText.length:0,order,srcLast:src? (src.nextElementSibling===null || [...v.querySelectorAll('.card')].pop()!==undefined):null,
               overflowX:document.documentElement.scrollWidth>innerWidth+1, docW:document.documentElement.scrollWidth,
               wide:[...v.querySelectorAll('*')].filter(e=>e.getBoundingClientRect().right>innerWidth+2).slice(0,3).map(e=>e.tagName+'.'+e.className)}}""")
            res[(name,i)]=r
        res[(name,'errs')]=errs
        pg.close()
    b.close()
bad=[(k,v) for k,v in res.items() if k[1]!='errs' and (not v['has'] or v['overflowX'] or v['order'] is not True or v['wide'])]
print('problems:',len(bad)); 
for k,v in bad[:12]: print(k,v)
print({k:v for k,v in res.items() if k[1]=='errs'})
print([ (k[1],v['textLen']) for k,v in res.items() if k[0]=='desktop' and k[1]!='errs'])
