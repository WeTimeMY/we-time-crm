import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(page_title="We Time CRM", layout="wide")
st.title("🎬 We Time Private Movie Cafe - CRM System")

# File paths
CUSTOMERS_FILE = "customers.csv"
TRANSACTIONS_FILE = "transactions.csv"

# ================== SAFE DATA LOADING ==================
def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        try:
            df = pd.read_csv(CUSTOMERS_FILE)
            # Force phone and name to string
            df['phone'] = df['phone'].astype(str).str.strip()
            df['name'] = df['name'].astype(str).str.strip()
            if 'email' in df.columns:
                df['email'] = df['email'].astype(str).str.strip()
            # Convert birthday safely
            if 'birthday' in df.columns:
                df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce').dt.date
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()
    else:
        # Create empty dataframe with correct columns
        return pd.DataFrame(columns=['customer_id', 'name', 'phone', 'email', 'birthday', 
                                     'join_date', 'total_points', 'sign_up_voucher_used'])

def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        try:
            return pd.read_csv(TRANSACTIONS_FILE)
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame(columns=['date', 'customer_id', 'type', 'amount', 'points', 
                                     'outlet', 'notes', 'voucher_used'])

customers = load_customers()
transactions = load_transactions()

outlets = ["Austin Crest", "Eco Botanic"]

# Sidebar
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
            
            st.success(f"✅ Customer ID **{new_id}** registered successfully at {outlet}! RM10 Sign-up Voucher Issued.")
        else:
            st.error("❌ Name and Phone Number are required!")

# ================== RECORD SPENDING (Fixed) ==================
elif menu == "💰 Record Spending":
    st.subheader("Record Spending / Visit")
    
    phone_input = st.text_input("Enter Customer Phone Number")
    
    if phone_input:
        # Safe string search
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        
        if not matching.empty:
            customer = matching.iloc[0]
            st.success(f"✅ Found: **{customer['name']}** (ID: {customer['customer_id']})")
            
            amount = st.number_input("Spending Amount (RM)", min_value=0.0, step=1.0)
            outlet = st.selectbox("Outlet", outlets)
            notes = st.text_input("Notes (e.g. Movie Package, Table No.)")
            
            if st.button("Record Spending & Add Points", type="primary"):
                points = int(amount)
                
                idx = customers[customers['customer_id'] == customer['customer_id']].index[0]
                customers.at[idx, 'total_points'] += points
                customers.to_csv(CUSTOMERS_FILE, index=False)
                
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
                
                st.success(f"✅ RM{amount} recorded at **{outlet}** → +{points} points!")
        else:
            st.error("❌ Customer not found with this phone number.")

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
            st.warning("No matching customer found.")

# ================== VOUCHERS ==================
elif menu == "🎟️ Vouchers":
    st.subheader("Issue Birthday Voucher (RM20)")
    phone_input = st.text_input("Customer Phone Number")
    if phone_input and st.button("Issue RM20 Birthday Voucher"):
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            st.success(f"✅ RM20 Birthday Voucher issued to **{matching.iloc[0]['name']}**")
        else:
            st.error("Customer not found.")

# ================== REPORTS ==================
elif menu == "📊 Reports":
    st.subheader("All Customers")
    if not customers.empty:
        st.dataframe(customers, use_container_width=True)
        csv = customers.to_csv(index=False).encode('utf-8')
        st.download_button("Download Customer List", csv, "we_time_customers.csv", "text/csv")
    else:
        st.info("No customers yet.")

st.sidebar.info("""
**We Time CRM v1.3**
• 1 Point = RM1
• Sign-up: RM10
• Birthday: RM20
• Outlets: Austin Crest & Eco Botanic
""")
