# Hardware-PCF und Inventarerfassung

## Ziel

Die Hardware-Erfassung reduziert die Unsicherheit im Embodied-Carbon-Term `M` der SCI-Formel. Ohne DHL-Inventar bleibt HW-001 ein Proxywert.

## Datenpriorität

| Priorität | Quelle | Verwendung | Unsicherheit |
|---|---|---|---|
| 1 | Vendor Product Carbon Footprint oder Supplier EPD | bevorzugter Eingabewert für `embodied_co2_kg` | niedrig bis mittel |
| 2 | öffentliche LCA-Datenbank oder Hersteller-Nachhaltigkeitsbericht | Ersatzwert bei fehlendem PCF | mittel |
| 3 | TDP-Proxy aus PRX-003 | Fallback für Demonstration | hoch, ca. +/-50 % |

## Pflichtfelder

Die Vorlage liegt in `data/hardware_inventory_template.yaml`. Für jeden Pilot-Asset werden mindestens benötigt:

- `asset_id`
- `hardware_type`
- `vendor`
- `model`
- `tdp_w`
- `embodied_co2_kg`
- `pcf_source`
- `lifetime_months`
- `request_allocation_basis`

## Bewertungsregel

Ein KPI-Wert darf erst als beobachtbar oder auditnah gelten, wenn `embodied_co2_kg`, Nutzungsdauer, Servicegrenze und Request-Allokation dokumentiert sind. Fehlt mindestens eine dieser Angaben, bleibt der Wert proxybasiert.
