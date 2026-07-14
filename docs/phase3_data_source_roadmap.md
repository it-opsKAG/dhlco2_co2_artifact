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

### 1. ENTSO-E Transparency Platform — offizielle EU-Netzdaten

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

**Aufwand/Status:** Connector (XML-Parsing + Emissionsfaktor-Tabelle) wird vorbereitet, Test gegen dokumentiertes Antwortformat — Live-Verifikation folgt, sobald der Token vorliegt.

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

## Geprüft und bewusst zurückgestellt

| Quelle | Grund |
|---|---|
| **WattTime API** | Live und methodisch stark (marginale statt durchschnittliche Emissionen), aber kostenloser Zugriff nur für die US-Zone CAISO_NORTH — für Deutschland/EU kostenpflichtig. Kein Kandidat, solange der Pilot nicht in den USA liegt. |

---

## Für die Präsentation — Kernaussage

Wir sind nicht auf DHL-Input angewiesen, um an Realitätsnähe zu gewinnen: Boavizta, energy-charts.info, ENTSO-E und Eco-CI liefern bereits heute oder in den nächsten Tagen echte externe Daten, ohne dass DHL etwas liefern muss. Nur der letzte, wertvollste Schritt — echte Emissionsdaten aus DHLs eigener Cloud-Nutzung — braucht Zugriff, den nur DHL freigeben kann (deckt sich mit OC-01/OC-04).
