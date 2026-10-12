CREATE SCHEMA IF NOT EXISTS `{{WAREHOUSE_DATASET_ID}}`
OPTIONS(location = '{{LOCATION}}');


-- Check staging counts against the local quality reports.
ASSERT (
  SELECT COUNT(*) = @expected_institutions
  FROM `{{STAGING_DATASET_ID}}.institutions`
) AS 'Unexpected institution count';

ASSERT (
  SELECT COUNT(*) = @expected_programs
  FROM `{{STAGING_DATASET_ID}}.programs`
) AS 'Unexpected program count';


CREATE TEMP TABLE prepared_programs AS
SELECT
  unitid,
  CIPCODE AS cipcode,
  CREDLEV AS credlev,
  REGEXP_REPLACE(TRIM(CIPDESC), r'\.+$', '') AS field_title,
  TRIM(CREDDESC) AS credential_title,
  debt_all_stgp_any_mdn,
  debt_all_stgp_any_mdn_status,
  earn_mdn_1yr,
  earn_mdn_1yr_status,
  earn_mdn_4yr,
  earn_mdn_4yr_status,
  earn_mdn_5yr,
  earn_mdn_5yr_status,
  source_zip,
  source_record
FROM `{{STAGING_DATASET_ID}}.programs`;


ASSERT (
  SELECT COUNTIF(
    field_title IS NULL OR field_title = ''
    OR credential_title IS NULL OR credential_title = ''
  ) = 0
  FROM prepared_programs
) AS 'Missing reference descriptions';

ASSERT (
  SELECT COUNT(*) = 0
  FROM (
    SELECT cipcode
    FROM prepared_programs
    GROUP BY cipcode
    HAVING COUNT(DISTINCT field_title) > 1
  )
) AS 'Conflicting CIP descriptions';

ASSERT (
  SELECT COUNT(*) = 0
  FROM (
    SELECT credlev
    FROM prepared_programs
    GROUP BY credlev
    HAVING COUNT(DISTINCT credential_title) > 1
  )
) AS 'Conflicting credential descriptions';


-- Check program identifiers and relationships before building.
ASSERT (
  SELECT COUNTIF(
    unitid IS NULL OR cipcode IS NULL OR credlev IS NULL
  ) = 0
  FROM prepared_programs
) AS 'Null program identifiers';

ASSERT (
  SELECT COUNT(*) = 0
  FROM (
    SELECT unitid, cipcode, credlev
    FROM prepared_programs
    GROUP BY unitid, cipcode, credlev
    HAVING COUNT(*) > 1
  )
) AS 'Repeated program keys';

ASSERT (
  SELECT
    COUNTIF(unitid IS NULL) = 0
    AND COUNT(*) = COUNT(DISTINCT unitid)
  FROM `{{STAGING_DATASET_ID}}.institutions`
) AS 'Invalid institution keys';

ASSERT (
  SELECT COUNT(*) = 0
  FROM prepared_programs p
  LEFT JOIN `{{STAGING_DATASET_ID}}.institutions` i
    ON p.unitid = i.unitid
  WHERE i.unitid IS NULL
) AS 'Programs without matching institutions';


CREATE OR REPLACE TABLE
  `{{WAREHOUSE_DATASET_ID}}.institutions` AS
SELECT
  unitid, name, city, state, url, ownership,
  student_size, admission_rate,
  tuition_in_state, tuition_out_of_state,
  source_run_id, source_page
FROM `{{STAGING_DATASET_ID}}.institutions`;

CREATE OR REPLACE TABLE
  `{{WAREHOUSE_DATASET_ID}}.cip_fields` AS
SELECT DISTINCT cipcode, field_title AS title
FROM prepared_programs;

CREATE OR REPLACE TABLE
  `{{WAREHOUSE_DATASET_ID}}.credential_levels` AS
SELECT DISTINCT credlev, credential_title AS title
FROM prepared_programs;

CREATE OR REPLACE TABLE
  `{{WAREHOUSE_DATASET_ID}}.programs` AS
SELECT * EXCEPT(field_title, credential_title)
FROM prepared_programs;


-- Return counts to the Python runner.
SELECT 'institutions' AS table_name, COUNT(*) AS row_count
FROM `{{WAREHOUSE_DATASET_ID}}.institutions`
UNION ALL
SELECT 'programs', COUNT(*)
FROM `{{WAREHOUSE_DATASET_ID}}.programs`
UNION ALL
SELECT 'cip_fields', COUNT(*)
FROM `{{WAREHOUSE_DATASET_ID}}.cip_fields`
UNION ALL
SELECT 'credential_levels', COUNT(*)
FROM `{{WAREHOUSE_DATASET_ID}}.credential_levels`;