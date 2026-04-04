# Directory Structure Guidelines

This boilerplate project follows a modern data pipeline structure, loosely inspired by dbt layout paradigms but fully natively written in Python and Pandas. 

```text
models/
├── sources/          # Declarative YAMLs defining where the data initially resides.
├── staging/          # Light python wrappers / data cleaning (e.g. jaffle_shop, payments).
├── intermediate/     # Complex joins, aggregations not yet a full fact or dimension.
├── marts/            # The final business-ready tables (Fact/Dimension logic).
├── metrics/          # Semantic definitions of metrics, KPIs and calculations.
└── exposures/        # Final layer that directly serves a BI tool (e.g. Streamlit dashboard).
```

## Creating a new schema
When creating models for a new data schema (e.g. `ecommerce`, `marketing`), ensure that subdirectories exist per layer: `models/staging/ecommerce`, `models/marts/ecommerce`, etc., to enforce semantic boundaries.
