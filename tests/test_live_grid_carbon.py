import pytest

from live_grid_carbon import parse_co2eq_response


SAMPLE_RESPONSE = {
    "unix_seconds": [1783893600, 1783894500, 1783895400, 1783896300, 1783897200],
    "co2eq": [491.5, 497.4, 502.6, None, None],
    "co2eq_forecast": [None, None, None, 505.0, 508.0],
    "deprecated": False,
}


def test_parse_co2eq_response_picks_latest_non_null_value():
    snapshot = parse_co2eq_response(SAMPLE_RESPONSE, zone="de")

    assert snapshot.carbon_intensity_gco2e_per_kwh == 502.6
    assert snapshot.zone == "DE"
    assert snapshot.provider == "energy-charts.info (Fraunhofer ISE)"
    assert snapshot.unit == "gCO2e/kWh"
    assert snapshot.observed_at == "2026-07-12T22:30:00+00:00"
    assert snapshot.metadata["deprecated"] is False


def test_parse_co2eq_response_raises_on_all_null_window():
    all_null = {**SAMPLE_RESPONSE, "co2eq": [None, None, None, None, None]}
    with pytest.raises(ValueError):
        parse_co2eq_response(all_null)


def test_parse_co2eq_response_raises_on_shape_mismatch():
    mismatched = {"unix_seconds": [1, 2], "co2eq": [1.0]}
    with pytest.raises(ValueError):
        parse_co2eq_response(mismatched)


@pytest.mark.live
def test_fetch_live_grid_carbon_intensity_smoke():
    """Real network call — skipped by default, run explicitly with `-m live`."""
    from live_grid_carbon import fetch_live_grid_carbon_intensity

    snapshot = fetch_live_grid_carbon_intensity()
    assert snapshot.carbon_intensity_gco2e_per_kwh > 0
