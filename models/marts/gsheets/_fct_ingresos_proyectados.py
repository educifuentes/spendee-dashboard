from models.intermediate.gsheets._int_gsheets__ingresos_proyectados import int_gsheets__ingresos_proyectados

def fct_ingresos_proyectados():
    """
    Fact table for Ingresos Proyectados.
    Currently acts as a pass-through from the intermediate model.
    """
    df = int_gsheets__ingresos_proyectados()

    selected_columns = [
                "date",
                "area",
                "name",
                "cliente",
                "monto",
                "status",
                "nota"]

    df = df[selected_columns]
    
    return df
