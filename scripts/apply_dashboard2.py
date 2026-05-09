"""apply_dashboard2.py — Dashboard upgrade: CDN, CSS, inline actions, cola rapida, skeleton."""
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

# ─── 1. CDN qrcode.js ──────────────────────────────────────────────
fx('cdn-qrcode',
   '<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.min.js"></script>',
   ('<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.min.js"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>'))

# ─── 2. CSS skeleton + cola-card + btns ────────────────────────────
CSS_NEW = (
    '@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}\n'
    '.skel{background:linear-gradient(90deg,var(--gris) 25%,var(--borde) 50%,var(--gris) 75%);'
    'background-size:200% 100%;animation:shimmer 1.4s infinite;border-radius:var(--radio);}\n'
    '.cola-card{display:grid;grid-template-columns:110px 1fr 100px 90px auto;gap:10px;'
    'padding:11px 16px;background:var(--surface);border-radius:var(--radio);'
    'border:1px solid var(--borde);border-left:3px solid var(--warn);margin-bottom:5px;'
    'align-items:center;font-size:12px;transition:all 0.15s;}\n'
    '.cola-card:hover{box-shadow:var(--sombra-lg);}\n'
    '.cola-folio{font-family:"JetBrains Mono",monospace;font-size:12px;font-weight:600;color:var(--verde);}\n'
    '.cola-prov{font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}\n'
    '.cola-monto{font-family:"JetBrains Mono",monospace;font-size:12px;font-weight:600;text-align:right;}\n'
    '.cola-actions{display:flex;gap:5px;justify-content:flex-end;}\n'
    '.btn-approve{font-size:17px;line-height:1;background:var(--verde-l);border:1.5px solid var(--verde);'
    'color:var(--verde);border-radius:6px;padding:4px 10px;cursor:pointer;transition:all 0.15s;font-family:inherit;}\n'
    '.btn-approve:hover{background:var(--verde);color:white;transform:scale(1.08);}\n'
    '.btn-reject{font-size:17px;line-height:1;background:var(--guinda-l);border:1.5px solid var(--guinda);'
    'color:var(--guinda);border-radius:6px;padding:4px 10px;cursor:pointer;transition:all 0.15s;font-family:inherit;}\n'
    '.btn-reject:hover{background:var(--guinda);color:white;transform:scale(1.08);}\n'
    '.cola-panel{background:var(--surface);border:1px solid var(--borde);border-radius:12px;'
    'padding:18px 20px;margin-bottom:18px;box-shadow:var(--sombra);}\n'
    '.cola-panel-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;}\n'
    '.cola-panel-title{font-size:14px;font-weight:600;color:var(--texto);}\n'
    '.cola-panel-badge{background:var(--warn);color:white;font-size:11px;font-weight:600;'
    'padding:2px 10px;border-radius:10px;}\n'
    '.cola-col-hdr{display:grid;grid-template-columns:110px 1fr 100px 90px auto;gap:10px;'
    'padding:5px 16px;font-size:10px;font-weight:600;text-transform:uppercase;'
    'letter-spacing:0.05em;color:var(--sec);margin-bottom:6px;}\n'
    '@media(max-width:700px){'
)
fx('css-additions', '@media(max-width:700px){', CSS_NEW)

# ─── 3. cambiarStatus: aceptar comentario por parámetro ─────────────
fx('cambiarStatus-param',
   ("async function cambiarStatus(id,status){\n"
    "  const comentario=document.getElementById('modal-coment')?.value||'';"),
   ("async function cambiarStatus(id,status,comentarioInline){\n"
    "  const comentario=comentarioInline!==undefined\n"
    "    ?comentarioInline\n"
    "    :(document.getElementById('modal-coment')?.value||'');"))

# ─── 4. aprobarInline / rechazarInline ──────────────────────────────
fx('inline-fns',
   'async function eliminarOrden(id){',
   ('// ══ ACCIONES INLINE ADMIN ══\n'
    'async function aprobarInline(id){\n'
    "  if(!confirm('¿Aprobar esta orden?'))return;\n"
    "  await cambiarStatus(id,'Aprobado','');\n"
    '}\n'
    'async function rechazarInline(id){\n'
    "  const m=prompt('Motivo del rechazo:');\n"
    "  if(!m?.trim()){toast('Escribe un motivo',true);return;}\n"
    "  await cambiarStatus(id,'Rechazado',m.trim());\n"
    '}\n\n'
    'async function eliminarOrden(id){'))

# ─── 5. renderLista: botones inline ✓ ✗ ↗ para admin pending ────────
fx('renderLista-inline',
   ('    const accion=adm&&!ap&&!re\n'
    '      ?`<button class="btn btn-g" style="font-size:10px;padding:5px 9px;" onclick="abrirOrden(\'${o.id}\',true)">Revisar</button>`'),
   ('    const accion=adm&&!ap&&!re\n'
    '      ?`<div style="display:flex;gap:3px;">'
    '<button class="btn-approve" onclick="aprobarInline(\'${o.id}\')" title="Aprobar">✓</button>'
    '<button class="btn-reject"  onclick="rechazarInline(\'${o.id}\')" title="Rechazar">✗</button>'
    '<button class="btn btn-n" style="font-size:10px;padding:4px 8px;" '
    'onclick="abrirOrden(\'${o.id}\',true)" title="Ver detalle">↗</button></div>`'))

# ─── 6. HTML: cola-panel antes de stats-grid ────────────────────────
COLA_HTML = (
    '      <div class="cola-panel" id="cola-panel" style="display:none;">\n'
    '        <div class="cola-panel-hdr">\n'
    '          <div class="cola-panel-title">Cola de aprobación rápida</div>\n'
    '          <span class="cola-panel-badge" id="cola-badge">0 pendientes</span>\n'
    '        </div>\n'
    '        <div class="cola-col-hdr"><div>Folio</div><div>Proveedor</div>'
    '<div style="text-align:right">Unidad</div>'
    '<div style="text-align:right">Total</div><div></div></div>\n'
    '        <div id="cola-items"></div>\n'
    '        <div id="cola-ver-mas" style="text-align:center;padding:8px;'
    'font-size:11px;color:var(--sec);display:none;">'
    '<a href="#" onclick="'
    "document.getElementById('af-status').value='pendiente';filtrarAdmin();return false;"
    '" style="color:var(--verde)">Ver todas →</a></div>\n'
    '      </div>\n'
    '      <div class="stats-grid" id="stats-grid"></div>'
)
fx('html-cola-panel',
   '      <div class="stats-grid" id="stats-grid"></div>',
   COLA_HTML)

# ─── 7. renderColaRapida function ────────────────────────────────────
COLA_FN = (
    "// ══ COLA RAPIDA ══\n"
    "function renderColaRapida(ordenes){\n"
    "  const pend=ordenes.filter(o=>o.status&&o.status.toLowerCase().includes('pendiente'));\n"
    "  const panel=document.getElementById('cola-panel');\n"
    "  if(!panel)return;\n"
    "  if(!pend.length){panel.style.display='none';return;}\n"
    "  panel.style.display='block';\n"
    "  document.getElementById('cola-badge').textContent=\n"
    "    pend.length+' pendiente'+(pend.length!==1?'s':'');\n"
    "  const vis=pend.slice(0,8);\n"
    "  document.getElementById('cola-items').innerHTML=vis.map(function(o){\n"
    "    return '<div class=\"cola-card\">'\n"
    "      +'<div class=\"cola-folio\">'+esc(o.folio||'--')+'</div>'\n"
    "      +'<div class=\"cola-prov\">'+esc(o.nombre_proveedor||'--')+'</div>'\n"
    "      +'<div style=\"font-size:11px;color:var(--sec);text-align:right\">'+esc(o.unidad||'--')+'</div>'\n"
    "      +'<div class=\"cola-monto\">'+fmt(o.total)+'</div>'\n"
    "      +'<div class=\"cola-actions\">'\n"
    "      +'<button class=\"btn-approve\" onclick=\"aprobarInline(\\''+o.id+'\\')\" title=\"Aprobar\">&#10003;</button>'\n"
    "      +'<button class=\"btn-reject\" onclick=\"rechazarInline(\\''+o.id+'\\')\" title=\"Rechazar\">&#10007;</button>'\n"
    "      +'<button class=\"btn btn-n\" style=\"font-size:10px;padding:4px 8px;\" onclick=\"abrirOrden(\\''+o.id+'\\',true)\" title=\"Ver\">&#8599;</button>'\n"
    "      +'</div></div>';\n"
    "  }).join('');\n"
    "  var vm=document.getElementById('cola-ver-mas');\n"
    "  if(vm)vm.style.display=pend.length>8?'block':'none';\n"
    "}\n\n"
    "// ══ TOAST ══"
)
fx('renderColaRapida-fn', '// ══ TOAST ══', COLA_FN)

# ─── 8. call renderColaRapida en cargarTodasOrdenes ─────────────────
fx('call-cola-rapida',
   "  renderStats(todasOrdenes);\n  renderLista(todasOrdenes,'lista-admin',true);",
   "  renderStats(todasOrdenes);\n  renderColaRapida(todasOrdenes);\n  renderLista(todasOrdenes,'lista-admin',true);")

# ─── 9. Skeleton en cargarMisOrdenes ────────────────────────────────
fx('skeleton-mis',
   'async function cargarMisOrdenes(){',
   ("async function cargarMisOrdenes(){\n"
    "  var _lm=document.getElementById('lista-mis');\n"
    "  if(_lm)_lm.innerHTML=Array(3).fill('<div class=\"skel\" style=\"height:50px;margin-bottom:6px;\"></div>').join('');"))

# ─── 10. QR ya aplicado ─────────────────────────────────────────────
sk('QR-in-PDF')

# ─── SIEMPRE GUARDAR ────────────────────────────────────────────────
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'\nTotal: {ok} OK, {skip} SKIP, {fail} FAIL')
print(f'Guardado: {len(html):,} chars')
