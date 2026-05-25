import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(page_title="We Time CRM", layout="wide")
st.title("🎬 We Time Private Movie Cafe - CRM System")

# File paths for saving data
CUSTOMERS_FILE = "customers.csv"
TRANSACTIONS_FILE = "transactions.csv"

# Load data
@st.cache_data
def load_data():
    if os.path.exists(CUSTOMERS_FILE):
        return pd.read_csv(CUSTOMERS_FILE)
    else:
        return pd.DataFrame(columns=['customer_id', 'name', 'phone', 'email', 'birthday', 'join_date', 'total_points', 'sign_up_voucher_used'])
    
@st.cache_data
def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        return pd.read_csv(TRANSACTIONS_FILE)
    else:
        return pd.DataFrame(columns=['date', 'customer_id', 'type', 'amount', 'points', 'outlet', 'notes', 'voucher_used'])

customers = load_data()
transactions = load_transactions()

# Sidebar
menu = st.sidebar.selectbox("Menu", ["🏠 Dashboard", "➕ Add Customer", "💰 Record Spending", "🔍 Search", "🎟️ Vouchers", "📊 Reports"])

# Define your outlets
outlets = ["Austin Crest", "Eco Botanic"]

if menu == "🏠 Dashboard":
    st.header("Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", len(customers))
    col2.metric("Total Points", int(customers['total_points'].sum()) if not customers.empty else 0)

# ================== ADD NEW CUSTOMER ==================
elif menu == "➕ Add Customer":
    st.subheader("Register New Customer")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *")
        phone = st.text_input("Phone Number *")
        email = st.text_input("Email (Optional)")
    with col2:
        # Fixed Birthday Picker - Allow years from 1950 to current year
        birthday = st.date_input(
            "Birthday", 
            value=date(2000, 1, 1),
            min_value=date(1950, 1, 1),   # Earliest year
            max_value=date.today()         # Cannot choose future date
        )
        outlet = st.selectbox("Registered At", outlets)
    
    if st.button("Register + Give RM10 Sign-up Voucher", type="primary"):
        if name and phone:
            new_id = 1000 + len(customers) + 1
            
            new_row = pd.DataFrame([{
                'customer_id': new_id,
                'name': name.strip(),
                'phone': phone.strip(),
                'email': email.strip() if email else "",
                'birthday': str(birthday),
                'join_date': str(date.today()),
                'total_points': 10,
                'sign_up_voucher_used': False
            }])
            
            customers = pd.concat([customers, new_row], ignore_index=True)
            customers.to_csv(CUSTOMERS_FILE, index=False)
            
            st.success(f"""
            🎉 **Customer Registered Successfully!**
            **Customer ID:** {new_id}
            **RM10 Sign-up Voucher Issued**
            """)
        else:
            st.error("❌ Name and Phone Number are required!")

# Record Spending
elif menu == "💰 Record Spending":
    st.subheader("Record Spending")
    cust_id = st.number_input("Customer ID", min_value=1001)
    amount = st.number_input("Amount (RM)", min_value=0.0)
    outlet = st.selectbox("Outlet", outlets)
    notes = st.text_input("Notes")
    
    if st.button("Record & Add Points"):
        if cust_id in customers['customer_id'].values:
            points = int(amount)
            idx = customers[customers['customer_id'] == cust_id].index[0]
            customers.at[idx, 'total_points'] += points
            customers.to_csv(CUSTOMERS_FILE, index=False)
            
            new_trans = pd.DataFrame([{
                'date': str(datetime.now()), 'customer_id': cust_id, 'type': 'Spending',
                'amount': amount, 'points': points, 'outlet': outlet, 'notes': notes, 'voucher_used': ''
            }])
            transactions = pd.concat([transactions, new_trans], ignore_index=True)
            transactions.to_csv(TRANSACTIONS_FILE, index=False)
            
            st.success(f"✅ RM{amount} recorded! +{points} points")
        else:
            st.error("Customer not found")

# Add other menus similarly...

st.sidebar.info("We Time CRM Online\n1 Point = RM1\nSign-up: RM10\nBirthday: RM20")
