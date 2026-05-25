import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(page_title="We Time CRM", layout="wide")
st.title("🎬 We Time Private Movie Cafe - CRM System")

# File paths
CUSTOMERS_FILE = "customers.csv"
TRANSACTIONS_FILE = "transactions.csv"

# Load data
def load_data():
    if os.path.exists(CUSTOMERS_FILE):
        df = pd.read_csv(CUSTOMERS_FILE)
        df['birthday'] = pd.to_datetime(df['birthday']).dt.date
        return df
    else:
        return pd.DataFrame(columns=['customer_id', 'name', 'phone', 'email', 'birthday', 
                                     'join_date', 'total_points', 'sign_up_voucher_used'])

def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        return pd.read_csv(TRANSACTIONS_FILE)
    else:
        return pd.DataFrame(columns=['date', 'customer_id', 'type', 'amount', 'points', 
                                     'outlet', 'notes', 'voucher_used'])

customers = load_data()
transactions = load_transactions()

# Define Outlets
outlets = ["Austin Crest", "Eco Botanic"]

# Sidebar Menu
menu = st.sidebar.selectbox(
    "Main Menu", 
    ["🏠 Dashboard", "➕ Add New Customer", "💰 Record Spending", 
     "🔍 Search Customer", "🎟️ Vouchers", "📊 Reports"]
)

# ================== DASHBOARD ==================
if menu == "🏠 Dashboard":
    st.header("Welcome to We Time CRM")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", len(customers))
    col2.metric("Total Points Issued", int(customers['total_points'].sum()) if not customers.empty else 0)
    col3.metric("Active Outlets", len(outlets))

# ================== ADD NEW CUSTOMER ==================
elif menu == "➕ Add New Customer":
    st.subheader("Register New Customer")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *")
        phone = st.text_input("Phone Number *")
        email = st.text_input("Email (Optional)")
    with col2:
        birthday = st.date_input(
            "Birthday", 
            value=date(2000, 1, 1),
            min_value=date(1950, 1, 1),
            max_value=date.today()
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
            **Outlet:** {outlet}
            **RM10 Sign-up Voucher Issued (10 Points)**
            """)
        else:
            st.error("❌ Name and Phone Number are required!")

# ================== RECORD SPENDING ==================
elif menu == "💰 Record Spending":
    st.subheader("Record Spending / Visit")
    
    st.write("**Search Customer by Phone Number**")
    phone_input = st.text_input("Enter Customer Phone Number")
    
    if phone_input:
        matching = customers[customers['phone'].str.contains(phone_input, case=False, na=False)]
        
        if not matching.empty:
            customer = matching.iloc[0]
            st.success(f"✅ Found: **{customer['name']}** (ID: {customer['customer_id']})")
            
            amount = st.number_input("Spending Amount (RM)", min_value=0.0, step=1.0)
            outlet = st.selectbox("Outlet", outlets)
            notes = st.text_input("Notes (e.g. Movie Package, Table No.)")
            
            if st.button("Record Spending & Add Points", type="primary"):
                points = int(amount)
                
                # Update points
                idx = customers[customers['customer_id'] == customer['customer_id']].index[0]
                customers.at[idx, 'total_points'] += points
                customers.to_csv(CUSTOMERS_FILE, index=False)
                
                # Save transaction
                new_trans = pd.DataFrame([{
                    'date': str(datetime.now()),
                    'customer_id': customer['customer_id'],
                    'type': 'Spending',
                    'amount': amount,
                    'points': points,
                    'outlet': outlet,
                    'notes': notes,
                    'voucher_used': ''
                }])
                transactions = pd.concat([transactions, new_trans], ignore_index=True)
                transactions.to_csv(TRANSACTIONS_FILE, index=False)
                
                st.success(f"""
                🎉 **Transaction Recorded!**
                Customer: {customer['name']}
                Outlet: {outlet}
                Amount: RM{amount}
                Points Added: +{points}
                """)
        else:
            st.error("❌ Customer not found with this phone number.")
    else:
        st.info("Enter phone number to search")

# ================== SEARCH CUSTOMER ==================
elif menu == "🔍 Search Customer":
    st.subheader("Search Customer")
    search = st.text_input("Search by Name or Phone")
    
    if search:
        results = customers[
            customers['name'].str.contains(search, case=False, na=False) |
            customers['phone'].str.contains(search, case=False, na=False)
        ]
        if not results.empty:
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("No customer found")

# ================== VOUCHERS ==================
elif menu == "🎟️ Vouchers":
    st.subheader("Issue Birthday Voucher (RM20)")
    phone_input = st.text_input("Customer Phone Number")
    
    if phone_input and st.button("Issue RM20 Birthday Voucher"):
        matching = customers[customers['phone'].str.contains(phone_input, case=False, na=False)]
        if not matching.empty:
            cust = matching.iloc[0]
            st.success(f"✅ RM20 Birthday Voucher issued to **{cust['name']}**")
        else:
            st.error("Customer not found")

# ================== REPORTS ==================
elif menu == "📊 Reports":
    st.subheader("All Customers")
    if not customers.empty:
        st.dataframe(customers, use_container_width=True)
        
        csv = customers.to_csv(index=False).encode('utf-8')
        st.download_button("Download Customer List (CSV)", csv, "we_time_customers.csv", "text/csv")
    else:
        st.info("No customers yet")

# Sidebar Info
st.sidebar.info("""
**We Time CRM v1.1**
- 1 Point = RM1
- Sign-up: RM10 (10 points)
- Birthday: RM20 Voucher
- Outlets: Austin Crest & Eco Botanic
""")
