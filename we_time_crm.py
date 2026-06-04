import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os

st.set_page_config(page_title="We Time CRM", layout="wide")
st.title("🎬 We Time Private Movie Cafe - CRM System")

st.sidebar.info("**Data Recovery Mode**")

# File paths
CUSTOMERS_FILE = "customers.csv"
TRANSACTIONS_FILE = "transactions.csv"

def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        try:
            df = pd.read_csv(CUSTOMERS_FILE)
            st.success(f"✅ Loaded {len(df)} customers from file")
            return df
        except Exception as e:
            st.error(f"Error loading customers: {e}")
            return pd.DataFrame()
    else:
        st.warning("customers.csv file not found.")
        return pd.DataFrame()

def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        try:
            df = pd.read_csv(TRANSACTIONS_FILE)
            st.success(f"✅ Loaded {len(df)} transactions")
            return df
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

customers = load_customers()
transactions = load_transactions()

st.write(f"**Total Customers in system:** {len(customers)}")

if not customers.empty:
    st.dataframe(customers.head(10), use_container_width=True)
else:
    st.error("No customer data found. Your previous data may have been lost during updates.")

st.info("If your data is gone, we may need to restore from backup or you may need to re-register customers.")

# Simple menu for now
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Record Spending", "Birthday Notifications"])

if menu == "Dashboard":
    st.header("Dashboard")
    st.metric("Customers", len(customers))
    
if menu == "Record Spending":
    st.subheader("Record Spending - Test")
    st.info("Test if the system is working.")

if menu == "Birthday Notifications":
    st.subheader("Birthday Notifications")
    st.info("Testing birthday section...")

st.sidebar.info("**Data Recovery Mode** - Please tell me how many customers you should have.")
