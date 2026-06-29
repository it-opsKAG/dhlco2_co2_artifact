from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "carbon_benchmarks.yaml"

WORLD_BANK_LEGACY_INDICATOR = "EN.ATM.CO2E.PC"
WORLD_BANK_CURRENT_INDICATOR = "EN.GHG.CO2.PC.CE.AR5"
WORLD_BANK_COUNTRIES = ["DEU", "FRA", "NLD", "POL", "USA"]


def _fetch_json(url: str, timeout_s: int = 20) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "dhlco2-carbon-benchmarks/1.0"})
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        return json.loads(response.read().decode("utf-8"))


def _fetch_world_bank_indicator(indicator: str, source_id: str, name: str) -> dict[str, Any]:
    country_path = ";".join(WORLD_BANK_COUNTRIES)
    url = (
        f"https://api.worldbank.org/v2/country/{country_path}/indicator/{indicator}"
        "?format=json&per_page=200"
    )
    try:
        payload = _fetch_json(url)
        if isinstance(payload, list) and payload and isinstance(payload[0], dict) and "message" in payload[0]:
            raise ValueError(str(payload[0]["message"]))
        rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        latest_by_country: dict[str, dict[str, Any]] = {}
        for row in rows:
            if not isinstance(row, dict) or row.get("value") is None:
                continue
            iso3 = str(row.get("countryiso3code") or "").strip()
            year = int(row.get("date"))
            value = float(row.get("value"))
            current = latest_by_country.get(iso3)
            if current is None or year > int(current["year"]):
                latest_by_country[iso3] = {"year": year, "value_tco2_per_capita": round(value, 4)}
        if not latest_by_country:
            raise ValueError("no non-null country values returned")
        status = "live"
        note = "Latest non-null value per country from World Bank API."
    except Exception as exc:
        latest_by_country = {}
        status = "fallback_or_unavailable"
        note = f"World Bank API unavailable or malformed: {exc}"

    return {
        "id": source_id,
        "indicator": indicator,
        "name": name,
        "unit": "tCO2/capita",
        "status": status,
        "source_url": url,
        "quality": "contextual_high" if status == "live" else "unavailable",
        "note": note,
        "values": latest_by_country,
    }


def _fetch_world_bank_co2_per_capita() -> list[dict[str, Any]]:
    legacy = _fetch_world_bank_indicator(
        WORLD_BANK_LEGACY_INDICATOR,
        "WB-CO2-PC-LEGACY",
        "CO2 emissions per capita (legacy WDI indicator)",
    )
    current = _fetch_world_bank_indicator(
        WORLD_BANK_CURRENT_INDICATOR,
        "WB-CO2-PC-EDGAR",
        "Carbon dioxide emissions excluding LULUCF per capita",
    )
    return [legacy, current]


def _fetch_eurostat_renewables() -> dict[str, Any]:
    query = urllib.parse.urlencode(
        {
            "geo": ["DE", "EU27_2020"],
            "time": ["2022", "2023", "2024"],
            "unit": "PC",
            "nrg_bal": "REN",
        },
        doseq=True,
    )
    url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ind_ren?{query}"
    try:
        payload = _fetch_json(url)
        dimensions = payload.get("dimension", {})
        values = payload.get("value", {})
        geo_index = dimensions.get("geo", {}).get("category", {}).get("index", {})
        time_index = dimensions.get("time", {}).get("category", {}).get("index", {})
        size = payload.get("size", [])
        if len(size) < 3:
            raise ValueError("unexpected Eurostat dimension shape")
        # Eurostat stores a flattened array. For this query shape the last two
        # dimensions are geo/time in the API response; if the shape changes, keep
        # the record unavailable rather than inventing values.
        parsed: dict[str, dict[str, Any]] = {}
        for geo, geo_pos in geo_index.items():
            for year, time_pos in time_index.items():
                flat_index = str((int(geo_pos) * int(size[-1])) + int(time_pos))
                if flat_index in values:
                    parsed.setdefault(geo, {})[year] = round(float(values[flat_index]), 3)
        if not parsed:
            raise ValueError("no Eurostat values parsed")
        status = "live"
        note = "Renewable-energy-share context from Eurostat nrg_ind_ren."
    except Exception as exc:
        parsed = {}
        status = "fallback_or_unavailable"
        note = f"Eurostat API unavailable or shape changed: {exc}"

    return {
        "id": "EUROSTAT-NRG-IND-REN",
        "indicator": "nrg_ind_ren",
        "name": "Share of energy from renewable sources",
        "unit": "percent",
        "status": status,
        "source_url": url,
        "quality": "contextual_medium" if status == "live" else "unavailable",
        "note": note,
        "values": parsed,
    }


def _uba_reference() -> dict[str, Any]:
    return {
        "id": "UBA-DE-STROMMIX-2024",
        "name": "German electricity mix emission factors",
        "status": "documented_reference",
        "source": "Umweltbundesamt, Entwicklung der spezifischen Treibhausgas-Emissionen des deutschen Strommix in den Jahren 1990-2024, Climate Change 13/2025",
        "source_url": "https://www.umweltbundesamt.de/publikationen/entwicklung-der-spezifischen-treibhausgas-11",
        "quality": "national_official_reference",
        "values": {
            "DE": {
                "year": 2024,
                "direct_co2_strommix_gco2_per_kwh": 363,
                "direct_co2_consumption_gco2_per_kwh": 353,
                "ghg_without_upstream_gco2e_per_kwh": 372,
                "ghg_with_upstream_gco2e_per_kwh": 427,
            }
        },
        "note": (
            "Use the direct CO2 Strommix value for location-based baseline scenarios. "
            "Use the GHG values when CH4/N2O and upstream chains are in scope."
        ),
    }


def build_payload() -> dict[str, Any]:
    return {
        "schema_version": "dhlco2.carbon_benchmarks.v1",
        "generated_at": date.today().isoformat(),
        "purpose": (
            "External calibration context for PRX-001 carbon-intensity assumptions. "
            "These values do not replace DHL-specific metering."
        ),
        "sources": [
            _uba_reference(),
            *_fetch_world_bank_co2_per_capita(),
            _fetch_eurostat_renewables(),
        ],
        "usage_rules": [
            "Treat national and macroeconomic values as calibration context, not as service-level measurements.",
            "Prefer DHL region/facility/provider carbon-intensity data once available.",
            "Mark any scenario using these values as proxy- or benchmark-based.",
        ],
    }


def main() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    DATA_PATH.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    print(f"wrote {DATA_PATH}")


if __name__ == "__main__":
    sys.exit(main())
