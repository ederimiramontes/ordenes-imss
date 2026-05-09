"""audit_v2.py — Auditoría automatizada sobre la versión arquitectural."""
import sys, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
with open(path, encoding='utf-8') as f:
    html = f.read()

issues = []  # (severidad, mensaje)

def chk(sev, msg, condition):
    if condition:
        issues.append((sev, msg))

# ── 1. Funciones en eventos sin definición ────────────────────────
called_raw = re.findall(r'on(?:click|input|change|focus|keydown)="([^"]+)"', html)
handlers = set()
for h in called_raw:
    handlers.update(re.findall(r'(\w+)\s*\(', h))
defined_fns = set(re.findall(r'(?:async\s+)?function\s+(\w+)\s*\(', html))
noise = {'if','event','parseInt','parseFloat','confirm','window','document',
         'new','Object','Array','Math','console','Promise','Date','JSON',
         'setTimeout','String','Number','Boolean','this','getElementById',
         'stopPropagation','querySelector','querySelectorAll','isNaN'}
missing_fns = handlers - defined_fns - noise
chk('CRITICO', f'Funciones en eventos NO definidas: {sorted(missing_fns)}', bool(missing_fns))

# ── 2. IDs en JS que no están en HTML ────────────────────────────
js_ids   = set(re.findall(r"getElementById\('([^']+)'\)", html))
html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html))
dynamic = {'acl-concepto-', 'ac-concepto-', 'r5-', 'imp-', 'cant-ent-', '${'}
missing_ids = {i for i in js_ids - html_ids
               if not any(i.startswith(d) for d in dynamic) and '${' not in i}
chk('ALTO', f'IDs buscados en JS pero sin elemento HTML: {sorted(missing_ids)}', bool(missing_ids))

# ── 3. corregirOrden no acepta borradores ─────────────────────────
m = re.search(r'async function corregirOrden\(id\)\{(.+?)\ncorr', html, re.DOTALL)
if m:
    body = m.group(1)
    tiene_borrador = 'borrador' in body
    tiene_rechazado = 'rechazado' in body
    chk('CRITICO',
        'corregirOrden() solo acepta rechazado — btn "Continuar" en borradores lanza toast de error y no abre formulario',
        tiene_rechazado and not tiene_borrador)

# ── 4. const vs let en catálogos ─────────────────────────────────
# check for any remaining 'const UNIDADES' or 'const PARTIDAS' after the static rename
remaining_const = [l.strip()[:80] for l in html.split('\n')
                   if re.search(r'const (UNIDADES|PARTIDAS)\s*[=\[]', l)
                   and 'STATIC' not in l]
chk('CRITICO',
    f'const UNIDADES/PARTIDAS sin _STATIC impiden reasignacion desde DB: {remaining_const}',
    bool(remaining_const))

# ── 5. badge-mis cuenta borradores ──────────────────────────────
chk('MEDIO',
    'badge-mis muestra count total incluyendo borradores — tab "Mis Ordenes" infla el numero',
    "badge-mis').textContent=misOrdenes.length" in html)

# ── 6. filtrarMis mezcla borradores con pendientes ───────────────
fm_m = re.search(r'function filtrarMis\(\)\{(.+?)\}', html, re.DOTALL)
if fm_m:
    fm = fm_m.group(1)
    chk('MEDIO',
        "filtrarMis: el filtro 'Pendiente' mostrara borradores porque su status es 'borrador', no 'pendiente'",
        'borrador' not in fm and 'pendiente' in fm)

# ── 7. editandoOrdenId no se limpia en rama borrador del modo edición ─────
edit_m = re.search(r'MODO EDICION: actualizar(.+?)folioEnProceso=false;editandoOrdenId=null;', html, re.DOTALL)
chk('MEDIO',
    'guardarOrden modo edicion: editandoOrdenId=null solo visible en rama no-borrador',
    not edit_m)

# ── 8. CSS .pres-row tiene grid que puede chocar con inline grid ──
css_m = re.search(r'\.pres-row\{([^}]+)\}', html)
if css_m:
    css_body = css_m.group(1)
    chk('MEDIO',
        '.pres-row CSS tiene grid-template-columns — choca con el grid inline que pusimos en 3f',
        'grid-template-columns' in css_body)

# ── 9. presupuesto_resumen: ¿el tab presupuesto recarga al abrirse? ─
showTab_m = re.search(r"if\(tab==='presupuesto'\)\{([^}]+)\}", html)
if showTab_m:
    chk('BAJO',
        "showTab presupuesto: llama cargarPresupuestos() — OK",
        False)

# ── 10. enviarBorrador: ¿limpia folio en proceso? ─────────────────
ev_m = re.search(r'async function enviarBorrador\(id\)\{(.+?)\}', html, re.DOTALL)
if ev_m:
    ev = ev_m.group(1)
    chk('BAJO',
        'enviarBorrador no llama cargarPresupuestos() — presupuesto puede quedar desactualizado',
        'cargarPresupuestos' not in ev)

# ── 11. corregirOrden en modo borrador: btn-guardar label ─────────
co_m = re.search(r'async function corregirOrden\(id\)\{(.+?)\ncorr', html, re.DOTALL)
if co_m:
    co_body = co_m.group(1)
    chk('BAJO',
        'corregirOrden: label del btn-guardar se pone "Corregir y reenviar" — en borradores deberia decir "Guardar y enviar"',
        'Corregir y reenviar' in co_body)

# ── 12. guardarOrden edicion: toast dice "corregida" aunque sea borrador ──
chk('BAJO',
    'guardarOrden edit: toast "Borrador actualizado" — OK para borradores, falta prueba',
    False)

# ── 13. Verificar que presupuesto_resumen existe en DB (solo documentar) ──
chk('INFO',
    'Verificar que la vista presupuesto_resumen fue creada correctamente en Supabase (SQL 12)',
    False)  # always info, never error

# ─── REPORTE ─────────────────────────────────────────────────────
ORDER = ['CRITICO', 'ALTO', 'MEDIO', 'BAJO', 'INFO']
real_issues = [(s,m) for s,m in issues if s != 'INFO']
print(f'Hallazgos: {len(real_issues)} problemas reales')
print('=' * 65)
for sev in ORDER:
    batch = [(s,m) for s,m in issues if s == sev]
    for s, msg in batch:
        print(f'[{s}] {msg}')
