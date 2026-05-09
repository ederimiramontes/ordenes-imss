"""arch_final.py — Aplica las 3 mejoras arquitecturales sobre el estado actual del archivo."""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
with open(path, encoding='utf-8') as f:
    html = f.read()

ok = skip = fail = 0

def fx(label, old, new):
    global html, ok, fail
    if old not in html:
        print(f'FAIL [{label}]'); fail += 1; return
    html = html.replace(old, new, 1)
    print(f'OK   [{label}]'); ok += 1

def sk(label):
    global skip
    print(f'SKIP [{label}]'); skip += 1

# ─── MEJORA 1: CATÁLOGOS A DB ─────────────────────────────────────────────────
fx('1a', 'const UNIDADES = [', '// Fallback estático\nconst UNIDADES_STATIC = [')
fx('1b', 'const PROVEEDORES_CAT = [',
   'let UNIDADES = [...UNIDADES_STATIC];\nconst PROVEEDORES_CAT = [')
fx('1c', 'const PARTIDAS = [', '// Fallback estático\nconst PARTIDAS_STATIC = [')
fx('1d', 'const USUARIOS_CAT = [',
   'let PARTIDAS = [...PARTIDAS_STATIC];\nconst USUARIOS_CAT = [')
fx('1e', '// ══ CATÁLOGO DE CONCEPTOS (DB) ══',
   '// ══ CATÁLOGOS DESDE DB (fallback estático) ══\n'
   'async function cargarCatalogosDB(){\n'
   '  try {\n'
   '    const [{data:u},{data:p}]=await Promise.all([\n'
   "      sb.from('catalogo_unidades').select('jcu,ui,cc,unidad,localidad').eq('activo',true).order('orden'),\n"
   "      sb.from('catalogo_partidas').select('clave,descripcion,tipo').eq('activo',true).order('clave')\n"
   '    ]);\n'
   "    if(u&&u.length>0){UNIDADES=u;console.log('[DB] Unidades:',u.length);}\n"
   "    if(p&&p.length>0){PARTIDAS=p;console.log('[DB] Partidas:',p.length);}\n"
   "  }catch(e){console.warn('[DB] Catálogos: usando fallback.',e.message);}\n"
   '}\n\n'
   '// ══ CATÁLOGO DE CONCEPTOS (DB) ══')
fx('1f', '  cargarCatalogoConceptos();            // carga catálogo de descripciones desde DB',
   '  cargarCatalogosDB();                  // carga unidades y partidas desde DB\n'
   '  cargarCatalogoConceptos();            // carga catálogo de descripciones desde DB')

# ─── MEJORA 2: ESTADO BORRADOR ────────────────────────────────────────────────
fx('2a', ('      <div class="acciones">\n'
   '        <button class="btn btn-n" onclick="nuevaOrden()">Limpiar</button>\n'
   '        <button class="btn btn-g" onclick="guardarOrden()" id="btn-guardar">Guardar Orden</button>\n'
   '      </div>'),
  ('      <div class="acciones">\n'
   '        <button class="btn btn-n" onclick="nuevaOrden()">Limpiar</button>\n'
   "        <button class=\"btn btn-n\" onclick=\"guardarOrden('borrador')\" id=\"btn-borrador\">Guardar borrador</button>\n"
   "        <button class=\"btn btn-g\" onclick=\"guardarOrden('pendiente')\" id=\"btn-guardar\">Guardar y enviar ›</button>\n"
   '      </div>'))
fx('2b', 'async function guardarOrden(){', "async function guardarOrden(targetStatus='pendiente'){")
fx('2c', "    status:'Folio guardado y pendiente de aprobacion',",
   "    status:targetStatus==='borrador'?'borrador':'Folio guardado y pendiente de aprobacion',")
sk('2d')  # toast borrador ya aplicado
fx('2e', "    const ordenEdit={...orden, status:'Folio guardado y pendiente de aprobacion'};",
   "    const ordenEdit={...orden, status:targetStatus==='borrador'?'borrador':'Folio guardado y pendiente de aprobacion'};")
fx('2f', "    toast('✓ Orden corregida y reenviada a aprobación');",
   "    toast(targetStatus==='borrador'?'✓ Borrador actualizado':'✓ Orden corregida y reenviada a aprobación');")
fx('2g', ('    const badge=ap?\'<span class="sb-a">Aprobado</span>\':'
          're?\'<span class="sb-r">Rechazado</span>\':'
          "'<span class=\"sb-p\">Pendiente</span>';"),
  ("    const bo=o.status==='borrador';\n"
   '    const badge=bo?\'<span class="sb-p" style="background:#f1f5f9;color:#64748b;border:1px solid #cbd5e1">Borrador</span>\':'
   'ap?\'<span class="sb-a">Aprobado</span>\':'
   're?\'<span class="sb-r">Rechazado</span>\':'
   "'<span class=\"sb-p\">Pendiente</span>';"))
fx('2h', ('    const puedeEliminar = !ap && !re;\n'
          '    const puedeCorregir = re && !adm;'),
  ('    const puedeEliminar = !ap && !re;\n'
   '    const puedeCorregir = re && !adm;\n'
   '    const puedeSendBorrador = bo && !adm;'))
sk('2j'); sk('2k')  # neq y hero stats ya aplicados

# 2i — accion block: add borrador buttons if not present
if 'Continuar</button>' not in html:
    m = re.search(r'(const accion=adm&&!ap&&!re\s*\?.*?`;\n)', html, re.DOTALL)
    if m:
        blk = m.group(1)
        new_blk = blk.replace(
            'onclick="abrirOrden(\'${o.id}\',false)">Ver</button>',
            ('${!bo?`onclick="abrirOrden(\'${o.id}\',false)">Ver</button>`:\'\'}\n'
             '        ${bo?`<button class="btn btn-a" style="font-size:10px;padding:5px 9px;" onclick="corregirOrden(\'${o.id}\')">Continuar</button>`:\'\'}\n'
             '        ${puedeSendBorrador?`<button class="btn btn-g" style="font-size:10px;padding:5px 9px;" onclick="enviarBorrador(\'${o.id}\')">Enviar ›</button>`:\'\'}'
             ), 1)
        if new_blk != blk:
            html = html.replace(blk, new_blk, 1)
            print('OK   [2i-accion borrador]'); ok += 1
        else:
            print('FAIL [2i-accion inner replace]'); fail += 1
    else:
        print('FAIL [2i-no match]'); fail += 1
else:
    sk('2i')

fx('2l', '// ══ CORREGIR ORDEN RECHAZADA ══',
   '// ══ ENVIAR BORRADOR ══\n'
   'async function enviarBorrador(id){\n'
   "  if(!confirm('¿Enviar esta orden a aprobación?\\nNo podrás editarla hasta que sea revisada.'))return;\n"
   "  const {error}=await sb.from('ordenes')\n"
   "    .update({status:'Folio guardado y pendiente de aprobacion'})\n"
   "    .eq('id',id).eq('created_by',currentUser.id).eq('status','borrador');\n"
   "  if(error){toast('Error: '+error.message,true);return;}\n"
   "  toast('✓ Orden enviada a aprobación');\n"
   '  cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();\n'
   '}\n\n'
   '// ══ CORREGIR ORDEN RECHAZADA ══')

# ─── MEJORA 3: PRESUPUESTO COMPROMETIDO ──────────────────────────────────────
sk('3a')  # presupuesto_resumen ya aplicado
fx('3b', ('          <div style="display:grid;grid-template-columns:1fr 120px 120px 120px 90px;'
   'gap:8px;padding:8px 14px;background:var(--verde-l);border-radius:var(--radio);'
   'border:1px solid var(--verde-m);font-size:10px;font-weight:600;text-transform:uppercase;'
   'letter-spacing:0.05em;color:var(--verde);margin-bottom:6px;">\n'
   '            <div>Partida</div>\n'
   '            <div style="text-align:right">Asignado</div>\n'
   '            <div style="text-align:right">En Folios</div>\n'
   '            <div style="text-align:right">Disponible</div>\n'
   '            <div style="text-align:center">Acción</div>\n'
   '          </div>'),
  ('          <div style="display:grid;grid-template-columns:1fr 110px 110px 110px 110px 80px;'
   'gap:8px;padding:8px 14px;background:var(--verde-l);border-radius:var(--radio);'
   'border:1px solid var(--verde-m);font-size:10px;font-weight:600;text-transform:uppercase;'
   'letter-spacing:0.05em;color:var(--verde);margin-bottom:6px;">\n'
   '            <div>Partida</div>\n'
   '            <div style="text-align:right">Asignado</div>\n'
   '            <div style="text-align:right;color:var(--warn)">Comprometido</div>\n'
   '            <div style="text-align:right">Ejecutado</div>\n'
   '            <div style="text-align:right">Disponible</div>\n'
   '            <div style="text-align:center">Acción</div>\n'
   '          </div>'))
fx('3c', '    const pct=p.monto>0?(p.consumido/p.monto)*100:0;',
   ('    const pct=p.asignado>0?((p.comprometido||0)+(p.ejecutado||p.consumido||0))/p.asignado*100:0;\n'
    '    const consumido=p.ejecutado||p.consumido||0;\n'
    '    const comprometido=p.comprometido||0;'))
fx('3d', "    const cls=p.disponible<=0?'pres-agotado':pct>80?'pres-bajo':'pres-ok';",
   "    const cls=p.disponible<=0?'pres-agotado':pct>80?'pres-bajo':'pres-ok';\n    const monto=p.asignado||p.monto||0;")
fx('3e', ('      <div class="pres-disponible" style="text-align:right">${fmtPesos(p.monto)}</div>\n'
   '      <div class="pres-disponible pres-agotado" style="text-align:right">${fmtPesos(p.consumido)}</div>'),
  ('      <div class="pres-disponible" style="text-align:right">${fmtPesos(monto)}</div>\n'
   '      <div class="pres-disponible" style="text-align:right;color:var(--warn)">${fmtPesos(comprometido)}</div>\n'
   '      <div class="pres-disponible pres-agotado" style="text-align:right">${fmtPesos(consumido)}</div>'))
fx('3f', ("    return `<div class=\"pres-row\" onclick=\"verHistorial('${p.partida}')\" style=\"cursor:pointer;\">\n      <div>"),
  ("    return `<div class=\"pres-row\" style=\"display:grid;grid-template-columns:1fr 110px 110px 110px 110px 80px;"
   "gap:8px;padding:12px 14px;background:var(--surface);border-radius:var(--radio);"
   "border:1px solid var(--borde);margin-bottom:5px;align-items:center;font-size:13px;"
   "transition:all 0.15s;cursor:pointer;\" onclick=\"verHistorial('${p.partida}')\">\n      <div>"))

print(f'\nTotal: {ok} OK, {skip} SKIP, {fail} FAIL')
if fail == 0:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Guardado: {len(html):,} chars')
else:
    print('NO GUARDADO')
