"""
gen_sql_catalogos.py
Genera sql/11_catalogo_unidades_partidas.sql leyendo los datos
directamente de las constantes JS de index.html.
"""
import sys, io, re, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(base, 'index.html'), encoding='utf-8') as f:
    content = f.read()

unidades = json.loads(re.search(r'const UNIDADES = (\[.*?\]);', content, re.DOTALL).group(1))
partidas  = json.loads(re.search(r'const PARTIDAS = (\[.*?\]);',  content, re.DOTALL).group(1))

def sq(v):
    if v is None: return 'NULL'
    return "'" + str(v).replace("'", "''") + "'"

lines = ["""-- ══════════════════════════════════════════════════════════════════
-- 11_catalogo_unidades_partidas.sql
-- Mueve los catálogos de UNIDADES y PARTIDAS de constantes JS a Supabase.
-- Aplicar en: SQL Editor del dashboard de Supabase o vía Management API.
-- ══════════════════════════════════════════════════════════════════

-- ── CATÁLOGO DE UNIDADES MÉDICAS ─────────────────────────────────
CREATE TABLE IF NOT EXISTS catalogo_unidades (
  id         uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  jcu        integer,
  ui         integer,
  cc         integer,
  unidad     text NOT NULL,
  localidad  text,
  activo     boolean NOT NULL DEFAULT true,
  orden      integer,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_catun_unidad  ON catalogo_unidades(unidad);
CREATE INDEX IF NOT EXISTS idx_catun_activo  ON catalogo_unidades(activo);

ALTER TABLE catalogo_unidades ENABLE ROW LEVEL SECURITY;
CREATE POLICY "catun_read"   ON catalogo_unidades FOR SELECT TO authenticated USING (activo = true);
CREATE POLICY "catun_write"  ON catalogo_unidades FOR ALL    TO authenticated
  USING   (EXISTS(SELECT 1 FROM perfiles WHERE id=auth.uid() AND tipo='Admin'))
  WITH CHECK (EXISTS(SELECT 1 FROM perfiles WHERE id=auth.uid() AND tipo='Admin'));

-- ── CATÁLOGO DE PARTIDAS PRESUPUESTALES ──────────────────────────
CREATE TABLE IF NOT EXISTS catalogo_partidas (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  clave       text NOT NULL UNIQUE,
  descripcion text NOT NULL,
  tipo        text,
  activo      boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_catpar_clave  ON catalogo_partidas(clave);
CREATE INDEX IF NOT EXISTS idx_catpar_activo ON catalogo_partidas(activo);

ALTER TABLE catalogo_partidas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "catpar_read"  ON catalogo_partidas FOR SELECT TO authenticated USING (activo = true);
CREATE POLICY "catpar_write" ON catalogo_partidas FOR ALL    TO authenticated
  USING   (EXISTS(SELECT 1 FROM perfiles WHERE id=auth.uid() AND tipo='Admin'))
  WITH CHECK (EXISTS(SELECT 1 FROM perfiles WHERE id=auth.uid() AND tipo='Admin'));

-- ── SEED: UNIDADES ────────────────────────────────────────────────
INSERT INTO catalogo_unidades (jcu, ui, cc, unidad, localidad, orden) VALUES"""]

rows = []
for i, u in enumerate(unidades):
    rows.append(f"  ({u.get('jcu') or 'NULL'}, {u.get('ui') or 'NULL'}, {u.get('cc') or 'NULL'}, {sq(u['unidad'])}, {sq(u.get('localidad'))}, {i+1})")
lines.append(',\n'.join(rows) + '\nON CONFLICT DO NOTHING;\n')

lines.append("-- ── SEED: PARTIDAS ──────────────────────────────────────────────")
lines.append("INSERT INTO catalogo_partidas (clave, descripcion, tipo) VALUES")
rows2 = []
for p in partidas:
    rows2.append(f"  ({sq(p['clave'])}, {sq(p['descripcion'])}, {sq(p.get('tipo'))})")
lines.append(',\n'.join(rows2) + '\nON CONFLICT (clave) DO NOTHING;\n')

sql = '\n'.join(lines)
out = os.path.join(base, 'sql', '11_catalogo_unidades_partidas.sql')
with open(out, 'w', encoding='utf-8') as f:
    f.write(sql)
print(f'Generado: {out}')
print(f'  {len(unidades)} unidades, {len(partidas)} partidas')
