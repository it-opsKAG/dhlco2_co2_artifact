# Lifecycle Mapping

## Lifecycle Steps

| ID | Step |
| --- | --- |
| STEP-01 | Plan |
| STEP-02 | Code |
| STEP-03 | Build |
| STEP-04 | Test |
| STEP-05 | Release |
| STEP-06 | Deploy |
| STEP-07 | Operate |
| STEP-08 | Monitor |

## KPI to Lifecycle Mapping

| ID | KPI ID | Primary Step | Secondary Steps | Direct/Indirect | Source Refs |
| --- | --- | --- | --- | --- | --- |
| MAP-001 | BLD-001 | Build | Test | direct | DHLCO2-10; Offer para 45; Offer para 64 |
| MAP-002 | BLD-002 | Test | Build | direct | DHLCO2-10; Offer para 45; Offer para 64 |
| MAP-003 | BLD-003 | Build | Release | mixed | DHLCO2-10; Offer para 45; Offer para 64 |
| MAP-004 | BLD-004 | Build | Test | mixed | DHLCO2-10; Offer para 45; Offer para 64 |
| MAP-005 | BLD-005 | Plan | Build | indirect | DHLCO2-10; DHLCO2-4; Offer para 45; Offer para 64 |
| MAP-006 | RUN-001 | Operate | Monitor | mixed | DHLCO2-11; Offer para 46; Offer para 64 |
| MAP-007 | RUN-002 | Operate | Monitor | direct | DHLCO2-11; Offer para 46; Offer para 64 |
| MAP-008 | RUN-003 | Deploy | Operate | direct | DHLCO2-11; Offer para 46; Offer para 64 |
| MAP-009 | RUN-004 | Monitor | Operate | direct | DHLCO2-11; Offer para 46; Offer para 64 |
