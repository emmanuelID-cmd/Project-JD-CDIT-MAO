-- Multiple synthetic tickets may reference the same catalog prompt.
DROP INDEX IF EXISTS synthetic_cases_catalog_id_uq;
