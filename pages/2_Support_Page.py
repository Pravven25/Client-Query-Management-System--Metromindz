import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from db_connection import get_db

st.set_page_config(page_title="Support Page", page_icon="🎧", layout="wide")

# Check login
if "logged_in" not in st.session_state:
    st.warning("⚠️ Please login first from the main page!")
    st.info("👉 Go back to the main page to login")
    st.stop()

if not st.session_state.logged_in:
    st.warning("⚠️ You are not logged in!")
    st.info("👉 Go back to the main page to login")
    st.stop()

# Page content
if st.session_state.role == "Support":
    st.title("🎧 Support Team Dashboard")
else:
    st.title("📊 All Queries Dashboard")
st.write(f"**Welcome, {st.session_state.username}!** 👋")
st.markdown("---")

# Get all queries
try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT query_id, client_name, mail_id, mobile_number, query_heading,
               query_description, status, priority, query_created_time,
               query_closed_time, assigned_to
        FROM client_queries
        ORDER BY query_created_time DESC
    """)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    
    if data:
        df = pd.DataFrame(data, columns=[
            'query_id', 'client_name', 'mail_id', 'mobile_number', 'query_heading',
            'query_description', 'status', 'priority', 'query_created_time',
            'query_closed_time', 'assigned_to'
        ])
        
        # System Metrics
        st.subheader("📊 System Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Queries", len(df))
        with col2:
            st.metric("🔴 Open", len(df[df['status'] == 'Open']))
        with col3:
            st.metric("🟡 In Progress", len(df[df['status'] == 'In Progress']))
        with col4:
            st.metric("🟢 Resolved", len(df[df['status'] == 'Resolved']))
        
        st.markdown("---")
        
        # Charts
        st.subheader("📈 Query Trends & Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Queries by Status**")
            try:
                import plotly.express as px
                status_counts = df['status'].value_counts()
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
            except:
                status_counts = df['status'].value_counts()
                for status, count in status_counts.items():
                    st.write(f"**{status}:** {count}")
        
        with col2:
            st.markdown("**📅 Queries Over Time**")
            try:
                import plotly.express as px
                df['date'] = pd.to_datetime(df['query_created_time']).dt.date
                date_counts = df.groupby('date').size().reset_index(name='count')
                fig = px.line(date_counts, x='date', y='count', markers=True)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            except:
                df['date'] = pd.to_datetime(df['query_created_time']).dt.date
                date_counts = df.groupby('date').size()
                st.bar_chart(date_counts)
        
        st.markdown("---")
        
        # Manage Queries
        st.subheader("📂 Manage Queries")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.radio(
                "🔍 Filter by Status",
                ['All', 'Open', 'In Progress', 'Resolved'],
                horizontal=True
            )
        with col2:
            priority_filter = st.multiselect(
                "⚡ Filter by Priority",
                ['Low', 'Medium', 'High'],
                default=['Low', 'Medium', 'High']
            )
        with col3:
            search_text = st.text_input("🔎 Search")
        
        # Apply filters
        filtered_df = df.copy()
        if status_filter != 'All':
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if priority_filter:
            filtered_df = filtered_df[filtered_df['priority'].isin(priority_filter)]
        if search_text:
            filtered_df = filtered_df[
                filtered_df['query_heading'].str.contains(search_text, case=False, na=False) |
                filtered_df['mail_id'].str.contains(search_text, case=False, na=False)
            ]
        
        st.write(f"**Showing {len(filtered_df)} of {len(df)} queries**")
        
        if len(filtered_df) > 0:
            # Display table
            display_df = filtered_df[['query_id', 'client_name', 'mail_id', 'query_heading', 
                                     'status', 'priority', 'query_created_time']].copy()
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Update Query Section
            st.subheader("🛠️ Update Query")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                query_id_update = st.number_input(
                    "Enter Query ID to Update",
                    min_value=1,
                    step=1,
                    value=int(filtered_df['query_id'].iloc[0]) if len(filtered_df) > 0 else 1
                )
            
            with col2:
                new_status = st.selectbox(
                    "Select New Status",
                    ['Open', 'In Progress', 'Resolved']
                )
            
            with col3:
                st.write("")
                st.write("")
                if st.button("✅ Update Query", use_container_width=True):
                    if query_id_update in filtered_df['query_id'].values:
                        try:
                            db = get_db()
                            cursor = db.cursor()
                            
                            if new_status == 'Resolved':
                                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                cursor.execute("""
                                    UPDATE client_queries 
                                    SET status = ?, query_closed_time = ?
                                    WHERE query_id = ?
                                """, (new_status, now, query_id_update))
                            else:
                                cursor.execute("""
                                    UPDATE client_queries 
                                    SET status = ?
                                    WHERE query_id = ?
                                """, (new_status, query_id_update))
                            
                            db.commit()
                            st.success(f"✅ Query {query_id_update} updated to {new_status}!")
                        except Exception as e:
                            st.error(f"❌ Error updating query: {str(e)}")
                        finally:
                            if cursor:
                                cursor.close()
                            if db:
                                db.close()
                    else:
                        st.error("❌ Query ID not found in filtered results!")
        else:
            st.info("ℹ️ No queries match the selected filters.")
    else:
        st.info("ℹ️ No queries in the system yet.")

except Exception as e:
    st.error(f"❌ Error loading queries: {str(e)}")
