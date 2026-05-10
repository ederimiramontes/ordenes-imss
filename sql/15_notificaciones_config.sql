-- ══════════════════════════════════════════════════════════════════
-- 15_notificaciones_config.sql
-- Setup completo para el sistema de notificaciones vía n8n.
--
-- YA APLICADO en producción (igosubejkzrxgpuqmbpo) — Mayo 2026
-- Incluye: configuracion_sistema, email_notificacion, pg_net,
--          función trigger actualizada con campos de email.
--
-- Para aplicar en un proyecto nuevo:
--   Supabase Dashboard → SQL Editor → New Query → Run
-- ══════════════════════════════════════════════════════════════════

-- ── 1. Tabla configuracion_sistema ──────────────────────────────
CREATE TABLE IF NOT EXISTS configuracion_sistema (
  clave       TEXT PRIMARY KEY,
  valor       TEXT NOT NULL,
  descripcion TEXT,
  updated_at  TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE configuracion_sistema ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE tablename='configuracion_sistema' AND policyname='config_read'
  ) THEN
    CREATE POLICY "config_read" ON configuracion_sistema
      FOR SELECT TO authenticated USING (true);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE tablename='configuracion_sistema' AND policyname='config_write'
  ) THEN
    CREATE POLICY "config_write" ON configuracion_sistema
      FOR ALL TO authenticated
      USING (EXISTS(SELECT 1 FROM perfiles WHERE id=auth.uid() AND tipo='Admin'))
      WITH CHECK (EXISTS(SELECT 1 FROM perfiles WHERE id=auth.uid() AND tipo='Admin'));
  END IF;
END $$;

INSERT INTO configuracion_sistema (clave, valor, descripcion) VALUES
  ('admin_emails', 'ederimiramontes@hotmail.com',
   'Correos de admins separados por coma que reciben notificaciones de nuevas ordenes')
ON CONFLICT (clave) DO NOTHING;

-- ── 2. Columna email_notificacion en perfiles y solicitudes ──────
ALTER TABLE perfiles           ADD COLUMN IF NOT EXISTS email_notificacion TEXT;
ALTER TABLE solicitudes_usuarios ADD COLUMN IF NOT EXISTS email_notificacion TEXT;

-- ── 3. Extensión pg_net (envío HTTP desde triggers) ──────────────
CREATE EXTENSION IF NOT EXISTS pg_net;

-- ── 4. Función trigger actualizada (incluye email_solicitante y admin_emails) ──
-- Sustituye a la versión original de sql/13_webhook_notificaciones.sql
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
  _url := current_setting('app.notif_webhook', true);
  IF _url IS NULL OR _url = '' OR _url = 'TU_WEBHOOK_URL_AQUI' THEN
    RETURN NEW;
  END IF;

  IF OLD.status IS NOT DISTINCT FROM NEW.status THEN
    RETURN NEW;
  END IF;

  _body := jsonb_build_object(
    'evento',            'orden_status_changed',
    'folio',             NEW.folio,
    'status_anterior',   OLD.status,
    'status_nuevo',      NEW.status,
    'nombre_solicitante',COALESCE(NEW.nombre_solicitante, ''),
    'nombre_proveedor',  COALESCE(NEW.nombre_proveedor, ''),
    'unidad',            COALESCE(NEW.unidad, ''),
    'partida',           COALESCE(NEW.partida, ''),
    'total',             COALESCE(NEW.total, 0),
    'comentario_admin',  COALESCE(NEW.comentario_aprobacion, ''),
    'timestamp_mx',      to_char(
                           NOW() AT TIME ZONE 'America/Tijuana',
                           'DD/MM/YYYY HH24:MI'
                         ),
    'url_sistema',       'https://ederimiramontes.github.io/ordenes-imss/',
    'email_solicitante', COALESCE(
                           (SELECT email_notificacion FROM perfiles WHERE id = NEW.created_by),
                           (SELECT email FROM auth.users WHERE id = NEW.created_by)
                         ),
    'admin_emails',      (SELECT valor FROM configuracion_sistema WHERE clave = 'admin_emails')
  );

  PERFORM net.http_post(
    url     := _url,
    headers := '{"Content-Type": "application/json"}'::jsonb,
    body    := _body::text
  );

  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    RAISE WARNING 'trg_notificar_status: error enviando webhook: %', SQLERRM;
    RETURN NEW;
END;
$$;

-- ── 5. Recrear trigger ───────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_notificar_status ON ordenes;
CREATE TRIGGER trg_notificar_status
  AFTER UPDATE OF status ON ordenes
  FOR EACH ROW
  EXECUTE FUNCTION trg_fn_notificar_status();

-- ── 6. Activar webhook (hacer después de crear workflow en n8n) ──
-- Reemplazar con la URL real del webhook de n8n:
-- ALTER DATABASE postgres SET app.notif_webhook = 'https://n8n.../webhook/...';

-- ── Verificar ────────────────────────────────────────────────────
-- SELECT tgname, tgenabled FROM pg_trigger WHERE tgname='trg_notificar_status';
-- SELECT * FROM configuracion_sistema;
-- SELECT extname FROM pg_extension WHERE extname='pg_net';
