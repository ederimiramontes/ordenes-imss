-- ══════════════════════════════════════════════════════════════════
-- 10_fix_rls_catalogo.sql
-- Restricción RLS en catalogo_conceptos: solo admins pueden eliminar.
-- INSERT/UPDATE: cualquier autenticado (los usuarios pueden proponer).
-- DELETE: solo perfiles con tipo = 'Admin'.
-- ══════════════════════════════════════════════════════════════════

-- Eliminar política de delete demasiado permisiva
DROP POLICY IF EXISTS "catcon_delete" ON catalogo_conceptos;

-- Nueva política: solo Admin puede borrar
CREATE POLICY "catcon_delete_admin"
  ON catalogo_conceptos FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM perfiles
      WHERE perfiles.id = auth.uid()
        AND perfiles.tipo = 'Admin'
    )
  );
