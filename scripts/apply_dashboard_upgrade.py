"""
apply_dashboard_upgrade.py
Implementa:
  1. CSS skeleton screens + quick-action styles
  2. CDN qrcode.js para QR en PDF
  3. cambiarStatus: acepta comentario por parámetro (inline actions)
  4. aprobarInline / rechazarInline functions
  5. renderLista admin: botones inline ✓ ✗ en filas pendientes
  6. Cola de aprobación rápida en tab Aprobaciones
  7. renderColaRapida() function
  8. QR en PDF
"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
with open(path, encoding='utf-8') as f:
    html = f.read()

ok = fail = 0

def fx(label, old, new):
    global html, ok, fail
    if old not in html:
        print(f'FAIL [{label}]'); fail += 1; return False
    html = html.replace(old, new, 1)
    print(f'OK   [{label}]'); ok += 1; return True

# ══════════════════════════════════════════════════════════════════
# 1. CDN qrcode.js
# ══════════════════════════════════════════════════════════════════
fx('cdn-qrcode',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.min.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.min.js"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>'
)

# ══════════════════════════════════════════════════════════════════
# 2. CSS: skeleton shimmer + cola-rapida + quick-action styles
# ══════════════════════════════════════════════════════════════════
fx('css-dashboard-additions',
    '@media(max-width:700px){',
    '''/* ═══ DASHBOARD UPGRADE ═══ */

/* Skeleton shimmer — loading state */
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.skel{background:linear-gradient(90deg,var(--gris) 25%,var(--borde) 50%,var(--gris) 75%);
  background-size:200% 100%;animation:shimmer 1.4s infinite;border-radius:var(--radio);}

/* Cola de aprobación rápida */
.cola-card{display:grid;grid-template-columns:110px 1fr 100px 90px auto;
  gap:10px;padding:11px 16px;background:var(--surface);border-radius:var(--radio);
  border:1px solid var(--borde);border-left:3px solid var(--warn);margin-bottom:5px;
  align-items:center;font-size:12px;transition:all 0.15s;}
.cola-card:hover{box-shadow:var(--sombra-lg);}
.cola-folio{font-family:\'JetBrains Mono\',monospace;font-size:12px;
  font-weight:600;color:var(--verde);}
.cola-prov{font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.cola-monto{font-family:\'JetBrains Mono\',monospace;font-size:12px;
  font-weight:600;text-align:right;color:var(--texto);}
.cola-actions{display:flex;gap:5px;justify-content:flex-end;}
.btn-approve{font-size:18px;line-height:1;background:var(--verde-l);
  border:1.5px solid var(--verde);color:var(--verde);border-radius:6px;
  padding:4px 10px;cursor:pointer;transition:all 0.15s;font-family:inherit;}
.btn-approve:hover{background:var(--verde);color:white;transform:scale(1.05);}
.btn-reject{font-size:18px;line-height:1;background:var(--guinda-l);
  border:1.5px solid var(--guinda);color:var(--guinda);border-radius:6px;
  padding:4px 10px;cursor:pointer;transition:all 0.15s;font-family:inherit;}
.btn-reject:hover{background:var(--guinda);color:white;transform:scale(1.05);}

/* Panel de cola de aprobación */
.cola-panel{background:var(--surface);border:1px solid var(--borde);
  border-radius:12px;padding:18px 20px;margin-bottom:18px;
  box-shadow:var(--sombra);}
.cola-panel-hdr{display:flex;align-items:center;justify-content:space-between;
  margin-bottom:14px;}
.cola-panel-title{font-size:14px;font-weight:600;color:var(--texto);}
.cola-panel-badge{background:var(--warn);color:white;font-size:11px;
  font-weight:600;padding:2px 10px;border-radius:10px;}
.cola-col-hdr{display:grid;grid-template-columns:110px 1fr 100px 90px auto;
  gap:10px;padding:5px 16px;font-size:10px;font-weight:600;text-transform:uppercase;
  letter-spacing:0.05em;color:var(--sec);margin-bottom:6px;}

@media(max-width:700px){'''
)

# ══════════════════════════════════════════════════════════════════
# 3. cambiarStatus: aceptar comentario por parámetro
# ══════════════════════════════════════════════════════════════════
fx('cambiarStatus-param',
    'async function cambiarStatus(id,status){\n'
    '  const comentario=document.getElementById(\'modal-coment\')?.value||\'\';',
    'async function cambiarStatus(id,status,comentarioInline){\n'
    '  const comentario=comentarioInline!==undefined\n'
    '    ?comentarioInline\n'
    '    :(document.getElementById(\'modal-coment\')?.value||\'\');'
)

# ══════════════════════════════════════════════════════════════════
# 4. aprobarInline / rechazarInline — insertar antes de eliminarOrden
# ══════════════════════════════════════════════════════════════════
INLINE_FNS = (
    '// ══ ACCIONES INLINE ADMIN ══\n'
    'async function aprobarInline(id){\n'
    '  if(!confirm(\'¿Aprobar esta orden?\'))return;\n'
    '  await cambiarStatus(id,\'Aprobado\',\'\');\n'
    '}\n'
    'async function rechazarInline(id){\n'
    '  const m=prompt(\'Motivo del rechazo (requerido):\');\n'
    '  if(!m?.trim()){toast(\'Escribe un motivo de rechazo\',true);return;}\n'
    '  await cambiarStatus(id,\'Rechazado\',m.trim());\n'
    '}\n\n'
)
fx('inline-fns-insert',
    'async function eliminarOrden(id){',
    INLINE_FNS + 'async function eliminarOrden(id){'
)

# ══════════════════════════════════════════════════════════════════
# 5. renderLista: reemplazar "Revisar" por botones inline ✓ ✗ Ver
# ══════════════════════════════════════════════════════════════════
fx('renderLista-inline-actions',
    '    const accion=adm&&!ap&&!re\n'
    '      ?`<button class="btn btn-g" style="font-size:10px;padding:5px 9px;" onclick="abrirOrden(\'${o.id}\',true)">Revisar</button>`',
    '    const accion=adm&&!ap&&!re\n'
    '      ?`<div style="display:flex;gap:3px;">\n'
    '          <button class="btn-approve" onclick="aprobarInline(\'${o.id}\')" title="Aprobar">✓</button>\n'
    '          <button class="btn-reject"  onclick="rechazarInline(\'${o.id}\')" title="Rechazar">✗</button>\n'
    '          <button class="btn btn-n" style="font-size:10px;padding:4px 8px;" onclick="abrirOrden(\'${o.id}\',true)">↗</button>\n'
    '        </div>`'
)

# ══════════════════════════════════════════════════════════════════
# 6. HTML: cola de aprobación rápida en tab Aprobaciones (antes de stats-grid)
# ══════════════════════════════════════════════════════════════════
fx('html-cola-rapida',
    '      <div class="stats-grid" id="stats-grid"></div>',
    '      <!-- COLA DE APROBACIÓN RÁPIDA -->\n'
    '      <div class="cola-panel" id="cola-panel" style="display:none;">\n'
    '        <div class="cola-panel-hdr">\n'
    '          <div class="cola-panel-title">Cola de aprobación</div>\n'
    '          <span class="cola-panel-badge" id="cola-badge">0 pendientes</span>\n'
    '        </div>\n'
    '        <div class="cola-col-hdr">\n'
    '          <div>Folio</div><div>Proveedor</div>'
    '<div style="text-align:right">Unidad</div>'
    '<div style="text-align:right">Total</div>'
    '<div></div>\n'
    '        </div>\n'
    '        <div id="cola-items"></div>\n'
    '        <div id="cola-ver-mas" style="text-align:center;padding:8px;'
    'font-size:11px;color:var(--sec);display:none;">'
    '<a href="#" onclick="document.getElementById(\'af-status\').value=\'pendiente\';'
    'filtrarAdmin();return false;" style="color:var(--verde)">Ver todas →</a></div>\n'
    '      </div>\n'
    '      <div class="stats-grid" id="stats-grid"></div>'
)

# ══════════════════════════════════════════════════════════════════
# 7. renderColaRapida() — insertar antes de // ══ TOAST ══
# ══════════════════════════════════════════════════════════════════
COLA_FN = (
    '// ══ COLA DE APROBACIÓN RÁPIDA ══\n'
    'function renderColaRapida(ordenes){\n'
    '  const pendientes=ordenes.filter(o=>o.status?.toLowerCase().includes(\'pendiente\'));\n'
    '  const panel=document.getElementById(\'cola-panel\');\n'
    '  const badge=document.getElementById(\'cola-badge\');\n'
    '  const cont=document.getElementById(\'cola-items\');\n'
    '  const verMas=document.getElementById(\'cola-ver-mas\');\n'
    '  if(!panel)return;\n'
    '  if(!pendientes.length){panel.style.display=\'none\';return;}\n'
    '  panel.style.display=\'block\';\n'
    '  badge.textContent=pendientes.length+\' pendiente\'+(pendientes.length!==1?\'s\':\'\');\n'
    '  const visible=pendientes.slice(0,8);\n'
    '  cont.innerHTML=visible.map(o=>{\n'
    '    const prov=esc(o.nombre_proveedor||\'—\');\n'
    '    return `<div class="cola-card">\n'
    '      <div class="cola-folio">${esc(o.folio||\'—\')}</div>\n'
    '      <div class="cola-prov" title="${prov}">${prov}</div>\n'
    '      <div style="font-size:11px;color:var(--sec);text-align:right">${esc(o.unidad||\'—\')}</div>\n'
    '      <div class="cola-monto">${fmt(o.total)}</div>\n'
    '      <div class="cola-actions">\n'
    '        <button class="btn-approve" onclick="aprobarInline(\'${o.id}\')" title="Aprobar">✓</button>\n'
    '        <button class="btn-reject"  onclick="rechazarInline(\'${o.id}\')" title="Rechazar">✗</button>\n'
    '        <button class="btn btn-n" style="font-size:10px;padding:4px 8px;" '
    'onclick="abrirOrden(\'${o.id}\',true)" title="Ver detalle">↗</button>\n'
    '      </div>\n'
    '    </div>`;\n'
    '  }).join(\'\');\n'
    '  verMas.style.display=pendientes.length>8?\'block\':\'none\';\n'
    '}\n\n'
)
fx('renderColaRapida-fn',
    '// ══ TOAST ══',
    COLA_FN + '// ══ TOAST ══'
)

# ══════════════════════════════════════════════════════════════════
# 8. Llamar renderColaRapida en cargarTodasOrdenes
# ══════════════════════════════════════════════════════════════════
fx('call-renderColaRapida',
    '  renderStats(todasOrdenes);\n'
    '  renderLista(todasOrdenes,\'lista-admin\',true);',
    '  renderStats(todasOrdenes);\n'
    '  renderColaRapida(todasOrdenes);\n'
    '  renderLista(todasOrdenes,\'lista-admin\',true);'
)

# ══════════════════════════════════════════════════════════════════
# 9. Skeleton antes de cargar datos (en cargarMisOrdenes y cargarTodasOrdenes)
# ══════════════════════════════════════════════════════════════════
fx('skeleton-mis-ordenes',
    'async function cargarMisOrdenes(){\n'
    '  const {data,error}=await sb',
    'async function cargarMisOrdenes(){\n'
    '  // Mostrar skeleton mientras carga\n'
    '  const _lm=document.getElementById(\'lista-mis\');\n'
    '  if(_lm)_lm.innerHTML=Array(3).fill(\'<div class="skel" style="height:50px;margin-bottom:6px;"></div>\').join(\'\');\n'
    '  const {data,error}=await sb'
)

# ══════════════════════════════════════════════════════════════════
# 10. QR en PDF — insertar justo después de generar el PDF base
# ══════════════════════════════════════════════════════════════════
# Find the spot right before doc.save() in generarPDF
fx('qr-in-pdf',
    "  toast('✓ PDF generado');",
    (
        '  // ── QR de verificación interna ──────────────────────────\n'
        '  try{\n'
        '    const qrCanvas=document.createElement(\'canvas\');\n'
        '    const qrData=`Folio: ${o.folio}\\nSistema: Gestión Órdenes BC\\n'
        'URL: https://ederimiramontes.github.io/ordenes-imss/`;\n'
        "    await QRCode.toCanvas(qrCanvas,qrData,{width:64,margin:1,"
        "color:{dark:'#059669',light:'#ffffff'}});\n"
        '    const qrImg=qrCanvas.toDataURL(\'image/png\');\n'
        '    doc.addImage(qrImg,\'PNG\',W-mr-22,mt,22,22);\n'
        '    doc.setFontSize(5);doc.setTextColor(150,150,150);\n'
        "    doc.text('Verificar en sistema',W-mr-11,mt+24.5,{align:'center'});\n"
        '  }catch(qe){console.warn(\'QR no generado:\',qe);}\n\n'
        "  toast('✓ PDF generado');"
    )
)

# ══════════════════════════════════════════════════════════════════
print(f'\nTotal: {ok} OK, {fail} FAIL')
if fail == 0:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Guardado: {len(html):,} chars')
else:
    print('NO GUARDADO')
