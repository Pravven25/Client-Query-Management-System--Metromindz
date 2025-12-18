import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path to import db_connection
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from db_connection import get_db

st.set_page_config(page_title="Client Page", page_icon="📝", layout="wide")

# Check if user is logged in
if "logged_in" not in st.session_state:
    st.warning("⚠️ Please login first from the main page!")
    st.info("👉 Go back to the main page to login")
    st.stop()

if not st.session_state.logged_in:
    st.warning("⚠️ You are not logged in!")
    st.info("👉 Go back to the main page to login")
    st.stop()

if st.session_state.role != "Client":
    st.error("❌ This page is only for Clients!")
    st.info("👉 You are logged in as Support. Please go to the Support Page.")
    st.stop()

# Page content
st.title("📝 Client Query Submission")
st.write(f"**Welcome, {st.session_state.username}!** 👋")
st.markdown("---")

# Two column layout
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🆕 Submit New Query")
    
    with st.form("query_form", clear_on_submit=True):
        email = st.text_input("📧 Email", value=st.session_state.email or "", placeholder="your@email.com")
        mobile = st.text_input("📱 Mobile Number", placeholder="1234567890")
        heading = st.text_input("📌 Query Heading", placeholder="Brief description")
        description = st.text_area("📝 Query Description", placeholder="Describe your issue in detail...", height=150)
        priority = st.selectbox("⚡ Priority", ["Low", "Medium", "High"], index=1)
        
        submit_btn = st.form_submit_button("🚀 Submit Query", use_container_width=True)
        
        if submit_btn:
            if email and mobile and heading and description:
                if "@" in email and mobile.isdigit() and len(mobile) >= 10:
                    try:
                        db = get_db()
                        cursor = db.cursor()
                        
                        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        cursor.execute("""
                            INSERT INTO client_queries 
                            (client_name, mail_id, mobile_number, query_heading, 
                             query_description, status, priority, query_created_time)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (st.session_state.username, email, mobile, heading, 
                              description, 'Open', priority, now))
                        
                        db.commit()
                        query_id = cursor.lastrowid
                        cursor.close()
                        db.close()
                        
                        st.success(f"✅ Query submitted successfully! Query ID: {query_id}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Please enter valid email (with @) and 10-digit mobile number!")
            else:
                st.error("❌ Please fill in all fields!")

with col_right:
    st.subheader("📊 Your Quick Stats")
    
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT status FROM client_queries WHERE client_name=?",
            (st.session_state.username,)
        )
        data = cursor.fetchall()
        cursor.close()
        db.close()
        
        if data:
            df = pd.DataFrame(data, columns=['status'])
            total = len(df)
            open_count = len(df[df['status'] == 'Open'])
            in_progress = len(df[df['status'] == 'In Progress'])
            resolved = len(df[df['status'] == 'Resolved'])
            
            st.metric("📋 Total Queries", total)
            st.metric("🔴 Open", open_count)
            st.metric("🟡 In Progress", in_progress)
            st.metric("🟢 Resolved", resolved)
        else:
            st.info("No queries yet.\nSubmit your first query!")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.subheader("📂 Your Submitted Queries")

try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT query_id, mail_id, mobile_number, query_heading, 
               query_description, status, priority, query_created_time,
               query_closed_time, assigned_to
        FROM client_queries 
        WHERE client_name=?
        ORDER BY query_created_time DESC
    """, (st.session_state.username,))
    
    data = cursor.fetchall()
    cursor.close()
    db.close()
    
    if data:
        df = pd.DataFrame(data, columns=[
            'query_id', 'mail_id', 'mobile_number', 'query_heading', 
            'query_description', 'status', 'priority', 'query_created_time',
            'query_closed_time', 'assigned_to'
        ])
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_options = df['status'].unique().tolist()
            status_filter = st.multiselect(
                "🔍 Filter by Status",
                status_options,
                default=status_options
            )
        with col2:
            priority_options = df['priority'].unique().tolist()
            priority_filter = st.multiselect(
                "⚡ Filter by Priority",
                priority_options,
                default=priority_options
            )
        
        filtered_df = df
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if priority_filter:
            filtered_df = filtered_df[filtered_df['priority'].isin(priority_filter)]
        
        if len(filtered_df) > 0:
            st.write(f"**Showing {len(filtered_df)} of {len(df)} queries**")
            
            # Show pie chart and table
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**📊 Status Distribution**")
                try:
                    import plotly.express as px
                    status_counts = filtered_df['status'].value_counts()
                    fig = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        color=status_counts.index,
                        color_discrete_map={
                            'Open': '#ff4b4b',
                            'In Progress': '#ffa500',
                            'Resolved': '#00cc00'
                        }
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show counts
                    for status, count in status_counts.items():
                        pct = (count/len(filtered_df))*100
                        if status == 'Open':
                            st.markdown(f"🔴 **Open:** {count} ({pct:.1f}%)")
                        elif status == 'Resolved':
                            st.markdown(f"🟢 **Resolved:** {count} ({pct:.1f}%)")
                        else:
                            st.markdown(f"🟡 **In Progress:** {count} ({pct:.1f}%)")
                except:
                    # If plotly doesn't work, show simple counts
                    status_counts = filtered_df['status'].value_counts()
                    for status, count in status_counts.items():
                        st.write(f"**{status}:** {count}")
            
            with col2:
                # Display table
                display_df = filtered_df[['query_id', 'mail_id', 'query_heading', 
                                         'status', 'priority', 'query_created_time']].copy()
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # View details
            st.markdown("---")
            st.subheader("🔍 View Query Details")
            
            query_ids = filtered_df['query_id'].tolist()
            if query_ids:
                selected_id = st.selectbox("Select Query ID to view details:", query_ids)
                
                if selected_id:
                    row = filtered_df[filtered_df['query_id'] == selected_id].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Query ID:** {row['query_id']}")
                        st.write(f"**Email:** {row['mail_id']}")
                        st.write(f"**Mobile:** {row['mobile_number']}")
                        st.write(f"**Status:** {row['status']}")
                        st.write(f"**Priority:** {row['priority']}")
                    
                    with col2:
                        st.write(f"**Created:** {row['query_created_time']}")
                        if pd.notna(row['query_closed_time']):
                            st.write(f"**Closed:** {row['query_closed_time']}")
                        if pd.notna(row['assigned_to']):
                            st.write(f"**Assigned To:** {row['assigned_to']}")
                    
                    st.info(f"**Query Heading:**\n{row['query_heading']}")
                    st.text_area("**Query Description:**", row['query_description'], height=100, disabled=True, key=f"desc_{selected_id}")
        else:
            st.info("No queries match the selected filters")
    else:
        st.info("📭 You haven't submitted any queries yet. Use the form above to submit your first query!")

except Exception as e:
    st.error(f"❌ Error loading queries: {str(e)}")

st.markdown("---")
st.subheader("📊 Sample Client Queries Database")
st.write("Below is a sample dataset of client queries:")

try:
    csv_path = os.path.join(parent_dir, "synthetic_client_queries.csv")
    df_synthetic = pd.read_csv(csv_path)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Total Queries", len(df_synthetic))
    with col2:
        st.metric("✅ Closed", len(df_synthetic[df_synthetic['status'] == 'Closed']))
    with col3:
        st.metric("🔴 Open", len(df_synthetic[df_synthetic['status'] == 'Open']))
    
    st.write("")
    
    st.dataframe(df_synthetic, use_container_width=True, hide_index=True)
    
    st.download_button(
        label="📥 Download CSV",
        data=df_synthetic.to_csv(index=False),
        file_name="client_queries.csv",
        mime="text/csv"
    )
    
except Exception as e:
    st.error(f"❌ Error loading synthetic queries: {str(e)}")