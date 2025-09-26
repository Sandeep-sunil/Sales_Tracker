import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(
    page_title="Sales Prediction Dashboard",
    page_icon="📊",
    layout="wide",
)

# ------------------------------
# Helper Functions
# ------------------------------
def predict_sales(sales_data, weeks_to_predict=1):
    """Simple prediction using average sales"""
    avg_sales = np.mean(sales_data)
    return [avg_sales for _ in range(weeks_to_predict)]

def export_to_csv(data):
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode("utf-8")

# ------------------------------
# Sidebar Navigation
# ------------------------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Dashboard", "📈 Graphs", "📊 Predictions"])

st.sidebar.markdown("---")
theme = st.sidebar.radio("Theme", ["Light", "Dark"])

# ------------------------------
# Apply Themes
# ------------------------------
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

# ------------------------------
# Dashboard Page
# ------------------------------
if page == "🏠 Dashboard":
    st.title("📊 Sales Prediction Dashboard")
    st.write("Enter your sales data manually or upload a CSV file.")

    # Option: Manual Input OR CSV Upload
    input_method = st.radio("Choose input method:", ["Manual Entry", "Upload CSV"])

    sales_data = []

    if input_method == "Manual Entry":
        # Center Input
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
            st.write("✅ File uploaded successfully!")
            st.dataframe(df.head())

            if "Sales" in df.columns:
                sales_data = df["Sales"].tolist()
            else:
                st.error("CSV must contain a 'Sales' column.")

    if sales_data and st.button("Predict Sales"):
        predictions = predict_sales(sales_data, weeks_to_predict=3)

        # KPI Cards
        avg_sales = np.mean(sales_data)
        growth = (sales_data[-1] - sales_data[0]) / (sales_data[0] + 1e-5) * 100
        next_pred = predictions[0]

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("📊 Avg Sales", f"{avg_sales:.2f}")
        kpi2.metric("📈 Growth Rate", f"{growth:.2f}%")
        kpi3.metric("🔮 Next Predicted", f"{next_pred:.2f}")

        # Save for later pages
        st.session_state["sales_data"] = sales_data
        st.session_state["predictions"] = predictions

# ------------------------------
# Graphs Page
# ------------------------------
elif page == "📈 Graphs":
    st.title("📈 Sales Graphs")

    if "sales_data" in st.session_state:
        sales_data = st.session_state["sales_data"]
        predictions = st.session_state["predictions"]

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
        st.warning("⚠️ Please enter or upload sales data in the Dashboard first.")

# ------------------------------
# Predictions Page
# ------------------------------
elif page == "📊 Predictions":
    st.title("🔮 Predictions")

    if "predictions" in st.session_state:
        data = {
            "Week": list(range(1, len(st.session_state["sales_data"]) + len(st.session_state["predictions"]) + 1)),
            "Sales": st.session_state["sales_data"] + st.session_state["predictions"]
        }
        df = pd.DataFrame(data)
        st.dataframe(df)

        # Export
        csv = export_to_csv(df)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="sales_predictions.csv",
            mime="text/csv",
        )
    else:
        st.warning("⚠️ Please enter or upload sales data in the Dashboard first.")
