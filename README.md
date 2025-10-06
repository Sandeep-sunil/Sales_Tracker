# Sales Prediction Dashboard

A **Streamlit-based interactive dashboard** for sales forecasting using **ARIMA**, with a **login/register system** backed by **SQLite**.

---

## Features

- 🔐 **User Authentication**
  - Login/Register with SQLite database.
  - Session-safe login; only authenticated users can access the dashboard.
  
- 📊 **Sales Prediction**
  - Manual entry or CSV upload of sales data.
  - Forecast future sales using **ARIMA**.
  - Adjustable ARIMA parameters `(p, d, q)` via sliders.

- 📈 **Visualizations**
  - Graph of actual vs. predicted sales.
  - Interactive KPI cards: average sales, growth rate, next predicted value.

- 💾 **Export**
  - Download combined sales data (actual + predicted) as CSV.

- 🌓 **Theme**
  - Light and Dark mode toggle.

---

## Installation

1. Clone the repository or copy the project files.
2. Install required Python libraries:
3. pip install streamlit pandas numpy matplotlib statsmodels sqlite3(python come with built-in)

CSV Format
Sales
120
150
130
170
160

sales_app.py       # Main Streamlit app
user_cred.db       # SQLite database for login credentials
README.md          # Project documentation


License
This project is free to use and modify.
