# Naming Conventions

Consistency across models enables the automatic `build_global_model_registry` catalog builder to accurately surface datasets to end-users. Always use standard prefixes.

## Prefixes
* **sources**: `_src_<schema>.yml`
* **staging**: `_stg_<schema>__<model>.py`
* **intermediate**: `_int_<schema>__<model>.py`
* **marts**: `_dim_<model>.py` (dimension), `_fct_<model>.py` (fact)
* **metrics**: `_metric_<name>.py`
* **exposures**: `_exp_<name>.py`

## Rules
- Model names should be written in `snake_case`.
- Prefixes like `_` denote internal models imported dynamically. 
- Python functions defining the dataset inside the `.py` file must match the filename precisely (excluding the prefixed underscore).
