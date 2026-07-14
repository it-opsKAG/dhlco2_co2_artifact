"""ENTSO-E Transparency Platform connector — official EU grid generation mix -> carbon intensity.

Status 2026-07-15: awaiting API security token (registration done, access request
sent to transparency@entsoe.eu, see docs/phase3_data_source_roadmap.md #1). This
module is written and unit-tested against a synthetic fixture response now so the
only remaining step once the token arrives is a live smoke test (marked `live`,
excluded from the default test run — see tests/test_entsoe_grid_carbon.py).

Unlike generators/live_grid_carbon.py (a single black-box CO2-equivalent number
from energy-charts.info), this connector fetches generation-per-type (documentType
A75, processType A16 "Realised") and computes the weighted carbon intensity from
ENTSO-E's own generation-mix data using a documented, auditable per-fuel
emission-factor table instead of trusting an opaque third-party number.
"""

from __future__ import annotations

import os
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

API_BASE_URL = "https://web-api.tp.entsoe.eu/api"
DEFAULT_TIMEOUT_S = 15.0

# EIC codes for relevant bidding zones (extend as needed once the pilot region is known).
BIDDING_ZONES = {
    "DE_LU": "10Y1001A1001A83F",
}

# Life-cycle GHG emission factors per ENTSO-E PSR (Power System Resource) type,
# gCO2eq/kWh. Median IPCC AR5 (2014) life-cycle values, except solar which reuses
# the Fraunhofer ISE figure already used in docs/phase3_simulation_concept.md for
# internal consistency with the rest of this repo. Unmapped codes fall back to the
# German grid average (data/carbon_benchmarks.yaml) rather than guessing.
FALLBACK_EF_GCO2E_PER_KWH = 485.0  # UBA 2024 DE grid average

PSR_EMISSION_FACTORS_GCO2E_PER_KWH: dict[str, float] = {
    "B01": 230.0,   # Biomass
    "B02": 1054.0,  # Fossil Brown coal/Lignite
    "B03": 490.0,   # Fossil Coal-derived gas
    "B04": 490.0,   # Fossil Gas
    "B05": 820.0,   # Fossil Hard coal
    "B06": 650.0,   # Fossil Oil
    "B07": 650.0,   # Fossil Oil shale
    "B08": 820.0,   # Fossil Peat
    "B09": 38.0,    # Geothermal
    "B10": 24.0,    # Hydro Pumped Storage
    "B11": 24.0,    # Hydro Run-of-river and poundage
    "B12": 24.0,    # Hydro Water Reservoir
    "B13": 17.0,    # Marine
    "B14": 12.0,    # Nuclear
    "B15": 38.0,    # Other renewable
    "B16": 41.0,    # Solar (Fraunhofer ISE)
    "B17": 700.0,   # Waste
    "B18": 12.0,    # Wind Offshore
    "B19": 11.0,    # Wind Onshore
    "B20": FALLBACK_EF_GCO2E_PER_KWH,  # Other
    "B25": 0.0,     # Energy storage (charge/discharge, not primary generation)
}


@dataclass(frozen=True)
class GenerationMixSnapshot:
    zone: str
    period_start: str
    period_end: str
    generation_mw_by_psr: dict[str, float]
    weighted_carbon_intensity_gco2e_per_kwh: float
    unmapped_psr_types: tuple[str, ...] = ()


def compute_weighted_carbon_intensity(
    generation_mw_by_psr: dict[str, float],
) -> tuple[float, tuple[str, ...]]:
    """Weighted-average carbon intensity (gCO2e/kWh) from a generation-mix snapshot.

    Returns (intensity, sorted tuple of PSR-type codes not in the emission-factor
    table — these fell back to FALLBACK_EF_GCO2E_PER_KWH and should be reviewed).
    """
    total_mw = sum(generation_mw_by_psr.values())
    if total_mw <= 0:
        return FALLBACK_EF_GCO2E_PER_KWH, ()

    unmapped = tuple(
        sorted(psr for psr in generation_mw_by_psr if psr not in PSR_EMISSION_FACTORS_GCO2E_PER_KWH)
    )
    weighted_sum = sum(
        mw * PSR_EMISSION_FACTORS_GCO2E_PER_KWH.get(psr, FALLBACK_EF_GCO2E_PER_KWH)
        for psr, mw in generation_mw_by_psr.items()
    )
    return weighted_sum / total_mw, unmapped


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def parse_generation_mix_xml(xml_text: str) -> dict[str, float]:
    """Parse an ENTSO-E A75 (actual generation per type) response.

    Returns {psr_type_code: average_quantity_mw} per fuel type across all Points
    in the response window. Namespace-agnostic (strips `{...}` prefixes) since the
    exact schema namespace URI hasn't been captured from a live response yet.
    """
    root = ET.fromstring(xml_text)
    totals: dict[str, float] = {}
    for timeseries in root.iter():
        if _strip_ns(timeseries.tag) != "TimeSeries":
            continue
        psr_type = next(
            (
                (el.text or "").strip()
                for el in timeseries.iter()
                if _strip_ns(el.tag) == "psrType"
            ),
            None,
        )
        if not psr_type:
            continue
        quantities = [
            float(el.text) for el in timeseries.iter() if _strip_ns(el.tag) == "quantity" and el.text
        ]
        if quantities:
            avg_quantity = sum(quantities) / len(quantities)
            totals[psr_type] = totals.get(psr_type, 0.0) + avg_quantity
    return totals


def fetch_generation_mix(
    *,
    security_token: str,
    zone_eic: str = BIDDING_ZONES["DE_LU"],
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> GenerationMixSnapshot:
    """Fetch actual generation per production type (documentType A75, processType A16)."""
    now = datetime.now(timezone.utc)
    period_end = period_end or now
    period_start = period_start or (period_end - timedelta(hours=2))

    def fmt(dt: datetime) -> str:
        return dt.strftime("%Y%m%d%H%M")

    url = (
        f"{API_BASE_URL}?documentType=A75&processType=A16&in_Domain={zone_eic}"
        f"&periodStart={fmt(period_start)}&periodEnd={fmt(period_end)}"
        f"&securityToken={security_token}"
    )
    request = urllib.request.Request(
        url, headers={"User-Agent": "dhlco2-co2-artifact/entsoe-connector"}
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:  # nosec B310 (fixed https host)
        xml_text = response.read().decode("utf-8")

    generation_mw_by_psr = parse_generation_mix_xml(xml_text)
    intensity, unmapped = compute_weighted_carbon_intensity(generation_mw_by_psr)
    return GenerationMixSnapshot(
        zone=zone_eic,
        period_start=period_start.isoformat(timespec="minutes"),
        period_end=period_end.isoformat(timespec="minutes"),
        generation_mw_by_psr=generation_mw_by_psr,
        weighted_carbon_intensity_gco2e_per_kwh=intensity,
        unmapped_psr_types=unmapped,
    )


def main() -> None:
    token = os.getenv("ENTSOE_SECURITY_TOKEN")
    if not token:
        print(
            "ENTSOE_SECURITY_TOKEN nicht gesetzt. Registrierung/Freigabe-Ablauf siehe "
            "docs/phase3_data_source_roadmap.md Abschnitt 1."
        )
        return
    snapshot = fetch_generation_mix(security_token=token)
    print(f"Zone: {snapshot.zone}  Zeitraum: {snapshot.period_start} .. {snapshot.period_end}")
    print(f"Gewichteter CO2-Faktor: {snapshot.weighted_carbon_intensity_gco2e_per_kwh:.1f} gCO2e/kWh")
    if snapshot.unmapped_psr_types:
        print(f"Achtung, unbekannte PSR-Typen (Fallback verwendet): {snapshot.unmapped_psr_types}")


if __name__ == "__main__":
    main()
