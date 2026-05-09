-- ══════════════════════════════════════════════════════════════════
-- 12_borrador_y_comprometido.sql
-- 1. Documenta los valores de status válidos (no hay ENUM en Supabase/Postgres
--    fácilmente, usamos CHECK constraint).
-- 2. Vista presupuesto_resumen que separa comprometido (pendiente) de
--    ejecutado (aprobado) para control financiero real.
-- ══════════════════════════════════════════════════════════════════

-- ── 1. CONSTRAINT de status en ordenes ───────────────────────────
-- (Solo agrega si no existe — idempotente)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'ordenes_status_values'
  ) THEN
    ALTER TABLE ordenes
      ADD CONSTRAINT ordenes_status_values
      CHECK (status IN (
        'borrador',
        'Folio guardado y pendiente de aprobacion',
        'Aprobado',
        'Rechazado',
        'Cancelado'
      ));
  END IF;
END $$;

-- ── 2. VISTA: presupuesto_resumen con comprometido ────────────────
-- Reemplaza la lógica de cálculo dispersa en JS con una vista DB.
-- comprometido = suma de órdenes PENDIENTES (enviadas, esperando decisión)
-- ejecutado    = suma de órdenes APROBADAS
-- disponible   = asignado - comprometido - ejecutado

CREATE OR REPLACE VIEW presupuesto_resumen AS
SELECT
  p.partida,
  p.descripcion_partida,
  COALESCE(SUM(p.monto), 0)                                          AS asignado,
  COALESCE(SUM(CASE
    WHEN o.status = 'Folio guardado y pendiente de aprobacion'
    THEN o.total ELSE 0 END), 0)                                     AS comprometido,
  COALESCE(SUM(CASE
    WHEN o.status = 'Aprobado'
    THEN o.total ELSE 0 END), 0)                                     AS ejecutado,
  COALESCE(SUM(p.monto), 0)
    - COALESCE(SUM(CASE
        WHEN o.status IN ('Folio guardado y pendiente de aprobacion','Aprobado')
        THEN o.total ELSE 0 END), 0)                                 AS disponible
FROM (
  SELECT DISTINCT ON (partida) partida, descripcion_partida,
    SUM(monto) OVER (PARTITION BY partida) AS monto
  FROM presupuestos
  GROUP BY partida, descripcion_partida, monto
) p
LEFT JOIN ordenes o
  ON o.partida = p.partida
  AND o.status NOT IN ('borrador','Rechazado','Cancelado')
GROUP BY p.partida, p.descripcion_partida;

-- La consulta JS cambia de presupuestos_partidas → presupuesto_resumen
-- Nota: si existía una vista "presupuestos_partidas", esta la complementa.
-- El JS puede usar cualquiera; el nuevo cargarPresupuestos() usa presupuesto_resumen.
