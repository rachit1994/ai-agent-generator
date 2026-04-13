# Phase 1: Identity Resolution & Executive Graph

[← Phase 0](phase-00.md) | [Overview](00-overview.md) | [Phase 2 →](phase-02.md)

---

## Purpose

Maintain a single canonical identity for every executive, enabling accurate matching and deduplication.

## Teams

Data Engineering, CRM Operations.

## Tools

- HubSpot / Salesforce (core storage).
- Clay (enrichment workflows).
- Clearbit (firmographics).
- Apollo (contact verification).
- Neo4j (graph database).
- BigQuery (ETL pipelines).

## Process

```
Raw contacts ingestion (forms, APIs, referrals)
↓
Email normalization (standardization, hashing)
↓
Domain validation (company ownership checks)
↓
LinkedIn verification (profile scraping, role confirmation)
↓
Identity scoring (confidence model: 0–100)
↓
Canonical executive ID assignment (unique UUID)
```

## Deliverables

- Unified executive profiles (JSON exports).
- Deduplicated CRM (merge logs).
- Relationship graph nodes (initial edges from past interactions).

## Metrics

| Metric             | Target |
|--------------------|--------|
| Duplicate rate     | <1%    |
| Enrichment coverage| >95%   |

## Success Criteria

Graph accuracy >98%; enables 30% faster qualification.
