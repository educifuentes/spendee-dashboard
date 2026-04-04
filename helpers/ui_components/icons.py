ICONS = {
    # branding
    "logo": "energy_program_saving",
    # core pages
    "home": "home",
    "catalog": "view_list",
    "documentation": "article",
    "projects": "rocket",
    "metrics": "calculate",
    "not_apply": "circle",
    "query": "query_stats",
    "lineage": "layers",
    # other pages
    "dashboard": "dashboard",
    "search": "search",
    "layers": "layers_clear",
    "settings": "settings_input_component",
    "database": "database",
    # validations   
    "check": "check_box",
    "warning": "warning",
    "close": "close",
    # models
    "clientes": "sports_bar",
    "censos": "checklist_rtl",
    "bases_ccu": "assignment",
    # dev data build
    "staging": "steppers",
    "intermediate": "factory",
    "marts": "rocket",
    "exposures": "bar_chart_4_bars",
}

def render_icon(icon_key: str) -> str:
    """
    Returns the streamlit material icon format for a given key.
    """
    icon_name = ICONS.get(icon_key, "help")
    return f":material/{icon_name}:"


# icons from https://fonts.google.com/icons