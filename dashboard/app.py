"""DHLCO2 Interactive Dashboard — local demo app.

Run with:
  uv run streamlit run dashboard/app.py

Reads directly from the same SSOT data files (data/*.yaml) and generator modules
(generators/hardware_model.py, generators/rdc_pareto.py, generators/decision_support.py)
that the CI export pipeline uses. No mocked or invented numbers — every chart is either
the deterministic simulation model's real output for the chosen scenario, or a
live-fetched external data point (clearly labeled as such).

Layout follows the 2026-07-16 stakeholder review: lead with the decision question
("which infrastructure configuration is best for this workload?"), not the KPI catalog.
A named scenario (generators/demo_scenarios.py) seeds sensible defaults; every value
underneath stays fully adjustable — nothing here locks users out of exploring arbitrary
control-variable combinations.

Scope note: KPI values are simulation output, not real DHL measurements — the KPI
catalog itself still carries status "candidate" for all 19 KPIs until the pilot
scope (OC-01..OC-05) is resolved. This dashboard demonstrates decision capability
on top of the methodology, not live DHL telemetry.
"""

from __future__ import annotations

import os
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
    build_demo_scenario_options,
    build_gate_contribution_rows,
    build_lever_ranking_rows,
    build_pareto_rows,
    build_scenario_rows,
    build_sensitivity_rows,
    gate_zone,
    has_defined_gate,
    load_cross_repo_benchmark_rows,
    load_evidence_ledger_rows,
    load_green_gates,
    load_kpi_catalog,
    rank_co2_levers,
    recommend_tier,
)
from entsoe_grid_carbon import BIDDING_ZONES, fetch_generation_mix
from hardware_model import EmissionFactorProfile, WorkloadProfile, rdc_rank
from live_grid_carbon import STATIC_FALLBACK_GCO2E_PER_KWH, fetch_live_grid_carbon_intensity

st.set_page_config(page_title="DHLCO2 — CO2/Kosten-Entscheidungsmodell", layout="wide")

st.title("DHLCO2 — CO2/Kosten-Entscheidungsmodell")
st.markdown(
    "#### Entscheidungsfrage: Welche Infrastrukturkonfiguration ist für einen "
    "beispielhaften DHL-Service unter CO₂-, Kosten- und Effizienzgesichtspunkten die beste?"
)
st.caption(
    "Simulationsgestützte Entscheidungsunterstützung auf Basis der Phase-1/2-Methodik "
    "(19 KPIs, GSF SCI Spec v1.1.0). Werte sind Modell-Output für das gewählte "
    "Szenario, keine gemessenen DHL-Produktivdaten."
)

# ---------------------------------------------------------------------------
# Sidebar — named scenario + Stellvariablen (control variables)
# ---------------------------------------------------------------------------
st.sidebar.header("Ausgangsszenario")

scenario_options = build_demo_scenario_options()
scenario_labels = ["Custom / Freie Eingabe"] + list(scenario_options.keys())
_default_label = next(
    (label for label in scenario_labels if label.startswith("DEMO-02")), scenario_labels[0]
)
scenario_label = st.sidebar.selectbox(
    "Beispielhafter DHL-Service", scenario_labels, index=scenario_labels.index(_default_label)
)
scenario = scenario_options.get(scenario_label)
if scenario is not None:
    st.sidebar.caption(f"_{scenario.description}_")
    st.sidebar.caption(f"Achsen: {scenario.function_label} × {scenario.volume_label}")
    defaults = dict(
        min_vram_gb=scenario.min_vram_gb,
        requests_per_month=scenario.requests_per_month,
        pv_share=scenario.pv_share,
        grid_ef=scenario.grid_ef_gco2e_per_kwh,
        avg_latency_s=scenario.avg_latency_s,
        quality_score=scenario.quality_score,
        business_value_score=scenario.business_value_score,
    )
else:
    st.sidebar.caption("_Frei wählbare Stellvariablen ohne Szenario-Vorbelegung._")
    defaults = dict(
        min_vram_gb=48,
        requests_per_month=10_000,
        pv_share=0.0,
        grid_ef=485,
        avg_latency_s=5.0,
        quality_score=0.9,
        business_value_score=0.9,
    )

# Widget keys are suffixed by scenario id: switching scenario resets every slider to
# that scenario's defaults, but tweaking a slider within the same scenario persists
# across reruns — "start from a real example, then adjust anything freely".
key_suffix = scenario.id if scenario is not None else "custom"

st.sidebar.header("Stellvariablen (jederzeit frei anpassbar)")

min_vram_gb = st.sidebar.select_slider(
    "Min. VRAM-Bedarf (GB) — Workload-Proxy",
    options=[16, 24, 48, 96],
    value=defaults["min_vram_gb"],
    key=f"min_vram_{key_suffix}",
)
requests_per_month = st.sidebar.number_input(
    "Requests/Monat",
    min_value=100,
    max_value=20_000_000,
    value=int(defaults["requests_per_month"]),
    step=1_000,
    key=f"requests_{key_suffix}",
)
avg_latency_s = st.sidebar.slider(
    "Ø Latenz pro Request (s)",
    min_value=0.1,
    max_value=60.0,
    value=float(defaults["avg_latency_s"]),
    step=0.1,
    key=f"latency_{key_suffix}",
    help="Treibt RUN-CO2/Energie direkt: Leistung(W) x Latenz(s) = Energie.",
)
quality_score = st.sidebar.slider(
    "Qualitätsanspruch (quality_score)",
    min_value=0.0,
    max_value=1.0,
    value=float(defaults["quality_score"]),
    step=0.05,
    key=f"quality_{key_suffix}",
    help="Skaliert UsefulOutputs -> beeinflusst Kosten je Nutzenoutput, nicht CO2.",
)
business_value_score = st.sidebar.slider(
    "Geschäftlicher Wert (business_value_score)",
    min_value=0.0,
    max_value=1.0,
    value=float(defaults["business_value_score"]),
    step=0.05,
    key=f"bizvalue_{key_suffix}",
)
pv_share = st.sidebar.slider(
    "PV-/Ökostrom-Anteil am Energiemix",
    0.0,
    1.0,
    float(defaults["pv_share"]),
    step=0.05,
    key=f"pv_{key_suffix}",
)
grid_ef_manual = st.sidebar.slider(
    "Netz-Emissionsfaktor (gCO2e/kWh) — manuell/Szenario",
    min_value=41,
    max_value=800,
    value=int(defaults["grid_ef"]),
    step=5,
    key=f"grid_ef_{key_suffix}",
)

grid_ef_source = st.sidebar.radio(
    "Mit Live-Daten überschreiben?",
    ["Nein (manuell/Szenario oben)", "Live: energy-charts.info (DE)", "Live: ENTSO-E (DE_LU)"],
    key=f"ef_source_{key_suffix}",
)
grid_ef = grid_ef_manual
live_ef_note = None
if grid_ef_source == "Live: energy-charts.info (DE)":
    try:
        snapshot = fetch_live_grid_carbon_intensity()
        grid_ef = snapshot.carbon_intensity_gco2e_per_kwh
        live_ef_note = (
            f"Live energy-charts.info: {grid_ef:.1f} gCO2e/kWh ({snapshot.observed_at} UTC)"
        )
    except Exception as exc:  # noqa: BLE001 — demo must never crash on network failure
        live_ef_note = (
            f"Live-Abruf fehlgeschlagen ({type(exc).__name__}) — verwende manuellen Wert "
            f"{grid_ef_manual:.0f} gCO2e/kWh."
        )
elif grid_ef_source == "Live: ENTSO-E (DE_LU)":
    token = os.getenv("ENTSOE_SECURITY_TOKEN")
    if not token:
        live_ef_note = (
            "ENTSOE_SECURITY_TOKEN nicht gesetzt — verwende manuellen Wert. Siehe "
            "docs/phase3_data_source_roadmap.md §1 für den Zugriffsablauf."
        )
    else:
        try:
            snapshot = fetch_generation_mix(security_token=token, zone_eic=BIDDING_ZONES["DE_LU"])
            grid_ef = snapshot.weighted_carbon_intensity_gco2e_per_kwh
            live_ef_note = f"Live ENTSO-E (DE_LU): {grid_ef:.1f} gCO2e/kWh"
        except Exception as exc:  # noqa: BLE001
            live_ef_note = (
                f"ENTSO-E-Abruf fehlgeschlagen ({type(exc).__name__}) — verwende manuellen "
                f"Wert {grid_ef_manual:.0f} gCO2e/kWh."
            )
if live_ef_note:
    st.sidebar.caption(live_ef_note)

workload = WorkloadProfile(
    id="dashboard-session",
    model_size_b=70,
    quantization="Q4_K_M",
    min_vram_gb=min_vram_gb,
    requests_per_month=requests_per_month,
    quality_score=quality_score,
    business_value_score=business_value_score,
    avg_latency_s=avg_latency_s,
)
ef = EmissionFactorProfile(grid_ef_gco2e_per_kwh=grid_ef, pv_share=pv_share)
scenario_label_for_rationale = scenario.name if scenario is not None else "das gewählte Custom-Szenario"

# ---------------------------------------------------------------------------
# Result box — always visible, independent of which tab is open below
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Empfehlung für dieses Szenario")
recommendation = recommend_tier(workload, ef, scenario_label=scenario_label_for_rationale)

if recommendation is None:
    st.error(
        "Keine Hardware-Konfiguration erfüllt die gewählte Mindest-VRAM-Anforderung für "
        "dieses Szenario — Empfehlung nicht möglich."
    )
else:
    if recommendation.all_candidates_red:
        st.warning(
            "Jede machbare Konfiguration ist für dieses Lastprofil bei mindestens einem "
            "Green Gate rot — die folgende Empfehlung ist die am wenigsten kritische "
            "verfügbare Option, kein unproblematisches Ergebnis."
        )
    with st.container(border=True):
        col_rec, col_co2, col_cost, col_gate, col_dq = st.columns([2, 1, 1, 1, 1.6])
        col_rec.metric("Empfohlene Konfiguration", recommendation.config_label)
        col_co2.metric("CO2/Request", f"{recommendation.total_co2_gco2e_per_request:.4f} g")
        col_cost.metric("Kosten/Nutzenoutput", f"{recommendation.cost_useful_outcome_eur:.4f} €")
        col_gate.metric(
            "Green-Gate",
            f"{ZONE_EMOJI.get(recommendation.gate.overall_zone, '⚪')} {recommendation.gate.overall_zone}",
        )
        col_dq.metric(
            "Datenqualität",
            "candidate / M0–M1",
            help=(
                "Alle Werte sind Simulationsergebnisse auf Basis der Phase-1/2-Methodik, "
                "keine gemessenen DHL-Produktivdaten. Alle 19 KPIs tragen Status "
                "'candidate' bis der Pilot-Scope (OC-01..OC-05) geklärt ist — siehe "
                "KPI-Katalog-Tab."
            ),
        )
        st.caption(recommendation.rationale)

tab_decision, tab_hw, tab_pareto, tab_sim, tab_kpi, tab_live, tab_audit, tab_cross_repo = st.tabs(
    [
        "Entscheidung & Begründung",
        "Hardware-Vergleich",
        "Pareto-Frontier",
        "Sensitivität (Detail)",
        "KPI-Katalog & Green Gates",
        "Live-Kontext",
        "Auditability",
        "Cross-Repo-Benchmark",
    ]
)

# ---------------------------------------------------------------------------
# Tab 1 — Decision detail: rationale, gate breakdown, strongest lever, pilot path
# ---------------------------------------------------------------------------
with tab_decision:
    st.subheader("Warum diese Empfehlung?")
    if recommendation is None:
        st.warning("Keine machbare Konfiguration für dieses Szenario.")
    else:
        st.markdown(recommendation.rationale)

        st.markdown("**Aufschlüsselung der Green-Gate-Bewertung (worst-of über die KPIs unten):**")
        st.dataframe(
            pd.DataFrame(build_gate_contribution_rows(recommendation.gate)),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "HW-001 (Embodied CO2/Request) und HW-002 (CAPEX/Request) fließen nicht ein — "
            "beide haben noch keinen definierten Schwellenwert (`threshold_basis: tbd` in "
            "data/green_gates.yaml, wartet auf Hardware-Inventar bzw. Finanzdaten)."
        )

        st.divider()
        st.markdown(
            "**Stärkster verbleibender Hebel zur CO2-Reduktion** "
            "(ab den aktuellen Szenario-Werten, Hardware fixiert auf die Empfehlung oben):"
        )
        co2_levers = rank_co2_levers(workload, ef, recommendation.config_id)
        if co2_levers and co2_levers[0].delta > 0:
            top = co2_levers[0]
            st.info(
                f"Stärkster verbleibender Hebel: **{top.axis_label}** — von aktuell "
                f"{top.current_value} auf {top.best_value} (Modell-Bestwert) spart "
                f"{top.delta:.4f} gCO2e/Request, alle anderen Stellvariablen unverändert."
            )
        elif co2_levers:
            st.success(
                "Alle Stellvariablen liegen bereits an oder über den Modell-Bestwerten — "
                "kein verbleibender CO2-Hebel innerhalb des Simulationsbereichs."
            )
        if co2_levers:
            st.dataframe(
                pd.DataFrame(build_lever_ranking_rows(workload, ef, recommendation.config_id, "co2")),
                use_container_width=True,
                hide_index=True,
            )
        st.markdown("**Verbleibende Hebel bei den Kosten je Nutzenoutput:**")
        cost_lever_rows = build_lever_ranking_rows(workload, ef, recommendation.config_id, "cost")
        if cost_lever_rows:
            st.dataframe(pd.DataFrame(cost_lever_rows), use_container_width=True, hide_index=True)
        st.caption(
            "„Verbleibendes Potenzial“ = Verbesserung von den aktuellen Szenario-Werten "
            "zum jeweiligen Modell-Bestwert (0 = bereits ausgeschöpft). Qualitätsanspruch "
            "(quality_score) wirkt nur auf die Kosten-, nicht auf die CO2-Kennzahl — "
            "Strommix/Standort (PV-Anteil, Netz-EF) wirken nur auf CO2, nicht auf die "
            "Kosten. Beide Rankings bewusst getrennt statt zu einem künstlichen "
            "Gesamt-Score verrechnet."
        )

        with st.expander("Pilotfähigkeit: Wie wird das ein echter DHL-Pilot?"):
            st.markdown(
                "- Gleicher Berechnungsweg wie im gesamten Artefakt — kein Parallelmodell "
                "für die Demo.\n"
                "- Die Szenario-Werte links sind illustrative Platzhalter; ein Pilot ersetzt "
                "sie 1:1 durch echte DHL-Telemetrie (Requests/Monat, Latenz, Auslastung), "
                "sobald Pilot-Scope und Monitoring-Zugriff geklärt sind "
                "(siehe NEXT_STEPS.md, OC-01..OC-05).\n"
                "- Der Hardware-Katalog (`data/hardware_configs.yaml`) ist 1:1 austauschbar "
                "gegen das reale DHL-Hardware-Inventar.\n"
                "- Ergebnis: Dashboard, Empfehlung und Reporting laufen unverändert weiter — "
                "nur mit echten statt illustrativen Eingabewerten."
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
        st.caption(
            "Gate-Spalte: aggregierter Status über RUN-001/RUN-002/RUN-004 (worst-of), "
            "siehe generators/decision_support.py::aggregate_gate_status()."
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
# Tab 4 — Sensitivity analysis (detail)
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
        st.caption(
            "Detailansicht ergänzend zum zusammengefassten Hebel-Ranking im Tab "
            "„Entscheidung & Begründung“."
        )

# ---------------------------------------------------------------------------
# Tab 5 — KPI catalog + green gates
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

    st.divider()
    st.markdown("**Green-Gate-Einordnung der Run-Phase-KPIs für das gewählte Szenario**")
    rows = build_scenario_rows(workload, ef)
    if rows:
        best = rows[0]
        zone_run001 = gate_zone(best["Total gCO2e/req"], gates.get("RUN-001"))
        gc1, gc2 = st.columns(2)
        gc1.metric(
            f"RUN-001 Zone ({best['Config']})",
            f"{ZONE_EMOJI.get(zone_run001, '⚪')} {zone_run001}",
            help="Simulierter Gesamt-CO2-Wert gegen den definierten Green Gate geprüft.",
        )
        st.caption(
            "Hinweis: Green Gates wurden für Kandidaten-Schwellenwerte definiert "
            "(`threshold_basis: krallmann_default`), nicht DHL-abgenommen. Der "
            "aggregierte Gate-Status über RUN-001/002/004 steht im Tab "
            "„Entscheidung & Begründung“ bzw. als Spalte im Hardware-Vergleich."
        )

# ---------------------------------------------------------------------------
# Tab 6 — Live context
# ---------------------------------------------------------------------------
with tab_live:
    st.subheader("Live-Kontext: echte externe Datenpunkte")
    st.caption(
        "Der Netz-Emissionsfaktor links in den Stellvariablen kann direkt auf diese "
        "Live-Quellen umgestellt werden (Radio-Auswahl „Mit Live-Daten überschreiben?“) "
        "— die folgenden Buttons sind nur zum Nachschlagen ohne die Auswahl zu ändern."
    )
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
    st.markdown("**EU-Netz-CO2-Faktor (ENTSO-E Transparency Platform)**")
    if st.button("Jetzt live abrufen (ENTSO-E, DE_LU)"):
        token = os.getenv("ENTSOE_SECURITY_TOKEN")
        if not token:
            st.warning(
                "ENTSOE_SECURITY_TOKEN nicht gesetzt — siehe "
                "`docs/phase3_data_source_roadmap.md` §1 für den Zugriffsablauf."
            )
        else:
            try:
                snapshot = fetch_generation_mix(
                    security_token=token, zone_eic=BIDDING_ZONES["DE_LU"]
                )
                st.success(
                    f"{snapshot.weighted_carbon_intensity_gco2e_per_kwh:.1f} gCO2e/kWh — "
                    f"Zone DE_LU, Zeitraum {snapshot.period_start} .. {snapshot.period_end} (UTC)"
                )
                if snapshot.unmapped_psr_types:
                    st.caption(
                        f"Achtung, unbekannte PSR-Typen (Fallback verwendet): "
                        f"{snapshot.unmapped_psr_types}"
                    )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Live-Abruf fehlgeschlagen: {type(exc).__name__}: {exc}")
    st.caption(
        "Regulatorisch-autoritative EU-Quelle, eigener CO2-Faktor je Energieträger "
        "(nicht Black-Box wie energy-charts.info) — siehe `docs/phase3_data_source_roadmap.md` §1."
    )

    st.divider()
    st.markdown("**Boavizta-Referenzwerte für Embodied Carbon (Hardware)**")
    st.dataframe(pd.DataFrame(BOAVIZTA_REFERENCES), use_container_width=True, hide_index=True)
    st.caption(
        "Quelle: api.boavizta.org (frei, offen, Bottom-up-LCA-Methodik). Ersetzt seit "
        "2026-07-15 den reinen TDP-Proxy für embodied_co2_kg in 6 von 7 Hardware-Tiers."
    )

# ---------------------------------------------------------------------------
# Tab 7 — Auditability / evidence ledger
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

# ---------------------------------------------------------------------------
# Tab 8 — Cross-repo energy benchmark
# ---------------------------------------------------------------------------
with tab_cross_repo:
    st.subheader("Cross-Repo Energy Benchmark")
    st.caption(
        "Zeigt, dass die SCI-Methodik technologieunabhängig ist — nicht auf das "
        "DHLCO2-Repo zugeschnitten, sondern auf beliebige Software-Projekte "
        "anwendbar. Portfolio-Inventur 2026-07-15: 51 eigene Repos gescannt, 9 "
        "hatten bereits GitHub-Actions-CI; 7 kundenneutrale davon wurden für "
        "dieses Benchmark ausgewählt (2 gehören zu einem anderen Kundenprojekt "
        "und wurden bewusst ausgeklammert)."
    )
    cross_repo_rows = load_cross_repo_benchmark_rows()
    if not cross_repo_rows:
        st.info("Noch keine Cross-Repo-Daten gefunden.")
    else:
        cross_repo_df = pd.DataFrame(cross_repo_rows)
        measured_df = cross_repo_df[cross_repo_df["Status"] == "measured"]
        if not measured_df.empty:
            st.caption("Gemessene Werte (real, aus einem tatsächlichen CI-Lauf):")
            st.bar_chart(measured_df.set_index("Repo")["SCI gCO2eq/Lauf"])
        st.dataframe(cross_repo_df, use_container_width=True, hide_index=True)
        status_counts = cross_repo_df["Status"].value_counts().to_dict()
        status_labels = {
            "measured": "gemessen",
            "awaiting_verification": "wartet auf Verifikation",
            "failed_needs_diagnosis": "fehlgeschlagen (Diagnose offen)",
            "blocked_pre_existing_infra_issue": "blockiert (vorbestehendes Infra-Problem)",
            "deferred_to_next_session": "auf nächste Session vertagt (Diagnose-Doc im Repo)",
            "deferred_needs_decision": "zurückgestellt (Entscheidung offen)",
        }
        status_summary = ", ".join(
            f"{count} {status_labels.get(status, status)}" for status, count in status_counts.items()
        )
        st.caption(
            f"Status: {status_summary}. Werte werden "
            "nur eingetragen, wenn sie aus einem echten, geprüften CI-Lauf stammen — "
            "siehe `evidence/cross_repo_benchmark.yaml`."
        )
