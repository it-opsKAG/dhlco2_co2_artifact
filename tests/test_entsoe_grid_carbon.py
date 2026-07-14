import os

import pytest

from entsoe_grid_carbon import (
    FALLBACK_EF_GCO2E_PER_KWH,
    compute_weighted_carbon_intensity,
    parse_generation_mix_xml,
)

# Synthetic fixture matching the documented ENTSO-E A75 (actual generation per type)
# response shape (GL_MarketDocument > TimeSeries > MktPSRType > psrType, Period > Point
# > quantity) — not a captured real response, since we don't have a token yet.
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationdocument:4:0">
  <TimeSeries>
    <MktPSRType>
      <psrType>B16</psrType>
    </MktPSRType>
    <Period>
      <Point><position>1</position><quantity>1200</quantity></Point>
      <Point><position>2</position><quantity>1400</quantity></Point>
    </Period>
  </TimeSeries>
  <TimeSeries>
    <MktPSRType>
      <psrType>B04</psrType>
    </MktPSRType>
    <Period>
      <Point><position>1</position><quantity>3000</quantity></Point>
      <Point><position>2</position><quantity>3200</quantity></Point>
    </Period>
  </TimeSeries>
  <TimeSeries>
    <MktPSRType>
      <psrType>ZZZ</psrType>
    </MktPSRType>
    <Period>
      <Point><position>1</position><quantity>50</quantity></Point>
    </Period>
  </TimeSeries>
</GL_MarketDocument>
"""


def test_parse_generation_mix_xml_extracts_averages_per_psr_type():
    result = parse_generation_mix_xml(SAMPLE_XML)

    assert result["B16"] == pytest.approx(1300.0)  # avg(1200, 1400)
    assert result["B04"] == pytest.approx(3100.0)  # avg(3000, 3200)
    assert result["ZZZ"] == pytest.approx(50.0)


def test_compute_weighted_carbon_intensity_flags_unmapped_psr_type():
    generation = {"B16": 1300.0, "B04": 3100.0, "ZZZ": 50.0}
    intensity, unmapped = compute_weighted_carbon_intensity(generation)

    total = 1300.0 + 3100.0 + 50.0
    expected = (1300.0 * 41.0 + 3100.0 * 490.0 + 50.0 * FALLBACK_EF_GCO2E_PER_KWH) / total
    assert intensity == pytest.approx(expected)
    assert unmapped == ("ZZZ",)


def test_compute_weighted_carbon_intensity_pure_solar_matches_solar_factor():
    intensity, unmapped = compute_weighted_carbon_intensity({"B16": 500.0})
    assert intensity == pytest.approx(41.0)
    assert unmapped == ()


def test_compute_weighted_carbon_intensity_empty_generation_uses_fallback():
    intensity, unmapped = compute_weighted_carbon_intensity({})
    assert intensity == FALLBACK_EF_GCO2E_PER_KWH
    assert unmapped == ()


def test_end_to_end_sample_xml_to_intensity():
    generation = parse_generation_mix_xml(SAMPLE_XML)
    intensity, unmapped = compute_weighted_carbon_intensity(generation)

    assert unmapped == ("ZZZ",)
    assert 41.0 < intensity < 490.0  # blended between solar and gas, plausible range


@pytest.mark.live
def test_fetch_generation_mix_smoke():
    """Real network call against the live ENTSO-E API — needs ENTSOE_SECURITY_TOKEN.

    Skipped by default. Run explicitly once the token is available:
      ENTSOE_SECURITY_TOKEN=... uv run pytest tests/test_entsoe_grid_carbon.py -m live
    """
    token = os.getenv("ENTSOE_SECURITY_TOKEN")
    if not token:
        pytest.skip("ENTSOE_SECURITY_TOKEN not set")

    from entsoe_grid_carbon import fetch_generation_mix

    snapshot = fetch_generation_mix(security_token=token)
    assert snapshot.weighted_carbon_intensity_gco2e_per_kwh > 0
