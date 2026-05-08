#!/bin/bash
# scripts/validate_html.sh
# Valida que el JS embebido en index.html tenga sintaxis correcta antes de hacer push
# Uso: ./scripts/validate_html.sh
# Falla con exit 1 si hay error de sintaxis (para usar en pre-commit hook)

set -e

INDEX="${1:-index.html}"

if [ ! -f "$INDEX" ]; then
  echo "❌ No se encontró $INDEX"
  exit 1
fi

if ! command -v node &> /dev/null; then
  echo "❌ Node.js no está instalado. Instala con: brew install node"
  exit 1
fi

TMP=$(mktemp /tmp/validate_html_XXXXX.js)
trap "rm -f $TMP" EXIT

# En Git Bash / MSYS Windows, python3 es Windows-nativo y no entiende rutas /tmp/.
# Convertimos la ruta a formato Windows para Python; bash sigue usando $TMP.
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) TMP_FOR_PY=$(cygpath -w "$TMP") ;;
  *) TMP_FOR_PY="$TMP" ;;
esac

# Stubs del DOM para que node pueda parsear el script
cat > "$TMP" << 'STUBS'
const document = {
  getElementById: () => ({
    value:'', style:{display:''}, classList:{add:()=>{}, remove:()=>{}, toggle:()=>{}, contains:()=>false},
    textContent:'', innerHTML:'', disabled:false, checked:false,
    getBoundingClientRect: () => ({bottom:0,left:0,width:0,top:0,right:0,height:0}),
    scrollIntoView:()=>{}, focus:()=>{}, select:()=>{}, click:()=>{},
    appendChild:()=>{}, addEventListener:()=>{}, removeEventListener:()=>{},
    querySelector:()=>null, querySelectorAll:()=>[],
    selectedOptions:[{dataset:{}}], dataset:{}, options:[]
  }),
  querySelector: () => null,
  querySelectorAll: () => [],
  createElement: () => ({
    click:()=>{}, setAttribute:()=>{}, appendChild:()=>{},
    className:'', innerHTML:'', textContent:'', style:{},
    addEventListener:()=>{}, onclick:null, dataset:{}
  }),
  addEventListener: () => {},
  scripts:[{text:''}]
};
const window = {scrollY:0, jspdf:{jsPDF:function(){return{
  addImage:()=>{}, setFontSize:()=>{}, setFont:()=>{}, setTextColor:()=>{},
  text:()=>{}, line:()=>{}, rect:()=>{}, roundedRect:()=>{},
  setFillColor:()=>{}, setDrawColor:()=>{}, setLineWidth:()=>{},
  splitTextToSize:()=>[''], addPage:()=>{}, save:()=>{}
}}}};
// Mock de Supabase: cada método del query builder regresa el mismo objeto,
// permitiendo encadenar arbitrariamente (sb.from(x).select(y).eq(...)... .limit(n)).
// .then() permite que el chain sea awaitable y devuelva {data, error}.
const _sbChain = {};
['select','eq','neq','order','limit','single','range','is','like','ilike','match',
 'filter','in','contains','overlaps','rangeAdjacent','textSearch',
 'insert','update','delete','upsert','from','rpc','count']
  .forEach(m => { _sbChain[m] = function(){ return _sbChain; }; });
_sbChain.then = function(fn){ return fn({data: null, error: null}); };
const supabase = {
  createClient: () => Object.assign({}, _sbChain, {
    auth: {
      getSession: async () => ({data:{}}),
      signOut: async () => {},
      signInWithPassword: async () => ({data:{}}),
      admin: { createUser: async () => ({data:{}}) }
    }
  })
};
const confirm = ()=>true;
const alert = ()=>{};
const prompt = ()=>'';
const event = {key:'',preventDefault:()=>{},stopPropagation:()=>{}};
STUBS

# Extraer el último <script>...</script> del HTML (el principal)
# Escribimos directo al archivo con encoding utf-8 para evitar problemas en Windows
# (el HTML tiene caracteres no ASCII como en-dash, acentos, etc.).
python3 << PYEOF
with open(r'$INDEX', 'r', encoding='utf-8') as f:
    html = f.read()
start = html.rfind('<script>')
end = html.rfind('</script>')
if start < 0 or end < 0:
    raise SystemExit("No se encontró el bloque <script> principal")
with open(r'$TMP_FOR_PY', 'a', encoding='utf-8') as out:
    out.write(html[start+len('<script>'):end])
PYEOF

# Validar sintaxis con node
if node --check "$TMP" 2>&1; then
  echo "✓ Sintaxis JS OK — seguro para hacer push"
  exit 0
else
  echo ""
  echo "❌ ERROR DE SINTAXIS — NO HAGAS PUSH"
  echo ""
  echo "Causas comunes:"
  echo "  1. Comillas simples mal escapadas dentro de innerHTML"
  echo "  2. Variables const duplicadas en mismo scope"
  echo "  3. Template literals con backticks mezclados con apóstrofes en datos"
  echo ""
  echo "Lee docs/DEBUGGING.md para más detalles."
  exit 1
fi
