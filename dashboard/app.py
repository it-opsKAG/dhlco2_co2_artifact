"""DHLCO2 Interactive Dashboard — local demo app.

Run with:
  uv run streamlit run dashboard/app.py

Reads directly from the same SSOT data files (data/*.yaml) and generator modules
(generators/hardware_model.py, generators/rdc_pareto.py) that the CI export pipeline
uses. No mocked or invented numbers — every chart is either the deterministic
simulation model's real output for the chosen scenario, or a live-fetched external
data point (clearly labeled as such).

Scope note: KPI values are simulation output, not real DHL measurements — the KPI
catalog itself still carries status "candidate" for all 19 KPIs until the pilot
scope (OC-01..OC-05) is resolved. This dashboard demonstrates decision capability
on top of the methodology, not live DHL telemetry.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
sys.path.insert(0, str(ROOT / "generators"))

import pandas as pd
import streamlit as st

from data_helpers import (
    BOAVIZTA_REFERENCES,
    ZONE_EMOJI,
    build_pareto_rows,
    build_scenario_rows,
    build_sensitivity_rows,
    gate_zone,
    has_defined_gate,
    load_evidence_ledger_rows,
    load_green_gates,
    load_kpi_catalog,
)
from hardware_model import EmissionFactorProfile, WorkloadProfile, rdc_rank
from live_grid_carbon import STATIC_FALLBACK_GCO2E_PER_KWH, fetch_live_grid_carbon_intensity

st.set_page_config(page_title="DHLCO2 — CO2/Kosten-Entscheidungsmodell", layout="wide")

st.title("DHLCO2 — CO2/Kosten-Entscheidungsmodell")
st.caption(
    "Simulationsgestützte Entscheidungsunterstützung auf Basis der Phase-1/2-Methodik "
    "(19 KPIs, GSF SCI Spec v1.1.0). Werte sind Modell-Output für die gewählte "
    "Szenario-Einstellung links, keine gemessenen DHL-Produktivdaten."
)

# ---------------------------------------------------------------------------
# Sidebar — Stellvariablen (control variables) for the whole session
# ---------------------------------------------------------------------------
st.sidebar.header("Stellvariablen")

min_vram_gb = st.sidebar.select_slider(
    "Min. VRAM-Bedarf (GB) — Workload-Proxy", options=[16, 24, 48, 96], value=48
)
requests_per_month = st.sidebar.select_slider(
    "Requests/Monat",
    options=[1_000, 10_000, 100_000, 1_000_000],
    value=10_000,
    format_func=lambda v: f"{v:,}",
)
pv_share = st.sidebar.slider("PV-Anteil am Energiemix", 0.0, 1.0, 0.0, step=0.05)

use_live = st.sidebar.checkbox("Live-Netz-CO2-Wert (Deutschland) statt Slider verwenden")
if use_live:
    try:
        snapshot = fetch_live_grid_carbon_intensity()
        grid_ef = snapshot.carbon_intensity_gco2e_per_kwh
        st.sidebar.success(
            f"Live: {grid_ef:.1f} gCO2e/kWh\n\n"
            f"Quelle: {snapshot.provider}\n\nZeitstempel: {snapshot.observed_at}"
        )
    except Exception as exc:  # noqa: BLE001 — demo must never crash on network failure
        st.sidebar.warning(
            f"Live-Abruf fehlgeschlagen ({type(exc).__name__}). "
            f"Fallback: statischer UBA-2024-Wert {STATIC_FALLBACK_GCO2E_PER_KWH:.0f} gCO2e/kWh."
        )
        grid_ef = STATIC_FALLBACK_GCO2E_PER_KWH
else:
    grid_ef = st.sidebar.slider(
        "Netz-Emissionsfaktor (gCO2e/kWh)", min_value=41, max_value=800, value=485, step=5
    )

workload = WorkloadProfile(
    id="dashboard-session",
    model_size_b=70,
    quantization="Q4_K_M",
    min_vram_gb=min_vram_gb,
    requests_per_month=requests_per_month,
    quality_score=0.9,
    business_value_score=0.9,
)
ef = EmissionFactorProfile(grid_ef_gco2e_per_kwh=grid_ef, pv_share=pv_share)

tab_kpi, tab_hw, tab_pareto, tab_sim, tab_live, tab_audit = st.tabs(
    [
        "KPI-Katalog & Green Gates",
        "Hardware-Vergleich",
        "Pareto-Frontier",
        "Sensitivität",
        "Live-Kontext",
        "Auditability",
    ]
)

# ---------------------------------------------------------------------------
# Tab 1 — KPI catalog + green gates
# ---------------------------------------------------------------------------
with tab_kpi:
    st.subheader("KPI-Katalog (19 Kandidaten, 6 Gruppen)")
    kpis = load_kpi_catalog()
    gates = load_green_gates()

    catalog_df = pd.DataFrame(
        [
            {
                "ID": kpi["id"],
                "Gruppe": kpi["group"],
                "Name": kpi["name"],
                "Functional Unit": kpi["functional_unit"],
                "Status": kpi["status"],
                "Green Gate": "definiert"
                if has_defined_gate(gates.get(kpi["id"]))
                else ZONE_EMOJI["tbd"] + " kein Gate",
            }
            for kpi in kpis
        ]
    )
    st.dataframe(catalog_df, use_container_width=True, hide_index=True)
    st.caption(
        "Alle 19 KPIs haben Status `candidate` — echte Messwerte folgen der "
        "Pilot-Scope-Klärung (OC-01..OC-05). SCI-001/SCI-002 haben aktuell kein "
        "definiertes Green Gate (aggregierte, boundary-abhängige Kennzahlen ohne "
        "universellen Schwellenwert)."
    )

# ---------------------------------------------------------------------------
# Tab 2 — Hardware comparison for the current scenario
# ---------------------------------------------------------------------------
with tab_hw:
    st.subheader("Hardware-Vergleich für das gewählte Szenario")
    rows = build_scenario_rows(workload, ef)
    if not rows:
        st.warning("Kein Hardware-Tier erfüllt die gewählte Mindest-VRAM-Anforderung.")
    else:
        df = pd.DataFrame(rows).set_index("Config")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("EfficiencyScore (höher = besser)")
            st.bar_chart(df["EfficiencyScore"])
        with col2:
            st.caption("Gesamt-CO2 pro Request (gCO2e)")
            st.bar_chart(df["Total gCO2e/req"])
        with col3:
            st.caption("Kosten pro Request (EUR)")
            st.bar_chart(df["EUR/req"])
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("**Green-Gate-Einordnung der Run-Phase-KPIs für dieses Szenario**")
        gates = load_green_gates()
        best = rows[0]
        run001_gate = gates.get("RUN-001")
        run002_gate = gates.get("RUN-002")
        zone_run001 = gate_zone(best["Total gCO2e/req"], run001_gate)
        gc1, gc2 = st.columns(2)
        gc1.metric(
            f"RUN-001 Zone ({best['Config']})",
            f"{ZONE_EMOJI.get(zone_run001, '⚪')} {zone_run001}",
            help="Simulierter Gesamt-CO2-Wert gegen den definierten Green Gate geprüft.",
        )
        st.caption(
            "Hinweis: Green Gates wurden für Kandidaten-Schwellenwerte definiert "
            "(`threshold_basis: krallmann_default`), nicht DHL-abgenommen."
        )

# ---------------------------------------------------------------------------
# Tab 3 — Pareto frontier
# ---------------------------------------------------------------------------
with tab_pareto:
    st.subheader("Pareto-Frontier: CO2 vs. Kosten vs. EfficiencyScore")
    all_rows, frontier_labels = build_pareto_rows(workload, ef)
    if not all_rows:
        st.warning("Keine machbaren Konfigurationen für dieses Szenario.")
    else:
        chart_df = pd.DataFrame(all_rows)
        chart_df["Auf Pareto-Frontier"] = chart_df["Config"].isin(frontier_labels)
        st.scatter_chart(
            chart_df,
            x="Total gCO2e/req",
            y="EUR/req",
            size="EfficiencyScore",
            color="Auf Pareto-Frontier",
        )
        st.markdown(f"**{len(frontier_labels)} von {len(all_rows)} Konfigurationen sind Pareto-optimal:**")
        for label in sorted(frontier_labels):
            st.markdown(f"- {label}")
        st.caption(
            "Pareto-optimal = keine andere Konfiguration ist in allen drei "
            "Dimensionen (CO2, Kosten, EfficiencyScore) gleichzeitig besser."
        )

# ---------------------------------------------------------------------------
# Tab 4 — Sensitivity analysis
# ---------------------------------------------------------------------------
with tab_sim:
    st.subheader("Sensitivität: CO2/Request vs. Request-Volumen")
    ranked = rdc_rank(workload, ef)
    if not ranked:
        st.warning("Keine machbare Konfiguration für dieses Szenario.")
    else:
        top_config_id = ranked[0]["id"]
        top_config_label = ranked[0]["label"]
        volumes = [1_000, 10_000, 100_000, 1_000_000]
        sens_rows = build_sensitivity_rows(workload, ef, top_config_id, volumes)
        st.markdown(f"**Top-Konfiguration für dieses Szenario:** {top_config_label}")
        if sens_rows:
            sens_df = pd.DataFrame(sens_rows)
            st.dataframe(sens_df, use_container_width=True, hide_index=True)
            st.caption(
                "Ratio = Δ(gCO2e/Request) / Δ(Requests/Monat) zwischen zwei "
                "benachbarten Volumenstufen — zeigt den Amortisierungseffekt: mehr "
                "Requests verteilen die Embodied-Carbon-Komponente auf mehr Nutzung."
            )
        st.divider()
        st.markdown("**CO2-Sensitivität: Netzstrom vs. PV 70%**")
        ef_grid = EmissionFactorProfile(grid_ef_gco2e_per_kwh=grid_ef, pv_share=0.0)
        ef_pv = EmissionFactorProfile(grid_ef_gco2e_per_kwh=grid_ef, pv_share=0.70, battery_share=0.10)
        rows_grid = {r["Config"]: r for r in build_scenario_rows(workload, ef_grid)}
        rows_pv = {r["Config"]: r for r in build_scenario_rows(workload, ef_pv)}
        compare_rows = []
        for label, grid_row in rows_grid.items():
            pv_row = rows_pv.get(label)
            if pv_row is None:
                continue
            compare_rows.append(
                {
                    "Config": label,
                    "CO2 Netzstrom": grid_row["Total gCO2e/req"],
                    "CO2 PV 70%": pv_row["Total gCO2e/req"],
                }
            )
        if compare_rows:
            compare_df = pd.DataFrame(compare_rows).set_index("Config")
            st.bar_chart(compare_df)

# ---------------------------------------------------------------------------
# Tab 5 — Live context
# ---------------------------------------------------------------------------
with tab_live:
    st.subheader("Live-Kontext: echte externe Datenpunkte")
    st.markdown("**Deutscher Netz-CO2-Faktor**")
    if st.button("Jetzt live abrufen (energy-charts.info, Fraunhofer ISE)"):
        try:
            snapshot = fetch_live_grid_carbon_intensity()
            st.success(
                f"{snapshot.carbon_intensity_gco2e_per_kwh:.1f} gCO2e/kWh — "
                f"Zeitstempel {snapshot.observed_at} (UTC), Quelle: {snapshot.provider}"
            )
        except Exception as exc:  # noqa: BLE001
            st.error(f"Live-Abruf fehlgeschlagen: {type(exc).__name__}: {exc}")
    st.caption(
        f"Statischer Vergleichswert (UBA 2024): {STATIC_FALLBACK_GCO2E_PER_KWH:.0f} gCO2e/kWh. "
        "Tokenlos, kostenlos, keine Registrierung nötig."
    )

    st.divider()
    st.markdown("**Boavizta-Referenzwerte für Embodied Carbon (Hardware)**")
    st.dataframe(pd.DataFrame(BOAVIZTA_REFERENCES), use_container_width=True, hide_index=True)
    st.caption(
        "Quelle: api.boavizta.org (frei, offen, Bottom-up-LCA-Methodik). Ersetzt seit "
        "2026-07-15 den reinen TDP-Proxy für embodied_co2_kg in 6 von 7 Hardware-Tiers."
    )

# ---------------------------------------------------------------------------
# Tab 6 — Auditability / evidence ledger
# ---------------------------------------------------------------------------
with tab_audit:
    st.subheader("Evidence Ledger — auditierbare Simulationsläufe")
    ledger_rows = load_evidence_ledger_rows()
    if not ledger_rows:
        st.info("Noch kein Ledger-Eintrag gefunden. Lauf `generators/evidence_ledger.py` aus.")
    else:
        st.dataframe(pd.DataFrame(ledger_rows), use_container_width=True, hide_index=True)
        st.caption(
            "Jeder Lauf ist mit RUN-ID, Git-Commit und SHA-256-Hash der Output-Dateien "
            "versehen — reproduzierbar und auditierbar im technischen, nicht nur im "
            "behaupteten Sinn. Siehe `evidence/SIMULATION_EVIDENCE_LEDGER.md`."
        )
