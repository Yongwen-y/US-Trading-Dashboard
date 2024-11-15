# Homepage

import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="US Trade Dashboard",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Page Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Trade Overview", "Product Focus", "Country Focus"])

if page == "Trade Overview":
    import demo
    demo.show_page()
elif page == "Product Focus":
    import product_focus
    product_focus.show_page()
elif page == "Country Focus":
    import app3
    app3.show_page()
