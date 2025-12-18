import streamlit as st
import hashlib
from db_connection import get_db, create_tables

# IMPORTANT: Setup tables first
create_tables()

# Page config
st.set_page_config(
    page_title="Query Management System",
    page_icon="📌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state FIRST
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "email" not in st.session_state:
    st.session_state.email = None

# Hash password function
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register function
def register(username, password, role, email):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return False, "❌ Username already exists!"
        
        hashed = hash_pw(password)
        cursor.execute(
            "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
            (username, hashed, role, email)
        )
        db.commit()
        cursor.close()
        db.close()
        return True, "✅ Registration successful! Please login."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# Login function
def login(username, password, role):
    try:
        db = get_db()
        cursor = db.cursor()
        hashed = hash_pw(password)
        cursor.execute(
            "SELECT username, role, email FROM users WHERE username=? AND password=? AND role=?",
            (username, hashed, role)
        )
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if result:
            return True, result[1], result[2]
        return False, None, None
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False, None, None

# CSS Styling
st.markdown("""
    <style>
    .big-title {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-title {
        font-size: 1.5rem;
        color: #ff7f0e;
        text-align: center;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# MAIN APPLICATION
if not st.session_state.logged_in:
    # NOT LOGGED IN - Show login/register
    st.markdown('<p class="big-title">📌 Client Query Management System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Welcome! Please Login or Register</p>', unsafe_allow_html=True)
    
    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔓 Login", "📝 Register"])
        
        # LOGIN TAB
        with tab1:
            st.subheader("Login to Your Account")
            
            login_username = st.text_input("👤 Username", key="login_user")
            login_password = st.text_input("🔒 Password", type="password", key="login_pass")
            login_role = st.selectbox("👥 Select Role", ["Client", "Support"], key="login_role")
            
            if st.button("🔓 Login", use_container_width=True):
                if login_username and login_password:
                    success, role, email = login(login_username, login_password, login_role)
                    if success:
                        # Set session state
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.session_state.role = role
                        st.session_state.email = email
                        st.success(f"✅ Welcome {login_username}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid username, password, or role!")
                else:
                    st.warning("⚠️ Please fill in all fields!")
        
        # REGISTER TAB
        with tab2:
            st.subheader("Create New Account")
            
            reg_username = st.text_input("👤 Username", key="reg_user")
            reg_email = st.text_input("📧 Email Address", key="reg_email")
            reg_password = st.text_input("🔒 Password", type="password", key="reg_pass")
            reg_confirm = st.text_input("🔒 Confirm Password", type="password", key="reg_confirm")
            reg_role = st.selectbox("👥 Select Role", ["Client", "Support"], key="reg_role")
            
            if st.button("📝 Register", use_container_width=True):
                if reg_username and reg_email and reg_password and reg_confirm:
                    if reg_password == reg_confirm:
                        if "@" in reg_email and "." in reg_email:
                            success, message = register(reg_username, reg_password, reg_role, reg_email)
                            if success:
                                st.success(message)
                                st.info("👉 Now go to Login tab to sign in!")
                            else:
                                st.error(message)
                        else:
                            st.error("❌ Please enter a valid email address!")
                    else:
                        st.error("❌ Passwords don't match!")
                else:
                    st.warning("⚠️ Please fill in all fields!")

else:
    # LOGGED IN - Show dashboard
    st.markdown('<p class="big-title">📌 Client Query Management System</p>', unsafe_allow_html=True)
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.write(f"**👤 Logged in as:** {st.session_state.username}")
    with col2:
        st.write(f"**👥 Role:** {st.session_state.role}")
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.email = None
            st.success("✅ Logged out successfully!")
            st.rerun()
    
    st.markdown("---")
    
    # Navigation instructions
    st.markdown("### 🎯 Welcome to Query Management System!")
    
    if st.session_state.role == "Client":
        st.success("✅ You are logged in as a **Client**")
        st.info("👉 **Go to the sidebar** and click on **'1_Client_Page'** to submit and view your queries")
        
        st.markdown("""
        #### What you can do:
        - ✅ Submit new support queries
        - ✅ View all your submitted queries
        - ✅ Track query status (Open/In Progress/Resolved)
        - ✅ See statistics and charts
        - ✅ Filter queries by status and priority
        """)
    else:
        st.success("✅ You are logged in as **Support Team**")
        st.info("👉 **Go to the sidebar** and click on **'2_Support_Page'** to manage all queries")
        
        st.markdown("""
        #### What you can do:
        - ✅ View all queries in the system
        - ✅ Update query status
        - ✅ Assign queries to team members
        - ✅ View system statistics and trends
        - ✅ Filter and search queries
        - ✅ Close resolved queries
        """)
    
    st.markdown("---")
    
    # Quick stats
    try:
        db = get_db()
        cursor = db.cursor()
        
        if st.session_state.role == "Client":
            cursor.execute(
                "SELECT COUNT(*) FROM client_queries WHERE client_name=?",
                (st.session_state.username,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM client_queries")
        
        total = cursor.fetchone()[0]
        cursor.close()
        db.close()
        
        st.metric("📊 Total Queries", total)
    except:
        pass
    