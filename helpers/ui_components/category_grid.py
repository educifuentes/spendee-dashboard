import streamlit as st

def render_category_grid(expenses_colors, income_colors):
    """
    Renders a grid of category badges based on the provided colors dictionaries,
    separated into Expenses and Income tabs.
    """
    st.subheader("Categories")
    t_exp, t_inc = st.tabs(["Expenses", "Income"])
    
    def _draw_grid(colors_dict):
        cat_cols = st.columns(6)
        for i, category in enumerate(sorted(colors_dict.keys())):
            color = colors_dict[category]
            with cat_cols[i % 6]:
                st.markdown(
                    f"""
                    <div style="
                        background-color: {color}; 
                        padding: 6px; 
                        border-radius: 6px; 
                        text-align: center; 
                        margin-bottom: 8px; 
                        font-size: 12px; 
                        font-weight: 600; 
                        color: white; 
                        text-shadow: 0px 1px 2px rgba(0,0,0,0.5);
                        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
                    ">
                        {category}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

    with t_exp:
        _draw_grid(expenses_colors)
    with t_inc:
        _draw_grid(income_colors)
