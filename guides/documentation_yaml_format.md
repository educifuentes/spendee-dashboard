# YAML Documentation Structure

Although models run natively in python, metadata configuration for columns, descriptive labels, and schema tracking is powered by declarative `.yml` files alongside your scripts.

## Format Example (`model_name.yml`)
```yaml
version: 2

models:
  - name: my_python_model
    description: A comprehensive dimension resolving customer lifetimes.
    columns:
      - name: id
        description: Primary Key
      - name: email
        description: Scrubbed user email or domain.
```

Whenever writing a `.py` file, prefer writing the complementary `.yml` document strictly detailing structural components.
