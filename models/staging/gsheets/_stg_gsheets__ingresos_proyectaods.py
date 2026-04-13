from helpers.data_connections.connect_gsheets import load_data_gsheets
from helpers.yaml_loader import get_table_config

def stg_gsheets__ingresos_proyectados():
    # Load configuration from YAML
    table_config = get_table_config(
        source_name="Ingresos Proyectados",
        table_name="ingresos_proyectados",
        yaml_path="models/sources/_src_gheets.yml"
    )
    
    if not table_config:
        raise ValueError("Configuration for table 'ingresos_proyectados' not found in _src_gheets.yml")
    
    worksheet = table_config.get("worksheet")
    
    df = load_data_gsheets(worksheet=worksheet)
    return df

