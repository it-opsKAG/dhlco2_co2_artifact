"""Live German grid carbon intensity (gCO2eq/kWh) via energy-charts.info (Fraunhofer ISE).

Standalone context signal for demos — NOT wired into the KPI calculation pipeline in
generators/hardware_model.py or generators/simulation_runner.py. Those still use the
static UBA-2024 assumption (485 gCO2e/kWh, see data/carbon_benchmarks.yaml and the
sensitivity_note fields in data/green_gates.yaml) until a carbon-intensity provider
policy is formally decided for GAP-001 (see docs/phase2_rdc_gap_analysis.md).

This module answers a narrower question: "can we pull one genuinely live, tokenless
external data point right now, in the room?" — energy-charts.info publishes Germany's
actual grid CO2-equivalent intensity at 15-minute resolution, no API key required.
Endpoint verified reachable 2026-07-14: https://api.energy-charts.info/co2eq?country=de

If the room has no internet access, fetch_live_grid_carbon_intensity() raises; the demo
script prints a clear fallback message instead of crashing (see main()).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

API_URL = "https://api.energy-charts.info/co2eq"
DEFAULT_TIMEOUT_S = 8.0
STATIC_FALLBACK_GCO2E_PER_KWH = 485.0  # UBA 2024, see data/carbon_benchmarks.yaml


@dataclass(frozen=True)
class GridCarbonIntensitySnapshot:
    provider: str
    zone: str
    carbon_intensity_gco2e_per_kwh: float
    observed_at: str
    unit: str = "gCO2e/kWh"
    source_kind: str = "grid_carbon_intensity"
    is_estimated: bool = False
    resolution_s: int = 900
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "zone": self.zone,
            "carbon_intensity_gco2e_per_kwh": self.carbon_intensity_gco2e_per_kwh,
            "unit": self.unit,
            "observed_at": self.observed_at,
            "source_kind": self.source_kind,
            "is_estimated": self.is_estimated,
            "resolution_s": self.resolution_s,
            "metadata": dict(self.metadata),
        }


def parse_co2eq_response(payload: dict[str, Any], *, zone: str = "DE") -> GridCarbonIntensitySnapshot:
    """Parse an energy-charts.info /co2eq response, picking the latest non-null value.

    The response includes forward-looking `co2eq_forecast` slots as `null` inside
    `co2eq` near the end of the requested window — walk backwards to find the last
    observed (non-null) reading.
    """
    timestamps = payload.get("unix_seconds") or []
    values = payload.get("co2eq") or []
    if not timestamps or not values or len(timestamps) != len(values):
        raise ValueError("Unexpected energy-charts.info co2eq response shape")

    for ts, value in zip(reversed(timestamps), reversed(values)):
        if value is not None:
            observed_at = datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat(
                timespec="seconds"
            )
            return GridCarbonIntensitySnapshot(
                provider="energy-charts.info (Fraunhofer ISE)",
                zone=zone.upper(),
                carbon_intensity_gco2e_per_kwh=float(value),
                observed_at=observed_at,
                metadata={
                    "endpoint": API_URL,
                    "deprecated": bool(payload.get("deprecated", False)),
                },
            )

    raise ValueError("No non-null co2eq value found in response window")


def fetch_live_grid_carbon_intensity(
    *,
    zone: str = "de",
    timeout_s: float = DEFAULT_TIMEOUT_S,
    now: Optional[datetime] = None,
    lookback_hours: int = 6,
) -> GridCarbonIntensitySnapshot:
    """Fetch the current German grid carbon intensity live. Raises on network failure."""
    now = now or datetime.now(timezone.utc)
    start = (now - timedelta(hours=lookback_hours)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    url = f"{API_URL}?country={zone}&start={start}&end={end}"
    request = urllib.request.Request(
        url, headers={"User-Agent": "dhlco2-co2-artifact/live-grid-carbon-demo"}
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:  # nosec B310 (fixed https host)
        payload = json.loads(response.read().decode("utf-8"))
    return parse_co2eq_response(payload, zone=zone.upper())


def main() -> None:
    try:
        snapshot = fetch_live_grid_carbon_intensity()
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        print(
            "Live-Abruf des Netz-Emissionsfaktors fehlgeschlagen "
            f"({type(exc).__name__}: {exc}). "
            f"Fallback: statischer UBA-2024-Wert {STATIC_FALLBACK_GCO2E_PER_KWH:.0f} gCO2e/kWh."
        )
        return

    print(
        "Live-Netz-Emissionsfaktor Deutschland: "
        f"{snapshot.carbon_intensity_gco2e_per_kwh:.1f} gCO2e/kWh"
    )
    print(f"Quelle: {snapshot.provider}")
    print(f"Zeitstempel (UTC): {snapshot.observed_at}")
    print(f"Statischer Vergleichswert (UBA 2024): {STATIC_FALLBACK_GCO2E_PER_KWH:.0f} gCO2e/kWh")


if __name__ == "__main__":
    main()
