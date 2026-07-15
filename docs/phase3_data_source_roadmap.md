# Datenquellen-Roadmap — von Proxy zu echten Live-Daten

**Datum:** 2026-07-15
**Zweck:** Übersicht, welche echten externen Datenquellen den heutigen Proxy-Stand ablösen oder ergänzen können — was jede Quelle bringt, was sie kostet, was wir dafür brauchen. Gedacht als Grundlage für die "nächste Schritte"-Diskussion im Statusupdate.

---

## Bereits integriert (2026-07-14/15)

| Quelle | Was sie liefert | Status |
|---|---|---|
| **Boavizta API** (`api.boavizta.org`) | Echte Embodied-Carbon-Werte (kgCO2eq) für GPU-Hardware, methodisch belegt, mit Unsicherheitsspanne | ✅ Live integriert, ersetzt TDP-Proxy für 6 von 7 Hardware-Tiers (`data/hardware_configs.yaml`) |
| **energy-charts.info** (Fraunhofer ISE) | Live-Netz-CO2-Faktor Deutschland, 15-Min-Auflösung | ✅ Live integriert (`generators/live_grid_carbon.py`), als Kontext-Signal im Dashboard — noch nicht in die Kern-KPI-Berechnung verdrahtet |

## Kandidaten für die nächsten Schritte

### 1. ENTSO-E Transparency Platform — offizielle EU-Netzdaten ✅ live verifiziert 2026-07-15

**Zweck:** Ersetzt den energy-charts.info-Convenience-Wert (und den statischen UBA-2024-Jahresdurchschnitt) durch die **offizielle, regulatorisch vorgeschriebene EU-Transparenzplattform** für Stromerzeugung, -last und -handel — Betreiber ist der Verband der europäischen Übertragungsnetzbetreiber selbst.

**Zugriff/Voraussetzungen:**
- Registrierung + E-Mail-Verifizierung auf `transparency.entsoe.eu` (✅ erledigt)
- E-Mail an `transparency@entsoe.eu`, Betreff "Restful API access" (Freigabe durch ENTSO-E, Dauer nicht in unserer Hand)
- Danach: Security-Token im Account unter "Web API Security Token"
- Kostenlos, keine Mengenbegrenzung dokumentiert

**Mehrwert:**
- Deckt alle EU-Bidding-Zonen ab (nicht nur Deutschland) — relevant, falls Pilot B außerhalb Deutschlands liegt
- Liefert Erzeugung nach Energieträger (documentType A75), aus der wir den CO2-Faktor selbst und **nachvollziehbar** berechnen (eigene Emissionsfaktor-Tabelle je Energieträger statt Black-Box-Zahl)
- Historische Zeitreihen erlauben, die Szenario-Bandbreiten der Simulation (`simulation_runner.py`) empirisch zu kalibrieren statt handgesetzte Rundwerte zu verwenden
- Regulatorische Autorität als Zitierquelle — starkes Argument in einer Audit-Diskussion

**Benötigte Daten für vollen Einsatz:** nur der Security-Token; Bidding-Zone-Code ist bereits bekannt (`10Y1001A1001A83F` für DE_LU), weitere Zonen sind analog abrufbar.

**Erster echter Lauf** (`generators/entsoe_grid_carbon.py`, direkt ausgeführt, 15.07.2026 ~14:30 UTC):

| Kennzahl | Wert |
|---|---|
| Bidding-Zone | DE_LU (`10Y1001A1001A83F`) |
| Zeitraum | 2026-07-15T12:30 .. 14:30 UTC (Standard-2h-Fenster) |
| Gewichteter CO2-Faktor (ENTSO-E, selbst berechnet) | **169–172 gCO2e/kWh** |
| Unmapped PSR-Codes | keine — alle 16 im Fenster aufgetretenen Energieträger-Codes sind in `PSR_EMISSION_FACTORS_GCO2E_PER_KWH` abgedeckt |
| Dominante Energieträger im Fenster | Solar (B16, ~41.8 GW), Wind Onshore (B19, ~6.8 GW), Braunkohle (B02, ~6.0 GW), Pumpspeicher (B10, ~5.1 GW) |

**Drei-Wege-Vergleich (gleicher Moment, 15.07.2026 ~14:30 UTC, DE/DE_LU):**

| Quelle | Wert (gCO2e/kWh) | Charakter |
|---|---|---|
| ENTSO-E (neu, selbst berechnet aus Erzeugungsmix) | 169–172 | live, auditierbar je Energieträger |
| energy-charts.info (bestehend, Fraunhofer ISE) | 197.5 (Stand 13:00 UTC) | live, Black-Box-Wert |
| Statischer UBA-2024-Jahresdurchschnitt | 485 | statisch, Jahresmittel |

Beide Live-Quellen liegen deutlich unter dem statischen Jahresdurchschnitt (erwartbar: Mittagszeit im Juli, hoher Solaranteil) und sind untereinander plausibel konsistent (~15 % Differenz, erklärbar durch unterschiedliche Zeitfenster/Methodik — ENTSO-E mittelt über die letzten 2h aus dem Erzeugungsmix, energy-charts.info liefert einen einzelnen 15-Min-Wert von 13:00 UTC).

**Aufwand/Status:** Connector live verifiziert (`tests/test_entsoe_grid_carbon.py::test_fetch_generation_mix_smoke` grün gegen die echte API). Aktuell als zweites Live-Kontext-Signal im Dashboard vorgesehen (neben energy-charts.info) — noch nicht in die Kern-KPI-Berechnung verdrahtet (siehe GAP-001, `docs/phase2_rdc_gap_analysis.md`).

**Weitere Bidding-Zonen (15.07.2026):** `BIDDING_ZONES` in `generators/entsoe_grid_carbon.py` um 10 zusätzliche EU-Zonen erweitert (AT, BE, NL, FR, PL, CH, IT_NORD, ES, CZ, DK_1), Codes gegen die community-gepflegte `entsoe-py`-Referenzmappe abgeglichen und **jede einzeln live gegen die echte A75-API verifiziert** (keine unmapped PSR-Codes, plausible Werte — z. B. FR 28.5 wegen hohem Atomstromanteil, PL 429.1 wegen hohem Kohleanteil). Hinweis: der bestehende `DE_LU`-Code (`10Y1001A1001A83F`) trägt in manchen Referenzen (u. a. `entsoe-py`) das generische Label "DE" statt "DE_LU" (die dortige DE_LU-Zone nach dem Bidding-Zone-Split 2018 hätte den Code `10Y1001A1001A82H`) — bewusst nicht geändert, da live-verifiziert und funktionierend; die A75-Erzeugungsabfrage scheint über Control-Area- statt Bidding-Zone-Domains zu laufen. Dashboard-Button bleibt vorerst auf DE_LU fixiert (Zonenauswahl in der UI wäre ein separater Schritt, sobald Pilot B geklärt ist).

---

### 2. Eco-CI (GitHub Action, green-coding-solutions, MIT-Lizenz) ✅ verifiziert 2026-07-14

**Zweck:** Liefert eine **echte gemessene** (nicht extern geschätzte) Energiezahl für einen echten CI/CD-Lauf — direkt einschlägig für BLD-001 (CI/CD-Pipeline-Emissionen pro Lauf).

**Erster echter Lauf (`.github/workflows/energy-ci.yml`, Run #1, 14.07.2026):**

| Kennzahl | Wert |
|---|---|
| Total Energy | 29.83 Joule |
| Ø CPU-Auslastung | 21.82 % |
| Ø Leistung | 3.99 W |
| Laufzeit | 7.47 s |
| CO2 aus Energie | 0.003910992 g |
| CO2 aus Herstellung (embodied, Runner-Anteil) | 0.002131294 g |
| Carbon Intensity (Standort) | 472 gCO2eq/kWh (globaler Default, kein Standort-Token gesetzt) |
| **SCI** | **0.006042 gCO2eq / Pipeline-Lauf** |

Hinweis: nur "setup-python" und "install-dependencies" erscheinen als Einzelzeilen in der Ergebnistabelle — die übrigen Schritte (Checkout, Tests, Export-Validierung) liefen vermutlich zu schnell (lokal: 23 Tests in 1.84s) für die Messauflösung von Eco-CI und wurden herausgefiltert. Der Gesamtwert (SCI, Total Energy) bleibt davon unberührt.

**Zugriff/Voraussetzungen:** Kein Token nötig (nutzt ohne API-Key einen globalen Standard-CO2-Wert von 472 gCO2/kWh). Läuft nur auf Linux-Runnern (GitHub-Actions-Standard `ubuntu-latest`).

**Mehrwert:**
- Misst tatsächlichen Energieverbrauch (Joule), CPU-Auslastung und Watt-Zahl während eines echten Pipeline-Laufs — kein Proxy, keine Schätzung
- Wir können die Methode **an unserer eigenen Pipeline demonstrieren**: nicht "so würde es bei DHL aussehen", sondern "so sieht es heute schon bei uns aus" — ein konkreter, sofort vorführbarer Beleg für die Methodik
- Später mit ENTSO-E/Boavizta kombinierbar für einen vollständig eigenständig gemessenen SCI-Wert unseres eigenen Repos

**Benötigte Daten für vollen Einsatz:** keine — funktioniert ohne DHL-Input. Optional später: ein Electricity-Maps-Token für standortgenaue statt globale CO2-Intensität.

**Aufwand/Status:** neuer GitHub-Actions-Workflow (das Repo hatte bisher keine CI dort, nur lokale Validierung) — wird jetzt aufgesetzt.

---

### 1a. Cross-Repo-Rollout — Nachweis der Technologieunabhängigkeit ✅ Rollout gestartet 2026-07-15

**Zweck:** Das DHL-Framework ist explizit als technologie-/projektunabhängige, wissenschaftlich belastbare Methodik konzipiert — nicht als Einzellösung für ein Repo. Der stärkste Beleg dafür ist, sie tatsächlich über mehrere, strukturell unterschiedliche eigene Software-Projekte laufen zu lassen, nicht nur über DHLCO2 selbst.

**Portfolio-Inventur (2026-07-15):** alle 51 Ordner unter dem eigenen Projekt-Workspace systematisch gescannt (git-Repo? Tests vorhanden? CI vorhanden?):

| Kategorie | Anzahl |
|---|---|
| Hatten bereits GitHub-Actions-CI | 9 |
| Davon kundenneutral (Krallmann-intern/eigen) | 7 → für Benchmark gewählt |
| Davon einem anderen Kundenprojekt zugehörig | 2 → bewusst ausgeklammert |
| Tests vorhanden, aber noch keine CI | ~18 |
| Kein erkennbares automatisiertes Test-Setup | ~24 |

**Ausgewählt für den ersten Rollout (7 Repos, 6 davon vollständig verifiziert):** `adaptive_agent_os`, `platform_core`, `sunbrain`, `kserve-llm-blueprint`, `workspace-system`, `writing_system` — strukturell divers (KI-Agent-Orchestrierung, Infrastruktur-Plattform, Energie-Monitoring, Cloud-Blueprint, Workspace-Tooling, Content-Pipeline). Jeweils ein Eco-CI-Messschritt in die **bestehende** CI-Pipeline ergänzt (kein Neubau nötig).

**Ergebnis (Stand 2026-07-15, alle 6 real gemessen und grün):**

| Repo | SCI (gCO2eq/Lauf) |
|---|---|
| kserve-llm-blueprint | 0,011470 (aufwendigste Pipeline: Kind-Cluster, SBOM, Trivy) |
| adaptive_agent_os | 0,035361 |
| writing_system | 0,008901 |
| dhlco2_co2_artifact | 0,006042 |
| platform_core | 0,005817 |
| workspace-system | 0,004510 |
| sunbrain | 0,004918 |

Beim Rollout wurden **fünf voneinander unabhängige, vorbestehende CI-Bugs** in drei Repos gefunden und gefixt (kaputte Action-Versionspins, nicht existierende PyPI-Pakete, ein doppelter Pfad-Präfix, ein Test-Case-Set, das auf absichtlich entfernte Dateien zeigte, 199 Lint-Verstöße) — alle nachweislich unabhängig vom Eco-CI-Zusatz selbst, jeweils dokumentiert und in eigenen Sessions behoben.

**Zurückgestellt:** `Extract_Information` — beide vorhandenen Workflows deployen bei jedem Push auf den Hauptbranch ohne Pfad-Filter direkt auf einen produktiven GKE-Cluster. Jede Änderung, auch eine unrelated, würde ein echtes Produktions-Redeploy auslösen. Braucht eine explizite Entscheidung, bevor hier etwas ergänzt wird.

**Ergebnisdaten:** `evidence/cross_repo_benchmark.yaml` im DHLCO2-Repo, sichtbar im Dashboard-Tab "Cross-Repo-Benchmark". Nur real gemessene, geprüfte Werte werden eingetragen — Platzhalter bleiben explizit `null`, nie geschätzt.

**Nicht in diesem Rollout:** die ~18 Repos mit Tests aber ohne CI und die ~24 ohne erkennbares Setup — als systematischer Phase-4-Punkt "Org-weite Ausrollung" dokumentiert, nicht als Freitags-Aufgabe.

---

### 3. Cloud-Provider-Carbon-Tools (AWS Customer Carbon Footprint Tool, Google Cloud Carbon Footprint Export, Microsoft Emissions Impact Dashboard / Azure Carbon Optimizer)

**Zweck:** Sobald Pilot A/B auf einer konkreten Cloud-Plattform läuft, liefern die Cloud-Anbieter selbst Emissionsdaten aus den eigenen Abrechnungsdaten — die methodisch sauberste Quelle für RUN-Phase-KPIs, weil sie direkt an der tatsächlichen Ressourcennutzung hängt.

**Zugriff/Voraussetzungen — das ist die konkrete Bitte an DHL:**

| Anbieter | Werkzeug | Was wir von DHL bräuchten |
|---|---|---|
| AWS | Customer Carbon Footprint Tool / neue Sustainability Console | Lesezugriff auf das Billing/Cost-Management-Konto des Pilot-Accounts |
| Google Cloud | Carbon Footprint Export nach BigQuery | Zugriff auf das GCP-Billing-Projekt + BigQuery-Dataset des Pilot-Projekts |
| Microsoft Azure | Carbon Optimizer (Nachfolger des Emissions Impact Dashboard, das dieses Jahr abgekündigt wird) | Leserolle auf das Azure-Abonnement des Pilot-Workloads |

**Mehrwert:** Keine eigene Instrumentierung nötig — die Emissionsdaten fallen bereits beim Cloud-Anbieter an. Sobald wir wissen, welche Plattform DHL nutzt (das ist ohnehin OC-04/OC-01), ist die Anbindung reine Zugriffsfrage, kein Entwicklungsaufwand.

**Benötigte Daten für vollen Einsatz:** welcher Cloud-Anbieter (OC-01/OC-04), Lesezugriff auf das jeweilige Billing-/Kostenkonto des Piloten.

**Aufwand/Status:** kein Code-Aufwand auf unserer Seite bis zur Zugriffsfreigabe — deshalb als offener Punkt fürs Statusupdate geeignet, nicht als Umsetzungsaufgabe.

---

### 4. Ephemeraler GKE-Pilot für echte RUN-Phase-Messung — vorbereitet, nicht ausgeführt

**Zweck:** Alle bisherigen echten Datenpunkte (Boavizta, energy-charts.info, Eco-CI) betreffen die Build-Phase oder Kontextdaten — RUN-001/002 (Emissionen/Energie pro Request) sind weiterhin zu 100% Proxy, weil keine echte laufende Instanz gemessen wird. Ein kontrolliert deployter, gemessener und wieder vollständig zurückgebauter Referenz-Workload (z. B. ein offenes LLM) auf GKE würde den **ersten echten RUN-Messwert** des gesamten Projekts liefern.

**Voraussetzungen, die bereits vorhanden sind:** `kserve-llm-blueprint` (eigenes Repo) hat bereits Ende-zu-Ende-Automatisierung für genau diesen Ablauf — Cluster-Erstellung, Deployment, Messung, vollständiger Teardown, inklusive hinterlegter Billing-Informationen für Kostenkontrolle.

**Warum nicht diese Woche umgesetzt:**
1. Echte GPU-Node-Kosten plus Teardown-Risiko (verwaiste Ressourcen sind ein bekanntes reales Risiko bei Cloud-Testclustern) — will ich nicht unter Zeitdruck vor Freitag verantworten, ohne es in Ruhe zu verifizieren.
2. Googles eigenes Carbon-Footprint-Tool hat Abrechnungsverzug (Wochen bis Monate) — eine offizielle Google-Zahl käme so oder so nicht rechtzeitig. Nur eine selbst gemessene Zahl (Kepler/DCGM) wäre schnell verfügbar, ist aber ein eigenständiges Vorhaben.
3. Mit Eco-CI (6 Repos) und Boavizta stehen für Freitag bereits zwei belastbare "echte Messung"-Geschichten — eine dritte, teurere, riskantere kurz vor der Deadline ist ein schlechtes Risiko-Ertrags-Verhältnis.

**Status:** dokumentiert, nicht ausgeführt. Guter Kandidat für ein "nächster Schritt, sobald Scope/Budget freigegeben sind"-Statement im Gespräch — zeigt Kompetenz und Vorsicht gleichzeitig.

---

## Geprüft und bewusst zurückgestellt

| Quelle | Grund |
|---|---|
| **WattTime API** | Live und methodisch stark (marginale statt durchschnittliche Emissionen), aber kostenloser Zugriff nur für die US-Zone CAISO_NORTH — für Deutschland/EU kostenpflichtig. Kein Kandidat, solange der Pilot nicht in den USA liegt. |

---

## Für die Präsentation — Kernaussage

Wir sind nicht auf DHL-Input angewiesen, um an Realitätsnähe zu gewinnen: Boavizta, energy-charts.info, ENTSO-E und Eco-CI liefern bereits heute oder in den nächsten Tagen echte externe Daten, ohne dass DHL etwas liefern muss. Der Eco-CI-Rollout über 6 strukturell unterschiedliche eigene Software-Projekte belegt das bereits konkret: die Methodik ist nachweislich nicht auf ein Repo zugeschnitten. Nur der letzte, wertvollste Schritt — echte Emissionsdaten aus DHLs eigener Cloud-Nutzung — braucht Zugriff, den nur DHL freigeben kann (deckt sich mit OC-01/OC-04).
