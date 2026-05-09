"""
apply_final_features.py
Implementa dos features finales pre-demo:
  1. XSS mitigation — DOMPurify CDN + helper esc() en innerHTML sensibles
  2. Corregir orden rechazada — flujo de edición para órdenes propias rechazadas
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base, 'index.html')

with open(path, encoding='utf-8') as f:
    html = f.read()

results = []

def fix(label, old, new, required=True):
    global html
    c = html.count(old)
    if c == 0:
        msg = f'FAIL [{label}]: old string not found'
        results.append(msg)
        if required:
            print(msg)
        return False
    html = html.replace(old, new, 1)
    results.append(f'OK   [{label}]')
    return True

# ══════════════════════════════════════════════════════════════
# FEATURE 1 — XSS: DOMPurify CDN en <head>
# ══════════════════════════════════════════════════════════════
fix('XSS-01 DOMPurify CDN',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.min.js"></script>'
)

# ══════════════════════════════════════════════════════════════
# FEATURE 1 — XSS: helper esc() justo antes de variables globales
# ══════════════════════════════════════════════════════════════
fix('XSS-02 esc() helper',
    'let currentUser = null, isAdmin = false, userNombre = \'\';',
    '''// Sanitizador XSS — usa DOMPurify si está disponible, fallback manual si no
function esc(s){
  const str=String(s==null?'':s);
  if(typeof DOMPurify!=='undefined') return DOMPurify.sanitize(str,{ALLOWED_TAGS:[],ALLOWED_ATTR:[]});
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

let currentUser = null, isAdmin = false, userNombre = \'\';'''
)

# ══════════════════════════════════════════════════════════════
# FEATURE 1 — XSS: aplicar esc() en renderLista (datos de usuario)
# ══════════════════════════════════════════════════════════════
fix('XSS-03 renderLista esc',
    "    const col4=adm?`<div style=\"font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap\">${o.nombre_solicitante||'—'}</div>`:`<div style=\"font-size:12px\">${o.unidad||'—'}</div>`;",
    "    const col4=adm?`<div style=\"font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap\">${esc(o.nombre_solicitante)||'—'}</div>`:`<div style=\"font-size:12px\">${esc(o.unidad)||'—'}</div>`;"
)

fix('XSS-04 renderLista row esc',
    'return `<div class="${lrcls}"><div class="ft">${o.folio||\'—\'}</div><div style="font-size:11px;color:var(--sec)">${fecha}</div><div style="font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${o.nombre_proveedor||\'—\'}</div>${col4}',
    'return `<div class="${lrcls}"><div class="ft">${esc(o.folio)||\'—\'}</div><div style="font-size:11px;color:var(--sec)">${fecha}</div><div style="font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(o.nombre_proveedor)||\'—\'}</div>${col4}'
)

# ══════════════════════════════════════════════════════════════
# FEATURE 1 — XSS: esc() en renderCatalogoConceptos
# ══════════════════════════════════════════════════════════════
fix('XSS-05 renderCatalogo esc descripcion',
    '        <div style="font-weight:500;line-height:1.4">${c.descripcion}</div>',
    '        <div style="font-weight:500;line-height:1.4">${esc(c.descripcion)}</div>'
)
fix('XSS-06 renderCatalogo esc proveedor',
    '        ${c.proveedor_razon_social||\'<span style="color:var(--sec-l)">Todos</span>\'}',
    '        ${c.proveedor_razon_social?esc(c.proveedor_razon_social):\'<span style="color:var(--sec-l)">Todos</span>\'}'
)

# ══════════════════════════════════════════════════════════════
# FEATURE 1 — XSS: esc() en acBuscarFolio dropdown
# ══════════════════════════════════════════════════════════════
fix('XSS-07 acBuscarFolio esc',
    "    div.innerHTML='<div class=\"ac-main\" style=\"font-family:monospace;font-size:13px\">'+o.folio+'</div>'+\n      '<div class=\"ac-sub\">'+(o.nombre_proveedor||'—')+' · '+(o.unidad||'—')+",
    "    div.innerHTML='<div class=\"ac-main\" style=\"font-family:monospace;font-size:13px\">'+esc(o.folio)+'</div>'+\n      '<div class=\"ac-sub\">'+esc(o.nombre_proveedor||'—')+' · '+esc(o.unidad||'—')+"
)

# ══════════════════════════════════════════════════════════════
# FEATURE 2 — Corregir orden rechazada: global var
# ══════════════════════════════════════════════════════════════
fix('EDIT-01 editandoOrdenId var',
    'let folioEnProceso = false; // true mientras hay folio generado sin guardar',
    'let folioEnProceso = false; // true mientras hay folio generado sin guardar\nlet editandoOrdenId = null;  // null=nueva orden, uuid=editando orden rechazada'
)

# ══════════════════════════════════════════════════════════════
# FEATURE 2 — Botón "Corregir" en renderLista para rechazadas propias
# ══════════════════════════════════════════════════════════════
fix('EDIT-02 renderLista boton corregir',
    '''    const puedeEliminar = !ap && !re;
    const accion=adm&&!ap&&!re
      ?`<button class="btn btn-g" style="font-size:10px;padding:5px 9px;" onclick="abrirOrden('${o.id}',true)">Revisar</button>`
      :`<div style="display:flex;gap:4px;">
        <button class="btn btn-n" style="font-size:10px;padding:5px 9px;" onclick="abrirOrden('${o.id}',false)">Ver</button>
        ${puedeEliminar?`<button class="btn btn-r" style="font-size:10px;padding:5px 9px;" onclick="confirmarEliminar('${o.id}','${o.folio}')">Eliminar</button>`:''}
       </div>`;''',
    '''    const puedeEliminar = !ap && !re;
    const puedeCorregir = re && !adm; // usuario puede corregir sus propias rechazadas
    const accion=adm&&!ap&&!re
      ?`<button class="btn btn-g" style="font-size:10px;padding:5px 9px;" onclick="abrirOrden('${o.id}',true)">Revisar</button>`
      :`<div style="display:flex;gap:4px;">
        <button class="btn btn-n" style="font-size:10px;padding:5px 9px;" onclick="abrirOrden('${o.id}',false)">Ver</button>
        ${puedeCorregir?`<button class="btn btn-a" style="font-size:10px;padding:5px 9px;" onclick="corregirOrden('${o.id}')">Corregir</button>`:''}
        ${puedeEliminar?`<button class="btn btn-r" style="font-size:10px;padding:5px 9px;" onclick="confirmarEliminar('${o.id}','${o.folio}')">Eliminar</button>`:''}
       </div>`;'''
)

# ══════════════════════════════════════════════════════════════
# FEATURE 2 — corregirOrden: también desde modal "Ver" de rechazadas
# ══════════════════════════════════════════════════════════════
fix('EDIT-03 modal footer corregir button',
    '''    footer.innerHTML=`<button class="btn btn-n" onclick="cerrarModal()">Cerrar</button>
      ${isAdmin&&!ap&&!re?`<button class="btn btn-a" onclick="eliminarOrden('${id}')">Eliminar</button>`:''}
      <button class="btn" style="background:#c0392b;color:white;" onclick="generarPDF('${id}')">⬇ PDF</button>`;''',
    '''    footer.innerHTML=`<button class="btn btn-n" onclick="cerrarModal()">Cerrar</button>
      ${re&&!isAdmin?`<button class="btn btn-a" onclick="cerrarModal();corregirOrden('${id}')">✏ Corregir y reenviar</button>`:''}
      ${isAdmin&&!ap&&!re?`<button class="btn btn-a" onclick="eliminarOrden('${id}')">Eliminar</button>`:''}
      <button class="btn" style="background:#c0392b;color:white;" onclick="generarPDF('${id}')">⬇ PDF</button>`;'''
)

# ══════════════════════════════════════════════════════════════
# FEATURE 2 — volverMenu limpia editandoOrdenId
# ══════════════════════════════════════════════════════════════
fix('EDIT-04 volverMenu reset editandoOrdenId',
    'function volverMenu(){\n  folioEnProceso=false;',
    'function volverMenu(){\n  folioEnProceso=false;\n  editandoOrdenId=null;'
)

# ══════════════════════════════════════════════════════════════
# FEATURE 2 — guardarOrden: manejar UPDATE vs INSERT según editandoOrdenId
# ══════════════════════════════════════════════════════════════
fix('EDIT-05 guardarOrden update vs insert',
    '''  const {data:od,error:oe}=await sb.from('ordenes').insert([orden]).select().single();
  if(oe){
    console.error('Error guardando orden:', oe);
    toast('Error al guardar: '+oe.message,true);
    btn.innerHTML='Guardar Orden';btn.disabled=false;return;
  }
  if(!od){toast('Error: no se recibió confirmación de Supabase',true);btn.innerHTML='Guardar Orden';btn.disabled=false;return;}
  const cds=conceptos.filter(c=>c.desc.trim()).map(c=>({orden_id:od.id,consecutivo:c.num,descripcion:c.desc,cantidad_solicitada:c.cantSol,cantidad_entregada:c.cantEnt,precio_unitario:c.pu,importe:c.imp}));
  if(cds.length)await sb.from('conceptos').insert(cds);
  folioEnProceso=false;
  toast('✓ Orden '+folioActual+' guardada');
  btn.innerHTML='Guardar Orden';btn.disabled=false;
  cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();cargarPresupuestos();
  setTimeout(()=>nuevaOrden(),1500);
}''',
    '''  if(editandoOrdenId){
    // ── MODO EDICIÓN: actualizar orden rechazada y reenviar a aprobación ──
    const ordenEdit={...orden, status:'Folio guardado y pendiente de aprobacion'};
    delete ordenEdit.folio;     // conservar folio original
    delete ordenEdit.created_by; // conservar creador original
    const {error:ue}=await sb.from('ordenes').update(ordenEdit).eq('id',editandoOrdenId);
    if(ue){toast('Error al actualizar: '+ue.message,true);btn.innerHTML='Guardar Orden';btn.disabled=false;return;}
    await sb.from('conceptos').delete().eq('orden_id',editandoOrdenId);
    const cdsE=conceptos.filter(c=>c.desc.trim()).map(c=>({orden_id:editandoOrdenId,consecutivo:c.num,descripcion:c.desc,cantidad_solicitada:c.cantSol,cantidad_entregada:c.cantEnt,precio_unitario:c.pu,importe:c.imp}));
    if(cdsE.length)await sb.from('conceptos').insert(cdsE);
    folioEnProceso=false;editandoOrdenId=null;
    toast('✓ Orden corregida y reenviada a aprobación');
    btn.innerHTML='Guardar Orden';btn.disabled=false;
    cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();cargarPresupuestos();
    setTimeout(()=>nuevaOrden(),1500);
  } else {
    // ── MODO NUEVO: insertar orden nueva ──
    const {data:od,error:oe}=await sb.from('ordenes').insert([orden]).select().single();
    if(oe){
      console.error('Error guardando orden:', oe);
      toast('Error al guardar: '+oe.message,true);
      btn.innerHTML='Guardar Orden';btn.disabled=false;return;
    }
    if(!od){toast('Error: no se recibió confirmación de Supabase',true);btn.innerHTML='Guardar Orden';btn.disabled=false;return;}
    const cds=conceptos.filter(c=>c.desc.trim()).map(c=>({orden_id:od.id,consecutivo:c.num,descripcion:c.desc,cantidad_solicitada:c.cantSol,cantidad_entregada:c.cantEnt,precio_unitario:c.pu,importe:c.imp}));
    if(cds.length)await sb.from('conceptos').insert(cds);
    folioEnProceso=false;
    toast('✓ Orden '+folioActual+' guardada');
    btn.innerHTML='Guardar Orden';btn.disabled=false;
    cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();cargarPresupuestos();
    setTimeout(()=>nuevaOrden(),1500);
  }
}'''
)

# ══════════════════════════════════════════════════════════════
# FEATURE 2 — corregirOrden function: insertar antes de toast section
# ══════════════════════════════════════════════════════════════
CORREGIR_FN = r"""
// ══ CORREGIR ORDEN RECHAZADA ══
async function corregirOrden(id){
  toast('Cargando orden...');
  const {data:o}=await sb.from('ordenes').select('*').eq('id',id).single();
  const {data:cs}=await sb.from('conceptos').select('*').eq('orden_id',id).order('consecutivo');
  if(!o){toast('Error al cargar la orden',true);return;}

  // Verificar que es del usuario actual y está rechazada
  if(o.created_by!==currentUser.id){toast('Solo puedes corregir tus propias órdenes',true);return;}
  if(!o.status?.toLowerCase().includes('rechazado')){toast('Solo puedes corregir órdenes rechazadas',true);return;}

  editandoOrdenId=id;
  folioActual=o.folio;

  // Mostrar formulario
  document.getElementById('menu-gestion').style.display='none';
  document.getElementById('form-orden').style.display='block';
  document.getElementById('folio-display').textContent=folioActual;
  folioEnProceso=true;

  // Aviso visual de modo edición
  const membrete=document.querySelector('#form-orden .membrete');
  if(membrete){
    let badge=document.getElementById('edit-mode-badge');
    if(!badge){
      badge=document.createElement('div');
      badge.id='edit-mode-badge';
      badge.style.cssText='background:var(--azul-l);color:var(--azul);font-size:11px;font-weight:600;padding:5px 14px;border-radius:6px;border:1px solid var(--azul);';
      badge.textContent='✏ Modo corrección — se reenviará a aprobación al guardar';
      membrete.after(badge);
    }
  }
  // Cambiar label del botón guardar
  const btnG=document.getElementById('btn-guardar');
  if(btnG)btnG.innerHTML='Corregir y reenviar';

  // Reconstruir objetos sel* desde catálogos estáticos + datos de la orden
  selUnidad=UNIDADES.find(u=>u.unidad===o.unidad)||{unidad:o.unidad,ui:(o.clave_unidad||'').split('-')[0],cc:(o.clave_unidad||'').split('-')[1],jcu:o.jcu};
  selPartida=PARTIDAS.find(p=>p.clave===o.partida)||{clave:o.partida,tipo:o.tipo_partida,descripcion:''};
  selProv=PROVEEDORES_CAT.find(p=>p.razon_social===o.nombre_proveedor)||{razon_social:o.nombre_proveedor,rfc:o.rfc_proveedor||'',domicilio:o.direccion_proveedor||'',ret_isr:false,consecutivo:o.num_proveedor||''};
  selElaboro=o.nombre_solicitante||'';

  // Poblar campos del formulario
  const set=(id,v)=>{const el=document.getElementById(id);if(el)el.value=v||'';};
  set('ac-unidad',o.unidad);
  set('clave-unidad',o.clave_unidad);
  set('jcu',o.jcu);
  set('f-sol',o.fecha_solicitud);
  set('f-emi',o.fecha_emision);
  set('f-rec',o.fecha_recepcion);
  set('origen',o.origen);
  set('ac-elaboro',o.nombre_solicitante);
  set('ac-partida',o.partida);
  set('tipo-partida',o.tipo_partida);
  set('especialidad',o.especialidad);
  set('subespecialidad',o.subespecialidad);
  set('destino',o.destino);
  set('f-ini',o.fecha_inicio);
  set('f-ter',o.fecha_termino);
  set('tiempo',o.tiempo);
  set('f-depto',o.folio_depto);
  set('f-segade',o.folio_segade);
  set('jefe-depto',o.jefe_departamento);
  set('matricula',o.nombre_matricula);
  set('ac-prov',o.nombre_proveedor);
  set('num-prov',o.num_proveedor);
  set('rfc-prov',o.rfc_proveedor);
  set('dom-prov',o.direccion_proveedor);
  set('sel-iva',o.iva_porcentaje);
  const fpn=document.getElementById('firma-prov-nombre');
  if(fpn)fpn.textContent=o.nombre_proveedor||'Proveedor';
  const avp=document.getElementById('aviso-partida');if(avp)avp.style.display='none';

  // Poblar conceptos (hasta 10 filas)
  conceptos=mkC();
  (cs||[]).forEach((c,i)=>{
    if(i<conceptos.length){
      conceptos[i].desc=c.descripcion||'';
      conceptos[i].cantSol=c.cantidad_solicitada||0;
      conceptos[i].cantEnt=c.cantidad_entregada||0;
      conceptos[i].pu=c.precio_unitario||0;
      conceptos[i].imp=c.importe||0;
      conceptos[i].ret5=false; // se recalcula al renderizar
    }
  });
  renderConceptos();
  calcTotales();
}

"""

fix('EDIT-06 corregirOrden function',
    '// ══ R5 TOGGLE ══',
    CORREGIR_FN + '// ══ R5 TOGGLE ══'
)

# ══════════════════════════════════════════════════════════════
# FEATURE 2 — limpiar badge de modo edición al volver al menú
# ══════════════════════════════════════════════════════════════
fix('EDIT-07 volverMenu limpia badge edición',
    'function volverMenu(){\n  folioEnProceso=false;\n  editandoOrdenId=null;',
    '''function volverMenu(){
  folioEnProceso=false;
  editandoOrdenId=null;
  const eb=document.getElementById('edit-mode-badge');if(eb)eb.remove();
  const btnG=document.getElementById('btn-guardar');if(btnG)btnG.innerHTML='Guardar Orden';'''
)

# ══════════════════════════════════════════════════════════════
# Guardar y reportar
# ══════════════════════════════════════════════════════════════
print('\n'.join(results))
ok   = sum(1 for r in results if r.startswith('OK'))
fail = sum(1 for r in results if r.startswith('FAIL'))
print(f'\nTotal: {ok} OK, {fail} FAIL')

if fail == 0:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Saved: {len(html):,} chars')
else:
    print('NOT SAVED — corrige los FAIL antes de guardar')
