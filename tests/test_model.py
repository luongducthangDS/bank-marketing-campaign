"""Data quality and integrity tests for Bank Marketing model."""
from pathlib import Path
import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def con():
    c = duckdb.connect()
    c.execute("SET enable_progress_bar = false")
    c.execute(f"SET file_search_path = '{ROOT}'")
    c.execute((ROOT / "sql" / "00_model.sql").read_text())
    c.execute((ROOT / "sql" / "10_powerbi_export.sql").read_text())
    return c


def one(con, sql):
    return con.execute(sql).fetchone()[0]


def test_row_count(con):
    assert one(con, "SELECT count(*) FROM fct_campaign_calls") == 41_188
    assert one(con, "SELECT count(*) - count(DISTINCT call_id) FROM fct_campaign_calls") == 0


def test_conversion_rate_reproducible(con):
    rate = one(con, "SELECT round(avg(is_subscribed::INT) * 100, 2) FROM fct_campaign_calls")
    assert rate == 11.27


def test_call_frequency_tier_logic(con):
    bad = one(con, """
        SELECT count(*) FROM fct_campaign_calls
        WHERE (campaign_contacts = 1 AND contact_frequency_tier <> '1 call')
           OR (campaign_contacts > 6 AND contact_frequency_tier <> '>6 calls (Excess/Fatigue)')
    """)
    assert bad == 0


def test_profile_dimension_unique_keys(con):
    dups = one(con, "SELECT count(*) - count(DISTINCT profile_id) FROM pbi_dim_client_profile")
    assert dups == 0


def test_referential_integrity(con):
    missing = one(con, """
        SELECT count(*) FROM pbi_fact_campaign_calls f
        LEFT JOIN pbi_dim_client_profile p USING (profile_id)
        WHERE p.profile_id IS NULL
    """)
    assert missing == 0
