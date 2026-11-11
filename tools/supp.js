/* Checkpoint 03: renders Appendix A + Certification supplement from extracted PDF structure. Source text stays last. */
(function(){'use strict';
const D=window.__SUPP||{};
const esc=t=>String(t==null?'':t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function store(){try{return (window.AcademyCtx&&window.AcademyCtx.S)||null}catch(e){return null}}
function save(){try{if(typeof Store!=='undefined'&&Store.save)Store.save();else{const s=store();if(s)localStorage.setItem('boomiAcademy.v1',JSON.stringify(s))}}catch(e){}}
function bag(id){const s=store();if(!s)return {};s.supp=s.supp||{};s.supp[id]=s.supp[id]||{};return s.supp[id]}
function hashId(){const m=location.hash.match(/^#\/l\/(.+)$/);return m?decodeURIComponent(m[1]):null}
const FLOW_TABLES={cert02:[0],cert08:[0]};
function short(t){const w=String(t).replace(/\s+/g,' ').split(' ');const s=w.slice(0,4).join(' ');return s+(w.length>4?'…':'')}
/* ---------- animated step flow (topic data comes from the source list/table) ---------- */
let flowSeq=0;
function flowHTML(title,nodes,note){const id='sf'+(++flowSeq);
 const track=nodes.map((n,i)=>`<button type="button" class="sflow-node" data-i="${i}" aria-label="Step ${i+1}: ${esc(n.label)}"><b>${n.num||('Step '+(i+1))}</b><span>${esc(short(n.label))}</span></button>`+(i<nodes.length-1?'<i class="sflow-link" aria-hidden="true"><i></i></i>':'')).join('');
 return `<div class="sflow" data-flow="${id}"><p class="sflow-title">${esc(title)}</p><div class="sflow-track">${track}</div><div class="sflow-prog"><span></span></div><div class="sflow-detail" aria-live="polite"></div><div class="sflow-ctl"><button class="btn" data-a="prev">◀ Previous</button><button class="btn primary" data-a="play">▶ Play</button><button class="btn" data-a="next">Next ▶</button><button class="btn" data-a="restart">↺ Restart</button><label>Speed <select data-a="speed" aria-label="Animation speed"><option value="4500">Slow</option><option value="3000" selected>Normal (3 s)</option><option value="1800">Fast</option></select></label><span class="sflow-count muted"></span></div>${note?`<p class="sflow-note">${esc(note)}</p>`:''}</div>`}
function wireFlow(root,nodes,listEl){
 let i=0,timer=null,speed=3000,playing=false;
 const ns=[...root.querySelectorAll('.sflow-node')],links=[...root.querySelectorAll('.sflow-link')],det=root.querySelector('.sflow-detail'),prog=root.querySelector('.sflow-prog span'),cnt=root.querySelector('.sflow-count'),pb=root.querySelector('[data-a=play]');
 function show(k){i=Math.max(0,Math.min(nodes.length-1,k));ns.forEach((n,j)=>{n.classList.toggle('active',j===i);n.classList.toggle('done',j<i);n.setAttribute('aria-current',j===i?'step':'false')});links.forEach((l,j)=>l.classList.toggle('on',j===i||j===i-1));
  det.innerHTML=`<strong>Step ${i+1} of ${nodes.length}${nodes[i].num&&!/^Step/.test(nodes[i].num)?' · '+esc(nodes[i].num):''}</strong><br>${esc(nodes[i].detail||nodes[i].label)}`;prog.style.width=((i+1)/nodes.length*100)+'%';cnt.textContent=`${i+1}/${nodes.length}`;
  if(listEl)[...listEl.children].forEach((li,j)=>li.classList.toggle('active',j===i))}
 function stop(){playing=false;clearInterval(timer);timer=null;pb.textContent='▶ Play'}
 function tick(){if(!document.body.contains(root)){stop();return}if(document.hidden){stop();return}if(i>=nodes.length-1){stop();return}show(i+1)}
 function play(){if(reduced){show(i>=nodes.length-1?0:i+1);return}if(i>=nodes.length-1)show(0);playing=true;pb.textContent='⏸ Pause';clearInterval(timer);timer=setInterval(tick,speed)}
 root.addEventListener('click',e=>{const b=e.target.closest('[data-a],.sflow-node');if(!b)return;if(b.classList.contains('sflow-node')){stop();show(+b.dataset.i);return}const a=b.dataset.a;
  if(a==='play'){playing?stop():play()}else if(a==='next'){stop();show(i+1)}else if(a==='prev'){stop();show(i-1)}else if(a==='restart'){stop();show(0)}});
 root.querySelector('[data-a=speed]').onchange=e=>{speed=+e.target.value;if(playing){clearInterval(timer);timer=setInterval(tick,speed)}};
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});
 show(0)}
/* ---------- renderers ---------- */
function tbl(head,rows,opts){opts=opts||{};
 return `<div class="supp-tblwrap"><table class="supp-tbl"><thead><tr>${opts.check?'<th>Done</th>':''}${head.map(h=>`<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map((r,ri)=>`<tr>${opts.check?`<td data-label="Done"><input type="checkbox" data-pc="${opts.check}:${ri}" aria-label="Mark row ${ri+1} done"></td>`:''}${r.map((c,ci)=>`<td data-label="${esc(head[ci]||'')}">${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`}
function callout(t){const m=t.match(/^((?:Memory cue|Scenario|Model approach|Concept to remember|Exam-information caution|Scope discipline|Important|Example|Safety|Scoring|EDITORIAL NOTE|FINAL TIP|Suggested readiness gate[^:]*|Current official[^:]*|Do not treat[^.]*\.?):?)\s*(.*)$/s);
 const warn=/caution|Safety|Important|Scope discipline|EDITORIAL|Do not/.test(t.slice(0,40));
 if(m&&m[2]&&/:\s*$|^[A-Z][a-zA-Z\- ]+:/.test(m[1]+':'))return `<div class="supp-callout${warn?' warn':''}"><b class="lbl">${esc(m[1].replace(/:$/,''))}</b>${esc(m[2])}</div>`;
 return `<div class="supp-callout${warn?' warn':''}">${esc(t)}</div>`}
function discHTML(head,rows){return `<div class="disc">${rows.map(r=>`<article class="disc-item"><h3>${esc(r[0])}. ${esc(r[1])}</h3><div class="disc-cols"><div><small>${esc(head[2]||'Source A says')}</small>${esc(r[2])}</div><div><small>${esc(head[3]||'Source B says')}</small>${esc(r[3])}</div><div class="h"><small>${esc(head[4]||'How this book handles it')}</small>${esc(r[4])}</div></div></article>`).join('')}</div>`}
function listHTML(items,lid,startIdx,kind){
 return `<ol class="supp-list" data-kind="${kind}">${items.map((s,k)=>{const idx=startIdx+k;
  if(kind==='check')return `<li><label><input type="checkbox" data-lc="${lid}:${idx}"><span class="tx">${esc(s.text)}</span></label></li>`;
  if(kind==='step')return `<li><span class="n">${k+1}</span><span class="tx">${esc(s.text)}</span></li>`;
  if(kind==='memory')return `<li><span class="n">${k+1}</span><span class="tx"><strong>${esc(s.text)}</strong></span></li>`;
  if(s.url)return `<li><span class="dot"></span><span class="tx">${esc(s.text)}</span><a class="go" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">Open official resource ↗</a></li>`;
  return `<li><span class="dot"></span><span class="tx">${esc(s.text)}</span></li>`}).join('')}</ol>`}
function mcqHTML(items,lid){const b=bag(lid);b.exam=b.exam||{};
 const answered=Object.keys(b.exam).length,score=Object.keys(b.exam).filter(k=>b.exam[k]===items[k-1].a).length;
 return `<div class="xbar"><strong id="xs">Score ${score} / ${answered} answered · ${items.length} questions</strong><span><button class="btn" id="xr">Reset answers</button></span></div>`+items.map((q,qi)=>`<article class="xq" data-q="${q.n}"><h3>Q${q.n}. ${esc(q.q)}</h3>${q.o.map((o,oi)=>`<button type="button" class="xopt" data-o="${oi}"><b>${'ABCD'[oi]}.</b> ${esc(o)}</button>`).join('')}<div class="xexp" hidden></div></article>`).join('')}
function scenHTML(items,lid){return items.map((s,i)=>`<article class="supp-card sc" data-sc="${i}"><h3>${esc(s.title)}</h3><label class="muted" for="sc${i}">Your first diagnostic action and evidence (saved locally):</label><textarea id="sc${i}" data-sn="${i}" placeholder="Write your approach before revealing the model answer."></textarea><p><button class="btn" data-rev="${i}" aria-expanded="false">Reveal model approach</button></p><div class="rev" hidden><div class="supp-callout"><b class="lbl">Model approach</b>${esc(s.model)}</div><div class="supp-callout warn"><b class="lbl">Concept to remember</b>${esc(s.concept)}</div></div></article>`).join('')}
function scoreHTML(sec,lid){const b=bag(lid);b.score=b.score||{};
 return `<div class="supp-card"><h2>Interactive readiness scorecard</h2><p class="muted">Rate each domain 0–4 using the scoring scale below. Your ratings are stored only in this browser.</p>${sec.rows.map((r,i)=>`<div class="score-row"><strong>${esc(r[0])}</strong><span><input type="range" min="0" max="4" step="1" value="${b.score[i]==null?0:b.score[i]}" data-sr="${i}" aria-label="Score for ${esc(r[0])}"> <span class="score-out" data-so="${i}">${b.score[i]==null?0:b.score[i]}</span> / 4</span><span class="ev">${esc(r[2])}</span></div>`).join('')}<div class="supp-callout" id="scsum" aria-live="polite"></div></div>`}
function renderLesson(id){const secs=D[id];if(!secs)return null;const pages=secs.reduce((a,s)=>s.page?[Math.min(a[0],s.page),Math.max(a[1],s.page)]:a,[999,0]);
 const isApp=id==='appA';let h=`<div class="supp-wrap" data-supp="${id}"><section class="supp-hero"><span class="pill">Structured learning · ${isApp?'Source-aligned editorial notes':'Certification supplement (additional coaching, not official exam content)'} · PDF pages ${pages[0]}–${pages[1]}</span>`;
 let open=false,stepFlows=[],tblIdx=0,i=0;const flows=[];
 {let k=secs.findIndex(x=>x.t==='h1');if(k>=0&&secs.slice(0,k).every(x=>x.t==='p')&&k<=6){secs.slice(0,k).forEach(x=>{h+=`<p class="muted">${esc(x.text)}</p>`});h+=`<h2>${esc(secs[k].text)}</h2>`;i=k+1;
   while(i<secs.length&&secs[i].t==='p'&&secs[i].page===secs[k].page&&secs[i-1].t==='p'&&k===0&&false){i++}}}
 h+='</section>';
 const openCard=t=>{if(open)h+='</section>';h+=`<section class="supp-card">${t?`<h2>${esc(t)}</h2>`:''}`;open=true};
 openCard('');
 while(i<secs.length){const s=secs[i];
  if(s.t==='h1'){h+=`<h2>${esc(s.text)}</h2>`;i++;continue}
  if(s.t==='h2'){openCard(s.text);i++;continue}
  if(s.t==='h3'){h+=`<h3>${esc(s.text)}</h3>`;i++;continue}
  if(s.t==='p'){h+=`<p>${esc(s.text)}</p>`;i++;continue}
  if(s.t==='callout'){h+=callout(s.text);i++;continue}
  if(s.t==='code'){h+=`<pre class="supp-code">${esc(s.text)}</pre>`;i++;continue}
  if(s.t==='li'){const g=[];const start=i;const kind=s.check?'check':s.step?'step':s.memory?'memory':'bullet';
   while(i<secs.length&&secs[i].t==='li'&&((secs[i].check?'check':secs[i].step?'step':secs[i].memory?'memory':'bullet')===kind)){g.push(secs[i]);i++}
   if(kind==='step'){const key='f'+flows.length;h+=flowHTML('Animated flow · '+(secs.slice(0,start).reverse().find(x=>x.t==='h2'||x.t==='h3')||{text:'Sequence'}).text,g.map(x=>({label:x.text,detail:x.text})),'Built from the numbered/bulleted sequence in the source pages; conceptual training animation, no live Boomi connection.')+'<!--FL'+flows.length+'-->';h+=listHTML(g,id,start,kind);flows.push({nodes:g.map(x=>({label:x.text,detail:x.text}))})}
   else if(kind==='memory'){const key='f'+flows.length;h+=listHTML(g,id,start,kind)}
   else h+=listHTML(g,id,start,kind);continue}
  if(s.t==='table'){const ti=tblIdx++;
   if(id==='appA'&&s.rows.length>=10){h+=discHTML(s.head,s.rows)}
   else if((FLOW_TABLES[id]||[]).includes(ti)){const nodes=s.rows.map((r,k)=>({label:r[0],num:'Stage '+(k+1),detail:r.slice(0,3).map((c,k)=>(s.head[k]?s.head[k]+': ':'')+c).join(' — ')}));h+=flowHTML('Animated flow · '+s.head[0]+' to '+s.head[s.head.length-1],nodes,'Stages are the table rows from the source page, in source order; conceptual training animation.')+'<!--FL'+flows.length+'-->';flows.push({nodes});h+=tbl(s.head,s.rows)}
   else h+=tbl(s.head,s.rows,id==='cert12'?{check:'plan'+ti}:null);
   i++;continue}
  if(s.t==='scorecard'){if(open){h+='</section>';open=false}h+=scoreHTML(s,id);i++;continue}
  if(s.t==='mcq'){h+=mcqHTML(s.items,id);i++;continue}
  if(s.t==='scenarios'){if(open){h+='</section>';open=false}h+=scenHTML(s.items,id);i++;continue}
  i++}
 if(open)h+='</section>';h+='</div>';h=h.replace(/<section class="supp-card"><\/section>/g,'');
 return {html:h,flows,secs}}
function wire(root,res,id){const b=bag(id);
 res.flows.forEach((f,k)=>{const fr=root.querySelectorAll('.sflow')[k];if(!fr)return;let list=fr.nextElementSibling;while(list&&!(list.classList&&list.classList.contains('supp-list')))list=list.nextElementSibling&&!list.nextElementSibling.classList.contains('sflow')?list.nextElementSibling:null;wireFlow(fr,f.nodes,list&&list.dataset.kind==='step'?list:null)});
 root.querySelectorAll('[data-lc]').forEach(cb=>{b.checks=b.checks||{};const k=cb.dataset.lc;cb.checked=!!b.checks[k];cb.closest('li').classList.toggle('checked',cb.checked);cb.onchange=()=>{b.checks[k]=cb.checked;cb.closest('li').classList.toggle('checked',cb.checked);save()}});
 root.querySelectorAll('[data-pc]').forEach(cb=>{b.plan=b.plan||{};const k=cb.dataset.pc;cb.checked=!!b.plan[k];cb.onchange=()=>{b.plan[k]=cb.checked;save()}});
 const items=((res.secs.find(s=>s.t==='mcq')||{}).items)||[];
 if(items.length){const ex=b.exam=b.exam||{};
  const upd=()=>{const a=Object.keys(ex).length,sc=Object.keys(ex).filter(k=>ex[k]===items[k-1].a).length;root.querySelector('#xs').textContent=`Score ${sc} / ${a} answered · ${items.length} questions`};
  const paint=card=>{const q=items[card.dataset.q-1],pick=ex[q.n];if(pick==null)return;card.querySelectorAll('.xopt').forEach((o,oi)=>{o.disabled=true;o.classList.toggle('ok',oi===q.a);o.classList.toggle('bad',oi===pick&&pick!==q.a)});const e=card.querySelector('.xexp');e.hidden=false;e.innerHTML=`<strong>${pick===q.a?'Correct.':'Not quite.'}</strong> Correct answer: ${'ABCD'[q.a]}. ${esc(q.e)}`};
  root.querySelectorAll('.xq').forEach(card=>{paint(card);card.querySelectorAll('.xopt').forEach(o=>o.onclick=()=>{ex[card.dataset.q]=+o.dataset.o;save();paint(card);upd()})});
  root.querySelector('#xr').onclick=()=>{Object.keys(ex).forEach(k=>delete ex[k]);save();root.querySelectorAll('.xq').forEach(card=>{card.querySelectorAll('.xopt').forEach(o=>{o.disabled=false;o.classList.remove('ok','bad')});const e=card.querySelector('.xexp');e.hidden=true;e.textContent=''});upd()};upd()}
 root.querySelectorAll('[data-rev]').forEach(btn=>btn.onclick=()=>{const r=btn.closest('.sc').querySelector('.rev');r.hidden=!r.hidden;btn.setAttribute('aria-expanded',String(!r.hidden));btn.textContent=r.hidden?'Reveal model approach':'Hide model approach'});
 root.querySelectorAll('[data-sn]').forEach(t=>{b.notes=b.notes||{};t.value=b.notes[t.dataset.sn]||'';t.oninput=()=>{b.notes[t.dataset.sn]=t.value;save()}});
 const sc=res.secs.find(s=>s.t==='scorecard');
 if(sc){b.score=b.score||{};const upd=()=>{const v=sc.rows.map((r,i)=>b.score[i]==null?0:+b.score[i]),avg=v.reduce((a,c)=>a+c,0)/v.length,low=sc.rows.filter((r,i)=>v[i]<3).map(r=>r[0]);root.querySelector('#scsum').innerHTML=`<b class="lbl">Your current result</b>Average ${avg.toFixed(2)} / 4 · lowest domain score ${Math.min(...v)} · ${low.length?'domains below 3: '+esc(low.join('; ')):'no domain below 3'}. Compare with the readiness gate quoted below; it is a study recommendation, not an official Boomi passing score.`};
  root.querySelectorAll('[data-sr]').forEach(r=>r.oninput=()=>{b.score[r.dataset.sr]=+r.value;root.querySelector(`[data-so="${r.dataset.sr}"]`).textContent=r.value;save();upd()});upd()}}
function mount(){const id=hashId();const v=document.getElementById('view');if(!id||!v||!D[id])return;if(v.querySelector('[data-supp="'+id+'"]'))return;
 if(!v.querySelector('h1')||!v.querySelector('.lesson-tools'))return;  /* lesson not rendered yet */
 const src=v.querySelector('details.lesson-source-final')||[...v.querySelectorAll('details')].find(d=>/Original PDF source text/.test(d.textContent));
 const old=v.querySelector('[data-supp]');if(old)old.remove();
 const res=renderLesson(id);if(!res)return;const holder=document.createElement('div');holder.innerHTML=res.html;const root=holder.firstElementChild;
 const anchor=src||v.querySelector('.card .src')?.closest('details');
 if(anchor)anchor.parentNode.insertBefore(root,anchor);else v.appendChild(root);
 /* the generic "Original source reader" tag line is redundant once structured content exists */
 wire(root,res,id)}
let t=null;const sched=()=>{clearTimeout(t);t=setTimeout(mount,60)};
const v=document.getElementById('view');
if(v)new MutationObserver(sched).observe(v,{childList:true});
addEventListener('hashchange',sched);sched();
window.__suppMount=mount;
})();
