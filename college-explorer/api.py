import logging
from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, HTTPException, Path,  Query
from google.cloud import bigquery

from settings import PROJECT_ID, LOCATION, MARTS_DATASET_ID


app = FastAPI(
    title="College Explorer API",
    version="0.1.0",
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_client():
    return bigquery.Client(
        project=PROJECT_ID,
        location=LOCATION,
    )


def query_rows(sql, parameters=None):
    config = bigquery.QueryJobConfig(
        query_parameters=parameters or [],
    )

    try:
        job = get_client().query(
            sql,
            job_config=config,
            location=LOCATION,
        )
        return [dict(row.items()) for row in job.result()]

    except Exception:
        logger.exception("BigQuery request failed.")
        raise HTTPException(
            status_code=503,
            detail="Data service is temporarily unavailable.",
        )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/data-status")
def data_status():
    rows = query_rows(
        f"SELECT * FROM `{MARTS_DATASET_ID}.data_status` LIMIT 2"
    )

    if len(rows) != 1:
        raise HTTPException(
            status_code=503,
            detail="Published data status is unavailable or invalid.",
        )

    return rows[0]


@app.get("/institutions")
def institutions(
    q: Optional[str] = Query(default=None, max_length=100),
    state: Optional[str] = Query(
        default=None, pattern=r"^[A-Za-z]{2}$"
    ),
    ownership: Optional[int] = Query(default=None, ge=1, le=3),
    tuition_min: Optional[float] = Query(default=None, ge=0),
    tuition_max: Optional[float] = Query(default=None, ge=0),
    size_min: Optional[int] = Query(default=None, ge=0),
    size_max: Optional[int] = Query(default=None, ge=0),
    admission_min: Optional[float] = Query(default=None, ge=0, le=1),
    admission_max: Optional[float] = Query(default=None, ge=0, le=1),
    cipcode: Optional[str] = Query(
        default=None, pattern=r"^[0-9]{4}$"
    ),
    credlev: Optional[int] = Query(default=None, gt=0),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100000),
):
    ranges = [
        ("tuition", tuition_min, tuition_max),
        ("student size", size_min, size_max),
        ("admission rate", admission_min, admission_max),
    ]

    for label, minimum, maximum in ranges:
        if (
            minimum is not None
            and maximum is not None
            and minimum > maximum
        ):
            raise HTTPException(
                status_code=422,
                detail=f"Minimum {label} cannot exceed maximum.",
            )

    if cipcode is not None:
        fields = query_rows(
            f"""
            SELECT cipcode
            FROM `{MARTS_DATASET_ID}.cip_fields`
            WHERE cipcode = @cipcode
            LIMIT 1
            """,
            [bigquery.ScalarQueryParameter(
                "cipcode", "STRING", cipcode
            )],
        )

        if not fields:
            raise HTTPException(
                status_code=422,
                detail="Unknown field-of-study code.",
            )

    if credlev is not None:
        credentials = query_rows(
            f"""
            SELECT credlev
            FROM `{MARTS_DATASET_ID}.credential_levels`
            WHERE credlev = @credlev
            LIMIT 1
            """,
            [bigquery.ScalarQueryParameter(
                "credlev", "INT64", credlev
            )],
        )

        if not credentials:
            raise HTTPException(
                status_code=422,
                detail="Unknown credential level.",
            )

    sql = f"""
    SELECT
      i.unitid,
      i.name,
      i.city,
      i.state,
      i.url,
      i.ownership,
      i.student_size,
      i.admission_rate,
      i.tuition_in_state,
      i.tuition_out_of_state
    FROM `{MARTS_DATASET_ID}.institutions` i
    WHERE
      (@search = '' OR STRPOS(LOWER(i.name), LOWER(@search)) > 0)
      AND (@state IS NULL OR i.state = @state)
      AND (@ownership IS NULL OR i.ownership = @ownership)
      AND (@tuition_min IS NULL OR i.tuition_in_state >= @tuition_min)
      AND (@tuition_max IS NULL OR i.tuition_in_state <= @tuition_max)
      AND (@size_min IS NULL OR i.student_size >= @size_min)
      AND (@size_max IS NULL OR i.student_size <= @size_max)
      AND (@admission_min IS NULL OR i.admission_rate >= @admission_min)
      AND (@admission_max IS NULL OR i.admission_rate <= @admission_max)
      AND (
        (@cipcode IS NULL AND @credlev IS NULL)
        OR EXISTS (
          SELECT 1
          FROM `{MARTS_DATASET_ID}.programs` p
          WHERE p.unitid = i.unitid
            AND (@cipcode IS NULL OR p.cipcode = @cipcode)
            AND (@credlev IS NULL OR p.credlev = @credlev)
        )
      )
    ORDER BY i.name, i.unitid
    LIMIT @fetch_limit
    OFFSET @offset
    """

    values = [
        ("search", "STRING", q.strip() if q else ""),
        ("state", "STRING", state.upper() if state else None),
        ("ownership", "INT64", ownership),
        ("tuition_min", "FLOAT64", tuition_min),
        ("tuition_max", "FLOAT64", tuition_max),
        ("size_min", "INT64", size_min),
        ("size_max", "INT64", size_max),
        ("admission_min", "FLOAT64", admission_min),
        ("admission_max", "FLOAT64", admission_max),
        ("cipcode", "STRING", cipcode),
        ("credlev", "INT64", credlev),
        ("fetch_limit", "INT64", limit + 1),
        ("offset", "INT64", offset),
    ]

    parameters = [
        bigquery.ScalarQueryParameter(name, data_type, value)
        for name, data_type, value in values
    ]

    rows = query_rows(sql, parameters)
    has_more = len(rows) > limit

    return {
        "items": rows[:limit],
        "returned": len(rows[:limit]),
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
        "next_offset": offset + limit if has_more else None,
    }


@app.get("/institutions/{unitid}")
def institution_profile(
    unitid: int = Path(..., gt=0),
):
    sql = f"""
    SELECT
      unitid,
      name,
      city,
      state,
      url,
      ownership,
      student_size,
      admission_rate,
      tuition_in_state,
      tuition_out_of_state,
      source_run_id
    FROM `{MARTS_DATASET_ID}.institutions`
    WHERE unitid = @unitid
    LIMIT 1
    """

    parameters = [
        bigquery.ScalarQueryParameter(
            "unitid", "INT64", unitid
        )
    ]

    rows = query_rows(sql, parameters)

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Institution not found.",
        )

    return rows[0]


@app.get("/institutions/{unitid}/programs")
def institution_programs(
    unitid: int = Path(..., gt=0),
):
    parameters = [
        bigquery.ScalarQueryParameter(
            "unitid", "INT64", unitid
        )
    ]

    # Distinguish an unknown institution from one without program records.
    institution_rows = query_rows(
        f"""
        SELECT unitid, name
        FROM `{MARTS_DATASET_ID}.institutions`
        WHERE unitid = @unitid
        LIMIT 1
        """,
        parameters,
    )

    if not institution_rows:
        raise HTTPException(
            status_code=404,
            detail="Institution not found.",
        )

    sql = f"""
    SELECT
      cipcode,
      field_of_study,
      credlev,
      credential,
      debt_all_stgp_any_mdn,
      debt_all_stgp_any_mdn_status,
      earn_mdn_1yr,
      earn_mdn_1yr_status,
      earn_mdn_4yr,
      earn_mdn_4yr_status,
      earn_mdn_5yr,
      earn_mdn_5yr_status,
      published_version
    FROM `{MARTS_DATASET_ID}.program_catalog`
    WHERE unitid = @unitid
    ORDER BY credlev, field_of_study, cipcode
    """

    rows = query_rows(sql, parameters)

    groups = {}

    for row in rows:
        credential_code = row["credlev"]

        if credential_code not in groups:
            groups[credential_code] = {
                "credlev": credential_code,
                "credential": row["credential"],
                "programs": [],
            }

        groups[credential_code]["programs"].append(row)

    return {
        "unitid": unitid,
        "institution_name": institution_rows[0]["name"],
        "program_count": len(rows),
        "credential_groups": list(groups.values()),
    }

@app.get("/fields")
def fields():
    return query_rows(
        f"""
        SELECT cipcode, title
        FROM `{MARTS_DATASET_ID}.cip_fields`
        ORDER BY title, cipcode
        """
    )


@app.get("/credential-levels")
def credential_levels():
    return query_rows(
        f"""
        SELECT credlev, title
        FROM `{MARTS_DATASET_ID}.credential_levels`
        ORDER BY credlev
        """
    )

@app.get("/fields/{cipcode}/institutions")
def field_institutions(
    cipcode: str = Path(..., pattern=r"^[0-9]{4}$"),
    state: Optional[str] = Query(
        default=None,
        pattern=r"^[A-Za-z]{2}$",
    ),
    credlev: Optional[int] = Query(default=None, gt=0),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100000),
):
    field_rows = query_rows(
        f"""
        SELECT cipcode, title
        FROM `{MARTS_DATASET_ID}.cip_fields`
        WHERE cipcode = @cipcode
        LIMIT 1
        """,
        [
            bigquery.ScalarQueryParameter(
                "cipcode", "STRING", cipcode
            )
        ],
    )

    if not field_rows:
        raise HTTPException(
            status_code=404,
            detail="Field of study not found.",
        )

    if credlev is not None:
        credential_rows = query_rows(
            f"""
            SELECT credlev
            FROM `{MARTS_DATASET_ID}.credential_levels`
            WHERE credlev = @credlev
            LIMIT 1
            """,
            [
                bigquery.ScalarQueryParameter(
                    "credlev", "INT64", credlev
                )
            ],
        )

        if not credential_rows:
            raise HTTPException(
                status_code=422,
                detail="Unknown credential level.",
            )

    sql = f"""
    SELECT
      i.unitid,
      i.name,
      i.city,
      i.state,
      i.ownership,
      i.student_size,
      i.admission_rate,
      i.tuition_in_state,
      i.tuition_out_of_state
    FROM `{MARTS_DATASET_ID}.institutions` i
    WHERE
      (@state IS NULL OR i.state = @state)
      AND EXISTS (
        SELECT 1
        FROM `{MARTS_DATASET_ID}.programs` p
        WHERE p.unitid = i.unitid
          AND p.cipcode = @cipcode
          AND (@credlev IS NULL OR p.credlev = @credlev)
      )
    ORDER BY i.name, i.unitid
    LIMIT @fetch_limit
    OFFSET @offset
    """

    parameters = [
        bigquery.ScalarQueryParameter(
            "cipcode", "STRING", cipcode
        ),
        bigquery.ScalarQueryParameter(
            "state", "STRING", state.upper() if state else None
        ),
        bigquery.ScalarQueryParameter(
            "credlev", "INT64", credlev
        ),
        bigquery.ScalarQueryParameter(
            "fetch_limit", "INT64", limit + 1
        ),
        bigquery.ScalarQueryParameter(
            "offset", "INT64", offset
        ),
    ]

    rows = query_rows(sql, parameters)
    has_more = len(rows) > limit

    return {
        "field": field_rows[0],
        "credlev": credlev,
        "items": rows[:limit],
        "returned": len(rows[:limit]),
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
        "next_offset": offset + limit if has_more else None,
    }

