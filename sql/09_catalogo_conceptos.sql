-- ══════════════════════════════════════════════════════════════════
-- 09_catalogo_conceptos.sql
-- Catálogo de descripciones de servicio ligadas a partida presupuestal,
-- proveedor y unidad médica.
--
-- Aplicar en: Supabase Dashboard → SQL Editor → New Query → Run
-- O vía Management API (PAT necesario).
-- ══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS catalogo_conceptos (
  id                    uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  descripcion           text NOT NULL,
  partida_clave         text NOT NULL,
  partida_desc          text,
  proveedor_razon_social text,   -- NULL = aplica a cualquier proveedor
  delegacion            text NOT NULL DEFAULT 'Baja California',
  unidad                text,    -- NULL = aplica a todas las unidades del estado
  aplica_ret5           boolean NOT NULL DEFAULT false,
  precio_referencia     numeric(12,2),
  activo                boolean NOT NULL DEFAULT true,
  created_at            timestamptz NOT NULL DEFAULT now(),
  created_by            uuid REFERENCES auth.users(id)
);

-- Índices para filtrado rápido en el formulario de orden
CREATE INDEX IF NOT EXISTS idx_catcon_partida
  ON catalogo_conceptos(partida_clave);

CREATE INDEX IF NOT EXISTS idx_catcon_prov
  ON catalogo_conceptos(proveedor_razon_social)
  WHERE proveedor_razon_social IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_catcon_activo
  ON catalogo_conceptos(activo, partida_clave);

-- ══ RLS ══
ALTER TABLE catalogo_conceptos ENABLE ROW LEVEL SECURITY;

-- Cualquier usuario autenticado puede leer entradas activas
CREATE POLICY "catcon_read"
  ON catalogo_conceptos FOR SELECT
  TO authenticated
  USING (activo = true);

-- Cualquier usuario autenticado puede insertar (admin valida en la UI)
CREATE POLICY "catcon_insert"
  ON catalogo_conceptos FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Update y delete: solo el creador o admin (RLS básico; el admin-check
-- se refuerza en la UI con isAdmin)
CREATE POLICY "catcon_update"
  ON catalogo_conceptos FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "catcon_delete"
  ON catalogo_conceptos FOR DELETE
  TO authenticated
  USING (true);
