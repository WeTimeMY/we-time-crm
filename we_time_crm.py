import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os

st.set_page_config(page_title="We Time CRM", layout="wide")
st.title("🎬 We Time Private Movie Cafe - CRM System")

# ================== ADMIN LOGIN ==================
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

PASSWORD = "wetimemanagement2026"   # ← CHANGE THIS TO YOUR SECURE PASSWORD

with st.sidebar:
    st.subheader("🔑 Admin Access")
    if not st.session_state.is_admin:
        admin_pass = st.text_input("Enter Admin Password", type="password")
        if st.button("Login as Admin"):
            if admin_pass == PASSWORD:
                st.session_state.is_admin = True
                st.success("✅ Admin Mode Activated")
            else:
                st.error("❌ Incorrect Password")
    else:
        st.success("✅ Admin Mode Active")
        if st.button("Logout Admin Mode"):
            st.session_state.is_admin = False

# File paths
CUSTOMERS_FILE = "customers.csv"
TRANSACTIONS_FILE = "transactions.csv"

def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        df = pd.read_csv(CUSTOMERS_FILE)
        df['phone'] = df['phone'].astype(str).str.strip()
        df['name'] = df['name'].astype(str).str.strip()
        if 'email' in df.columns:
            df['email'] = df['email'].astype(str).str.strip()
        if 'birthday' in df.columns:
            df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce').dt.date
        if 'last_birthday_voucher_year' not in df.columns:
            df['last_birthday_voucher_year'] = 0
        if 'sign_up_voucher_redeemed' not in df.columns:
            df['sign_up_voucher_redeemed'] = False
        return df
    else:
        return pd.DataFrame(columns=['customer_id', 'name', 'phone', 'email', 'birthday', 
                                     'join_date', 'total_points', 'sign_up_voucher_redeemed', 
                                     'last_birthday_voucher_year'])

def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        df = pd.read_csv(TRANSACTIONS_FILE)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df
    else:
        return pd.DataFrame(columns=['date', 'customer_id', 'type', 'amount', 'points', 'outlet', 'notes', 'voucher_used'])

customers = load_customers()
transactions = load_transactions()

outlets = ["Austin Crest", "Eco Botanic"]
current_year = datetime.now().year
today = date.today()

menu = st.sidebar.selectbox(
    "Main Menu", 
    ["🏠 Dashboard", "➕ Add New Customer", "💰 Record Spending", 
     "👤 Customer Record", "🎟️ Redeem Reward", "🎂 Birthday Notifications", 
     "🔍 Search", "📊 Reports"]
)

# ================== DASHBOARD ==================
if menu == "🏠 Dashboard":
    st.header("Welcome to We Time CRM")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", len(customers))
    col2.metric("Total Points", int(customers['total_points'].sum()) if not customers.empty else 0)
    col3.metric("Outlets", len(outlets))

# ================== ADD NEW CUSTOMER ==================
elif menu == "➕ Add New Customer":
    st.subheader("Register New Customer")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *")
        phone = st.text_input("Phone Number *")
        email = st.text_input("Email (Optional)")
    with col2:
        birthday = st.date_input("Birthday", value=date(2000, 1, 1), min_value=date(1950, 1, 1), max_value=date.today())
        outlet = st.selectbox("Registered At", outlets)
    
    if st.button("Register + Give RM10 Sign-up Voucher", type="primary"):
        if name and phone:
            new_id = 1000 + len(customers) + 1
            new_row = pd.DataFrame([{
                'customer_id': new_id, 'name': name.strip(), 'phone': phone.strip(),
                'email': email.strip() if email else "", 'birthday': str(birthday),
                'join_date': str(date.today()), 'total_points': 0,
                'sign_up_voucher_redeemed': False, 'last_birthday_voucher_year': 0
            }])
            customers = pd.concat([customers, new_row], ignore_index=True)
            customers.to_csv(CUSTOMERS_FILE, index=False)
            st.success(f"✅ Customer ID **{new_id}** registered! RM10 Sign-up Voucher Issued.")
        else:
            st.error("Name and Phone are required!")

# ================== RECORD SPENDING ==================
elif menu == "💰 Record Spending":
    st.subheader("Record Spending")
    phone_input = st.text_input("Customer Phone Number")
    if phone_input:
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            customer = matching.iloc[0]
            st.success(f"Found: **{customer['name']}** | Points: {customer['total_points']}")
            
            amount = st.number_input("Spending Amount (RM)", min_value=0.0, step=1.0)
            outlet = st.selectbox("Outlet", outlets)
            notes = st.text_input("Notes")
            
            if st.button("Record & Add Points", type="primary"):
                points = int(amount)
                idx = customers[customers['customer_id'] == customer['customer_id']].index[0]
                customers.at[idx, 'total_points'] += points
                customers.to_csv(CUSTOMERS_FILE, index=False)
                
                new_trans = pd.DataFrame([{
                    'date': str(datetime.now()), 'customer_id': customer['customer_id'],
                    'type': 'Spending', 'amount': amount, 'points': points, 
                    'outlet': outlet, 'notes': notes, 'voucher_used': ''
                }])
                transactions = pd.concat([transactions, new_trans], ignore_index=True)
                transactions.to_csv(TRANSACTIONS_FILE, index=False)
                st.success(f"✅ RM{amount} recorded at {outlet} → +{points} points!")
        else:
            st.error("Customer not found.")

# ================== REDEEM REWARD ==================
elif menu == "🎟️ Redeem Reward":
    st.subheader("🎟️ Redeem Rewards")
    phone_input = st.text_input("Customer Phone Number")
    if phone_input:
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            cust = matching.iloc[0]
            birthday_date = pd.to_datetime(cust['birthday'])
            birthday_month = birthday_date.month
            
            st.write(f"**Customer:** {cust['name']} | **Current Points:** {cust['total_points']}")
            
            st.write("### Vouchers")
            colA, colB = st.columns(2)
            with colA:
                if st.button("Redeem RM10 Sign-up Voucher"):
                    if not cust['sign_up_voucher_redeemed']:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'sign_up_voucher_redeemed'] = True
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("✅ RM10 Sign-up Voucher Redeemed!")
                    else:
                        st.warning("Already redeemed.")
            with colB:
                if st.button("Redeem RM20 Birthday Voucher"):
                    if datetime.now().month == birthday_month and cust['last_birthday_voucher_year'] < current_year:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'last_birthday_voucher_year'] = current_year
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("✅ RM20 Birthday Voucher Redeemed!")
                    else:
                        st.error("Not eligible now.")
            
            st.write("### Point-Based Rewards")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("1 Cup Drink (-300 pts)"):
                    if cust['total_points'] >= 300:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'total_points'] -= 300
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("✅ 1 Cup Drink Redeemed!")
            with col2:
                if st.button("1 Hour Nintendo Switch (-500 pts)"):
                    if cust['total_points'] >= 500:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'total_points'] -= 500
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("✅ 1 Hour Nintendo Switch Redeemed!")
            with col3:
                if st.button("1 Hour Free Small Room (-1000 pts)"):
                    if cust['total_points'] >= 1000:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'total_points'] -= 1000
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("✅ 1 Hour Free Small Room Redeemed!")
        else:
            st.error("Customer not found.")

# ================== IMPROVED REPORTS SECTION ==================
elif menu == "📊 Reports":
    st.subheader("📊 Business Intelligence Reports")
    
    report_type = st.selectbox("Select Report", [
        "Overall Summary",
        "Customers by Outlet",
        "Top Spenders",
        "Most Regular Customers",
        "Inactive Customers (No visit > 3 months)",
        "This Month Birthdays",
        "Revenue by Outlet",
        "Points Redemption Report",
        "New Customers per Month",
        "Voucher Redemption Rate"
    ])
    
    outlet_filter = st.selectbox("Filter by Outlet", ["All"] + outlets)
    
    if not customers.empty:
        # Prepare merged data
        if not transactions.empty:
            trans_summary = transactions.groupby('customer_id').agg({
                'amount': 'sum',
                'date': 'max',
                'outlet': 'first'
            }).reset_index()
            trans_summary = trans_summary.rename(columns={'amount': 'total_spent', 'date': 'last_visit'})
            report_df = customers.merge(trans_summary, on='customer_id', how='left')
        else:
            report_df = customers.copy()
            report_df['total_spent'] = 0
            report_df['last_visit'] = None
        
        if outlet_filter != "All":
            report_df = report_df[report_df.get('outlet', '') == outlet_filter]
        
        # Report Logic
        if report_type == "Overall Summary":
            st.write("### Overall Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Customers", len(report_df))
            col2.metric("Total Points", int(report_df['total_points'].sum()))
            col3.metric("Total Revenue (RM)", int(report_df.get('total_spent', 0).sum()))
            col4.metric("Active Customers", len(report_df))
        
        elif report_type == "Revenue by Outlet":
            if not transactions.empty:
                revenue = transactions.groupby('outlet')['amount'].sum().reset_index()
                st.dataframe(revenue, use_container_width=True)
            else:
                st.info("No revenue data yet.")
        
        elif report_type == "Points Redemption Report":
            redeemed = transactions[transactions['type'].str.contains('Redeem', na=False)]
            st.dataframe(redeemed, use_container_width=True)
        
        elif report_type == "New Customers per Month":
            customers['join_date'] = pd.to_datetime(customers['join_date'])
            new_cust = customers.groupby(customers['join_date'].dt.to_period('M')).size()
            st.dataframe(new_cust.reset_index(name='New Customers'), use_container_width=True)
        
        elif report_type == "Voucher Redemption Rate":
            total_customers = len(customers)
            signup_redeemed = customers['sign_up_voucher_redeemed'].sum()
            birthday_redeemed = (customers['last_birthday_voucher_year'] == current_year).sum()
            st.metric("Sign-up Voucher Redeemed", f"{signup_redeemed}/{total_customers}")
            st.metric("Birthday Voucher Redeemed (This Year)", birthday_redeemed)
        
        else:
            # Other reports (Top Spenders, Regular, Inactive, Birthdays)
            st.dataframe(report_df, use_container_width=True)
        
        # Download Button (Admin Only)
        if st.session_state.is_admin:
            csv = report_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download This Report", csv, f"report_{report_type.lower().replace(' ', '_')}.csv", "text/csv")
        else:
            st.info("Download available only in Admin Mode.")
    else:
        st.info("No data available yet.")

st.sidebar.info("""
**We Time CRM v2.3**
• Advanced Reports Added
• Admin Mode for Download
""")
