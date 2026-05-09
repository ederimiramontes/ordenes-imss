-- ══════════════════════════════════════════════════════════════════
-- 14_zona_proveedores_csf.sql
-- C: zona geográfica en proveedores
-- D: constancia de situación fiscal en proveedores
-- ══════════════════════════════════════════════════════════════════

-- ── C: zona geográfica ───────────────────────────────────────────
-- NULL = opera en todo BC (aparece en todas las unidades)
-- Valores: 'M' = Mexicali  'T' = Tijuana  'E' = Ensenada
-- Un proveedor puede tener múltiples zonas: 'M,T'
ALTER TABLE proveedores_catalogo
  ADD COLUMN IF NOT EXISTS zona TEXT;

ALTER TABLE solicitudes_proveedores
  ADD COLUMN IF NOT EXISTS zona TEXT;

COMMENT ON COLUMN proveedores_catalogo.zona IS
  'Zonas donde opera: M=Mexicali, T=Tijuana, E=Ensenada. NULL=todo BC.';

-- ── D: constancia de situación fiscal ────────────────────────────
ALTER TABLE proveedores_catalogo
  ADD COLUMN IF NOT EXISTS constancia_url TEXT;

ALTER TABLE solicitudes_proveedores
  ADD COLUMN IF NOT EXISTS constancia_url TEXT;

COMMENT ON COLUMN proveedores_catalogo.constancia_url IS
  'URL pública del PDF de Constancia de Situación Fiscal en Supabase Storage.';

-- ── Storage bucket para constancias ──────────────────────────────
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  VALUES (
    'constancias', 'constancias', true,
    5242880,                                    -- 5 MB máx por archivo
    ARRAY['application/pdf','image/jpeg','image/png']
  )
ON CONFLICT (id) DO NOTHING;

-- RLS: cualquier autenticado puede subir y leer
CREATE POLICY IF NOT EXISTS "constancias_select"
  ON storage.objects FOR SELECT TO authenticated
  USING (bucket_id = 'constancias');

CREATE POLICY IF NOT EXISTS "constancias_insert"
  ON storage.objects FOR INSERT TO authenticated
  WITH CHECK (bucket_id = 'constancias');
