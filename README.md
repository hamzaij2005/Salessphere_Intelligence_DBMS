# 📊 SalesSphere – Intelligent Sales Dashboard

SalesSphere is a modern interactive **sales analytics dashboard** built using Streamlit, PostgreSQL, and Plotly. It provides real-time insights into business performance, including sales, customers, products, payments, and reviews with role-based access control.

---

## 🚀 Features

### 🔐 Authentication System
- Role-based login (Admin / Viewer)
- Session-based authentication using Streamlit
- Secure logout system

---

## 📊 Dashboard Modules

### ◈ Overview
- Total Revenue
- Total Orders
- Active Customers
- Average Order Value
- Monthly revenue trends
- Category-wise revenue breakdown
- Top products
- Order status analytics

---

### ⟋ Sales Analytics
- Year-over-year comparison
- Quarterly revenue analysis
- Payment breakdown
- Revenue heatmap (Month × Year)

---

### ◎ Customer Analytics
- Top customers by revenue
- New customer registrations
- Spending behavior analysis
- Order frequency vs spending (scatter plot)

---

### ⬡ Product Intelligence
- Category performance analysis
- Units sold distribution
- Top products ranking
- Stock health monitoring (Critical / Low / Healthy)

---

### ◇ Payment Insights
- Payment method distribution
- Average payment per method
- Monthly payment trends

---

### ★ Reviews & Ratings
- Rating distribution (1–5 stars)
- Average rating by category
- Product review analytics
- Recent reviews table

---

### ⌗ SQL Explorer
- Run custom SQL queries
- Predefined query templates
- Visualization support:
  - Bar Chart
  - Line Chart
  - Pie Chart
  - Scatter Plot
- Live PostgreSQL integration

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (Custom UI + CSS)
- **Backend:** Python
- **Database:** PostgreSQL (psycopg2)
- **Visualization:** Plotly (Express + Graph Objects)
- **Data Processing:** Pandas

---

## ⚙️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/salessphere.git
cd salessphere
