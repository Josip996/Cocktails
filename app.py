import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cocktail Bar", layout="wide")
st.title("🍹 Welcome to the Cocktail Party!")
st.subheader("Mix Your Senses")

# Jednostavne testne kvačice
c1, c2 = st.columns(2)
with c1:
    st.checkbox("Vodka")
    st.checkbox("Gin")
with c2:
    st.checkbox("Orange Juice")
    st.checkbox("Lemonade")

if st.button("Order Cocktail 🚀"):
    st.success("Order successfully sent to the Bar!")
