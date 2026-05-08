-- ═══════════════════════════════════════════════════════════════
-- 08 ROLLBACK — DESHACE C-01 y C-04
-- IMSS Órdenes de Servicio · 2026-05-08
-- ═══════════════════════════════════════════════════════════════
-- Solo correr si el script 08_aplicar_C01_C04_pendientes.sql produjo
-- un comportamiento inesperado en producción y queremos volver al
-- estado anterior (sin las tablas folio_contador / audit_log y sin
-- el trigger de auditoría).
--
-- ⚠️ ADVERTENCIAS:
--   • Si ya hay registros en audit_log, se perderán al hacer DROP.
--     Si quieres conservarlos como evidencia, antes de correr esto:
--       SELECT * FROM audit_log;  -- copia el resultado a CSV manualmente.
--   • Si ya hay órdenes con folios generados por la función atómica,
--     el contador en folio_contador se pierde. Los folios YA emitidos
--     siguen en la tabla ordenes (no se borran), pero el siguiente
--     folio que genere el código viejo (genFolio client-side) puede
--     colisionar si no se cuida.
--   • Este script NO toca la tabla ordenes (los datos de órdenes son
--     intocables). Solo elimina los add-ons del hardening C-01 y C-04.
-- ═══════════════════════════════════════════════════════════════

BEGIN;

-- C-04 reversa: trigger y tabla de auditoría
DROP TRIGGER IF EXISTS trg_auditar_orden ON ordenes;
DROP FUNCTION IF EXISTS auditar_orden() CASCADE;
DROP VIEW IF EXISTS ordenes_activas;
DROP TABLE IF EXISTS audit_log;

-- Columnas de soft delete: las dejamos por seguridad (son nullable, no
-- estorban). Si quieres forzosamente quitarlas, descomenta:
-- ALTER TABLE ordenes DROP COLUMN IF EXISTS deleted_at;
-- ALTER TABLE ordenes DROP COLUMN IF EXISTS deleted_by;
-- ALTER TABLE ordenes DROP COLUMN IF EXISTS motivo_eliminacion;

-- C-01 reversa: función atómica y tabla contador
DROP FUNCTION IF EXISTS generar_folio_consecutivo() CASCADE;
DROP TABLE IF EXISTS folio_contador;

COMMIT;

-- ═══════════════════════════════════════════════════════════════
-- VERIFICACIÓN POST-ROLLBACK
-- ═══════════════════════════════════════════════════════════════

-- Estas queries deben regresar 0 filas si el rollback se aplicó bien:
SELECT 'folio_contador' AS objeto, COUNT(*) AS aun_existe
  FROM information_schema.tables
  WHERE table_name = 'folio_contador';

SELECT 'audit_log' AS objeto, COUNT(*) AS aun_existe
  FROM information_schema.tables
  WHERE table_name = 'audit_log';

SELECT 'generar_folio_consecutivo' AS objeto, COUNT(*) AS aun_existe
  FROM pg_proc
  WHERE proname = 'generar_folio_consecutivo';

SELECT 'auditar_orden' AS objeto, COUNT(*) AS aun_existe
  FROM pg_proc
  WHERE proname = 'auditar_orden';
