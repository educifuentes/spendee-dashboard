import json
from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

from models.exposures.spendee._exp_transactions import exp_transactions
from helpers.constants.budgets import BUDGETS, SORT_ORDER
from helpers.constants.category_and_label_colors import CATEGORY_COLORS

# ==========================================
# Helpers & Data Loaders
# ==========================================
@st.cache_data(ttl=600)
def load_all_transactions():
    """Load exposure transactions and ensure datetime and universal amount."""
    df = exp_transactions()
    if df.empty:
        return df
    
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["year"] = df["date"].dt.year
        df["month_num"] = df["date"].dt.month
        df["month_str"] = df["date"].dt.strftime("%Y-%m")
        df["month_name"] = df["date"].dt.strftime("%b")
    
    # Ensure amount_universal_clp exists
    if "amount_universal_clp" not in df.columns:
        df["amount_universal_clp"] = df["amount"].abs()
    else:
        df["amount_universal_clp"] = df["amount_universal_clp"].abs()
        
    # Budget classification
    df["budget_group"] = df["category"].map(BUDGETS).fillna("Otros")
    return df


def load_category_targets():
    """Load category targets from JSON and normalize keys."""
    targets_path = Path(__file__).parent.parent.parent / "helpers" / "constants" / "category_targets.json"
    if targets_path.exists():
        try:
            with open(targets_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                return {str(k).strip(): float(v) for k, v in raw.items()}
        except Exception:
            return {}
    return {}


# Spanish month names map
MONTH_NAMES_ES = {
    1: "01 - Ene", 2: "02 - Feb", 3: "03 - Mar", 4: "04 - Abr",
    5: "05 - May", 6: "06 - Jun", 7: "07 - Jul", 8: "08 - Ago",
    9: "09 - Sep", 10: "10 - Oct", 11: "11 - Nov", 12: "12 - Dic"
}

# ==========================================
# Custom CSS for Premium Dashboard
# ==========================================
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f3f4f6;
        line-height: 1.2;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    .badge-ok {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-warn {
        background-color: rgba(234, 179, 8, 0.15);
        color: #facc15;
        border: 1px solid rgba(234, 179, 8, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-neutral {
        background-color: rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .insight-box {
        background: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
    .recommendation-box {
        background: rgba(30, 41, 59, 0.4);
        border-left: 4px solid #a855f7;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# Main App Flow
# ==========================================
raw_df = load_all_transactions()
category_targets = load_category_targets()

if raw_df.empty:
    st.error("No se encontraron transacciones en la base de datos.")
    st.stop()

# Header
st.title("📊 Análisis de Gastos por Categoría")
st.caption("Evolución mensual detallada, dispersión (mín/máx/promedio), cumplimiento de presupuesto e insights automáticos.")

# ------------------------------------------
# Filters
# ------------------------------------------
with st.container():
    c_year, c_wallet, c_budget = st.columns([1.2, 2, 2])
    
    available_years = sorted(raw_df["year"].dropna().unique().astype(int), reverse=True)
    default_year_idx = available_years.index(2026) if 2026 in available_years else 0
    
    with c_year:
        selected_year = st.selectbox("📅 Año", available_years, index=default_year_idx)
        
    # Filter dataset for selected year & expenses
    df_year = raw_df[(raw_df["year"] == selected_year) & (raw_df["type"] == "Expense")].copy()
    
    with c_wallet:
        all_wallets = sorted(raw_df["wallet"].dropna().unique().tolist())
        selected_wallets = st.multiselect("👛 Billeteras", all_wallets, default=all_wallets)
        
    with c_budget:
        budget_groups = ["Todos"] + sorted(list(set(BUDGETS.values())))
        selected_budget = st.selectbox("🏷️ Grupo de Presupuesto", budget_groups, index=0)

# Apply filters
filtered_df = df_year.copy()
if selected_wallets:
    filtered_df = filtered_df[filtered_df["wallet"].isin(selected_wallets)]
if selected_budget != "Todos":
    filtered_df = filtered_df[filtered_df["budget_group"] == selected_budget]

if filtered_df.empty:
    st.warning("No hay transacciones de gasto para los filtros seleccionados.")
    st.stop()

# ------------------------------------------
# Pivot Table Data Preparation
# ------------------------------------------
filtered_df["month_label"] = filtered_df["month_num"].map(MONTH_NAMES_ES)
distinct_months = sorted(filtered_df["month_num"].unique().tolist())
distinct_month_labels = [MONTH_NAMES_ES[m] for m in distinct_months]
num_months = max(len(distinct_months), 1)

# Pivot sum of expenses
pivot_raw = filtered_df.pivot_table(
    index="category",
    columns="month_label",
    values="amount_universal_clp",
    aggfunc="sum",
    fill_value=0.0
)

# Ensure columns are sorted by month
ordered_cols = [MONTH_NAMES_ES[m] for m in distinct_months if MONTH_NAMES_ES[m] in pivot_raw.columns]
pivot_df = pivot_raw[ordered_cols].copy()

# Add Statistical Columns
pivot_df["Total Anual"] = pivot_df[ordered_cols].sum(axis=1)
pivot_df["Promedio Mes"] = pivot_df[ordered_cols].mean(axis=1)
pivot_df["Mínimo Mes"] = pivot_df[ordered_cols].min(axis=1)
pivot_df["Máximo Mes"] = pivot_df[ordered_cols].max(axis=1)

total_year_spend = pivot_df["Total Anual"].sum()
pivot_df["% del Total"] = (pivot_df["Total Anual"] / total_year_spend * 100).round(1)

# Map budget group and target
pivot_df["Grupo Presupuesto"] = [BUDGETS.get(cat.strip(), "Otros") for cat in pivot_df.index]
pivot_df["Target Mensual"] = [category_targets.get(cat.strip(), 0.0) for cat in pivot_df.index]

# Sort by Total Anual descending
pivot_df = pivot_df.sort_values(by="Total Anual", ascending=False)

# ------------------------------------------
# High Level KPI Cards
# ------------------------------------------
top_cat_name = pivot_df.index[0] if len(pivot_df) > 0 else "N/A"
top_cat_amount = pivot_df["Total Anual"].iloc[0] if len(pivot_df) > 0 else 0
top_cat_share = pivot_df["% del Total"].iloc[0] if len(pivot_df) > 0 else 0
avg_monthly_total = total_year_spend / num_months

# Count budget compliance
cats_with_target = pivot_df[pivot_df["Target Mensual"] > 0]
compliant_cats = cats_with_target[cats_with_target["Promedio Mes"] <= cats_with_target["Target Mensual"]]
compliance_rate = (len(compliant_cats) / len(cats_with_target) * 100) if len(cats_with_target) > 0 else 0

st.markdown("---")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">💸 Gasto Total ({selected_year})</div>
        <div class="metric-value">${total_year_spend:,.0f}</div>
        <div class="metric-subtitle">Acumulado en {num_months} mes(es) con datos</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">📅 Promedio Mensual Total</div>
        <div class="metric-value">${avg_monthly_total:,.0f}</div>
        <div class="metric-subtitle">Gasto medio mensual consolidado</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">👑 Categoría Principal</div>
        <div class="metric-value">{top_cat_name}</div>
        <div class="metric-subtitle">${top_cat_amount:,.0f} ({top_cat_share}% del total)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    color_badge = "badge-ok" if compliance_rate >= 70 else "badge-warn" if compliance_rate >= 40 else "badge-danger"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🎯 Cumplimiento de Metas</div>
        <div class="metric-value">{compliance_rate:.0f}%</div>
        <div class="metric-subtitle"><span class="{color_badge}">{len(compliant_cats)} de {len(cats_with_target)} categorías en meta</span></div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# Tabs Section
# ------------------------------------------
tab_table, tab_compliance, tab_insights, tab_charts, tab_drilldown = st.tabs([
    "📋 Tabla de Gastos por Mes",
    "🎯 Cumplimiento de Presupuestos",
    "💡 Insights & Sugerencias",
    "📈 Gráficos Comparativos",
    "🔍 Detalle de Transacciones"
])

# ==========================================
# TAB 1: Monthly Pivot Table
# ==========================================
with tab_table:
    st.subheader(f"Gasto Mensual por Categoría — Año {selected_year}")
    st.caption("Valores expresados en CLP universal. Incluye estadísticas de dispersión (Mínimo, Máximo, Promedio) y Total.")

    # Format Display DataFrame
    display_df = pivot_df.copy()
    
    # Calculate Totals Row
    totals_series = pd.Series(index=display_df.columns, dtype=object)
    for col in ordered_cols:
        totals_series[col] = display_df[col].sum()
    totals_series["Total Anual"] = display_df["Total Anual"].sum()
    totals_series["Promedio Mes"] = display_df["Promedio Mes"].sum()
    totals_series["Mínimo Mes"] = display_df[ordered_cols].sum().min()
    totals_series["Máximo Mes"] = display_df[ordered_cols].sum().max()
    totals_series["% del Total"] = 100.0
    totals_series["Grupo Presupuesto"] = "TOTAL"
    totals_series["Target Mensual"] = display_df["Target Mensual"].sum()
    
    full_table = pd.concat([display_df, pd.DataFrame([totals_series], index=["TOTAL GENERAL"])])

    # Build Column Config for st.dataframe
    col_config = {
        "Grupo Presupuesto": st.column_config.TextColumn("Grupo", width="medium"),
        "Total Anual": st.column_config.NumberColumn("Total Anual", format="dollar", step=1),
        "Promedio Mes": st.column_config.NumberColumn("Promedio / Mes", format="dollar", step=1),
        "Mínimo Mes": st.column_config.NumberColumn("Mínimo", format="dollar", step=1),
        "Máximo Mes": st.column_config.NumberColumn("Máximo", format="dollar", step=1),
        "% del Total": st.column_config.ProgressColumn("% del Total", format="%.1f%%", min_value=0, max_value=100),
        "Target Mensual": st.column_config.NumberColumn("Target Mensual", format="dollar", step=1),
    }
    for col in ordered_cols:
        col_config[col] = st.column_config.NumberColumn(col, format="dollar", step=1)

    # Column ordering
    cols_to_show = ["Grupo Presupuesto"] + ordered_cols + ["Total Anual", "Promedio Mes", "Mínimo Mes", "Máximo Mes", "% del Total"]

    st.dataframe(
        full_table[cols_to_show],
        use_container_width=True,
        column_config=col_config,
        height=min(38 * len(full_table) + 50, 700)
    )

    # Download button
    csv_data = full_table[cols_to_show].to_csv().encode('utf-8')
    st.download_button(
        label="📥 Descargar Tabla en CSV",
        data=csv_data,
        file_name=f"gastos_categorias_{selected_year}.csv",
        mime="text/csv"
    )

# ==========================================
# TAB 2: Budget Compliance
# ==========================================
with tab_compliance:
    st.subheader(f"¿He cumplido con los presupuestos en {selected_year}?")
    st.markdown("Evaluación del **Gasto Promedio Mensual Real** frente al **Target Asignado** por categoría y grupo.")

    comp_df = pivot_df.copy()
    
    # Calculate compliance metrics
    comp_df["Diferencia"] = comp_df["Promedio Mes"] - comp_df["Target Mensual"]
    comp_df["% Cumplimiento"] = comp_df.apply(
        lambda r: (r["Promedio Mes"] / r["Target Mensual"] * 100) if r["Target Mensual"] > 0 else None,
        axis=1
    )
    
    def get_status(row):
        if row["Target Mensual"] == 0:
            return "⚪ Sin Meta"
        ratio = row["Promedio Mes"] / row["Target Mensual"]
        if ratio <= 1.0:
            return "🟢 Dentro de Presupuesto"
        elif ratio <= 1.15:
            return "🟡 Al Límite (+15%)"
        else:
            return "🔴 Sobrepresupuesto"

    comp_df["Estado"] = comp_df.apply(get_status, axis=1)

    # Summary by Status
    st1, st2, st3, st4 = st.columns(4)
    with st1:
        ok_count = len(comp_df[comp_df["Estado"] == "🟢 Dentro de Presupuesto"])
        st.metric("🟢 En Presupuesto", f"{ok_count} categorías")
    with st2:
        warn_count = len(comp_df[comp_df["Estado"] == "🟡 Al Límite (+15%)"])
        st.metric("🟡 Al Límite", f"{warn_count} categorías")
    with st3:
        danger_count = len(comp_df[comp_df["Estado"] == "🔴 Sobrepresupuesto"])
        st.metric("🔴 Excedidas", f"{danger_count} categorías")
    with st4:
        no_target_count = len(comp_df[comp_df["Estado"] == "⚪ Sin Meta"])
        st.metric("⚪ Sin Meta Definida", f"{no_target_count} categorías")

    st.markdown("---")
    
    # Group Breakdown
    st.markdown("#### Desempeño por Grupo de Presupuesto")
    group_summary = comp_df.groupby("Grupo Presupuesto").agg(
        Gasto_Total=("Total Anual", "sum"),
        Promedio_Mes=("Promedio Mes", "sum"),
        Target_Total=("Target Mensual", "sum"),
        Categorias=("Total Anual", "count")
    ).reset_index()
    
    group_summary["Diferencia"] = group_summary["Promedio_Mes"] - group_summary["Target_Total"]
    group_summary["% Uso"] = group_summary.apply(
        lambda r: (r["Promedio_Mes"] / r["Target_Total"] * 100) if r["Target_Total"] > 0 else 0, axis=1
    )
    
    st.dataframe(
        group_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Grupo Presupuesto": st.column_config.TextColumn("Grupo"),
            "Gasto_Total": st.column_config.NumberColumn("Total Anual", format="dollar", step=1),
            "Promedio_Mes": st.column_config.NumberColumn("Promedio Mensual Real", format="dollar", step=1),
            "Target_Total": st.column_config.NumberColumn("Target Mensual Asignado", format="dollar", step=1),
            "Diferencia": st.column_config.NumberColumn("Diferencia (+/-)", format="dollar", step=1),
            "% Uso": st.column_config.ProgressColumn("% Uso Target", format="%.0f%%", min_value=0, max_value=200),
            "Categorias": st.column_config.NumberColumn("N° Categorías", step=1)
        }
    )

    st.markdown("#### Detalle por Categoría vs Target")
    
    # Show comparison table
    comp_display = comp_df[["Grupo Presupuesto", "Promedio Mes", "Target Mensual", "Diferencia", "% Cumplimiento", "Estado"]].copy()
    
    st.dataframe(
        comp_display,
        use_container_width=True,
        column_config={
            "Grupo Presupuesto": st.column_config.TextColumn("Grupo"),
            "Promedio Mes": st.column_config.NumberColumn("Promedio Real / Mes", format="dollar", step=1),
            "Target Mensual": st.column_config.NumberColumn("Meta / Mes", format="dollar", step=1),
            "Diferencia": st.column_config.NumberColumn("Diferencia Mensual", format="dollar", step=1),
            "% Cumplimiento": st.column_config.NumberColumn("% Gasto vs Meta", format="%.0f%%"),
            "Estado": st.column_config.TextColumn("Estado Presupuestario")
        }
    )

# ==========================================
# TAB 3: Insights & Suggestions
# ==========================================
with tab_insights:
    st.subheader(f"💡 Insights Clave de tus Gastos {selected_year}")
    
    # 1. Top spend category
    top_cat = pivot_df.index[0]
    top_cat_tot = pivot_df.loc[top_cat, "Total Anual"]
    top_cat_avg = pivot_df.loc[top_cat, "Promedio Mes"]
    top_cat_share = pivot_df.loc[top_cat, "% del Total"]
    
    # 2. Peak month overall
    monthly_totals = pivot_df[ordered_cols].sum()
    peak_month = monthly_totals.idxmax()
    peak_month_val = monthly_totals.max()
    
    # Find what caused peak month
    peak_cat = pivot_df[peak_month].idxmax()
    peak_cat_val = pivot_df.loc[peak_cat, peak_month]
    
    # 3. Highest variance category (Max - Min)
    pivot_df["Volatilidad"] = pivot_df["Máximo Mes"] - pivot_df["Mínimo Mes"]
    volatile_cat = pivot_df.sort_values(by="Volatilidad", ascending=False).index[0]
    vol_max = pivot_df.loc[volatile_cat, "Máximo Mes"]
    vol_min = pivot_df.loc[volatile_cat, "Mínimo Mes"]
    vol_diff = pivot_df.loc[volatile_cat, "Volatilidad"]
    
    # 4. Top Over-Budget Categories
    exceeded_df = comp_df[comp_df["Diferencia"] > 0].sort_values(by="Diferencia", ascending=False)
    
    # 5. Top Under-Budget / Disciplined Categories
    disciplined_df = comp_df[(comp_df["Target Mensual"] > 0) & (comp_df["Diferencia"] <= 0)].sort_values(by="Diferencia")

    # Render Insight Cards
    ins_col1, ins_col2 = st.columns(2)
    
    with ins_col1:
        st.markdown(f"""
        <div class="insight-box">
            <h4>🏆 Categoría de Mayor Gasto</h4>
            <p>La categoría donde más gastas es <strong>{top_cat}</strong> con un total de <strong>${top_cat_tot:,.0f}</strong> (promedio de <strong>${top_cat_avg:,.0f}/mes</strong>), representando el <strong>{top_cat_share}%</strong> de todo tu gasto anual.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>📈 Mes Pico del Año</h4>
            <p>El mes con mayor gasto registrado fue <strong>{peak_month}</strong> con <strong>${peak_month_val:,.0f}</strong>. El principal impulsor de este mes fue <strong>{peak_cat}</strong> con <strong>${peak_cat_val:,.0f}</strong>.</p>
        </div>
        """, unsafe_allow_html=True)

    with ins_col2:
        st.markdown(f"""
        <div class="insight-box">
            <h4>⚡ Mayor Volatilidad de Gasto</h4>
            <p>La categoría con mayor variación mensual es <strong>{volatile_cat}</strong>, oscilando entre un mínimo de <strong>${vol_min:,.0f}</strong> y un pico de <strong>${vol_max:,.0f}</strong> (diferencia de <strong>${vol_diff:,.0f}</strong>).</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not disciplined_df.empty:
            best_cat = disciplined_df.index[0]
            best_avg = disciplined_df.loc[best_cat, "Promedio Mes"]
            best_tar = disciplined_df.loc[best_cat, "Target Mensual"]
            savings_monthly = best_tar - best_avg
            st.markdown(f"""
            <div class="insight-box">
                <h4>🛡️ Categoría Más Disciplinada</h4>
                <p>En <strong>{best_cat}</strong> has mantenido un gasto promedio de <strong>${best_avg:,.0f}/mes</strong> vs una meta de <strong>${best_tar:,.0f}/mes</strong>, ahorrando un margen de <strong>${savings_monthly:,.0f}/mes</strong>.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎯 Sugerencias & Recomendaciones Accionables")
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.markdown("""
        <div class="recommendation-box">
            <h4>1. 🛑 Control y Poda en Categorías "Chao Culpa"</h4>
            <p>Las categorías de estilo de vida y compras discrecionales como <strong>Shopping</strong> y <strong>Activities</strong> presentan desviaciones recurrentes respecto a sus metas originales de $30.000.
            <br><em>Sugerencia:</em> Establecer un tope semanal o transferir el monto de "Chao Culpa" a una cuenta prepago/secundaria al inicio de cada mes para limitar compras impulsivas.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="recommendation-box">
            <h4>2. 🔄 Recalibración de Presupuestos Desactualizados</h4>
            <p>Categorías como <strong>Transport</strong> (gasto real ~$95k vs meta $25k) y <strong>Education</strong> (gasto real ~$91k vs meta $30k) superan sistemáticamente el target.
            <br><em>Sugerencia:</em> Actualizar los valores en <code>category_targets.json</code> con valores más realistas basados en el promedio histórico para que el indicador de cumplimiento refleje metas alcanzables.</p>
        </div>
        """, unsafe_allow_html=True)

    with rec_col2:
        st.markdown("""
        <div class="recommendation-box">
            <h4>3. 🗓️ Aprovisionamiento para Gastos Lump-Sum</h4>
            <p>Gastos fuertes pero esporádicos como <strong>Insurance</strong> ($320k en abril) y <strong>Tax</strong> ($290k en enero) generan picos mensuales agresivos.
            <br><em>Sugerencia:</em> Dividir el costo anual de pólizas y tributos en cuotas mensuales equivalentes en la cuenta de <strong>Savings</strong> para amortiguar el impacto del flujo de caja cuando vence la prima.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="recommendation-box">
            <h4>4. 🔍 Auditoría Periódica de Subscripciones y Servicios</h4>
            <p>El gasto en <strong>Subscriptions</strong> e <strong>Utilities</strong> se mantiene controlado, pero presenta dispersión.
            <br><em>Sugerencia:</em> Revisar cada 6 meses servicios digitales no utilizados y optimizar planes familiares o anuales con descuento.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 4: Visual Charts
# ==========================================
with tab_charts:
    st.subheader(f"Visualizaciones de Gastos {selected_year}")
    
    # 1. Bar Chart: Real vs Target
    chart_comp_data = comp_df[comp_df["Target Mensual"] > 0].reset_index()
    if not chart_comp_data.empty:
        st.markdown("#### Gasto Promedio Mensual Real vs Presupuesto Target")
        
        melted_comp = pd.melt(
            chart_comp_data,
            id_vars=["category", "Grupo Presupuesto"],
            value_vars=["Promedio Mes", "Target Mensual"],
            var_name="Tipo",
            value_name="Monto"
        )
        
        comp_chart = (
            alt.Chart(melted_comp)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("category:N", title="Categoría", sort="-y"),
                y=alt.Y("Monto:Q", title="Monto Mensual (CLP)", axis=alt.Axis(format="~s")),
                color=alt.Color("Tipo:N", scale=alt.Scale(domain=["Promedio Mes", "Target Mensual"], range=["#3b82f6", "#10b981"])),
                xOffset="Tipo:N",
                tooltip=[
                    alt.Tooltip("category:N", title="Categoría"),
                    alt.Tooltip("Tipo:N", title="Tipo"),
                    alt.Tooltip("Monto:Q", format="$,.0f", title="Monto"),
                    alt.Tooltip("Grupo Presupuesto:N", title="Grupo")
                ]
            )
            .properties(height=380)
        )
        st.altair_chart(comp_chart, use_container_width=True)

    # 2. Monthly Trend Chart by Category
    st.markdown("#### Evolución Mensual por Categoría")
    monthly_cat_data = filtered_df.groupby(["month_label", "category", "budget_group"])["amount_universal_clp"].sum().reset_index()
    
    trend_chart = (
        alt.Chart(monthly_cat_data)
        .mark_bar()
        .encode(
            x=alt.X("month_label:N", title="Mes"),
            y=alt.Y("amount_universal_clp:Q", title="Gasto (CLP)", axis=alt.Axis(format="~s")),
            color=alt.Color("category:N", title="Categoría", scale=alt.Scale(
                domain=list(CATEGORY_COLORS.keys()),
                range=list(CATEGORY_COLORS.values())
            )),
            tooltip=[
                alt.Tooltip("month_label:N", title="Mes"),
                alt.Tooltip("category:N", title="Categoría"),
                alt.Tooltip("amount_universal_clp:Q", format="$,.0f", title="Gasto"),
                alt.Tooltip("budget_group:N", title="Grupo")
            ]
        )
        .properties(height=400)
    )
    st.altair_chart(trend_chart, use_container_width=True)

# ==========================================
# TAB 5: Drill-Down Transactions Explorer
# ==========================================
with tab_drilldown:
    st.subheader(f"Explorador de Transacciones — {selected_year}")
    st.caption("Filtra y analiza los movimientos específicos de cualquier categoría y mes.")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        cat_choices = ["Todas"] + sorted(filtered_df["category"].dropna().unique().tolist())
        drill_cat = st.selectbox("Filtrar Categoría", cat_choices, index=0)
    with col_f2:
        month_choices = ["Todos"] + distinct_month_labels
        drill_month = st.selectbox("Filtrar Mes", month_choices, index=0)
    with col_f3:
        search_kw = st.text_input("🔍 Buscar en notas o etiquetas", "")
        
    drill_df = filtered_df.copy()
    if drill_cat != "Todas":
        drill_df = drill_df[drill_df["category"] == drill_cat]
    if drill_month != "Todos":
        drill_df = drill_df[drill_df["month_label"] == drill_month]
    if search_kw:
        mask = drill_df["note"].fillna("").str.contains(search_kw, case=False) | drill_df["labels"].fillna("").str.contains(search_kw, case=False)
        drill_df = drill_df[mask]
        
    st.markdown(f"**Total movimientos encontrados:** {len(drill_df)} | **Suma:** ${drill_df['amount_universal_clp'].sum():,.0f}")
    
    st.dataframe(
        drill_df[["date", "category", "amount", "currency", "amount_universal_clp", "wallet", "note", "labels"]].sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
            "category": st.column_config.TextColumn("Categoría"),
            "amount": st.column_config.NumberColumn("Monto Original", format="%.2f"),
            "currency": st.column_config.TextColumn("Moneda"),
            "amount_universal_clp": st.column_config.NumberColumn("Monto CLP", format="dollar", step=1),
            "wallet": st.column_config.TextColumn("Billetera"),
            "note": st.column_config.TextColumn("Nota"),
            "labels": st.column_config.TextColumn("Etiquetas")
        }
    )
