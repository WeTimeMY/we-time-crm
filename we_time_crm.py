import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(page_title="We Time CRM", layout="wide")
st.title("🎬 We Time Private Movie Cafe - CRM System")

# File paths
CUSTOMERS_FILE = "customers.csv"
TRANSACTIONS_FILE = "transactions.csv"

# Safe data loading
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
        return df
    else:
        return pd.DataFrame(columns=['customer_id', 'name', 'phone', 'email', 'birthday', 
                                     'join_date', 'total_points', 'sign_up_voucher_used', 
                                     'last_birthday_voucher_year'])

def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        return pd.read_csv(TRANSACTIONS_FILE)
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
        birthday = st.date_input("Birthday", value=date(2000, 1, 1), 
                               min_value=date(1950, 1, 1), max_value=date.today())
        outlet = st.selectbox("Registered At", outlets)
    
    if st.button("Register + RM10 Sign-up", type="primary"):
        if name and phone:
            new_id = 1000 + len(customers) + 1
            new_row = pd.DataFrame([{
                'customer_id': new_id, 'name': name.strip(), 'phone': phone.strip(),
                'email': email.strip() if email else "", 'birthday': str(birthday),
                'join_date': str(date.today()), 'total_points': 10,
                'sign_up_voucher_used': False, 'last_birthday_voucher_year': 0
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

# ================== CUSTOMER RECORD ==================
elif menu == "👤 Customer Record":
    st.subheader("Customer Full Record")
    phone_input = st.text_input("Enter Phone Number")
    if phone_input:
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            cust = matching.iloc[0]
            st.write(f"**{cust['name']}** | ID: {cust['customer_id']} | Points: **{cust['total_points']}**")
            cust_trans = transactions[transactions['customer_id'] == cust['customer_id']]
            if not cust_trans.empty:
                st.dataframe(cust_trans.sort_values('date', ascending=False), use_container_width=True)

# ================== REDEEM REWARD (Updated) ==================
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
            
            # Birthday Voucher
            if st.button("Redeem RM20 Birthday Voucher", type="primary"):
                if datetime.now().month == birthday_month:
                    if cust['last_birthday_voucher_year'] < current_year:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'last_birthday_voucher_year'] = current_year
                        customers.at[idx, 'total_points'] -= 20
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("🎉 RM20 Birthday Voucher Redeemed!")
                    else:
                        st.warning("Birthday voucher already redeemed this year.")
                else:
                    st.error("Can only redeem in birthday month.")
            
            st.write("### Other Rewards")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("1 Cup Drink (-300 pts)"):
                    if cust['total_points'] >= 300:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'total_points'] -= 300
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("✅ 1 Cup Drink Redeemed!")
                    else:
                        st.error("Not enough points!")
            
            with col2:
                if st.button("1 Hour Nintendo Switch (-500 pts)"):
                    if cust['total_points'] >= 500:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'total_points'] -= 500
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("✅ 1 Hour Nintendo Switch Redeemed!")
                    else:
                        st.error("Not enough points!")
            
            with col3:
                if st.button("1 Hour Free Small Room (-1000 pts)"):
                    if cust['total_points'] >= 1000:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'total_points'] -= 1000
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("✅ 1 Hour Free Small Room Redeemed!")
                    else:
                        st.error("Not enough points!")
        else:
            st.error("Customer not found.")

# ================== BIRTHDAY NOTIFICATIONS ==================
elif menu == "🎂 Birthday Notifications":
    st.subheader("🎂 Birthday Notifications")
    if customers.empty:
        st.info("No customers yet.")
    else:
        today_month = today.month
        today_day = today.day
        today_birthdays = []
        upcoming = []
        
        for _, cust in customers.iterrows():
            if pd.isna(cust['birthday']): continue
            b_date = pd.to_datetime(cust['birthday']).date()
            b_month = b_date.month
            b_day = b_date.day
            
            if b_month == today_month and b_day == today_day:
                today_birthdays.append(cust)
            
            try:
                this_year_bday = date(today.year, b_month, b_day)
                if this_year_bday < today:
                    this_year_bday = date(today.year + 1, b_month, b_day)
                days_until = (this_year_bday - today).days
                if 1 <= days_until <= 7:
                    upcoming.append({
                        'name': cust['name'],
                        'phone': cust['phone'],
                        'birthday': b_date,
                        'days_left': days_until,
                        'points': cust['total_points']
                    })
            except:
                continue
        
        st.write("### 🎉 Birthdays Today")
        if today_birthdays:
            today_df = pd.DataFrame(today_birthdays)
            st.success(f"**{len(today_birthdays)} customer(s) celebrating today!**")
            st.dataframe(today_df[['name', 'phone', 'birthday', 'total_points']], use_container_width=True)
        else:
            st.info("No birthdays today.")
        
        st.write("### 📅 Upcoming Birthdays (Next 7 Days)")
        if upcoming:
            st.dataframe(pd.DataFrame(upcoming).sort_values('days_left'), use_container_width=True)
        else:
            st.info("No upcoming birthdays in next 7 days.")

# Search & Reports
elif menu == "🔍 Search":
    st.subheader("Search Customer")
    search = st.text_input("Name or Phone")
    if search:
        results = customers[
            customers['name'].str.contains(search, case=False, na=False) |
            customers['phone'].str.contains(search, case=False, na=False)
        ]
        st.dataframe(results, use_container_width=True)

elif menu == "📊 Reports":
    st.subheader("All Customers")
    if not customers.empty:
        st.dataframe(customers, use_container_width=True)
        csv = customers.to_csv(index=False).encode('utf-8')
        st.download_button("Download Customer List", csv, "we_time_customers.csv", "text/csv")

st.sidebar.info("""
**We Time CRM v1.8**
• 1 Point = RM1
• Rewards: Drink (300), Switch (500), Room (1000)
• Birthday Voucher (Birthday Month Only)
""")
