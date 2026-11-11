/* Checkpoint 03: exact vector recreations of PDF diagrams (geometry/labels from the PDF), with step highlight + moving indicators. */
(function(){'use strict';
const D=window.__DIAG||[];const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const esc=t=>String(t==null?'':t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function hashId(){const m=location.hash.match(/^#\/l\/(.+)$/);return m?decodeURIComponent(m[1]):null}
function card(d,k,n){const cheat=d.page>=142&&d.page<=149;
 return `<section class="dgx" data-dg="${d.id}"><h3>Exact recreation · PDF page ${d.page}${n>1?` · diagram ${k} of ${n} on this page`:''}${cheat?' · Visual Flow Cheat Sheet':''}</h3>
<p class="dgx-note">Redrawn from the PDF's own vector geometry: same labels, boxes, colours, arrows and positions. Blue dots move along the original arrows. ${d.nodes.length} highlightable stages in reading order.</p>
<div class="dgx-tabs" role="group" aria-label="View"><button class="btn" data-v="svg" aria-pressed="true">Animated recreation</button><button class="btn" data-v="img" aria-pressed="false">Original PDF crop</button><button class="btn" data-v="zoom" aria-pressed="false">Large (scroll)</button></div>
<div class="dgx-stage"><div class="dgx-svg">${d.svg}</div><div class="dgx-img" hidden><img alt="Original PDF diagram from page ${d.page}" loading="lazy" src="${d.img}"></div></div>
<div class="dgx-step" aria-live="polite"></div><div class="sflow-prog"><span></span></div>
<div class="sflow-ctl"><button class="btn" data-a="prev">◀ Previous</button><button class="btn primary" data-a="play">▶ Play</button><button class="btn" data-a="next">Next ▶</button><button class="btn" data-a="restart">↺ Restart</button><label>Speed <select data-a="speed" aria-label="Speed"><option value="4500">Slow</option><option value="3000" selected>Normal (3 s)</option><option value="1800">Fast</option></select></label><button class="btn" data-a="dots" aria-pressed="true">Arrow motion: on</button><span class="muted dgx-cnt"></span></div></section>`}
function wire(root,d){let i=-1,timer=null,speed=3000,playing=false,zoom=false;
 const svg=root.querySelector('svg'),hl=svg.querySelector('.hl'),step=root.querySelector('.dgx-step'),prog=root.querySelector('.sflow-prog span'),cnt=root.querySelector('.dgx-cnt'),pb=root.querySelector('[data-a=play]'),N=d.nodes;
 if(reduced&&svg.pauseAnimations)svg.pauseAnimations();
 function show(k){if(!N.length)return;i=Math.max(0,Math.min(N.length-1,k));const n=N[i];hl.innerHTML=`<rect x="${n.x-2}" y="${n.y-2}" width="${n.w+4}" height="${n.h+4}" rx="6" fill="rgba(56,189,248,.16)" stroke="#0ea5e9" stroke-width="2.2"><animate attributeName="stroke-opacity" values="1;.35;1" dur="1.2s" repeatCount="indefinite"/></rect>`;
  step.innerHTML=`<strong>Stage ${i+1} of ${N.length}</strong><br>${esc(n.text)}`;prog.style.width=((i+1)/N.length*100)+'%';cnt.textContent=`${i+1}/${N.length}`}
 function stop(){playing=false;clearInterval(timer);pb.textContent='▶ Play'}
 function tick(){if(!document.body.contains(root)||document.hidden||i>=N.length-1){stop();return}show(i+1)}
 function play(){if(reduced){show(i+1>=N.length?0:i+1);return}if(i>=N.length-1)show(0);else if(i<0)show(0);playing=true;pb.textContent='⏸ Pause';clearInterval(timer);timer=setInterval(tick,speed)}
 root.addEventListener('click',e=>{const b=e.target.closest('button[data-a],button[data-v]');
  if(b&&b.dataset.v){const v=b.dataset.v;root.querySelectorAll('[data-v]').forEach(x=>x.setAttribute('aria-pressed',String(x===b&&v!=='zoom'||(v==='zoom'&&x===b&&!zoom)||(x.dataset.v==='svg'&&v==='zoom'&&zoom===false?false:false))));
   if(v==='zoom'){zoom=!zoom;root.querySelector('.dgx-stage').classList.toggle('big',zoom);b.setAttribute('aria-pressed',String(zoom));root.querySelector('[data-v=svg]').setAttribute('aria-pressed','true');root.querySelector('.dgx-svg').hidden=false;root.querySelector('.dgx-img').hidden=true;return}
   root.querySelector('.dgx-svg').hidden=v!=='svg';root.querySelector('.dgx-img').hidden=v!=='img';return}
  if(!b)return;const a=b.dataset.a;
  if(a==='play')playing?stop():play();else if(a==='next'){stop();show(i+1)}else if(a==='prev'){stop();show(i<0?0:i-1)}else if(a==='restart'){stop();show(0)}
  else if(a==='dots'){const on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',String(on));b.textContent='Arrow motion: '+(on?'on':'off');on?svg.unpauseAnimations():svg.pauseAnimations()}});
 root.querySelector('[data-a=speed]').onchange=e=>{speed=+e.target.value;if(playing){clearInterval(timer);timer=setInterval(tick,speed)}};
 svg.addEventListener('click',e=>{const r=svg.getBoundingClientRect(),vb=svg.viewBox.baseVal,x=(e.clientX-r.left)/r.width*vb.width,y=(e.clientY-r.top)/r.height*vb.height;let best=-1,ba=1e9;N.forEach((n,j)=>{if(x>=n.x&&x<=n.x+n.w&&y>=n.y&&y<=n.y+n.h&&n.w*n.h<ba){ba=n.w*n.h;best=j}});if(best>=0){stop();show(best)}});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});show(0)}
function mount(){const id=hashId(),v=document.getElementById('view');if(!id||!v)return;const list=D.filter(d=>d.lesson===id);if(!list.length||v.querySelector('[data-dgx="'+id+'"]'))return;
 if(!v.querySelector('h1')||!v.querySelector('.lesson-tools'))return;
 const src=v.querySelector('details.lesson-source-final')||[...v.querySelectorAll('details')].find(x=>/Original PDF source text/.test(x.textContent));
 const wrap=document.createElement('section');wrap.className='dgx-wrap';wrap.dataset.dgx=id;
 const per={};list.forEach(d=>per[d.page]=(per[d.page]||0)+1);const seen={};
 wrap.innerHTML=`<h2>Exact diagram recreations from the PDF</h2>`+list.map(d=>{seen[d.page]=(seen[d.page]||0)+1;return card(d,seen[d.page],per[d.page])}).join('');
 if(src)src.parentNode.insertBefore(wrap,src);else v.appendChild(wrap);
 wrap.querySelectorAll('.dgx').forEach(el=>wire(el,list.find(d=>d.id===el.dataset.dg)))}
let t=null;const sched=()=>{clearTimeout(t);t=setTimeout(mount,90)};const v=document.getElementById('view');
if(v)new MutationObserver(sched).observe(v,{childList:true});addEventListener('hashchange',sched);sched();
})();
