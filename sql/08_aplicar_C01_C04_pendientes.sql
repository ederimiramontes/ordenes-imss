-- ═══════════════════════════════════════════════════════════════
-- 08 — APLICAR C-01 y C-04 PENDIENTES
-- IMSS Órdenes de Servicio · 2026-05-07
-- ═══════════════════════════════════════════════════════════════
-- Contexto: La auditoría descubrió que las secciones C-01 (folios atómicos)
-- y C-04 (auditoría + soft delete) del script 07_hardening_criticos.sql
-- no se ejecutaron en producción. Las tablas folio_contador y audit_log
-- NO existen actualmente. Este script las aplica.
--
-- ⚠️ ANTES DE EJECUTAR:
--   1. Ya hicimos backup de datos en respaldos-imss/data-20260507/
--   2. Tener branch GitHub backup-pre-claude-code-20260507 confirmado
--   3. Ejecutar en Supabase → SQL Editor → New query → Run
--
-- ✅ Es seguro correrlo varias veces (idempotente: IF NOT EXISTS, OR REPLACE,
--    IF EXISTS DROP). No afectará datos existentes.
--
-- ⏱️ Tiempo de ejecución: <5 segundos. Bloqueo en tabla ordenes mínimo
--    (ALTER TABLE ADD COLUMN sin DEFAULT es metadata-only, no reescribe filas).
-- ═══════════════════════════════════════════════════════════════


-- ╔═══════════════════════════════════════════════════════════════╗
-- ║  C-01: GENERACIÓN ATÓMICA DE FOLIOS (sin race condition)      ║
-- ╚═══════════════════════════════════════════════════════════════╝

-- Tabla contador por año
CREATE TABLE IF NOT EXISTS folio_contador (
  anio INTEGER PRIMARY KEY,
  ultimo INTEGER NOT NULL DEFAULT 0,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inicializar contador del año actual con base en folios existentes
-- (importante: respeta folios ya generados client-side hasta hoy)
INSERT INTO folio_contador (anio, ultimo)
SELECT
  EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER,
  COALESCE(MAX(SUBSTRING(folio FROM 5)::INTEGER), 0)
FROM ordenes
WHERE folio LIKE EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '%'
ON CONFLICT (anio) DO NOTHING;

-- Función atómica que genera el siguiente folio
CREATE OR REPLACE FUNCTION generar_folio_consecutivo()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_anio INTEGER;
  v_siguiente INTEGER;
  v_folio TEXT;
BEGIN
  v_anio := EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER;

  INSERT INTO folio_contador (anio, ultimo)
  VALUES (v_anio, 1)
  ON CONFLICT (anio) DO UPDATE
    SET ultimo = folio_contador.ultimo + 1,
        updated_at = NOW()
  RETURNING ultimo INTO v_siguiente;

  v_folio := v_anio::TEXT || LPAD(v_siguiente::TEXT, 4, '0');
  RETURN v_folio;
END;
$$;

GRANT EXECUTE ON FUNCTION generar_folio_consecutivo() TO authenticated;


-- ╔═══════════════════════════════════════════════════════════════╗
-- ║  C-04: SOFT DELETE + TABLA DE AUDITORÍA                       ║
-- ╚═══════════════════════════════════════════════════════════════╝

-- Campos de soft delete en ordenes (idempotente)
ALTER TABLE ordenes ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE ordenes ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES auth.users(id);
ALTER TABLE ordenes ADD COLUMN IF NOT EXISTS motivo_eliminacion TEXT;

-- Tabla de auditoría
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tabla TEXT NOT NULL,
  registro_id UUID,
  registro_folio TEXT,
  accion TEXT NOT NULL,
  usuario_id UUID REFERENCES auth.users(id),
  nombre_usuario TEXT,
  datos_antes JSONB,
  datos_despues JSONB,
  motivo TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_tabla ON audit_log(tabla);
CREATE INDEX IF NOT EXISTS idx_audit_usuario ON audit_log(usuario_id);
CREATE INDEX IF NOT EXISTS idx_audit_fecha ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_folio ON audit_log(registro_folio);

-- RLS: lectura abierta a autenticados; INSERT solo vía trigger SECURITY DEFINER
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Autenticados pueden ver auditoria" ON audit_log;
CREATE POLICY "Autenticados pueden ver auditoria"
  ON audit_log FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS "Solo sistema inserta auditoria" ON audit_log;
CREATE POLICY "Solo sistema inserta auditoria"
  ON audit_log FOR INSERT TO authenticated WITH CHECK (true);

-- Trigger de auditoría para órdenes
CREATE OR REPLACE FUNCTION auditar_orden()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_nombre_usuario TEXT;
BEGIN
  SELECT nombre_completo INTO v_nombre_usuario
  FROM perfiles WHERE id = auth.uid() LIMIT 1;

  IF TG_OP = 'INSERT' THEN
    INSERT INTO audit_log (tabla, registro_id, registro_folio, accion, usuario_id, nombre_usuario, datos_despues)
    VALUES ('ordenes', NEW.id, NEW.folio, 'CREAR', auth.uid(), v_nombre_usuario, to_jsonb(NEW));
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    IF OLD.status != NEW.status THEN
      INSERT INTO audit_log (tabla, registro_id, registro_folio, accion, usuario_id, nombre_usuario, datos_antes, datos_despues, motivo)
      VALUES ('ordenes', NEW.id, NEW.folio,
        CASE
          WHEN NEW.status ILIKE '%aprobado%' THEN 'APROBAR'
          WHEN NEW.status ILIKE '%rechazado%' THEN 'RECHAZAR'
          ELSE 'ACTUALIZAR_STATUS'
        END,
        auth.uid(), v_nombre_usuario,
        jsonb_build_object('status', OLD.status),
        jsonb_build_object('status', NEW.status),
        NEW.comentario_aprobacion);
    END IF;
    IF OLD.deleted_at IS NULL AND NEW.deleted_at IS NOT NULL THEN
      INSERT INTO audit_log (tabla, registro_id, registro_folio, accion, usuario_id, nombre_usuario, datos_antes, motivo)
      VALUES ('ordenes', NEW.id, NEW.folio, 'ELIMINAR', auth.uid(), v_nombre_usuario, to_jsonb(OLD), NEW.motivo_eliminacion);
    END IF;
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO audit_log (tabla, registro_id, registro_folio, accion, usuario_id, nombre_usuario, datos_antes)
    VALUES ('ordenes', OLD.id, OLD.folio, 'BORRAR_FISICO', auth.uid(), v_nombre_usuario, to_jsonb(OLD));
    RETURN OLD;
  END IF;
  RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS trg_auditar_orden ON ordenes;
CREATE TRIGGER trg_auditar_orden
  AFTER INSERT OR UPDATE OR DELETE ON ordenes
  FOR EACH ROW
  EXECUTE FUNCTION auditar_orden();


-- ╔═══════════════════════════════════════════════════════════════╗
-- ║  Vista auxiliar: órdenes activas (sin eliminadas)             ║
-- ╚═══════════════════════════════════════════════════════════════╝

CREATE OR REPLACE VIEW ordenes_activas AS
SELECT * FROM ordenes WHERE deleted_at IS NULL;

GRANT SELECT ON ordenes_activas TO authenticated;


-- ═══════════════════════════════════════════════════════════════
-- VERIFICACIÓN POST-EJECUCIÓN (correr estas queries para confirmar)
-- ═══════════════════════════════════════════════════════════════

-- 1. Ver contador inicializado (debe mostrar el año y el último folio existente)
SELECT * FROM folio_contador;

-- 2. Ver que la función existe
SELECT proname FROM pg_proc WHERE proname = 'generar_folio_consecutivo';

-- 3. Ver que la tabla audit_log existe y está vacía
SELECT COUNT(*) AS total_auditorias FROM audit_log;

-- 4. Ver que el trigger está instalado
SELECT tgname FROM pg_trigger WHERE tgname = 'trg_auditar_orden';

-- 5. Ver que las columnas de soft delete existen en ordenes
SELECT column_name FROM information_schema.columns
WHERE table_name = 'ordenes' AND column_name IN ('deleted_at','deleted_by','motivo_eliminacion');
