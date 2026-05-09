-- ══════════════════════════════════════════════════════════════════
-- 13_webhook_notificaciones.sql
-- Trigger PostgreSQL que dispara un HTTP POST a Make.com (o n8n)
-- cada vez que cambia el status de una orden.
--
-- PREREQUISITOS:
--   1. Habilitar pg_net en Supabase:
--      Dashboard → Database → Extensions → buscar "pg_net" → Enable
--
--   2. Crear el escenario en Make.com:
--      a. Nuevo escenario → Webhooks → Custom Webhook → Copy address
--      b. Agregar módulo según destino:
--         - WhatsApp (Twilio): usar conexión LUCY-TWILIO-FREE existente
--         - Email: usar módulo Email o SendGrid
--      c. El webhook recibirá el JSON con los campos de abajo
--
--   3. Reemplazar 'TU_WEBHOOK_URL_AQUI' con la URL de Make.com
--
-- APLICA EN: Supabase Dashboard → SQL Editor → New Query → Run
-- ══════════════════════════════════════════════════════════════════

-- ── Paso 1: Habilitar extensión pg_net ──────────────────────────
CREATE EXTENSION IF NOT EXISTS pg_net;

-- ── Paso 2: Configurar URL del webhook ──────────────────────────
-- Reemplazar la URL con la de tu escenario de Make.com
-- La URL tiene el formato: https://hook.us2.make.com/XXXXXXXXXXXXX
ALTER DATABASE postgres
  SET app.notif_webhook = 'TU_WEBHOOK_URL_AQUI';

-- ── Paso 3: Función trigger ──────────────────────────────────────
CREATE OR REPLACE FUNCTION trg_fn_notificar_status()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  _url  text;
  _body jsonb;
BEGIN
  -- Leer URL configurada; si no está, salir silenciosamente
  _url := current_setting('app.notif_webhook', true);
  IF _url IS NULL OR _url = '' OR _url = 'TU_WEBHOOK_URL_AQUI' THEN
    RETURN NEW;
  END IF;

  -- Solo disparar si el status cambió
  IF OLD.status IS NOT DISTINCT FROM NEW.status THEN
    RETURN NEW;
  END IF;

  -- Construir payload
  _body := jsonb_build_object(
    'evento',             'orden_status_changed',
    'folio',              NEW.folio,
    'status_anterior',    OLD.status,
    'status_nuevo',       NEW.status,
    'nombre_solicitante', COALESCE(NEW.nombre_solicitante, ''),
    'nombre_proveedor',   COALESCE(NEW.nombre_proveedor, ''),
    'unidad',             COALESCE(NEW.unidad, ''),
    'partida',            COALESCE(NEW.partida, ''),
    'total',              COALESCE(NEW.total, 0),
    'comentario_admin',   COALESCE(NEW.comentario_aprobacion, ''),
    'timestamp_mx',       to_char(
                            NOW() AT TIME ZONE 'America/Tijuana',
                            'DD/MM/YYYY HH24:MI'
                          ),
    'url_sistema',        'https://ederimiramontes.github.io/ordenes-imss/'
  );

  -- Enviar HTTP POST asíncrono (pg_net no bloquea la transacción)
  PERFORM net.http_post(
    url     := _url,
    headers := '{"Content-Type": "application/json"}'::jsonb,
    body    := _body::text
  );

  RETURN NEW;
EXCEPTION
  -- Si el webhook falla, NO revertir la transacción de la orden
  WHEN OTHERS THEN
    RAISE WARNING 'trg_notificar_status: error enviando webhook: %', SQLERRM;
    RETURN NEW;
END;
$$;

-- ── Paso 4: Crear el trigger ─────────────────────────────────────
DROP TRIGGER IF EXISTS trg_notificar_status ON ordenes;

CREATE TRIGGER trg_notificar_status
  AFTER UPDATE OF status ON ordenes
  FOR EACH ROW
  EXECUTE FUNCTION trg_fn_notificar_status();

-- ── Verificar ────────────────────────────────────────────────────
-- Después de aplicar, confirma con:
-- SELECT * FROM pg_trigger WHERE tgname = 'trg_notificar_status';
-- SELECT * FROM pg_extension WHERE extname = 'pg_net';

-- ── Payload que Make.com recibirá (referencia) ────────────────────
-- {
--   "evento":             "orden_status_changed",
--   "folio":              "202534650",
--   "status_anterior":    "Folio guardado y pendiente de aprobacion",
--   "status_nuevo":       "Aprobado",
--   "nombre_solicitante": "ING. JUAN PÉREZ",
--   "nombre_proveedor":   "Servicios Integrales SA de CV",
--   "unidad":             "HGZ30",
--   "partida":            "_51351002",
--   "total":              45200.00,
--   "comentario_admin":   "Aprobado conforme a contrato",
--   "timestamp_mx":       "15/05/2026 14:30",
--   "url_sistema":        "https://ederimiramontes.github.io/ordenes-imss/"
-- }
--
-- Make.com: usar estos campos con {{1.folio}}, {{1.status_nuevo}}, etc.
-- WhatsApp template sugerido:
--   "✅ Orden *{{1.folio}}* ha sido *{{1.status_nuevo}}*
--    Proveedor: {{1.nombre_proveedor}}
--    Total: ${{1.total}}
--    {{1.comentario_admin}}"
