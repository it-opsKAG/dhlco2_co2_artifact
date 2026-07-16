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
    # The KPI catalog is no longer the first dataframe rendered (2026-07-16: the
    # dashboard now leads with the decision question and a recommendation box, not
    # the KPI catalog) — find it by its "ID"/"Gruppe" columns instead of assuming
    # position.
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()

    assert not at.exception
    dataframes = at.dataframe
    assert len(dataframes) > 0
    kpi_frames = [df.value for df in dataframes if list(df.value.columns[:2]) == ["ID", "Gruppe"]]
    assert len(kpi_frames) == 1
    assert len(kpi_frames[0]) == 19


def test_dashboard_shows_recommendation_box():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()

    assert not at.exception
    metric_labels = {m.label for m in at.metric}
    assert "Empfohlene Konfiguration" in metric_labels
    assert "Green-Gate" in metric_labels
    assert "Datenqualität" in metric_labels
