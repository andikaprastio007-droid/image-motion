const $=s=>document.querySelector(s);let S={pid:null,vars:[],analysis:null};
function toast(m,t='ok'){const d=document.createElement('div');d.textContent=({ok:'✓ ',warn:'⚠ ',err:'✕ '}[t])+m;$('#toast').append(d);setTimeout(()=>d.remove(),3500)}
async function api(u,o={}){try{const r=await fetch(u,{headers:o.body&&!(o.body instanceof FormData)?{'Content-Type':'application/json'}:{},...o,body:o.body instanceof FormData?o.body:o.body&&JSON.stringify(o.body)});const j=await r.json();if(j.status!=='success')throw new Error(j.message);return j}catch(e){toast(e.message,'err');throw e}}
function show(p){document.querySelectorAll('.page').forEach(e=>e.classList.toggle('on',e.id===p));document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('on',a.dataset.p===p));if(p==='dashboard'||p==='projects')loadProjects();if(p==='settings')health()}
$('#nav').onclick=e=>e.target.dataset.p&&show(e.target.dataset.p);
async function health(){const h=await api('/api/health');$('#hs').textContent=h.ffmpeg?'FFmpeg ✓':'FFmpeg ✕';$('#sinfo').textContent=JSON.stringify(h,null,2);if(!h.ffmpeg)toast(h.ffmpeg_message,'warn')}
$('#file').onchange=async e=>{const f=e.target.files[0];if(!f)return;const fd=new FormData();fd.append('image',f);$('#prev').src=URL.createObjectURL(f);$('#prev').hidden=false;$('#dt').hidden=true;
 try{const r=await api('/api/upload',{method:'POST',body:fd});S.pid=r.project_id;toast('Upload berhasil')}catch{$('#dt').hidden=false}};
$('#drop').ondragover=e=>e.preventDefault();$('#drop').ondrop=e=>{e.preventDefault();$('#file').files=e.dataTransfer.files;$('#file').onchange({target:$('#file')})};
$('#go').onclick=async()=>{if(!S.pid)return toast('Upload gambar dulu','warn');$('#go').disabled=true;$('#go').textContent='Memproses…';
 try{const a=await api('/api/analyze',{method:'POST',body:{project_id:S.pid}});S.analysis=a.analysis;
 const g=await api('/api/generate-prompts',{method:'POST',body:{project_id:S.pid,stock_safe:$('#safe').checked,duration:+$('#dur').value}});
 S.vars=g.variations;checks(g.stock_check);meta(g.stock_metadata);renderVars();toast('10 prompt siap, buka Lab')}catch{}
 $('#go').disabled=false;$('#go').textContent='⚡ ANALISIS + GENERATE DEWA'};
function checks(c){const e=$('#checks');e.hidden=false;e.innerHTML='<b>Potential stock issues</b>'+c.map(x=>`<div class="${x.level==='warn'?'warn':'okc'}">${x.level==='warn'?'⚠':'✓'} ${esc(x.msg)}</div>`).join('')}
function meta(m){const e=$('#meta');e.hidden=false;e.innerHTML=`<b>${esc(m.title)}</b><p>${esc(m.description)}</p>`+m.keywords.map(k=>`<span class="tag">${esc(k)}</span>`).join('')+`<br><button onclick="navigator.clipboard.writeText('${esc(m.title)}\\n${esc(m.description)}\\n${esc(m.keywords.join(', '))}');toast('Disalin')">📋 COPY</button>`}
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function renderVars(){$('#labinfo').textContent=S.pid?'Project '+S.pid:'';$('#vars').innerHTML=S.vars.map((v,i)=>`<div class="glass"><b>${v.id}. ${esc(v.name)}</b> <span class="muted">${esc(v.camera_motion)}</span>
<textarea data-i="${i}">${esc(v.prompt+'\nNEGATIVE PROMPT: '+v.negative_prompt)}</textarea>
<button onclick="cp(${i})">📋 COPY</button> <button onclick="fav(${i})">${v.favorite?'★':'☆'} Favorit</button> <button onclick="vid(${v.id})">🎬 Preview</button><div id="v${v.id}"></div></div>`).join('')}
window.cp=i=>{navigator.clipboard.writeText(document.querySelector(`textarea[data-i="${i}"]`).value);toast('Disalin')};
window.fav=async i=>{S.vars[i].favorite=!S.vars[i].favorite;syncEdits();await api('/api/save-prompts',{method:'POST',body:{project_id:S.pid,variations:S.vars}});renderVars()};
function syncEdits(){document.querySelectorAll('#vars textarea').forEach(t=>{const v=S.vars[t.dataset.i],[p,n]=t.value.split('\nNEGATIVE PROMPT: ');v.prompt=p;if(n!==undefined)v.negative_prompt=n})}
window.vid=async id=>{const b=$('#v'+id);b.textContent='Rendering…';syncEdits();try{await api('/api/save-prompts',{method:'POST',body:{project_id:S.pid,variations:S.vars}});
 const r=await api('/api/generate-video',{method:'POST',body:{project_id:S.pid,variation_id:id,ratio:$('#ratio').value,duration:+$('#dur').value,fps:+$('#fps').value}});
 b.innerHTML=`<video src="${r.video}" controls loop playsinline></video><small class="muted">${esc(r.note)}</small><br><a href="${r.video}" download>⬇ Export MP4</a>`}catch{b.textContent=''}};
$('#regen').onclick=async()=>{if(!S.pid)return;const g=await api('/api/generate-prompts',{method:'POST',body:{project_id:S.pid,stock_safe:$('#safe').checked,duration:+$('#dur').value}});S.vars=g.variations;renderVars();toast('Prompt dibuat ulang')};
async function loadProjects(){const r=await api('/api/projects');const h=r.projects.map(p=>`<div class="glass card"><img src="/api/projects/${p.id}/image" loading="lazy"><div class="muted">${esc(p.original_name||p.id)}<br>${p.videos} video</div><button onclick="openP('${p.id}')">Buka</button> <button onclick="delP('${p.id}')">🗑</button></div>`).join('')||'<p class="muted">Belum ada project.</p>';$('#plist').innerHTML=$('#pr').innerHTML=h}
window.openP=async id=>{const r=await api('/api/projects/'+id);S.pid=id;S.vars=r.variations||[];S.analysis=r.analysis;renderVars();show('lab')};
window.delP=async id=>{if(confirm('Hapus project?')){await api('/api/projects/'+id,{method:'DELETE'});loadProjects()}};
show('dashboard');health();
