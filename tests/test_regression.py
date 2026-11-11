from playwright.sync_api import sync_playwright
import json
ls=[c['id'] for c in json.load(open('/tmp/w/src/data__chapters.json'))]+[a['id'] for a in json.load(open('/tmp/w/src/data__activities.json'))]
xs=['exam','flash','glossary','planner','ready','sim','trouble']
res={'lessons':len(ls),'fail':[]}
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,w,h in (('desktop',1280,900),('tablet',820,1100),('android',390,844)):
        pg=b.new_page(viewport={'width':w,'height':h}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.goto('file:///tmp/w/build/index.html'); pg.wait_for_timeout(1800)
        for l in ls:
            pg.evaluate(f"location.hash='#/l/{l}'"); pg.wait_for_timeout(700)
            r=pg.evaluate("""()=>{const v=document.querySelector('#view');const src=v.querySelector('details.lesson-source-final');
              const det=[...v.querySelectorAll('details')];const lastCard=[...v.children].filter(e=>e.tagName!=='SCRIPT');
              const srcIdx=lastCard.indexOf(src);
              const after=srcIdx>=0?lastCard.slice(srcIdx+1).map(e=>e.className+'|'+(e.querySelector('h2,h3')?.textContent||'')).filter(t=>!/notes/i.test(t)&&t!=='|'):[];
              return {h1:!!v.querySelector('h1'),src:!!src,after:after.slice(0,3),ox:document.documentElement.scrollWidth>innerWidth+1,
               slides:v.querySelectorAll('.tut img,.tutorial img,[class*=tutorial] img').length}}""")
            if not r['h1'] or not r['src'] or r['ox'] or r['after']: res['fail'].append((name,l,r))
        for x in xs:
            pg.evaluate(f"location.hash='#/x/{x}'"); pg.wait_for_timeout(600)
            r=pg.evaluate("({len:document.querySelector('#view').innerText.length,ox:document.documentElement.scrollWidth>innerWidth+1})")
            if r['len']<100 or r['ox']: res['fail'].append((name,x,r))
        if errs: res['fail'].append((name,'errors',list(set(errs))[:4]))
        pg.close()
    # feature checks desktop
    pg=b.new_page(viewport={'width':1280,'height':900}); pg.goto('file:///tmp/w/build/index.html'); pg.wait_for_timeout(1500)
    pg.evaluate("location.hash='#/l/act03'"); pg.wait_for_timeout(1200)
    feats={}
    feats['bookmark']=(pg.click('#bm'),pg.wait_for_timeout(400),pg.inner_text('#bm'))[2]
    feats['studied']=(pg.click('#dn'),pg.wait_for_timeout(500),pg.inner_text('#dn'))[2]
    feats['notes']=(pg.fill('#nt','hello'),pg.evaluate("JSON.parse(localStorage.getItem('boomiAcademy.v1')).notes.act03"))[1]
    feats['theme']=(pg.click('#themeBtn'),pg.evaluate("document.documentElement.dataset.theme"))[1]
    pg.fill('#search','Disk'); pg.wait_for_timeout(300); feats['search']=pg.evaluate("[...document.querySelectorAll('#side a')].filter(a=>a.getAttribute('href').startsWith('#/l/')).length")
    pg.fill('#search','')
    feats['revision']=(pg.click('#revBtn'),pg.get_attribute('#revBtn','aria-pressed'))[1]
    # tutorial
    feats['tutorial']=pg.evaluate("""()=>{const v=document.querySelector('#view');return {text:[...v.querySelectorAll('summary,h2,h3,.pill')].map(e=>e.textContent.trim()).filter(t=>/tutorial/i.test(t)).slice(0,3),imgs:[...v.querySelectorAll('img')].filter(i=>i.offsetParent).length,controls:[...v.querySelectorAll('button')].map(b=>b.textContent.trim()).filter(t=>/Play|Pause|Previous|Next|Restart/.test(t)).slice(0,6)}}""")
    res['feats']=feats
    b.close()
print(json.dumps(res,indent=1)[:2500])
