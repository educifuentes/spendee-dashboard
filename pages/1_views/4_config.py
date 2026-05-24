import streamlit as st

from helpers.ui_components.category_grid import render_category_grid
from helpers.constants.category_and_label_colors import (
    EXPENSES_CATEGORY_COLORS, INCOME_CATEGORY_COLORS, LABEL_COLORS
)


st.title("Configuración")

st.subheader("Category Colors")

render_category_grid(EXPENSES_CATEGORY_COLORS, INCOME_CATEGORY_COLORS)

st.subheader("Label Colors")

render_category_grid(LABEL_COLORS, {})
