import streamlit as st

from helpers.ui_components.category_grid import render_category_grid
from helpers.constants.category_colors import CATEGORY_COLORS, EXPENSES_CATEGORY_COLORS, INCOME_CATEGORY_COLORS


st.title("Configuración")

st.subheader("Category Colors")

render_category_grid(EXPENSES_CATEGORY_COLORS, INCOME_CATEGORY_COLORS)
