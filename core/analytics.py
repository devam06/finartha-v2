# core/analytics.py
import streamlit as st
import pandas as pd

def _px():
    """Lazy import Plotly so missing dependency doesn't crash the whole app."""
    try:
        import plotly.express as px  # imported only when needed
        return px
    except Exception as e:
        st.session_state["_plotly_missing_reason"] = str(e)
        return None

def create_spending_pie_chart(df: pd.DataFrame):
    """
    Expects columns: category, amount (expenses only). Return a Plotly Figure or None.
    """
    px = _px()
    if px is None:
        st.error("Plotly is not installed. Add `plotly>=5.20` to requirements (or pyproject) and redeploy.")
        return None
    fig = px.pie(df, names="category", values="amount", hole=0.5, title="Spending by Category")
    fig.update_layout(legend_title=None)
    return fig

def create_income_expense_bar_chart(df_long: pd.DataFrame):
    """
    Expects long df with columns: date, amount, type ∈ {'Income','Expense'}.
    Return a Plotly Figure or None.
    """
    px = _px()
    if px is None:
        st.error("Plotly is not installed. Add `plotly>=5.20` to requirements (or pyproject) and redeploy.")
        return None
    fig = px.bar(df_long, x="date", y="amount", color="type", barmode="group", title="Income vs Expense")
    fig.update_layout(xaxis_title="", yaxis_title="Amount", legend_title=None)
    return fig

def st_plotly_chart_safe(fig, **kwargs):
    """Render a figure if present; otherwise show a gentle placeholder."""
    if fig is None:
        reason = st.session_state.get("_plotly_missing_reason")
        if reason:
            st.info(f"Chart unavailable because Plotly isn't installed ({reason}).")
        else:
            st.info("Chart unavailable.")
        return
    st.plotly_chart(fig, use_container_width=True, **kwargs)

