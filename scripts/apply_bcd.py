"""
apply_bcd.py — Implementa B (Reportes), C (Zona proveedores), D (CSF)
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
with open(path, encoding='utf-8') as f:
    html = f.read()

ok = skip = fail = 0

def fx(label, old, new):
    global html, ok, fail
    if old not in html:
        print(f'FAIL [{label}]'); fail += 1; return False
    html = html.replace(old, new, 1)
    print(f'OK   [{label}]'); ok += 1; return True

def sk(label):
    global skip
    print(f'SKIP [{label}]'); skip += 1

# ══════════════════════════════════════════════════════════════════
# B — MÓDULO DE REPORTES
# ══════════════════════════════════════════════════════════════════

# 1. CDN Chart.js
fx('B1-chartjs-cdn',
   '<script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>',
   ('<script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'))

# 2. CSS para reportes
fx('B2-css-reportes',
   '.cola-col-hdr{display:grid;grid-template-columns:110px 1fr 100px 90px auto;',
   ('.rp-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;}\n'
    '.rp-chart-box{background:var(--surface);border:1px solid var(--borde);border-radius:12px;'
    'padding:18px 20px;box-shadow:var(--sombra);}\n'
    '.rp-chart-title{font-size:13px;font-weight:600;color:var(--texto);margin-bottom:14px;}\n'
    '.rp-preset{font-family:inherit;font-size:11px;padding:5px 10px;border-radius:6px;'
    'border:1px solid var(--borde);background:var(--surface);color:var(--texto);'
    'cursor:pointer;transition:all 0.15s;}\n'
    '.rp-preset:hover,.rp-preset.active{background:var(--verde);color:white;'
    'border-color:var(--verde);}\n'
    '.cola-col-hdr{display:grid;grid-template-columns:110px 1fr 100px 90px auto;'))

# 3. HTML tab Reportes (admin) — insertar antes del cierre de app-screen
fx('B3-html-tab-reportes',
   '<!-- MODAL DETALLE -->',
   ('<!-- TAB REPORTES (Admin) -->\n'
    '  <div id="content-reportes" style="display:none;">\n'
    '    <div class="page">\n'
    '      <div class="filtros" style="margin-bottom:16px;">\n'
    '        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end;">\n'
    '          <div>\n'
    '            <div style="font-size:11px;font-weight:500;color:var(--sec);margin-bottom:6px;">Período rápido</div>\n'
    '            <div style="display:flex;gap:4px;">\n'
    '              <button class="rp-preset" onclick="setPeriodo(\'semana\',this)">Esta semana</button>\n'
    '              <button class="rp-preset" onclick="setPeriodo(\'mes\',this)">Este mes</button>\n'
    '              <button class="rp-preset active" onclick="setPeriodo(\'bimestre\',this)">Bimestre</button>\n'
    '              <button class="rp-preset" onclick="setPeriodo(\'trimestre\',this)">Trimestre</button>\n'
    '              <button class="rp-preset" onclick="setPeriodo(\'anio\',this)">Este año</button>\n'
    '            </div>\n'
    '          </div>\n'
    '          <div class="field" style="gap:4px;">\n'
    '            <label>Desde</label>\n'
    '            <input type="date" id="rp-desde" oninput="cargarReportes()">\n'
    '          </div>\n'
    '          <div class="field" style="gap:4px;">\n'
    '            <label>Hasta</label>\n'
    '            <input type="date" id="rp-hasta" oninput="cargarReportes()">\n'
    '          </div>\n'
    '          <div class="field" style="gap:4px;">\n'
    '            <label>Partida</label>\n'
    '            <select id="rp-partida" onchange="cargarReportes()" style="font-size:12px;">\n'
    '              <option value="">Todas</option>\n'
    '            </select>\n'
    '          </div>\n'
    '          <div class="field" style="gap:4px;">\n'
    '            <label>Estado</label>\n'
    '            <select id="rp-status" onchange="cargarReportes()" style="font-size:12px;">\n'
    '              <option value="">Todos</option>\n'
    '              <option value="pendiente">Pendiente</option>\n'
    '              <option value="aprobado">Aprobado</option>\n'
    '              <option value="rechazado">Rechazado</option>\n'
    '            </select>\n'
    '          </div>\n'
    '          <button class="btn btn-n" onclick="exportarReporteCSV()" '
    'style="font-size:11px;padding:8px 14px;">Exportar CSV</button>\n'
    '        </div>\n'
    '      </div>\n'
    '      <div class="stats-grid" id="rp-kpis" style="margin-bottom:20px;"></div>\n'
    '      <div class="rp-grid">\n'
    '        <div class="rp-chart-box">\n'
    '          <div class="rp-chart-title">Monto por Partida</div>\n'
    '          <canvas id="chart-partidas"></canvas>\n'
    '        </div>\n'
    '        <div class="rp-chart-box">\n'
    '          <div class="rp-chart-title">Top Proveedores</div>\n'
    '          <canvas id="chart-proveedores"></canvas>\n'
    '        </div>\n'
    '      </div>\n'
    '      <div class="rp-grid">\n'
    '        <div class="rp-chart-box">\n'
    '          <div class="rp-chart-title">Órdenes por Estado</div>\n'
    '          <canvas id="chart-estados" style="max-height:240px;"></canvas>\n'
    '        </div>\n'
    '        <div class="rp-chart-box">\n'
    '          <div class="rp-chart-title">Top Unidades por Monto</div>\n'
    '          <canvas id="chart-unidades"></canvas>\n'
    '        </div>\n'
    '      </div>\n'
    '    </div>\n'
    '  </div>\n\n'
    '<!-- MODAL DETALLE -->'))

# 4. ALL_TABS: agregar 'reportes'
fx('B4-alltabs-reportes',
   "const ALL_TABS=['nueva','mis-ordenes','proveedores','presupuesto','aprobaciones','usuarios'];",
   "const ALL_TABS=['nueva','mis-ordenes','proveedores','presupuesto','aprobaciones','usuarios','reportes'];")

# 5. mostrarApp: agregar tab Reportes para admin
fx('B5-mostrarApp-tab-reportes',
   ("    const t1=document.createElement('div');t1.className='tab atab';t1.id='tab-aprobaciones';\n"
    "    t1.innerHTML='Aprobaciones <span class=\"tab-badge\" id=\"badge-admin\">0</span>';\n"
    "    t1.onclick=()=>showTab('aprobaciones');tabs.appendChild(t1);"),
   ("    const t1=document.createElement('div');t1.className='tab atab';t1.id='tab-aprobaciones';\n"
    "    t1.innerHTML='Aprobaciones <span class=\"tab-badge\" id=\"badge-admin\">0</span>';\n"
    "    t1.onclick=()=>showTab('aprobaciones');tabs.appendChild(t1);\n"
    "    const tRp=document.createElement('div');tRp.className='tab atab';tRp.id='tab-reportes';\n"
    "    tRp.textContent='Reportes';tRp.onclick=()=>showTab('reportes');tabs.appendChild(tRp);"))

# 6. showTab: cargar reportes
fx('B6-showTab-reportes',
   "  if(tab==='presupuesto'){cargarPresupuestos();}",
   ("  if(tab==='presupuesto'){cargarPresupuestos();}\n"
    "  if(tab==='reportes'){cargarReportes();}"))

# 7. JS: funciones de reportes
REPORTES_JS = '''
// ══ MÓDULO DE REPORTES ══
let _chartInstances={};

function setPeriodo(tipo,btn){
  document.querySelectorAll('.rp-preset').forEach(b=>b.classList.remove('active'));
  if(btn)btn.classList.add('active');
  const hoy=new Date(),desde=new Date(hoy);
  if(tipo==='semana') desde.setDate(hoy.getDate()-7);
  else if(tipo==='mes') desde.setMonth(hoy.getMonth()-1);
  else if(tipo==='bimestre') desde.setMonth(hoy.getMonth()-2);
  else if(tipo==='trimestre') desde.setMonth(hoy.getMonth()-3);
  else if(tipo==='anio') desde.setFullYear(hoy.getFullYear()-1);
  document.getElementById('rp-desde').value=desde.toISOString().split('T')[0];
  document.getElementById('rp-hasta').value=hoy.toISOString().split('T')[0];
  cargarReportes();
}

async function cargarReportes(){
  const desde=document.getElementById('rp-desde')?.value;
  const hasta=document.getElementById('rp-hasta')?.value;
  const partida=document.getElementById('rp-partida')?.value;
  const status=document.getElementById('rp-status')?.value;

  // Poblar select de partidas si está vacío
  const selP=document.getElementById('rp-partida');
  if(selP&&selP.options.length<=1){
    PARTIDAS.forEach(p=>{
      const o=document.createElement('option');
      o.value=p.clave;o.textContent=p.clave+' — '+p.descripcion.substring(0,30);
      selP.appendChild(o);
    });
  }

  let query=sb.from('ordenes')
    .select('id,folio,fecha_solicitud,partida,nombre_proveedor,unidad,total,status')
    .neq('status','borrador');
  if(desde) query=query.gte('fecha_solicitud',desde);
  if(hasta) query=query.lte('fecha_solicitud',hasta);
  if(partida) query=query.eq('partida',partida);
  if(status) query=query.ilike('status','%'+status+'%');

  const {data}=await query.limit(2000);
  const ords=data||[];
  renderRpKPIs(ords);
  renderChart('chart-partidas','bar',agrupar(ords,'partida','total',8),'Monto','#059669');
  renderChart('chart-proveedores','bar',agrupar(ords,'nombre_proveedor','total',6,20),'Monto','#2563eb');
  renderChartEstados(ords);
  renderChart('chart-unidades','bar',agrupar(ords,'unidad','total',8),'Monto','#047857');
}

function agrupar(ords,campo,val,top,truncLen){
  const map={};
  ords.forEach(o=>{if(o[campo])map[o[campo]]=(map[o[campo]]||0)+(o[val]||0);});
  return Object.entries(map).sort((a,b)=>b[1]-a[1]).slice(0,top)
    .map(([k,v])=>({label:truncLen&&k.length>truncLen?k.substring(0,truncLen)+'…':k,value:v}));
}

function renderRpKPIs(ords){
  const total=ords.length;
  const apro=ords.filter(o=>o.status?.toLowerCase().includes('aprobado')).length;
  const monto=ords.reduce((s,o)=>s+(o.total||0),0);
  const prom=total>0?monto/total:0;
  const el=document.getElementById('rp-kpis');
  if(!el)return;
  el.innerHTML=
    '<div class="stat-card"><div class="stat-num">'+total+'</div><div class="stat-lbl">Órdenes en período</div></div>'+
    '<div class="stat-card s-vd"><div class="stat-num">'+apro+'</div><div class="stat-lbl">Aprobadas</div></div>'+
    '<div class="stat-card s-az"><div class="stat-num" style="font-size:18px">'+fmt(monto)+'</div><div class="stat-lbl">Monto total</div></div>'+
    '<div class="stat-card"><div class="stat-num" style="font-size:18px">'+fmt(prom)+'</div><div class="stat-lbl">Promedio por orden</div></div>';
}

function renderChart(id,type,data,label,color){
  if(_chartInstances[id]){_chartInstances[id].destroy();delete _chartInstances[id];}
  const canvas=document.getElementById(id);
  if(!canvas||typeof Chart==='undefined')return;
  _chartInstances[id]=new Chart(canvas.getContext('2d'),{
    type,
    data:{
      labels:data.map(d=>d.label),
      datasets:[{label,data:data.map(d=>d.value),
        backgroundColor:color,borderRadius:4,borderWidth:0}]
    },
    options:{
      responsive:true,
      plugins:{legend:{display:false}},
      scales:{y:{beginAtZero:true,ticks:{callback:v=>'$'+v.toLocaleString('es-MX',{maximumFractionDigits:0})}}}
    }
  });
}

function renderChartEstados(ords){
  if(_chartInstances['chart-estados']){_chartInstances['chart-estados'].destroy();}
  const canvas=document.getElementById('chart-estados');
  if(!canvas||typeof Chart==='undefined')return;
  const pend=ords.filter(o=>o.status?.toLowerCase().includes('pendiente')).length;
  const apro=ords.filter(o=>o.status?.toLowerCase().includes('aprobado')).length;
  const rech=ords.filter(o=>o.status?.toLowerCase().includes('rechazado')).length;
  _chartInstances['chart-estados']=new Chart(canvas.getContext('2d'),{
    type:'doughnut',
    data:{
      labels:['Pendiente','Aprobado','Rechazado'],
      datasets:[{data:[pend,apro,rech],
        backgroundColor:['#d97706','#059669','#dc2626'],
        borderWidth:2,borderColor:'#fff'}]
    },
    options:{responsive:true,plugins:{legend:{position:'bottom',labels:{font:{size:11}}}}}
  });
}

function exportarReporteCSV(){
  const desde=document.getElementById('rp-desde')?.value||'';
  const hasta=document.getElementById('rp-hasta')?.value||'';
  // Reusar la función exportCSV existente con filtro de fechas
  sb.from('ordenes').select('folio,fecha_solicitud,unidad,nombre_proveedor,partida,total,status')
    .neq('status','borrador')
    .gte('fecha_solicitud',desde||'2020-01-01')
    .lte('fecha_solicitud',hasta||'2099-12-31')
    .limit(5000)
    .then(({data})=>{
      if(!data||!data.length){toast('Sin datos para exportar',true);return;}
      const cols=['folio','fecha_solicitud','unidad','nombre_proveedor','partida','total','status'];
      const csv=[cols.join(','),...data.map(r=>cols.map(c=>`"${(r[c]||'').toString().replace(/"/g,'""')}"`).join(','))].join('\n');
      const a=document.createElement('a');
      a.href='data:text/csv;charset=utf-8,﻿'+encodeURIComponent(csv);
      a.download='reporte_ordenes_'+desde+'_'+hasta+'.csv';
      a.click();
      toast('CSV exportado');
    });
}

'''
fx('B7-reportes-js', '// ══ COLA RAPIDA ══', REPORTES_JS + '// ══ COLA RAPIDA ══')

# 8. Inicializar reportes con período por defecto al abrir tab
fx('B8-init-periodo',
   "  if(tab==='reportes'){cargarReportes();}",
   ("  if(tab==='reportes'){\n"
    "    if(!document.getElementById('rp-desde').value) setPeriodo('bimestre');\n"
    "    else cargarReportes();\n"
    "  }"))

# ══════════════════════════════════════════════════════════════════
# C — FILTRO PROVEEDORES POR ZONA
# ══════════════════════════════════════════════════════════════════

# 9. acSearch prov: priorizar por zona cuando hay unidad seleccionada
fx('C1-acSearch-zona',
   "  } else if(tipo==='prov'){\n"
   "    items=PROVEEDORES_CAT.filter(p=>matchAll||p.razon_social.toLowerCase().includes(q)||p.rfc.toLowerCase().includes(q)).slice(0,20).map(p=>({\n"
   "      main:p.razon_social, sub:'RFC: '+p.rfc, val:p.razon_social, data:p\n"
   "    }));",
   ("  } else if(tipo==='prov'){\n"
    "    const localidad=selUnidad?.localidad||'';\n"
    "    let provPool=PROVEEDORES_CAT.filter(p=>matchAll||p.razon_social.toLowerCase().includes(q)||p.rfc.toLowerCase().includes(q));\n"
    "    if(localidad){\n"
    "      // Proveedores con zona que incluye la localidad primero, luego sin zona (statewide)\n"
    "      provPool.sort((a,b)=>{\n"
    "        const aOk=!a.zona||a.zona.includes(localidad);\n"
    "        const bOk=!b.zona||b.zona.includes(localidad);\n"
    "        return (aOk===bOk)?0:aOk?-1:1;\n"
    "      });\n"
    "    }\n"
    "    items=provPool.slice(0,20).map(p=>({\n"
    "      main:p.razon_social,\n"
    "      sub:'RFC: '+p.rfc+(p.zona&&localidad&&!p.zona.includes(localidad)?' · Fuera de zona':''),\n"
    "      val:p.razon_social, data:p\n"
    "    }));"))

# 10. Zona en el formulario de solicitar proveedor
fx('C2-zona-en-form-prov',
   '            <div class="field c3" style="flex-direction:row;align-items:flex-end;justify-content:flex-end;">\n'
   '              <button class="btn btn-g" onclick="solicitarProveedor()">Enviar Solicitud</button>\n'
   '            </div>',
   ('            <div class="field">\n'
    '              <label>Zona de operación</label>\n'
    '              <select id="np-zona" style="font-size:13px;">\n'
    '                <option value="">Todo Baja California</option>\n'
    '                <option value="M">Solo Mexicali</option>\n'
    '                <option value="T">Solo Tijuana</option>\n'
    '                <option value="E">Solo Ensenada</option>\n'
    '                <option value="M,T">Mexicali y Tijuana</option>\n'
    '                <option value="M,E">Mexicali y Ensenada</option>\n'
    '                <option value="T,E">Tijuana y Ensenada</option>\n'
    '              </select>\n'
    '            </div>\n'
    '            <div class="field c2" style="flex-direction:row;align-items:flex-end;justify-content:flex-end;">\n'
    '              <button class="btn btn-g" onclick="solicitarProveedor()">Enviar Solicitud</button>\n'
    '            </div>'))

# 11. Guardar zona en solicitarProveedor
fx('C3-guardar-zona-prov',
   "  const {error}=await sb.from('solicitudes_proveedores').insert([{\n"
   "    razon_social:nombre,rfc,domicilio:dom,iva_rate:parseFloat(iva),\n"
   "    tipo:'alta',status:'pendiente',solicitado_por:currentUser.id,nombre_solicitante:userNombre\n"
   "  }]);",
   ("  const zona=document.getElementById('np-zona')?.value||null;\n"
    "  const {error}=await sb.from('solicitudes_proveedores').insert([{\n"
    "    razon_social:nombre,rfc,domicilio:dom,iva_rate:parseFloat(iva),zona,\n"
    "    tipo:'alta',status:'pendiente',solicitado_por:currentUser.id,nombre_solicitante:userNombre\n"
    "  }]);"))

# ══════════════════════════════════════════════════════════════════
# D — CONSTANCIA DE SITUACIÓN FISCAL (CSF)
# ══════════════════════════════════════════════════════════════════

# 12. Campo CSF en formulario de solicitar proveedor
fx('D1-csf-input-form',
   '            <div class="field c2"><label>Domicilio</label><input type="text" id="np-dom" placeholder="Calle, número, colonia, ciudad, C.P."></div>',
   ('            <div class="field c2"><label>Domicilio</label><input type="text" id="np-dom" placeholder="Calle, número, colonia, ciudad, C.P."></div>\n'
    '            <div class="field c3">\n'
    '              <label>Constancia de Situación Fiscal <span style="font-weight:400;color:var(--sec)">(PDF, JPG o PNG — máx 5MB)</span></label>\n'
    '              <input type="file" id="np-csf" accept=".pdf,.jpg,.jpeg,.png" '
    'style="font-size:12px;padding:8px;border:1.5px solid var(--borde-strong);border-radius:var(--radio);background:var(--surface);width:100%;">\n'
    '              <span style="font-size:10px;color:var(--sec)">Documento del SAT que acredita el RFC y la situación fiscal del proveedor</span>\n'
    '            </div>'))

# 13. Subir CSF a Supabase Storage al solicitar proveedor
fx('D2-upload-csf',
   "  const zona=document.getElementById('np-zona')?.value||null;\n"
   "  const {error}=await sb.from('solicitudes_proveedores').insert([{\n"
   "    razon_social:nombre,rfc,domicilio:dom,iva_rate:parseFloat(iva),zona,\n"
   "    tipo:'alta',status:'pendiente',solicitado_por:currentUser.id,nombre_solicitante:userNombre\n"
   "  }]);",
   ("  const zona=document.getElementById('np-zona')?.value||null;\n"
    "  // Subir CSF si se adjuntó\n"
    "  let csfUrl=null;\n"
    "  const csfFile=document.getElementById('np-csf')?.files?.[0];\n"
    "  if(csfFile){\n"
    "    const ext=csfFile.name.split('.').pop();\n"
    "    const fname=Date.now()+'_'+rfc.replace(/[^A-Z0-9]/gi,'_')+'.'+ext;\n"
    "    const {data:upData,error:upErr}=await sb.storage.from('constancias').upload(fname,csfFile,{upsert:true});\n"
    "    if(!upErr){\n"
    "      const {data:{publicUrl}}=sb.storage.from('constancias').getPublicUrl(fname);\n"
    "      csfUrl=publicUrl;\n"
    "    }\n"
    "  }\n"
    "  const {error}=await sb.from('solicitudes_proveedores').insert([{\n"
    "    razon_social:nombre,rfc,domicilio:dom,iva_rate:parseFloat(iva),zona,constancia_url:csfUrl,\n"
    "    tipo:'alta',status:'pendiente',solicitado_por:currentUser.id,nombre_solicitante:userNombre\n"
    "  }]);"))

# 14. Badge CSF y link en catálogo de proveedores activos
fx('D3-csf-badge-lista',
   '    <div style="font-weight:500">${p.razon_social}</div><div style="font-size:11px;color:var(--sec)">${p.rfc||\'\'}</div></div>',
   ('    <div style="font-weight:500">${p.razon_social}'
    '${p.constancia_url?\'<span style="background:var(--verde-l);color:var(--verde);font-size:9px;font-weight:600;padding:1px 6px;border-radius:4px;margin-left:6px;">CSF ✓</span>\':\'\'}'
    '</div>'
    '<div style="font-size:11px;color:var(--sec)">${p.rfc||\'\'}'
    '${p.zona?\'<span style="color:var(--sec-l)"> · \'+p.zona+\'</span>\':\'\'}\'</div></div>'))

# 15. Link para descargar/ver CSF en catálogo
fx('D4-csf-link-accion',
   "    <div>${isAdmin?`<button class=\"btn btn-n\" style=\"font-size:10px;padding:4px 10px;\" onclick=\"solicitarBajaProveedor('${p.razon_social}')\">Dar de baja</button>`:'<span style=\"font-size:11px;color:var(--sec)\">Activo</span>'}</div>",
   ("    <div style=\"display:flex;gap:4px;flex-wrap:wrap;\">\n"
    "      ${p.constancia_url?`<a href=\"${p.constancia_url}\" target=\"_blank\" class=\"btn btn-n\" style=\"font-size:10px;padding:4px 8px;\">CSF</a>`:''}\n"
    "      ${isAdmin?`<button class=\"btn btn-n\" style=\"font-size:10px;padding:4px 8px;\" onclick=\"solicitarBajaProveedor('${p.razon_social}')\">Dar de baja</button>`:'<span style=\"font-size:11px;color:var(--sec)\">Activo</span>'}\n"
    "    </div>"))

# GUARDAR SIEMPRE
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'\nTotal: {ok} OK, {skip} SKIP, {fail} FAIL')
print(f'Guardado: {len(html):,} chars')
