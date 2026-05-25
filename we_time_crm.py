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
        return df
    else:
        return pd.DataFrame(columns=['customer_id', 'name', 'phone', 'email', 'birthday', 
                                     'join_date', 'total_points', 'sign_up_voucher_used', 'birthday_voucher_redeemed'])

def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        return pd.read_csv(TRANSACTIONS_FILE)
    else:
        return pd.DataFrame(columns=['date', 'customer_id', 'type', 'amount', 'points', 'outlet', 'notes', 'voucher_used'])

customers = load_customers()
transactions = load_transactions()

outlets = ["Austin Crest", "Eco Botanic"]

menu = st.sidebar.selectbox(
    "Main Menu", 
    ["🏠 Dashboard", "➕ Add New Customer", "💰 Record Spending", 
     "👤 Customer Record", "🎟️ Redeem Voucher", "🔍 Search", "📊 Reports"]
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
    
    if st.button("Register + RM10 Sign-up", type="primary"):
        if name and phone:
            new_id = 1000 + len(customers) + 1
            new_row = pd.DataFrame([{
                'customer_id': new_id, 'name': name.strip(), 'phone': phone.strip(),
                'email': email.strip() if email else "", 'birthday': str(birthday),
                'join_date': str(date.today()), 'total_points': 10,
                'sign_up_voucher_used': False, 'birthday_voucher_redeemed': False
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
            st.success(f"Found: **{customer['name']}**")
            
            amount = st.number_input("Spending Amount (RM)", min_value=0.0, step=1.0)
            outlet = st.selectbox("Outlet", outlets)
            notes = st.text_input("Notes")
            
            if st.button("Record & Add Points", type="primary"):
                points = int(amount)
                idx = customers[customers['customer_id'] == customer['customer_id']].index[0]
                customers.at[idx, 'total_points'] += points
                customers.to_csv(CUSTOMERS_FILE, index=False)
                
                new_trans = pd.DataFrame([{'date': str(datetime.now()), 'customer_id': customer['customer_id'],
                    'type': 'Spending', 'amount': amount, 'points': points, 'outlet': outlet,
                    'notes': notes, 'voucher_used': ''}])
                transactions = pd.concat([transactions, new_trans], ignore_index=True)
                transactions.to_csv(TRANSACTIONS_FILE, index=False)
                st.success(f"✅ RM{amount} recorded! +{points} points added.")
        else:
            st.error("Customer not found.")

# ================== CUSTOMER RECORD (New) ==================
elif menu == "👤 Customer Record":
    st.subheader("Customer Record")
    phone_input = st.text_input("Enter Phone Number to View Record")
    if phone_input:
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            cust = matching.iloc[0]
            st.write(f"**Name:** {cust['name']} | **ID:** {cust['customer_id']} | **Points:** {cust['total_points']}")
            st.write(f"**Birthday:** {cust['birthday']}")
            
            # Show transaction history
            cust_trans = transactions[transactions['customer_id'] == cust['customer_id']]
            if not cust_trans.empty:
                st.dataframe(cust_trans.sort_values('date', ascending=False), use_container_width=True)
            else:
                st.info("No transactions yet.")
        else:
            st.error("Customer not found.")

# ================== REDEEM VOUCHER (New) ==================
elif menu == "🎟️ Redeem Voucher":
    st.subheader("Redeem Voucher")
    phone_input = st.text_input("Customer Phone Number")
    
    if phone_input:
        matching = customers[customers['phone'].str.contains(str(phone_input), case=False, na=False)]
        if not matching.empty:
            cust = matching.iloc[0]
            current_month = datetime.now().month
            birthday_month = pd.to_datetime(cust['birthday']).month
            
            st.write(f"Customer: **{cust['name']}** | Points: **{cust['total_points']}**")
            
            # Birthday Voucher
            if st.button("Redeem RM20 Birthday Voucher"):
                if current_month == birthday_month:
                    if not cust['birthday_voucher_redeemed']:
                        idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                        customers.at[idx, 'birthday_voucher_redeemed'] = True
                        customers.at[idx, 'total_points'] -= 20
                        customers.to_csv(CUSTOMERS_FILE, index=False)
                        st.success("🎉 RM20 Birthday Voucher Redeemed Successfully!")
                    else:
                        st.warning("Birthday voucher already redeemed this year.")
                else:
                    st.error("❌ Birthday voucher can only be redeemed in the customer's birthday month.")
            
            # Points Redemption (Custom)
            redeem_points = st.number_input("Redeem Points (Custom Reward)", min_value=0, max_value=int(cust['total_points']))
            if st.button("Redeem Custom Points"):
                if redeem_points > 0:
                    idx = customers[customers['customer_id'] == cust['customer_id']].index[0]
                    customers.at[idx, 'total_points'] -= redeem_points
                    customers.to_csv(CUSTOMERS_FILE, index=False)
                    st.success(f"✅ Redeemed {redeem_points} points!")
        else:
            st.error("Customer not found.")

# ================== Other Menus (Search & Reports) ==================
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
        st.download_button("Download CSV", csv, "customers.csv", "text/csv")

st.sidebar.info("""
**We Time CRM v1.4**
• 1 Point = RM1
• Sign-up: RM10
• Birthday Voucher: Redeemable only in birthday month
""")
