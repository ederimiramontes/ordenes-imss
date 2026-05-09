"""
apply_audit_fixes.py
Aplica todas las correcciones de la auditoría de seguridad + ingeniería pre-demo.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base, 'index.html')

with open(path, encoding='utf-8') as f:
    html = f.read()

results = []

def fix(label, old, new, count_expected=1):
    global html
    c = html.count(old)
    if c == 0:
        results.append(f'FAIL [{label}]: old string not found')
        return False
    if c > count_expected:
        results.append(f'WARN [{label}]: found {c} occurrences, replacing first only')
    html = html.replace(old, new, 1)
    results.append(f'OK   [{label}]')
    return True

# ══════════════════════════════════════════════════════════════
# FIX 1 — Var global folioEnProceso
# ══════════════════════════════════════════════════════════════
fix('01-folioEnProceso var',
    "let folioActual = '';",
    "let folioActual = '';\nlet folioEnProceso = false; // true mientras hay folio generado sin guardar"
)

# ══════════════════════════════════════════════════════════════
# FIX 2 — iniciarNuevoFolio: marcar folio en proceso
# ══════════════════════════════════════════════════════════════
fix('02-iniciarNuevoFolio set flag',
    "  document.getElementById('folio-display').textContent=folioActual;\n  selUnidad=null;",
    "  document.getElementById('folio-display').textContent=folioActual;\n  folioEnProceso=true;\n  selUnidad=null;"
)

# ══════════════════════════════════════════════════════════════
# FIX 3 — volverMenu: limpiar flag
# ══════════════════════════════════════════════════════════════
fix('03-volverMenu clear flag',
    "function volverMenu(){\n  document.getElementById('form-orden').style.display='none';\n  document.getElementById('menu-gestion').style.display='block';",
    "function volverMenu(){\n  folioEnProceso=false;\n  document.getElementById('form-orden').style.display='none';\n  document.getElementById('menu-gestion').style.display='block';"
)

# ══════════════════════════════════════════════════════════════
# FIX 4 — guardarOrden: validar subtotal > 0 + check presupuesto + clear flag
# ══════════════════════════════════════════════════════════════
fix('04a-guardarOrden $0 validation',
    "  if(!conceptos.some(c=>c.desc.trim())){toast('Agrega al menos un concepto',true);return;}",
    "  if(!conceptos.some(c=>c.desc.trim())){toast('Agrega al menos un concepto',true);return;}\n  const _csub=conceptos.reduce((s,c)=>s+(c.imp||0),0);\n  if(_csub<=0){toast('El importe total debe ser mayor a $0',true);return;}"
)

# Budget check + folioEnProceso=false on success — insert before "const btn=..."
fix('04b-guardarOrden budget check',
    "  const btn=document.getElementById('btn-guardar');\n  btn.innerHTML='<span class=\"spinner\"></span>Guardando...';btn.disabled=true;",
    """  // Verificar presupuesto disponible (advertencia, no bloqueo)
  if(selPartida&&presupuestosData&&presupuestosData.length){
    const _pr=presupuestosData.find(p=>p.partida===selPartida.clave);
    if(_pr&&_pr.disponible!=null){
      const _tot=_csub*(1+(parseFloat(document.getElementById('sel-iva').value)||0))-(selProv?.ret_isr?_csub*0.01:0);
      if(_pr.disponible<_tot){
        if(!confirm('⚠ Presupuesto insuficiente para '+selPartida.clave+'.\\nDisponible: $'+_pr.disponible.toLocaleString('es-MX')+'\\nTotal orden: $'+_tot.toLocaleString('es-MX')+'\\n\\n¿Guardar de todas formas?')){return;}
      }
    }
  }
  const btn=document.getElementById('btn-guardar');
  btn.innerHTML='<span class=\"spinner\"></span>Guardando...';btn.disabled=true;"""
)

# Limpiar flag cuando guardar OK
fix('04c-guardarOrden clear flag on success',
    "  toast('✓ Orden '+folioActual+' guardada');\n  btn.innerHTML='Guardar Orden';btn.disabled=false;\n  cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();",
    "  folioEnProceso=false;\n  toast('✓ Orden '+folioActual+' guardada');\n  btn.innerHTML='Guardar Orden';btn.disabled=false;\n  cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();cargarPresupuestos();"
)

# ══════════════════════════════════════════════════════════════
# FIX 5 — showTab: guardar folio + reset formulario
# ══════════════════════════════════════════════════════════════
fix('05-showTab guard',
    "function showTab(tab){\n  ALL_TABS.forEach(t=>{",
    """function showTab(tab){
  // Si hay folio en proceso y cambian de tab, advertir
  if(tab!=='nueva'&&folioEnProceso){
    if(!confirm('Hay un folio en proceso ('+folioActual+') sin guardar.\\n¿Salir de todos modos?\\nEl folio quedará reservado sin orden.'))return;
    folioEnProceso=false;volverMenu();
  }
  // Si vuelven a la tab Gestionar estando en el formulario, regresar al menú
  if(tab==='nueva'){const _f=document.getElementById('form-orden');if(_f&&_f.style.display!=='none')volverMenu();}
  ALL_TABS.forEach(t=>{"""
)

# ══════════════════════════════════════════════════════════════
# FIX 6 — cambiarStatus: comentario requerido en rechazo + guard estado
# ══════════════════════════════════════════════════════════════
fix('06-cambiarStatus improvements',
    "async function cambiarStatus(id,status){\n  const comentario=document.getElementById('modal-coment')?.value||'';\n  await sb.from('ordenes').update({status,comentario_aprobacion:comentario}).eq('id',id);\n  toast(status==='Aprobado'?'✓ Orden aprobada':'Orden rechazada',status!=='Aprobado');\n  cerrarModal();cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();\n}",
    """async function cambiarStatus(id,status){
  const comentario=document.getElementById('modal-coment')?.value||'';
  // Comentario requerido al rechazar
  if(status==='Rechazado'&&!comentario.trim()){toast('Escribe un motivo de rechazo antes de continuar',true);return;}
  // Guard: verificar que la orden no esté ya decidida
  const {data:curr}=await sb.from('ordenes').select('status').eq('id',id).single();
  const ya=curr?.status?.toLowerCase();
  if(ya&&(ya.includes('aprobado')||ya.includes('rechazado'))){
    toast('Esta orden ya fue '+curr.status+'. No se puede cambiar.',true);cerrarModal();return;
  }
  const {error}=await sb.from('ordenes').update({status,comentario_aprobacion:comentario}).eq('id',id);
  if(error){toast('Error: '+error.message,true);return;}
  toast(status==='Aprobado'?'✓ Orden aprobada':'Orden rechazada',status!=='Aprobado');
  cerrarModal();cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();cargarPresupuestos();
}"""
)

# ══════════════════════════════════════════════════════════════
# FIX 7 — Modal footer: admin NO puede eliminar órdenes aprobadas/rechazadas
# ══════════════════════════════════════════════════════════════
fix('07-modal footer no delete approved',
    "      ${isAdmin?`<button class=\"btn btn-a\" onclick=\"eliminarOrden('${id}')\">Eliminar</button>`:''}",
    "      ${isAdmin&&!ap&&!re?`<button class=\"btn btn-a\" onclick=\"eliminarOrden('${id}')\">Eliminar</button>`:''}"
)

# ══════════════════════════════════════════════════════════════
# FIX 8 — selectConcepto: if(item.precio != null) en vez de if(item.precio)
# ══════════════════════════════════════════════════════════════
fix('08-selectConcepto precio null check',
    "  if(item.precio) conceptos[rowIdx].pu=item.precio;",
    "  if(item.precio!=null) conceptos[rowIdx].pu=item.precio;"
)

# ══════════════════════════════════════════════════════════════
# FIX 9 — cargarMisOrdenes: re-aplicar filtros activos después de cargar
# ══════════════════════════════════════════════════════════════
fix('09-cargarMisOrdenes filtrarMis after load',
    "  renderLista(misOrdenes,'lista-mis',false);\n}",
    "  renderLista(misOrdenes,'lista-mis',false);\n  filtrarMis(); // re-aplica filtros activos\n}",
    count_expected=1
)

# ══════════════════════════════════════════════════════════════
# FIX 10 — eliminarOrden + confirmarEliminar: recargar presupuesto
# ══════════════════════════════════════════════════════════════
fix('10a-eliminarOrden reload presupuesto',
    "  toast('Orden eliminada');cerrarModal();cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();\n}",
    "  toast('Orden eliminada');cerrarModal();cargarMisOrdenes();if(isAdmin)cargarTodasOrdenes();cargarPresupuestos();\n}"
)

fix('10b-confirmarEliminar reload presupuesto',
    "  toast('Orden '+folio+' eliminada');\n  cargarMisOrdenes();\n  if(isAdmin)cargarTodasOrdenes();\n}",
    "  toast('Orden '+folio+' eliminada');\n  cargarMisOrdenes();\n  if(isAdmin)cargarTodasOrdenes();\n  cargarPresupuestos();\n}"
)

# ══════════════════════════════════════════════════════════════
# FIX 11 — Aumentar conceptos de 5 a 10 filas
# ══════════════════════════════════════════════════════════════
fix('11-conceptos 5->10 rows',
    "function mkC() { return Array(5).fill(null).map((_,i)=>({num:i+1,desc:'',cantSol:0,cantEnt:0,pu:0,imp:0,ret5:false})); }",
    "function mkC() { return Array(10).fill(null).map((_,i)=>({num:i+1,desc:'',cantSol:0,cantEnt:0,pu:0,imp:0,ret5:false})); }"
)

# ══════════════════════════════════════════════════════════════
# Print results
# ══════════════════════════════════════════════════════════════
print('\n'.join(results))
print()
ok = sum(1 for r in results if r.startswith('OK'))
fail = sum(1 for r in results if r.startswith('FAIL'))
print(f'Total: {ok} OK, {fail} FAIL')

if fail == 0:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Saved: {len(html):,} chars')
else:
    print('NOT SAVED due to failures')
