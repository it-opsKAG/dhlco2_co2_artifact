"""Smoke test for the Streamlit dashboard using Streamlit's official AppTest harness.

st.tabs() renders all tab bodies on every script run (only the visual selection is
client-side), so a single at.run() call exercises the whole file end to end.
"""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"


def test_dashboard_runs_without_exceptions():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()

    assert not at.exception, f"Dashboard raised: {[str(e) for e in at.exception]}"


def test_dashboard_shows_19_kpi_rows():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()

    assert not at.exception
    dataframes = at.dataframe
    assert len(dataframes) > 0
    kpi_df = dataframes[0].value
    assert len(kpi_df) == 19
