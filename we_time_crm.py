import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os

st.set_page_config(page_title="We Time CRM", layout="wide")
st.title("🎬 We Time Private Movie Cafe - CRM System")

# Admin Login
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

PASSWORD = "wetimemanagement2026"

with st.sidebar:
    st.subheader("🔑 Admin Access")
    if not st.session_state.is_admin:
        admin_pass = st.text_input("Admin Password", type="password")
        if st.button("Login as Admin"):
            if admin_pass == PASSWORD:
                st.session_state.is_admin = True
                st.success("✅ Admin Mode Activated")
            else:
                st.error("❌ Incorrect Password")
    else:
        st.success("✅ Admin Mode Active")
        if st.button("Logout Admin"):
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
     "👤 Customer Record", "🎟️ Redeem Reward", "🔧 Adjust Points",
     "🎂 Birthday Notifications", "🔍 Search", "📊 Reports"]
)

# ================== RECORD SPENDING ==================
elif menu == "💰 Record Spending":
    st.subheader("💰 Record Spending")
    phone_input = st.text_input("Customer Phone Number")
    if phone_input:
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            customer = matching.iloc[0]
            st.success(f"✅ Found: **{customer['name']}** | Points: {customer['total_points']}")
            
            amount = st.number_input("Spending Amount (RM)", min_value=0.0, step=1.0)
            outlet = st.selectbox("Outlet", outlets)
            notes = st.text_input("Notes")
            
            if st.button("Record Spending & Add Points", type="primary"):
                if amount > 0:
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
                    st.success(f"✅ Recorded RM{amount} for {customer['name']} → +{points} points!")
                    st.rerun()
        else:
            st.error("Customer not found.")

# ================== ADJUST POINTS ==================
elif menu == "🔧 Adjust Points":
    st.subheader("🔧 Adjust Points")
    phone_input = st.text_input("Customer Phone Number")
    if phone_input:
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            cust = matching.iloc[0]
            st.success(f"Customer: **{cust['name']}** | Current Points: {cust['total_points']}")
            
            adjustment = st.number_input("Points to Adjust", value=0, step=1, help="Negative = Deduct")
            reason = st.text_input("Reason", "Correction")
            
            if st.button("Apply Adjustment", type="primary"):
                if adjustment != 0:
                    idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                    old = cust['total_points']
                    new = old + adjustment
                    customers.at[idx, 'total_points'] = new
                    customers.to_csv(CUSTOMERS_FILE, index=False)
                    st.success(f"✅ Changed from {old} to {new}")
        else:
            st.error("Customer not found.")

# ================== BIRTHDAY NOTIFICATIONS (Fixed) ==================
elif menu == "🎂 Birthday Notifications":
    st.subheader("🎂 Birthday Notifications")
    
    if customers.empty:
        st.info("No customers registered yet.")
    else:
        today_month = today.month
        today_day = today.day
        today_birthdays = []
        upcoming = []
        
        for _, cust in customers.iterrows():
            if pd.isna(cust['birthday']): 
                continue
            b_date = pd.to_datetime(cust['birthday']).date()
            b_month = b_date.month
            b_day = b_date.day
            
            # Today's birthdays
            if b_month == today_month and b_day == today_day:
                today_birthdays.append({
                    'name': cust['name'],
                    'phone': cust['phone'],
                    'birthday': b_date,
                    'points': cust['total_points']
                })
            
            # Upcoming birthdays (next 7 days)
            try:
                this_year_bday = date(today.year, b_month, b_day)
                if this_year_bday < today:
                    this_year_bday = date(today.year + 1, b_month, b_day)
                days_until = (this_year_bday - today).days
                if 1 <= days_until <= 7:
                    upcoming.append({
                        'name': cust['name'],
                        'phone': cust['phone'],
                        'birthday': b_date.strftime('%d %B'),
                        'days_left': days_until,
                        'points': cust['total_points']
                    })
            except:
                continue
        
        # Display Today's Birthdays
        st.write("### 🎉 Birthdays Today")
        if today_birthdays:
            st.success(f"**{len(today_birthdays)} customer(s) have birthday today!**")
            st.dataframe(pd.DataFrame(today_birthdays), use_container_width=True)
        else:
            st.info("No birthdays today.")
        
        # Display Upcoming Birthdays
        st.write("### 📅 Upcoming Birthdays (Next 7 Days)")
        if upcoming:
            upcoming_df = pd.DataFrame(upcoming)
            upcoming_df = upcoming_df.sort_values('days_left')
            st.dataframe(upcoming_df, use_container_width=True)
        else:
            st.info("No upcoming birthdays in the next 7 days.")

# ================== Other Pages ==================
elif menu == "👤 Customer Record":
    st.subheader("Customer Full Record")
    phone_input = st.text_input("Enter Phone Number")
    if phone_input:
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            cust = matching.iloc[0]
            st.success(f"**{cust['name']}** (ID: {cust['customer_id']})")
            st.write(f"Points: {cust['total_points']}")
            cust_trans = transactions[transactions['customer_id'] == cust['customer_id']]
            if not cust_trans.empty:
                st.dataframe(cust_trans.sort_values('date', ascending=False), use_container_width=True)

elif menu == "🔍 Search":
    st.subheader("Search Customer")
    search = st.text_input("Name or Phone")
    if search:
        results = customers[
            customers['name'].str.contains(search, case=False, na=False) |
            customers['phone'].str.contains(search, case=False, na=False)
        ]
        st.dataframe(results, use_container_width=True)

st.sidebar.info("""
**We Time CRM v3.7**
• Birthday Notifications Fixed
• Full working version
""")
