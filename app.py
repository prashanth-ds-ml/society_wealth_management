
import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
import os
from typing import Dict, List, Any
import uuid

# Page configuration
st.set_page_config(
    page_title="Thrift Savings Management",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ThriftManager:
    def __init__(self, data_file="thrift_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Ensure we always return a dictionary
                if isinstance(data, dict):
                    return data
                else:
                    # If data is not a dict (e.g., a list), return empty dict
                    return {}
        return {}
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def calculate_interest(self, recovery_amount: float, days_held: int, has_receipt: bool) -> Dict:
        """Calculate interest based on business rules"""
        # Determine interest rate and transaction type
        if recovery_amount >= 100000:  # >= 1 Lakh
            interest_rate = 10.8
            transaction_type = "Bulk" if has_receipt else "Monthly"
        else:  # < 1 Lakh
            interest_rate = 8.5
            transaction_type = "Bulk" if has_receipt else "Monthly"
        
        # Calculate simple interest: (Recovery * InterestRate * DaysHeld) / 36500
        interest_amount = (recovery_amount * interest_rate * days_held) / 36500
        
        return {
            "InterestRate": interest_rate,
            "InterestAmount": round(interest_amount, 2),
            "TransactionType": transaction_type,
            "InterestBand": f"{interest_rate}%"
        }
    
    def add_member(self, member_id: str, member_data: Dict):
        """Add new member"""
        self.data[member_id] = member_data
        self.save_data()
    
    def get_member(self, member_id: str) -> Dict:
        """Get member data"""
        return self.data.get(member_id, {})
    
    def update_member(self, member_id: str, member_data: Dict):
        """Update member data"""
        self.data[member_id] = member_data
        self.save_data()
    
    def search_members(self, search_term: str) -> List[Dict]:
        """Search members by ID, Name, or MS No"""
        results = []
        search_term = search_term.lower()
        
        for member_id, member_data in self.data.items():
            if (search_term in member_id.lower() or 
                search_term in member_data.get("MemberName", "").lower() or
                search_term in str(member_data.get("MSNo", "")).lower()):
                results.append({**member_data, "MemberID": member_id})
        
        return results
    
    def add_transaction(self, member_id: str, transaction: Dict):
        """Add transaction to member"""
        if member_id not in self.data:
            return False
        
        if "ThriftRecords" not in self.data[member_id]:
            self.data[member_id]["ThriftRecords"] = []
        
        self.data[member_id]["ThriftRecords"].append(transaction)
        self.save_data()
        return True

def load_mock_data(manager: ThriftManager):
    """Load comprehensive mock data from JSON file"""
    mock_data_file = "attached_assets/mock_thrift_data_1754567673631.json"
    
    try:
        # Only load if no data exists to avoid overwriting user data
        if not manager.data:
            with open(mock_data_file, 'r') as f:
                mock_data_list = json.load(f)
            
            # Convert list format to dictionary format for our data structure
            for member in mock_data_list:
                member_copy = member.copy()  # Create a copy to avoid modifying original
                member_id = member_copy.pop("MemberID")  # Remove MemberID from member data
                manager.data[member_id] = member_copy
            
            manager.save_data()
            st.sidebar.success(f"✅ Loaded {len(mock_data_list)} members with mock data")
    except FileNotFoundError:
        # Fallback to basic sample data if mock file not found
        init_basic_sample_data(manager)
    except Exception as e:
        st.sidebar.error(f"Error loading mock data: {str(e)}")
        init_basic_sample_data(manager)

def init_basic_sample_data(manager: ThriftManager):
    """Initialize with basic sample data as fallback"""
    sample_member = {
        "MemberName": "Ramu Parasinma",
        "MSNo": "7036",
        "ShareCapital": 800,
        "OpeningBalance": {
            "Date": "2024-12-31",
            "ThriftBalance": 375463
        },
        "ThriftRecords": [
            {
                "Date": "2025-01-14",
                "Recovery": 120000,
                "ReceiptNumber": "RCP123",
                "Paid": 495463,
                "Balance": 495463,
                "DaysHeld": 167,
                "InterestRate": 10.8,
                "InterestAmount": 5910.74,
                "TransactionType": "Bulk",
                "InterestBand": "10.8%"
            }
        ]
    }
    
    if "1070135" not in manager.data:
        manager.add_member("1070135", sample_member)

def main():
    st.title("🏦 Thrift Savings Management System")
    st.markdown("---")
    
    # Initialize manager
    manager = ThriftManager()
    load_mock_data(manager)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["🔍 Search & View", "➕ Add Member", "📊 Add Transaction", "📈 Analytics", "📂 Data Management"]
    )
    
    if page == "🔍 Search & View":
        search_and_view_page(manager)
    elif page == "➕ Add Member":
        add_member_page(manager)
    elif page == "📊 Add Transaction":
        add_transaction_page(manager)
    elif page == "📈 Analytics":
        analytics_page(manager)
    elif page == "📂 Data Management":
        data_management_page(manager)

def search_and_view_page(manager: ThriftManager):
    st.header("🔍 Search & View Members")
    
    # Search functionality
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("Search by Member ID, Name, or MS No:", placeholder="Enter search term...")
    with col2:
        search_button = st.button("Search", type="primary")
    
    if search_term or search_button:
        results = manager.search_members(search_term)
        
        if results:
            st.success(f"Found {len(results)} member(s)")
            
            # Display search results
            for member in results:
                with st.expander(f"👤 {member['MemberName']} (ID: {member['MemberID']})"):
                    display_member_details(member, manager)
        else:
            st.warning("No members found matching your search criteria.")
    
    # Show all members if no search
    if not search_term:
        st.subheader("All Members")
        if manager.data:
            for member_id, member_data in manager.data.items():
                with st.expander(f"👤 {member_data['MemberName']} (ID: {member_id})"):
                    display_member_details({**member_data, "MemberID": member_id}, manager)
        else:
            st.info("No members found. Add some members to get started.")

def display_member_details(member: Dict, manager: ThriftManager):
    """Display detailed member information"""
    
    # Member basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Member ID", member['MemberID'])
    with col2:
        st.metric("MS No", member.get('MSNo', 'N/A'))
    with col3:
        st.metric("Share Capital", f"₹{member.get('ShareCapital', 0):,}")
    
    # Opening balance
    opening_balance = member.get('OpeningBalance', {})
    st.subheader("Opening Balance")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Date", opening_balance.get('Date', 'N/A'))
    with col2:
        st.metric("Thrift Balance", f"₹{opening_balance.get('ThriftBalance', 0):,}")
    
    # Transactions
    transactions = member.get('ThriftRecords', [])
    if transactions:
        st.subheader("Transactions")
        
        # Filter tabs
        tab1, tab2, tab3 = st.tabs(["All Transactions", "10.8% Transactions", "8.5% Transactions"])
        
        with tab1:
            display_transaction_table(transactions, "all")
        
        with tab2:
            filtered_108 = [t for t in transactions if t.get('InterestRate') == 10.8]
            display_transaction_table(filtered_108, "10.8%")
        
        with tab3:
            filtered_85 = [t for t in transactions if t.get('InterestRate') == 8.5]
            display_transaction_table(filtered_85, "8.5%")
        
        # Summary panel
        display_summary_panel(member)
    else:
        st.info("No transactions found for this member.")

def display_transaction_table(transactions: List[Dict], filter_type: str):
    """Display transaction table"""
    if not transactions:
        st.info(f"No {filter_type} transactions found.")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(transactions)
    
    # Format columns
    if not df.empty:
        # Format currency columns
        for col in ['Recovery', 'Paid', 'Balance', 'InterestAmount']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notnull(x) else "₹0.00")
        
        # Format receipt number
        if 'ReceiptNumber' in df.columns:
            df['ReceiptNumber'] = df['ReceiptNumber'].fillna('—')
        
        # Reorder columns
        column_order = ['Date', 'Recovery', 'TransactionType', 'ReceiptNumber', 'InterestRate', 'DaysHeld', 'InterestAmount']
        df_display = df[[col for col in column_order if col in df.columns]]
        
        st.dataframe(df_display, use_container_width=True)

def display_summary_panel(member: Dict):
    """Display summary panel"""
    st.subheader("📊 Summary")
    
    transactions = member.get('ThriftRecords', [])
    if not transactions:
        return
    
    # Calculate totals
    total_recovery = sum(t.get('Recovery', 0) for t in transactions)
    interest_108 = sum(t.get('InterestAmount', 0) for t in transactions if t.get('InterestRate') == 10.8)
    interest_85 = sum(t.get('InterestAmount', 0) for t in transactions if t.get('InterestRate') == 8.5)
    grand_interest = interest_108 + interest_85
    
    opening_balance = member.get('OpeningBalance', {}).get('ThriftBalance', 0)
    final_balance = opening_balance + total_recovery + grand_interest
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Recovery", f"₹{total_recovery:,.2f}")
    with col2:
        st.metric("Interest (10.8%)", f"₹{interest_108:,.2f}")
    with col3:
        st.metric("Interest (8.5%)", f"₹{interest_85:,.2f}")
    with col4:
        st.metric("Grand Interest", f"₹{grand_interest:,.2f}")
    with col5:
        st.metric("Final Balance", f"₹{final_balance:,.2f}")

def add_member_page(manager: ThriftManager):
    st.header("➕ Add New Member")
    
    with st.form("add_member_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            member_id = st.text_input("Member ID*", placeholder="e.g., 1070135")
            member_name = st.text_input("Member Name*", placeholder="e.g., John Doe")
            ms_no = st.text_input("MS No*", placeholder="e.g., 7036")
        
        with col2:
            share_capital = st.number_input("Share Capital*", min_value=0, value=800)
            opening_date = st.date_input("Opening Balance Date*", value=date(2024, 12, 31))
            opening_balance = st.number_input("Opening Thrift Balance*", min_value=0.0, value=0.0)
        
        submitted = st.form_submit_button("Add Member", type="primary")
        
        if submitted:
            if not all([member_id, member_name, ms_no]):
                st.error("Please fill in all required fields marked with *")
            elif member_id in manager.data:
                st.error("Member ID already exists!")
            else:
                new_member = {
                    "MemberName": member_name,
                    "MSNo": ms_no,
                    "ShareCapital": share_capital,
                    "OpeningBalance": {
                        "Date": opening_date.strftime("%Y-%m-%d"),
                        "ThriftBalance": opening_balance
                    },
                    "ThriftRecords": []
                }
                
                manager.add_member(member_id, new_member)
                st.success(f"Member {member_name} added successfully!")
                st.rerun()

def add_transaction_page(manager: ThriftManager):
    st.header("📊 Add Transaction")
    
    if not manager.data:
        st.warning("No members found. Please add members first.")
        return
    
    # Select member
    member_options = [(f"{data['MemberName']} ({mid})", mid) for mid, data in manager.data.items()]
    selected_member = st.selectbox(
        "Select Member",
        options=[option[1] for option in member_options],
        format_func=lambda x: next(option[0] for option in member_options if option[1] == x)
    )
    
    if selected_member:
        member_data = manager.get_member(selected_member)
        
        with st.form("add_transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_date = st.date_input("Transaction Date*", value=date.today())
                recovery_amount = st.number_input("Recovery Amount*", min_value=0.0, value=0.0, step=1000.0)
                receipt_number = st.text_input("Receipt Number (Optional)", placeholder="e.g., RCP123")
            
            with col2:
                paid_amount = st.number_input("Paid Amount*", min_value=0.0, value=0.0, step=1000.0)
                balance_amount = st.number_input("Balance Amount*", min_value=0.0, value=0.0, step=1000.0)
                days_held = st.number_input("Days Held*", min_value=1, value=30)
            
            submitted = st.form_submit_button("Add Transaction", type="primary")
            
            if submitted:
                if recovery_amount <= 0:
                    st.error("Recovery amount must be greater than 0")
                else:
                    # Calculate interest
                    has_receipt = bool(receipt_number.strip())
                    interest_calc = manager.calculate_interest(recovery_amount, days_held, has_receipt)
                    
                    new_transaction = {
                        "Date": transaction_date.strftime("%Y-%m-%d"),
                        "Recovery": recovery_amount,
                        "ReceiptNumber": receipt_number.strip() if receipt_number.strip() else None,
                        "Paid": paid_amount,
                        "Balance": balance_amount,
                        "DaysHeld": days_held,
                        **interest_calc
                    }
                    
                    if manager.add_transaction(selected_member, new_transaction):
                        st.success("Transaction added successfully!")
                        
                        # Show calculated values
                        st.subheader("Calculated Values")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Interest Rate", f"{interest_calc['InterestRate']}%")
                        with col2:
                            st.metric("Interest Amount", f"₹{interest_calc['InterestAmount']:,.2f}")
                        with col3:
                            st.metric("Transaction Type", interest_calc['TransactionType'])
                        
                        st.rerun()
                    else:
                        st.error("Failed to add transaction")

def analytics_page(manager: ThriftManager):
    st.header("📈 Analytics Dashboard")
    
    if not manager.data:
        st.warning("No data available for analytics.")
        return
    
    # Overall statistics
    total_members = len(manager.data)
    total_transactions = sum(len(member.get('ThriftRecords', [])) for member in manager.data.values())
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Members", total_members)
    with col2:
        st.metric("Total Transactions", total_transactions)
    
    if total_transactions == 0:
        st.info("No transactions found for analytics.")
        return
    
    # Aggregate data
    all_transactions = []
    for member_id, member_data in manager.data.items():
        for transaction in member_data.get('ThriftRecords', []):
            all_transactions.append({
                **transaction,
                'MemberID': member_id,
                'MemberName': member_data.get('MemberName', '')
            })
    
    df = pd.DataFrame(all_transactions)
    
    if not df.empty:
        # Interest band analysis
        st.subheader("Interest Band Analysis")
        interest_summary = df.groupby('InterestBand').agg({
            'Recovery': 'sum',
            'InterestAmount': 'sum',
            'MemberID': 'count'
        }).rename(columns={'MemberID': 'TransactionCount'})
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(interest_summary.style.format({
                'Recovery': '₹{:,.2f}',
                'InterestAmount': '₹{:,.2f}'
            }))
        
        with col2:
            # Simple chart using metrics
            st.subheader("Summary by Interest Rate")
            for band in interest_summary.index:
                st.metric(
                    f"{band} Band",
                    f"₹{interest_summary.loc[band, 'InterestAmount']:,.2f}",
                    f"{interest_summary.loc[band, 'TransactionCount']} transactions"
                )
        
        # Transaction type analysis
        st.subheader("Transaction Type Distribution")
        type_summary = df.groupby('TransactionType').agg({
            'Recovery': 'sum',
            'InterestAmount': 'sum',
            'MemberID': 'count'
        }).rename(columns={'MemberID': 'Count'})
        
        st.dataframe(type_summary.style.format({
            'Recovery': '₹{:,.2f}',
            'InterestAmount': '₹{:,.2f}'
        }))

def data_management_page(manager: ThriftManager):
    st.header("📂 Data Management")
    
    # Current data status
    st.subheader("Current Data Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_members = len(manager.data)
        st.metric("Total Members", total_members)
    
    with col2:
        total_transactions = sum(len(member.get('ThriftRecords', [])) for member in manager.data.values())
        st.metric("Total Transactions", total_transactions)
    
    with col3:
        data_file_exists = os.path.exists(manager.data_file)
        st.metric("Data File Status", "✅ Exists" if data_file_exists else "❌ Missing")
    
    st.markdown("---")
    
    # Data Actions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Reload Mock Data")
        st.info("This will reload the comprehensive sample data with 20+ members and their transaction history.")
        
        if st.button("🔄 Reload Mock Data", type="secondary"):
            # Clear existing data
            manager.data = {}
            # Reload mock data
            load_mock_data(manager)
            st.success("Mock data reloaded successfully!")
            st.rerun()
    
    with col2:
        st.subheader("🗑️ Clear All Data")
        st.warning("This will permanently delete all current data!")
        
        if st.button("🗑️ Clear All Data", type="secondary"):
            manager.data = {}
            manager.save_data()
            st.success("All data cleared!")
            st.rerun()
    
    st.markdown("---")
    
    # Export functionality
    st.subheader("📤 Export Data")
    if manager.data:
        # Convert data to exportable format
        export_data = []
        for member_id, member_data in manager.data.items():
            export_data.append({
                "MemberID": member_id,
                **member_data
            })
        
        export_json = json.dumps(export_data, indent=2, default=str)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download JSON",
                data=export_json,
                file_name=f"thrift_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Convert to CSV for easier viewing
            csv_data = []
            for member_id, member_data in manager.data.items():
                for transaction in member_data.get('ThriftRecords', []):
                    csv_data.append({
                        'MemberID': member_id,
                        'MemberName': member_data.get('MemberName', ''),
                        'MSNo': member_data.get('MSNo', ''),
                        'ShareCapital': member_data.get('ShareCapital', 0),
                        'OpeningBalance': member_data.get('OpeningBalance', {}).get('ThriftBalance', 0),
                        **transaction
                    })
            
            if csv_data:
                df_export = pd.DataFrame(csv_data)
                csv_string = df_export.to_csv(index=False)
                
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_string,
                    file_name=f"thrift_transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    else:
        st.info("No data available for export.")
    
    # Data preview
    if manager.data:
        st.subheader("📋 Data Preview")
        st.write(f"Preview of current data structure (showing first 3 members):")
        
        preview_data = dict(list(manager.data.items())[:3])
        st.json(preview_data)

if __name__ == "__main__":
    main()
