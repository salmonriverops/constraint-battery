-- The landing schema. Six tables. This is the asset.
-- Resist adding a seventh. If a business seems to need one, say so instead of adding it.
--
-- kind and role are free strings. No probe may branch on a specific value of either.
-- money is deliberately omitted from version one.

CREATE TABLE work (
  work_id TEXT PRIMARY KEY, work_type TEXT, start_ts TIMESTAMP, end_ts TIMESTAMP,
  location_id TEXT, status TEXT, customer_count INTEGER,
  source_system TEXT, source_id TEXT, extracted_at TIMESTAMP
);
CREATE TABLE resources (
  resource_id TEXT PRIMARY KEY, kind TEXT, name TEXT, home_location_id TEXT,
  active_from DATE, active_to DATE,
  source_system TEXT, source_id TEXT, extracted_at TIMESTAMP
);
CREATE TABLE assignments (
  assignment_id TEXT PRIMARY KEY, resource_id TEXT, work_id TEXT, role TEXT,
  start_ts TIMESTAMP, end_ts TIMESTAMP,
  source_system TEXT, source_id TEXT, extracted_at TIMESTAMP
);
CREATE TABLE locations (location_id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE location_travel (from_id TEXT, to_id TEXT, minutes INTEGER, is_estimate BOOLEAN);
CREATE TABLE changes (
  change_id TEXT PRIMARY KEY, entity_table TEXT, entity_id TEXT, field TEXT,
  old_value TEXT, new_value TEXT, changed_at TIMESTAMP, changed_by TEXT,
  source_system TEXT, source_id TEXT, extracted_at TIMESTAMP
);
