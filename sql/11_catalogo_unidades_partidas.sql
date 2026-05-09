-- ══════════════════════════════════════════════════════════════════
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
INSERT INTO catalogo_unidades (jcu, ui, cc, unidad, localidad, orden) VALUES
  (1, 20101, 142902, 'HGZ30', 'M', 1),
  (11, 20201, 142902, 'HGZ8', 'E', 2),
  (17, 20701, 142902, 'HGSZMF6', 'TKT', 3),
  (6, 20702, 142902, 'HGSZMF12', 'SL', 4),
  (7, 20501, 142902, 'HGR20', 'T', 5),
  (15, 20502, 142902, 'HGR1', 'T', 6),
  (8, 21301, 142902, 'HGOMF7', 'T', 7),
  (2, 21601, 142902, 'HGPMF31', 'M', 8),
  (16, 22201, 142902, 'UMF15', 'SL', 9),
  (16, 22202, 142902, 'UMF3', 'SL', 10),
  (16, 22203, 142902, 'UMF2', 'SL', 11),
  (5, 22204, 142902, 'UMF5', 'M', 12),
  (5, 22205, 142902, 'UMF4', 'M', 13),
  (5, 22206, 142902, 'UMF10', 'M', 14),
  (16, 22207, 142902, 'UMF9', 'SL', 15),
  (13, 22208, 142902, 'UMF13', 'E', 16),
  (5, 22209, 142902, 'UMF24', 'M', 17),
  (4, 22401, 142902, 'UMF26', 'M', 18),
  (5, 22402, 142902, 'UMF16', 'M', 19),
  (4, 22403, 142902, 'UMF28', 'M', 20),
  (4, 22404, 142902, 'UMF37', 'M', 21),
  (12, 22405, 142902, 'UMF25', 'E', 22),
  (12, 22406, 142902, 'UMF32', 'E', 23),
  (9, 22407, 142902, 'UMF27', 'T', 24),
  (10, 22408, 142902, 'UMF19', 'T', 25),
  (14, 22409, 142902, 'UMF36', 'T', 26),
  (10, 22410, 142902, 'UMF33', 'T', 27),
  (14, 22411, 142902, 'UMF34', 'T', 28),
  (14, 22412, 142902, 'UMF35', 'T', 29),
  (12, 22413, 142902, 'UMF11', 'E', 30),
  (12, 22414, 142902, 'UMF29', 'E', 31),
  (12, 22415, 142902, 'UMF14', 'E', 32),
  (10, 22416, 142902, 'UMF17', 'T', 33),
  (12, 22417, 142901, 'UMF22', 'E', 34),
  (16, 22418, 142902, 'UMF38', 'SL', 35),
  (18, 22420, 142902, 'UMF39', 'TKT', 36),
  (19, 22422, 142902, 'UMF18', 'T', 37),
  (20, 22421, 142902, 'UMF40', 'M', 38),
  (10, 22424, 142902, 'UMF21', 'R', 39),
  (15, 23701, 142902, 'MAMA', 'T', 40),
  (5, 25301, 310203, 'CSSMXLI', 'M', 41),
  (6, 25302, 310203, 'CSSSL', 'SL', 42),
  (8, 25303, 310203, 'CSSTJ', 'TJ', 43),
  (3, 25402, 310202, 'CAMPO BEIS', 'M', 44),
  (1, 25501, 310209, 'TEAMXLI', 'M', 45),
  (8, 25502, 310209, 'TEATJ', 'TJ', 46),
  (12, 25801, 800201, 'CCAPAC', 'TJ', 47),
  (12, 25902, 380200, 'TIENDAENS', 'ENS', 48),
  (9, 25904, 380200, 'TIENDATJ', 'TJ', 49),
  (4, 26301, 320200, 'GUARDMXLI', 'M', 50),
  (12, 26302, 320200, 'GUARDENS', 'ENS', 51),
  (10, 26303, 320200, 'GUARDTJ', 'TJ', 52),
  (3, 28001, 142902, 'ALMDELEG', 'M', 53),
  (3, 28102, 380903, 'ALMKM11.5', 'M', 54),
  (3, 29001, 100100, 'OFDELEG', 'M', 55),
  (3, 29001, 50100, 'CASADELEG', 'M', 56),
  (3, 29101, 900110, 'SUBDELEMXLI', 'M', 57),
  (17, 29102, 900110, 'SUBDELETKT', 'TKT', 58),
  (12, 29103, 900110, 'SUBDELEGENS', 'ENS', 59),
  (6, 29104, 900110, 'SUBDELESL', 'SL', 60),
  (8, 29105, 900110, 'SUBDELEGTJ', 'TJ', 61),
  (14, 23101, 250901, 'ESCENF', 'TJ', 62),
  (13, 520301, 73200, 'HRO69', 'SQ', 63),
  (13, 524001, 73200, 'UMR´S', 'SQ', 64)
ON CONFLICT DO NOTHING;

-- ── SEED: PARTIDAS ──────────────────────────────────────────────
INSERT INTO catalogo_partidas (clave, descripcion, tipo) VALUES
  ('_42060509', 'Prendas  de Protección Personal', 'compra emergente'),
  ('_42060901', 'Productos Minerales No Metálicos', 'compra emergente'),
  ('_42060902', 'Cemento Y Productos de Concreto', 'compra emergente'),
  ('_42060903', 'Cal, Yeso Y Productos de Yeso', 'compra emergente'),
  ('_42060904', 'Madera Y Productos de Madera', 'compra emergente'),
  ('_42060905', 'Vidrio Y Productos de Vidrio', 'compra emergente'),
  ('_42060906', 'Material Eléctrico Y Electrónico', 'compra emergente'),
  ('_42060907', 'Artículos Metálicos Para La Construcción', 'compra emergente'),
  ('_42060908', 'Materiales Complementarios', 'compra emergente'),
  ('_42060909', 'Otros Materiales Y Artículos de Construcción Y Reparación', 'compra emergente'),
  ('_42062441', 'Otros Productos Químicos', 'compra emergente'),
  ('_51351003', 'Mantenimiento Y Conservación de Mobiliario Y Equipo de Administración', 'servicio subrrogado'),
  ('_51351002', 'Servicios Subrogados de Mantenimiento Y Conservación de Inmuebles', 'servicio subrrogado'),
  ('_51351005', 'Instalación, Reparación Y Mantenimiento de Equipo E Instrumental Médico Y de Laboratorio', 'servicio subrrogado'),
  ('_51351008', 'Mantenimiento Y Conservación de Maquinaria Y Equipo', 'servicio subrrogado'),
  ('_51351013', 'Servicios de Jardinería Y Fumigación', 'servicio subrrogado'),
  ('_42062517', 'Herramientas Menores', 'compra emergente'),
  ('_42062527', 'Refacciones Y Accesorios Menores de Edificios', 'compra emergente'),
  ('_42062528', 'Refacciones Y Accesorios Menores de Mobiliario Y Equipo de Administración', 'compra emergente'),
  ('_42062529', 'Refacciones Y Accesorios Menores de Equipo E Instrumental Médico Y de Laboratorio', 'compra emergente'),
  ('_42062530', 'Refacciones Y Accesorios Menores de Maquinaria Y Otros Equipos', 'compra emergente')
ON CONFLICT (clave) DO NOTHING;
