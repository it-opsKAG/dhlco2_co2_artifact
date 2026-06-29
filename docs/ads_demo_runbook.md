# ADS-Demo-Runbook mit DHLCO2-SSOT

## Ziel

Der Adaptive Decision Simulator demonstriert die Entscheidungsstrecke auf Basis des DHLCO2-SSOT. Die Demo erzeugt keine DHL-Messwerte.

## Umgebung

PowerShell:

```powershell
$env:ADS_DHL_ARTIFACT_ROOT='C:\Users\emanu\workspace\Projects\dhlco2_co2_artifact'
cd C:\Users\emanu\workspace\Projects\adaptive_decision_simulator
```

## Szenarien

### Build-only

```powershell
python -m pytest tests\test_monitoring_api.py
```

Payload-Idee:

```json
{
  "raw_text": "DHL Build Monitoring für eine CI/CD-Pipeline mit CO2- und Energie-KPIs.",
  "context": {
    "phases_in_scope": ["build"],
    "telemetry_sources_available": ["ci_logs", "cloud_billing", "carbon_intensity_feed"],
    "allow_proxies": true,
    "carbon_intensity_mode": "region_average"
  }
}
```

### Run-only

```json
{
  "raw_text": "DHL Run-Service mit Request-Zähler, Energie je Request und Carbon-Intensity-Kontext.",
  "context": {
    "phases_in_scope": ["run"],
    "telemetry_sources_available": ["service_metrics", "apm_traces", "carbon_intensity_feed"],
    "allow_proxies": true,
    "preferred_functional_unit": "service_request"
  }
}
```

### Portfolio

```json
{
  "raw_text": "DHL will Build und Run über mehrere Projekte vergleichbar und ISO-nah monitoren.",
  "context": {
    "portfolio_scope": "multi_project",
    "phases_in_scope": ["build", "run"],
    "require_iso_traceability": true,
    "require_project_comparability": true,
    "allow_proxies": true
  }
}
```

### Proxy-Baseline

Nutzt wenige verfügbare Quellen und erlaubt Proxies. Erwartet wird ein SSOT-Proxy-Baseline-Blueprint mit sichtbaren Gaps.

### Plattformprofil

Setzt `project_profile` auf `github_actions`, `gitlab_ci`, `azure_devops`, `kubernetes` oder `datadog_apm`.

## Erwartetes Ergebnis

- `artifact_context.source_mode` ist `dhlco2_ssot`.
- Die Szenarien enthalten IDs mit `dhlco2_ssot_`.
- Die Antwort nennt offene Gaps wie Carbon-Intensity-Policy, Source-System-Bindung oder ISO-Mapping.
- Die Empfehlung ist eine Monitoring-Blueprint-Auswahl, keine CO2-Baseline.
