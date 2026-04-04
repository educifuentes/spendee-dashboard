import os
import pandas as pd

def build_global_model_registry(root_path="models"):
    """
    Recursively scans a multi-schema directory structure and produces a Pandas DataFrame
    acting as a searchable catalog of all models.
    """
    records = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Ignore Python cache directories
        if "__pycache__" in dirnames:
            dirnames.remove("__pycache__")
            
        rel_path = os.path.relpath(dirpath, root_path)
        if rel_path == ".":
            continue
            
        path_parts = rel_path.split(os.sep)
        
        if len(path_parts) >= 1:
            stage = path_parts[0]
            
            # If there's a subfolder, it's the schema. Otherwise, assume 'core'.
            schema = path_parts[1] if len(path_parts) >= 2 else "core"
            
            for file in filenames:
                if file == "__init__.py" or not file.endswith(".py"):
                    continue
                    
                model_name_full = file[:-3] # Strip .py
                
                # The url points to the model_details page
                link = f"model_details?model={model_name_full}"
                
                records.append({
                    "schema": schema,
                    "stage": stage,
                    "model": model_name_full,
                    "link": link
                })
                
    # Return empty DataFrame with columns if no records
    if not records:
        return pd.DataFrame(columns=["schema", "stage", "model", "link"])

    # sort by model
    df = pd.DataFrame(records)
    df = df.sort_values(by="model", ascending=False)
        
    return df
