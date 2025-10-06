import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from statsmodels.tsa.arima.model import ARIMA
# ==============================================================
# 1️⃣ Page Config
# ==============================================================
st.set_page_config(
    page_title="Sales Prediction Dashboard",
    page_icon="📊",
    layout="wide",
)
# ==============================================================
# 2️⃣ Database Setup
# ==============================================================
def init_db():
    conn = sqlite3.connect("user_cred.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
def check_login(username, password):
    conn = sqlite3.connect("user_cred.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None
def add_user(username, password):
    conn = sqlite3.connect("user_cred.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
init_db()
# ==============================================================
# 3️⃣ Session State Initialization
# ==============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "sales_data" not in st.session_state:
    st.session_state.sales_data = []
if "predictions" not in st.session_state:
    st.session_state.predictions = []
# ==============================================================
# 4️⃣ Login Page
# ==============================================================
def login_page():
    st.title(" Login / Register")

    tab1, tab2 = st.tabs([" Login", " Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(" Login successful!")
                st.rerun()
            else:
                st.error(" Invalid username or password")

    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            if new_user and new_pass:
                add_user(new_user, new_pass)
                st.success(f" Account created for '{new_user}'! You can now log in.")
            else:
                st.warning(" Please enter both username and password.")

    st.stop()
# ==============================================================
# 5️⃣ ARIMA Prediction Function
# ==============================================================
def predict_sales(sales_data, weeks_to_predict=3, p=1, d=1, q=1):
    """Predict future sales using ARIMA."""
    try:
        model = ARIMA(sales_data, order=(p, d, q))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=weeks_to_predict)
        return forecast.tolist()
    except Exception as e:
        st.error(f"Error in prediction: {e}")
        return []
def export_to_csv(data):
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode("utf-8")
# ==============================================================
# 6️⃣ Main Dashboard (After Login)
# ==============================================================
def main_app():
    st.sidebar.title(" Navigation")
    page = st.sidebar.radio("Go to", ["🏠 Dashboard", "📈 Graphs", "📊 Predictions"])
    st.sidebar.markdown("---")
    theme = st.sidebar.radio("Theme", ["Light", "Dark"])
    # Apply theme
    if theme == "Dark":
        st.markdown(
            """
            <style>
            body { background-color: #0d1b2a; color: white; }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            body { background-color: #f5f7fa; color: black; }
            </style>
            """,
            unsafe_allow_html=True
        )
    # ==========================================================
    # 🏠 Dashboard
    # ==========================================================
    if page == "🏠 Dashboard":
        st.title("📊 Sales Prediction Dashboard")
        st.write("Enter your sales data manually or upload a CSV file.")
        input_method = st.radio("Choose input method:", ["Manual Entry", "Upload CSV"])
        sales_data = []
        if input_method == "Manual Entry":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                n_weeks = st.number_input("Number of weeks of sales data:", 1, 52, 3)
                for i in range(n_weeks):
                    sales = st.number_input(f"Week {i+1} sales:", min_value=0.0, step=0.1)
                    sales_data.append(sales)
        elif input_method == "Upload CSV":
            uploaded_file = st.file_uploader("Upload your sales CSV file", type=["csv"])
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                st.write(" File uploaded successfully!")
                st.dataframe(df.head())
                if "Sales" in df.columns:
                    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0)
                    sales_data = df["Sales"].tolist()
                else:
                    st.error("CSV must contain a 'Sales' column.")
        with st.expander(" ARIMA Settings"):
            p = st.slider("AR term (p)", 0, 5, 1)
            d = st.slider("Differencing (d)", 0, 2, 1)
            q = st.slider("MA term (q)", 0, 5, 1)
        predictions = []
        if sales_data and st.button("Predict Sales"):
            predictions = predict_sales(sales_data, weeks_to_predict=3, p=p, d=d, q=q)
            if len(predictions) > 0:
                avg_sales = np.mean(sales_data)
                growth = (sales_data[-1] - sales_data[0]) / (sales_data[0] + 1e-5) * 100
                next_pred = predictions[0]
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric(" Avg Sales", f"{avg_sales:.2f}")
                kpi2.metric(" Growth Rate", f"{growth:.2f}%")
                kpi3.metric(" Next Predicted", f"{next_pred:.2f}")
                st.session_state.sales_data = sales_data
                st.session_state.predictions = predictions
            else:
                st.error(" Prediction failed. Try adjusting ARIMA parameters or data.")
    # ==========================================================
    # 📈 Graphs
    # ==========================================================
    elif page == " Graphs":
        st.title(" Sales Graphs")
        if st.session_state.sales_data:
            sales_data = st.session_state.sales_data
            predictions = st.session_state.predictions
            weeks = list(range(1, len(sales_data) + 1))
            future_weeks = list(range(len(sales_data) + 1, len(sales_data) + len(predictions) + 1))
            fig, ax = plt.subplots()
            ax.plot(weeks, sales_data, marker='o', label="Actual Sales")
            ax.plot(future_weeks, predictions, marker='x', linestyle="--", label="Predicted Sales")
            ax.set_xlabel("Weeks")
            ax.set_ylabel("Sales")
            ax.legend()
            st.pyplot(fig)
        else:
            st.warning(" Please enter or upload sales data in the Dashboard first.")
    # ==========================================================
    # 📊 Predictions
    # ==========================================================
    elif page == "📊 Predictions":
        st.title("🔮 Predictions")
        if st.session_state.predictions:
            data = {
                "Week": list(range(1, len(st.session_state.sales_data) + len(st.session_state.predictions) + 1)),
                "Sales": st.session_state.sales_data + st.session_state.predictions
            }
            df = pd.DataFrame(data)
            st.dataframe(df)
            csv = export_to_csv(df)
            st.download_button(
                label=" Download as CSV",
                data=csv,
                file_name="sales_predictions.csv",
                mime="text/csv",
            )
        else:
            st.warning(" Please enter or upload sales data in the Dashboard first.")
# ==============================================================
# 7️⃣ Run App
# ==============================================================
if not st.session_state.logged_in:
    login_page()
else:
    main_app()