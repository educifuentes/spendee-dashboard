import importlib
import inspect
import streamlit as st

from helpers.utilities.model_catalog import build_global_model_registry

def find_model(model_name):
    """
    Looks up a model by name in the global registry, dynamically imports it, 
    executes its primary function, and returns the resulting DataFrame.
    Returns None if the model cannot be found or executed.
    """
    if not model_name:
        return None
        
    # 1. Lookup the model schema and stage natively in the registry
    df_catalog = build_global_model_registry()
    model_row = df_catalog[df_catalog["model"] == model_name]
    
    if not model_row.empty:
        schema = model_row.iloc[0]["schema"]
        stage = model_row.iloc[0]["stage"]
        
        # 2. Build explicit module python path depending on if it has a schema folder
        if schema == "core":
            module_path = f"models.{stage}.{model_name}"
        else:
            module_path = f"models.{stage}.{schema}.{model_name}"
        
        try:
            # 3. Dynamically inject the raw module into execution scope
            module = importlib.import_module(module_path)
            
            # Find the primary internal function defined specifically within this module script (ignoring imports)
            model_func = None
            for name, member in inspect.getmembers(module, callable):
                # Ensure the member is defined in this module and is not a class
                if getattr(member, "__module__", "") == module.__name__ and not inspect.isclass(member):
                    model_func = member
                    break
                    
            if model_func:                
                # 4. Invoke it natively!
                df = model_func()
                return df
                
            else:
                st.error(f"Could not find any declared functions inside the script `{module_path}`")
                
        except Exception as e:
            st.error(f"Failed to execute dynamic model `{module_path}`: {e}")
            
    else:
        st.error(f"Model `{model_name}` could not be resolved from the current Model Registry.")
        
    return None
