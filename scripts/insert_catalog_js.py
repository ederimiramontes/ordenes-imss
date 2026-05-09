"""insert_catalog_js.py — inserts catalog JS functions into index.html before // ══ TOAST ══"""
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html_path = os.path.join(base, 'index.html')

CATALOG_JS = r"""
// ══ CATÁLOGO DE CONCEPTOS (DB) ══

async function cargarCatalogoConceptos() {
  try {
    const {data,error}=await sb.from('catalogo_conceptos')
      .select('*').eq('activo',true).order('partida_clave').order('descripcion').limit(2000);
    if(!error) catalogoConceptosDB=data||[];
  } catch(e){ console.warn('catalogo_conceptos no disponible:',e.message); }
  renderCatalogoConceptos();
}

function renderCatalogoConceptos() {
  const cont=document.getElementById('lista-catalogo-conceptos');
  if(!cont) return;
  let lista=catalogoConceptosDB;
  if(ccFiltroText) lista=lista.filter(c=>c.descripcion.toLowerCase().includes(ccFiltroText));
  if(ccFiltroPartida) lista=lista.filter(c=>c.partida_clave===ccFiltroPartida);
  const cnt=document.getElementById('cc-count');
  if(cnt) cnt.textContent=lista.length+' descripción'+(lista.length!==1?'es':'');
  if(!lista.length){cont.innerHTML='<div class="empty">Sin resultados — usa el formulario de arriba para agregar descripciones</div>';return;}
  const chunk=lista.slice(0,150);
  cont.innerHTML=chunk.map(c=>`
    <div style="display:grid;grid-template-columns:1fr 130px 130px 70px 80px;gap:8px;padding:10px 12px;background:var(--surface);border-radius:var(--radio);border:1px solid var(--borde);margin-bottom:5px;font-size:12px;align-items:center;">
      <div>
        <div style="font-weight:500;line-height:1.4">${c.descripcion}</div>
        ${c.unidad?`<div style="font-size:10px;color:var(--sec)">Unidad: ${c.unidad}</div>`:''}
      </div>
      <div style="font-size:11px;color:var(--verde);font-weight:500">${c.partida_clave}</div>
      <div style="font-size:11px;color:var(--sec);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
        ${c.proveedor_razon_social||'<span style="color:var(--sec-l)">Todos</span>'}
      </div>
      <div style="text-align:center">
        ${c.aplica_ret5?'<span style="font-size:10px;background:var(--warn-l);color:var(--warn);border-radius:4px;padding:2px 6px;white-space:nowrap;">R5/1000</span>':'—'}
      </div>
      <div style="text-align:center">
        ${isAdmin?`<button class="btn btn-r" style="font-size:10px;padding:4px 8px;" onclick="eliminarCatalogoConcepto('${c.id}')">Eliminar</button>`:''}
      </div>
    </div>`).join('');
  if(lista.length>150)
    cont.innerHTML+=`<div class="empty" style="font-size:11px">Mostrando 150 de ${lista.length}. Usa los filtros para ver más.</div>`;
}

function filtrarCatalogo(){
  ccFiltroText=(document.getElementById('cc-f-text')?.value||'').toLowerCase();
  renderCatalogoConceptos();
}
function limpiarFiltroCC(){
  ccFiltroText='';ccFiltroPartida='';
  const t=document.getElementById('cc-f-text');if(t)t.value='';
  const p=document.getElementById('ac-cc-f-partida');if(p)p.value='';
  renderCatalogoConceptos();
}

// Autocomplete unificado para el catálogo
function acCC(tipo,val){
  const q=(val||'').toLowerCase();
  const matchAll=!val||val.trim()==='';
  let listEl,items=[];
  if(tipo==='partida'){
    listEl=document.getElementById('acl-cc-partida');
    items=PARTIDAS.filter(p=>matchAll||p.clave.toLowerCase().includes(q)||p.descripcion.toLowerCase().includes(q)).slice(0,15)
      .map((p,i)=>({lbl:p.clave,sub:p.descripcion.substring(0,50),idx:i,data:p,tipo:'partida'}));
  } else if(tipo==='prov'){
    listEl=document.getElementById('acl-cc-prov');
    items=PROVEEDORES_CAT.filter(p=>matchAll||p.razon_social.toLowerCase().includes(q)||p.rfc.toLowerCase().includes(q)).slice(0,15)
      .map((p,i)=>({lbl:p.razon_social,sub:'RFC: '+p.rfc,idx:i,data:p,tipo:'prov'}));
  } else if(tipo==='unidad-cc'){
    listEl=document.getElementById('acl-cc-unidad');
    items=UNIDADES.filter(u=>matchAll||u.unidad.toLowerCase().includes(q)).slice(0,15)
      .map((u,i)=>({lbl:u.unidad,sub:u.localidad||'',idx:i,data:u,tipo:'unidad-cc'}));
  } else if(tipo==='f-partida'){
    listEl=document.getElementById('acl-cc-f-partida');
    items=PARTIDAS.filter(p=>matchAll||p.clave.toLowerCase().includes(q)||p.descripcion.toLowerCase().includes(q)).slice(0,12)
      .map((p,i)=>({lbl:p.clave,sub:p.descripcion.substring(0,40),idx:i,data:p,tipo:'f-partida'}));
  }
  if(!listEl) return;
  if(!items.length){listEl.classList.remove('open');return;}
  listEl.innerHTML=items.map(it=>`<div class="ac-item" onclick="selCC('${it.tipo}',${it.idx})">
    <div class="ac-main">${highlight(it.lbl,q)}</div>
    ${it.sub?`<div class="ac-sub">${it.sub}</div>`:''}
  </div>`).join('');
  listEl._items=items;
  listEl.classList.add('open');
}

function selCC(tipo,i){
  if(tipo==='partida'){
    const listEl=document.getElementById('acl-cc-partida');
    const it=listEl._items[i];
    document.getElementById('ac-cc-partida').value=it.data.clave;
    document.getElementById('cc-partida-val').value=it.data.clave;
    document.getElementById('cc-partida-desc').value=it.data.descripcion;
    listEl.classList.remove('open');
  } else if(tipo==='prov'){
    const listEl=document.getElementById('acl-cc-prov');
    const it=listEl._items[i];
    document.getElementById('ac-cc-prov').value=it.data.razon_social;
    document.getElementById('cc-prov-val').value=it.data.razon_social;
    listEl.classList.remove('open');
  } else if(tipo==='unidad-cc'){
    const listEl=document.getElementById('acl-cc-unidad');
    const it=listEl._items[i];
    document.getElementById('ac-cc-unidad').value=it.data.unidad;
    document.getElementById('cc-unidad-val').value=it.data.unidad;
    listEl.classList.remove('open');
  } else if(tipo==='f-partida'){
    const listEl=document.getElementById('acl-cc-f-partida');
    const it=listEl._items[i];
    document.getElementById('ac-cc-f-partida').value=it.data.clave;
    ccFiltroPartida=it.data.clave;
    listEl.classList.remove('open');
    renderCatalogoConceptos();
  }
}

async function guardarCatalogoConcepto(){
  const desc=(document.getElementById('cc-descripcion')?.value||'').trim();
  const partida=document.getElementById('cc-partida-val')?.value||'';
  const partidaDesc=document.getElementById('cc-partida-desc')?.value||'';
  const prov=document.getElementById('cc-prov-val')?.value.trim()||null;
  const unidad=document.getElementById('cc-unidad-val')?.value.trim()||null;
  const ret5=document.getElementById('cc-ret5')?.checked||false;
  const precioRaw=document.getElementById('cc-precio')?.value;
  const precio=precioRaw?parseFloat(precioRaw):null;
  if(!desc){toast('La descripción es requerida',true);return;}
  if(!partida){toast('Selecciona una Partida Presupuestal',true);return;}
  const btn=document.getElementById('btn-guardar-cc');
  btn.innerHTML='<span class="spinner"></span>Guardando...';btn.disabled=true;
  const {error}=await sb.from('catalogo_conceptos').insert([{
    descripcion:desc,partida_clave:partida,partida_desc:partidaDesc,
    proveedor_razon_social:prov,unidad,
    aplica_ret5:ret5,precio_referencia:precio,
    created_by:currentUser.id
  }]);
  btn.innerHTML='Agregar al Catálogo';btn.disabled=false;
  if(error){toast('Error: '+error.message,true);return;}
  toast('✓ Descripción agregada al catálogo');
  ['cc-descripcion','ac-cc-partida','ac-cc-prov','ac-cc-unidad','cc-precio'].forEach(id=>{
    const el=document.getElementById(id);if(el)el.value='';
  });
  ['cc-partida-val','cc-prov-val','cc-unidad-val','cc-partida-desc'].forEach(id=>{
    const el=document.getElementById(id);if(el)el.value='';
  });
  document.getElementById('cc-ret5').checked=false;
  await cargarCatalogoConceptos();
}

async function eliminarCatalogoConcepto(id){
  const item=catalogoConceptosDB.find(c=>c.id===id);
  const preview=item?item.descripcion.substring(0,40):'esta descripción';
  if(!confirm('¿Eliminar "'+preview+'..."?\nNo se puede deshacer.')) return;
  const {error}=await sb.from('catalogo_conceptos').delete().eq('id',id);
  if(error){toast('Error: '+error.message,true);return;}
  toast('Descripción eliminada del catálogo');
  catalogoConceptosDB=catalogoConceptosDB.filter(c=>c.id!==id);
  renderCatalogoConceptos();
}

"""

ANCHOR = '// ══ TOAST ══'
with open(html_path, encoding='utf-8') as f:
    content = f.read()

if ANCHOR not in content:
    print('ERROR: anchor not found')
    sys.exit(1)

content2 = content.replace(ANCHOR, CATALOG_JS + ANCHOR, 1)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content2)

print('OK: funciones catálogo insertadas')
print('Size:', len(content2), 'chars')
