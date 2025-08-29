# ui/reports.py
import streamlit as st
import pandas as pd
from datetime import datetime

from core.analytics import (
    create_spending_pie_chart,
    create_income_expense_bar_chart,
    st_plotly_chart_safe,  # NEW: safe renderer
)

def _ensure_df():
    proj = st.session_state.get("selected_project")
    projects = st.session_state.get("projects", {})
    df = projects.get(proj) if proj in projects else None
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "category", "amount", "note"])
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["amount"] = pd.to_numeric(out["amount"], errors="coerce").fillna(0.0)
    out["category"] = out["category"].astype(str)
    return out.dropna(subset=["date"])

def _as_long_income_expense(df: pd.DataFrame) -> pd.DataFrame:
    """Map to a long form df with columns: date, amount, type."""
    if df.empty:
        return df
    # Income heuristic: category == 'Income' (case-insensitive). Adjust if you use another rule.
    df = df.copy()
    df["type"] = df["category"].str.strip().str.lower().eq("income").map({True: "Income", False: "Expense"})
    return df[["date", "amount", "type"]]

def _top_expense_by_category(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    exp = df[df["category"].str.strip().str.lower() != "income"]
    return (
        exp.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )

def render_reports_tab():
    st.subheader("Reports")

    df = _ensure_df()
    if df.empty:
        st.info("No data yet. Add transactions to see reports.")
        return

    col1, col2 = st.columns(2)

    # Spending by category (pie)
    with col1:
        cat_sum = _top_expense_by_category(df)
        fig = create_spending_pie_chart(cat_sum)
        st_plotly_chart_safe(fig)

    # Income vs Expense (bar)
    with col2:
        long_df = _as_long_income_expense(df)
        fig2 = create_income_expense_bar_chart(long_df)
        st_plotly_chart_safe(fig2)

    # Raw table (latest first) for transparency
    st.markdown("### Transactions (latest first)")
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
