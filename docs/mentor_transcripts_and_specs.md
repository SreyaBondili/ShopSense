# MENTOR SPECIFICATIONS AND TRANSCRIPTS REPOSITORY

## 1. MILESTONE 3 WORD DOCUMENT (media_1793995515388_dcb8aea5.docx)

Milestone 3 (Weeks 5–6) – Advanced Analytics, APIs & Reporting
• Deploy FastAPI services supporting vendor analytics, forecasting, and customer intelligence
operations.
• Implement advanced revenue analysis and marketplace benchmarking features.
• Configure MLflow model registry and automated analytical workflow pipelines.
• Build business intelligence dashboard prototypes with interactive visualizations and export
capabilities.
Evaluation Criteria
• REST API endpoints respond within 300ms for 95th percentile analytical requests under
simulated marketplace loads.
• Business intelligence dashboards update analytical metrics in near real-time with ≥99% data
consistency.
• Automated analytical workflows successfully complete scheduled processing without
operational failures.
moves from data analytics into a production-grade analytics platform.
Customer Segmentation Panel
Recommendation Engine Panel
Inventory Forecast Section
Navigation Menu (Dashboard, Vendors, Products, Transactions)
Milestone 3 Architecture
ShopSense/
│
├── app/
│   ├── api/
│   ├── analytics/
│   ├── forecasting/
│   ├── recommendations/
│   ├── customer_intelligence/
│   ├── mlflow_tracking/
│   ├── scheduler/
│
├── dashboard/
│   ├── admin_dashboard.py
│   ├── vendor_dashboard.py
│   ├── customer_dashboard.py
│
├── reports/
│   ├── pdf_reports.py
│   ├── excel_reports.py
│
└── models/
MODULE 1
FASTAPI ANALYTICS SERVICES
Folder Structure
api/
│
├── revenue_routes.py
├── forecast_routes.py
├── customer_routes.py
├── recommendation_routes.py
Revenue Analytics API
revenue_routes.py
from fastapi import APIRouter
import pandas as pd
router = APIRouter()
@router.get("/analytics/revenue")
def revenue_analysis():
   df = pd.read_csv(
       "data/transactions.csv"
   )
   revenue = float(
       df["amount"].sum()
   )
   return {
       "total_revenue": revenue
   }
Vendor Analytics API
@router.get(
"/analytics/vendor-performance"
)
def vendor_performance():
   df = pd.read_csv(
       "data/transactions.csv"
   )
   result = (
       df.groupby(
           "vendor_id"
       )
       ["amount"]
       .sum()
       .reset_index()
   )
   return result.to_dict(
       orient="records"
   )
Customer Intelligence API
customer_routes.py
from fastapi import APIRouter
import pandas as pd
router = APIRouter()
@router.get(
"/analytics/customers"
)
def customer_metrics():
   df = pd.read_csv(
     "data/customers.csv"
   )
   return {
     "customers":
     len(df),
     "avg_spend":
     float(
        df[
        "total_spent"
        ].mean()
     )
   }
Forecast API
forecast_routes.py
from fastapi import APIRouter
import joblib
router = APIRouter()
model = joblib.load(
    "models/inventory_model.pkl"
)
@router.get(
"/forecast/{month}"
)
def forecast(month:int):
   prediction = model.predict(
      [[month]]
   )
   return {
      "forecast":
      float(prediction[0])
   }
Recommendation API
recommendation_routes.py
@router.get(
"/recommend/{customer_id}"
)
def recommend(customer_id:int):
   return {
     "customer":customer_id,
     "recommended_product":
     "Wireless Mouse"
   }
Main FastAPI Registration
main.py
from fastapi import FastAPI
from api.revenue_routes import router as revenue_router
from api.forecast_routes import router as forecast_router
from api.customer_routes import router as customer_router
app = FastAPI()
app.include_router(
    revenue_router
)
app.include_router(
    forecast_router
)
app.include_router(
    customer_router
)
MODULE 2
ADVANCED REVENUE ANALYSIS
revenue_analysis.py
import pandas as pd
transactions = pd.read_csv(
   "data/transactions.csv"
)
GMV
def calculate_gmv():
   return (
       transactions["amount"]
       .sum()
   )
Revenue Growth
monthly = (
transactions.groupby(
"month"
)
["amount"]
.sum()
)
growth = (
monthly.pct_change()
*100
)
Average Order Value
def avg_order_value():
   return (
      transactions[
          "amount"
      ].mean()
   )
Vendor Benchmarking
vendor = (
transactions.groupby(
  "vendor_id"
)
["amount"]
.sum()
.reset_index()
)
Rank Vendors
vendor["rank"] = (
vendor["amount"]
.rank(
ascending=False
)
)
MODULE 3
MLFLOW MODEL REGISTRY
Install
pip install mlflow
track_inventory.py
import mlflow
mlflow.start_run()
Log Parameters
mlflow.log_param(
  "Model",
  "RandomForest"
)
Log Metric
mlflow.log_metric(
  "Accuracy",
  accuracy
)
Save Model
mlflow.sklearn.log_model(
     model,
     "InventoryModel"
)
End Run
mlflow.end_run()
Model Registry
mlflow.register_model(
   model_uri,
   "InventoryForecast"
)
MODULE 4
AUTOMATED WORKFLOW PIPELINE
Install APScheduler
Expected Evaluation Metrics
Metric
Target
API Response Time
≤300 ms
Dashboard Consistency
≥99%
Workflow Success Rate
100%
Forecasting Accuracy
≥80%
Segmentation Quality
≥85%
Recommendation Relevance
≥75%
7. Workflow Diagram
8. Architecture Diagram
9. Database Schema
 MODULE 4
AUTOMATED WORKFLOW PIPELINE
Install APScheduler
pip install apscheduler
scheduler.py
from apscheduler.schedulers.blocking import (
     BlockingScheduler
)
Daily Forecast Update
def retrain_model():
   print(
     "Retraining Model..."
   )
scheduler = (
  BlockingScheduler()
)
scheduler.add_job(
   retrain_model,
   'cron',
   hour=2
)
scheduler.start()
 MODULE 5
BUSINESS INTELLIGENCE DASHBOARD
The provided dashboard mockup can be expanded into a production dashboard with three sections:
Customer Intelligence
Inventory Intelligence
Recommendation Intelligence
Admin Dashboard
dashboard/admin_dashboard.py
import streamlit as st
import pandas as pd
Configure Page
st.set_page_config(
    layout="wide"
)
Header
st.title(
"ShopSense Admin Dashboard"
)
KPI Row
col1,col2,col3,col4=st.columns(4)
with col1:
   st.metric(
       "Revenue",
       "₹12.5 L"
   )
with col2:
   st.metric(
       "Products",
       "2,450"
   )
with col3:
   st.metric(
       "Customers",
       "1,240"
   )
with col4:
   st.metric(
       "Forecast Accuracy",
       "84%"
   )
Customer Segmentation Panel
st.subheader(
"Customer Segmentation"
)
segments = [
   "High Spenders",
   "Frequent Buyers",
   "Dormant Users"
]
st.write(
segments
)
Recommendation Panel
st.subheader(
"Recommendation Engine"
)
st.success(
"High Spenders ➜ Laptop"
)
Inventory Forecast Panel
st.subheader(
"Inventory Forecast"
)
st.info(
  "Item B : 45 Units"
)
Real-Time Revenue Visualization
import plotly.express as px
fig = px.line(
sales,
x="date",
y="amount",
title="Revenue Trend"
)
st.plotly_chart(
   fig,
   use_container_width=True
)
 MODULE 6
PDF REPORT EXPORT
Install
pip install reportlab
pdf_reports.py
from reportlab.pdfgen import canvas
def generate_report():
   pdf = canvas.Canvas(
       "RevenueReport.pdf"
   )
   pdf.drawString(
       100,
       750,
       "Revenue Analytics Report"
   )
   pdf.save()
EXCEL REPORT EXPORT
import pandas as pd
report.to_excel(
  "RevenueReport.xlsx",
  index=False
)
 MODULE 7
PERFORMANCE TESTING
Install
Expected Evaluation Metrics
Metric
Target
API Response Time
≤300 ms
Dashboard Consistency
≥99%
Workflow Success Rate
100%
Forecasting Accuracy
≥80%
Segmentation Quality
≥85%
Recommendation Relevance
≥75%
7. Workflow Diagram
8. Architecture Diagram
9. Database Schema
MODULE 7
PERFORMANCE TESTING
Install
pip install locust
locustfile.py
from locust import HttpUser
from locust import task
class AnalyticsUser(
    HttpUser
):
   @task
   def test_revenue_api(
        self
   ):
       self.client.get(
        "/analytics/revenue"
       )
Run:
Locust
Target:
95%
requests under
300ms
MODULE 8
DASHBOARD DATA-CONSISTENCY VALIDATION
db_revenue = 1250000
dashboard_revenue = 1250000
if db_revenue == dashboard_revenue:
   print(
     "99% consistency achieved"
   )
MODULE 9
AUTOMATED ANALYTICAL WORKFLOW VALIDATION
workflow_runs = 100
success = 100
reliability = (
success /
workflow_runs
) * 100
Output
100%
Milestone 3 Deliverables
✅ FastAPI Vendor Analytics APIs✅ Forecasting APIs✅ Customer Intelligence APIs✅ Recommendation APIs✅ Advanced Revenue Analytics✅ Marketplace Benchmarking✅ MLflow Model Tracking✅ Model Registry✅ Automated Workflow Scheduler✅ BI Dashboard Prototype✅ Interactive Plotly Visualizations✅ PDF Export✅ Excel Export✅ API Performance Testing✅ Workflow Monitoring
Expected Evaluation Metrics
Metric
Target
API Response Time
≤300 ms
Dashboard Consistency
≥99%
Workflow Success Rate
100%
Forecasting Accuracy
≥80%
Segmentation Quality
≥85%
Recommendation Relevance
≥75%

---

## 2. MILESTONE 2 WORD DOCUMENT (media_1793345850906_7491ef3e.docx)

Milestone 2
2. Product & Inventory Analytics Engine
• Maintain centralized repositories for products, inventory levels, pricing data, category
hierarchies, and warehouse information.
• Monitor stock movements, inventory turnover rates, and product availability across multiple
vendors.
• Implement inventory forecasting models using historical sales patterns and seasonal demand
trends.
• Generate low-stock alerts, replenishment recommendations, and product demand forecasts.
Milestone 2 (Weeks 3–4) – Inventory Intelligence & Customer Analytics
• Develop inventory tracking and forecasting systems using historical transaction data.
• Implement customer behavior analysis and segmentation pipelines.
• Build recommendation engines for personalized product suggestions.
• Validate analytical outputs against historical marketplace performance datasets.
6. Evaluation Criteria
Milestone 2 (Week 4)
• Inventory forecasting models achieve ≥80% forecasting accuracy on held-out sales datasets.
• Customer segmentation algorithms demonstrate meaningful behavioral grouping with ≥85%
clustering quality metrics.
• Product recommendation engine achieves ≥75% recommendation relevance based on historical user interactions.
For Milestone 2 (Weeks 3-4), you need to build three major modules:
Module 1: Product & Inventory Analytics Engine
Inventory Tracking System
Inventory Forecasting System
Low Stock Alert System
Replenishment Recommendation Engine
Module 2: Customer Analytics
Customer Behavior Analysis
Customer Segmentation using K-Means
Module 3: Recommendation Engine
Product Recommendation Model
Recommendation Evaluation
WEEK 3 IMPLEMENTATION
STEP 1: Create Additional Folder Structure
app/
│
├── inventory/
│   ├── inventory_tracking.py
│   ├── inventory_forecasting.py
│   ├── stock_alert.py
│
├── customer/
│   ├── segmentation.py
│   └── analytics.py
│
├── recommendation/
│   └── recommendation.py
│
├── data/
│   ├── transactions.csv
│   ├── products.csv
│   ├── inventory.csv
│   └── customers.csv
STEP 2: Inventory Database Model
models/inventory.py
from sqlalchemy import *
from app.database import Base
class Inventory(Base):
   __tablename__ = "inventory"
   inventory_id = Column(
       Integer,
       primary_key=True,
       index=True
   )
   product_id = Column(Integer)
   vendor_id = Column(Integer)
   warehouse_id = Column(Integer)
   current_stock = Column(Integer)
   reorder_level = Column(Integer)
   last_updated = Column(DateTime)
STEP 3: Warehouse Table
models/warehouse.py
from sqlalchemy import *
from app.database import Base
class Warehouse(Base):
   __tablename__ = "warehouse"
   warehouse_id = Column(
       Integer,
       primary_key=True
   )
   warehouse_name = Column(String)
   location = Column(String)
 STEP 4: Product Hierarchy
models/category.py
from sqlalchemy import *
from app.database import Base
class Category(Base):
   __tablename__="categories"
   category_id = Column(
       Integer,
       primary_key=True
   )
   category_name = Column(String)
   parent_category = Column(String)
Example
Electronics
├── Mobile
├── Laptop
Fashion
├── Men
├── Women
STEP 5: Inventory Dataset
data/inventory.csv
product_id,vendor_id,current_stock,reorder_level
101,1,150,40
102,1,15,25
103,2,90,30
104,2,10,20
105,3,5,15
STEP 6: Inventory Tracking
inventory_tracking.py
import pandas as pd
inventory = pd.read_csv(
   "data/inventory.csv"
)
def inventory_status():
   inventory["Status"] = (
       inventory["current_stock"] >
       inventory["reorder_level"]
   )
   inventory["Status"] = inventory[
       "Status"
   ].map({
       True:"Available",
       False:"Low Stock"
   })
   return inventory
STEP 7: Inventory Turnover Rate
Inventory Turnover =
Cost of Goods Sold
------------------
Average Inventory
inventory_tracking.py
def turnover_rate(cogs, avg_inventory):
   return round(
         cogs/avg_inventory,
         2
   )
Example
print(
   turnover_rate(
       100000,
       25000
   )
)
Output
4.0
STEP 8: Historical Sales Data
sales_history.csv
date,product_id,quantity_sold
2025-01-10,101,30
2025-02-15,101,32
2025-03-20,101,40
2025-04-15,101,38
2025-05-12,101,42
2025-06-18,101,48
2025-07-20,101,50
STEP 9: Inventory Forecasting Model
Evaluation requirement:
Forecast Accuracy >= 80%
inventory_forecasting.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
Load Dataset
df = pd.read_csv(
   "data/sales_history.csv"
)
df["date"] = pd.to_datetime(
   df["date"]
)
Feature Engineering
df["month"] = df.date.dt.month
df["quarter"] = df.date.dt.quarter
df["year"] = df.date.dt.year
Features
X = df[
   [
       "month",
       "quarter"
   ]
]
y = df["quantity_sold"]
Train-Test Split
X_train,\
X_test,\
y_train,\
y_test = train_test_split(
     X,
     y,
     test_size=0.2,
     random_state=42
)
Train Model
model = RandomForestRegressor(
           n_estimators=100
       )
model.fit(
    X_train,
    y_train
)
Accuracy
pred = model.predict(X_test)
accuracy = r2_score(
     y_test,
     pred
)
print(
  accuracy * 100
)
Target
>=80%
Forecast Demand
future = pd.DataFrame({
   "month":[8],
   "quarter":[3]
})
forecast = model.predict(
            future
         )
print(forecast)
STEP 10: Low Stock Alert
stock_alert.py
import pandas as pd
inventory = pd.read_csv(
   "data/inventory.csv"
)
def low_stock_alert():
   alerts = inventory[
      inventory[
       "current_stock"
      ] <= inventory[
       "reorder_level"
      ]
   ]
   return alerts
STEP 11: Replenishment Recommendation
stock_alert.py
def replenishment():
   inventory[
     "reorder_qty"
   ] = (
     inventory["reorder_level"]*2
     -
     inventory["current_stock"]
   )
   return inventory[
      [
       "product_id",
       "reorder_qty"
      ]
   ]
STEP 12: Inventory API
routes/inventory_routes.py
from fastapi import APIRouter
from app.inventory.stock_alert import \
    low_stock_alert
router = APIRouter()
@router.get(
   "/inventory/alerts"
)
def alerts():
   return (
     low_stock_alert()
     .to_dict()
   )
STEP 13: Customer Analytics
Dataset
customer_id,total_orders,total_spent
1,15,25000
2,10,15000
3,3,2000
4,20,35000
5,1,400
STEP 14: Customer Segmentation
Clustering Quality >=85%
segmentation.py
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
Load Data
df = pd.read_csv(
   "data/customers.csv"
)
Features
X = df[
   [
     "total_orders",
     "total_spent"
   ]
]
KMeans
kmeans = KMeans(
   n_clusters=3,
   random_state=42
)
Predict Clusters
df["cluster"] = (
   kmeans.fit_predict(X)
)
Clustering Score
score = silhouette_score(
   X,
   df["cluster"]
)
print(score)
0.85+
Label Clusters
cluster_map = {
   0:"High Value",
   1:"Regular",
   2:"Dormant"
}
df["segment"] = (
   df["cluster"]
   .map(cluster_map)
)
STEP 15: Customer Behavior Analytics
analytics.py
import pandas as pd
transactions = pd.read_csv(
    "data/transactions.csv"
)
customer_stats = (
transactions.groupby(
   "customer_id"
)
.agg({
  "amount":"sum",
  "transaction_id":"count"
})
)
STEP 16: Recommendation Engine
Requirement:
Recommendation Relevance >=75%
recommendation.py
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
matrix = pd.pivot_table(
         interactions,
         index="customer_id",
         columns="product_id",
         values="rating",
         fill_value=0
)
Similarity Matrix
similarity = cosine_similarity(
               matrix
            )
Recommendation Function
def recommend_products(
     customer_id,
     top_n=5
):
   user_index = (
      matrix.index
      .tolist()
      .index(customer_id)
   )
   scores = similarity[
       user_index
   ]
   return scores
STEP 17: Recommendation Accuracy
Simple Precision Metric
Precision =
Relevant Recommendations
------------------------
Total Recommendations
relevant = 80
recommended = 100
precision = (
 relevant/recommended
) * 100
print(precision)
Output
80%
Passes
>=75%
STEP 18: Dashboard Metrics
Inventory Dashboard
Show:
Current Stock
Low Stock Products
Inventory Turnover
Forecast Demand
Reorder Recommendations
Customer Dashboard
Show:
Customer Segments
Top Customers
Average Spending
Average Order Value
Recommendation Dashboard
Show:
Recommended Products
Recommendation Score
Click-through Metrics
MILESTONE 2
Milestone-2
│
├── Product Repository
├── Inventory Management
├── Warehouse Management
├── Category Hierarchy
├── Inventory Tracking Engine
├── Inventory Turnover Analytics
├── Inventory Forecasting
├── Low Stock Alert
├── Replenishment Engine
├── Customer Analytics
├── Customer Segmentation
├── Recommendation Engine
└── Dashboards
Target evaluation metrics
Inventory Forecasting Accuracy ≥ 80%
Customer Segmentation Quality ≥ 85% (Silhouette Score)
Recommendation Relevance ≥ 75%

---

## 3. MILESTONE 3 MEETING TRANSCRIPT (Pasted text(5).txt)

advanced analytics API and reporting is our milestone three.analytics.

So what is that?

Initially we have performed the data analysis in the milestone one and two basic data analytics you have performed.

So you are moving from basic data analysis into the further production grade analytics, okay?

We need to have one customer segmentation, one recommendation engine, and information forecasting, and navigation with the various menus.

These are the things which are required.

Follow milestone 1 and 2.

Milestone 1, you have just uploaded the data and other basic details, login and all. In the milestone 2, you have performed some basic analytics.

In milestone 3, you are performing further analytics and also into the dashboard.

Mile Store 3 is slightly large.

So we shall see the architecture.

So To the existing architecture, you will just add whatever else is required.

This is your architecture.

You would be already having the structure for the project, so for that you will modify it accordingly.

We'll try to have the various other things.

We'll divide it into various modules each. For the fast API analytics, we shall have one structure for the folder.

recommendation further.

For the revenue analysis, you will write the respective code, how you will perform the revenue analysis.

I'll give you all at once one minute.

Then non-similar lines, vendor analysis.

intelligence then forecasting and recommendation.

Just one more and your main function.

So in this, this is the tomorrow I'll give you this, you just try it out. This is slightly large.

This is mainly for the communication with the various APIs.In which we have four objectives.

One is to deploy fast API services supporting vendor analytics, forecasting, and customer intelligence operations.

So this we saw the code how to implement it yesterday.

Right, we have other objectives to take care to implement advanced revenue analysis and marketplace benchmarking features.

Then configure the ML flow model registry and automated analytical workflow pipeline, business build, business intelligence dashboard prototypes with. Interactive visualization and export capabilities.

I will give you this whatever we have discussed milestone three again in case if any of one of you have missed this. So document all this so that it will help you for your documentation also. So just cross check it. Okay. So further we will proceed with the next objective of our milestone three.

So next step is advanced revenue analysis.

So here we are performing the analysis of each of the data. So this is for the revenue analysis.

So we take our data set, we create the data frame which is the object and we want to calculate the revenue because we want to check whether is there a profit, loss or how it is functioning.

So you will take that. transactions data set and you will create the data frame object.

Then you will calculate the amount.

write the definition to calculate the amount.

Then the revenue for which you will group it, whether you want it on a week daily basis, weekly basis, monthly basis, so you can. calculate on what basis as per that you will perform the grouping.

So here it test for the monthly basis preferably you see which is more feasible Then you will calculate what is the growth because you want to see what is the growth, right?

Then you can calculate what is the average orders.

value.

So all the basic mathematical operations to calculate profit, loss, everything you will write the function definition and you will calculate it. All the basic mathematical operations, profit, loss, everything, percentage, you will translate it into the Python code appropriately.

Then you can have some benchmarking.

Suppose you want to sell 5 products of a particular, that you can have some benchmark.
. So, here we are just calculating what is the average orders.

So you can take one order or multiple orders, calculate the average order.

Then you can do some benchmarking, maybe you have a target to sell some 10.

cell phones, iPhones or something like that, whatever the products you have taken, you can have some benchmark or with respect to winter amount.

Okay, some benchmarking so that you meet that target, okay. Then So then you can also rank the vendors or rank the products that you can do. Okay, so either you want to rank the various vendors, rank the various products.

So that you can do here. This is ranking with respect to the vendors, means based upon the total sales, who has done the highest sales will get the first rank. like that. So these are few simple analytics you want to add any so that you can add. Okay. I'll give you this. Okay. So just take a minute to go through this, okay?

Once okay, you please let know. So do you have both fast API and this revenue analysis of milestone three?

So till here, able to follow?

Take some two minutes and you please let me Discussing in your groups, those groups and I think you have not provided the group GitHub link. Are all of you able to follow till here?

Have the workflow diagram.

See, this is one. Just take it down. You can have it for your documentation also. Texture Diagram This it will architecture you have. I don't remember whether I gave you or not. Anyway, you take this, but you don't know whether you have or not. This is easy, but pictorially it is, you should be able to follow, or if any, you please let them. The basic architecture of our complete internship project, starting from the user request till the order completion.

And database schema is one more. This helps you to design the database or modify it if any changes are required.

See, I think these should be self-explanatory, right?

With respect to the database schema and architecture.

and workflow.

You just go through this. If further, it is like how initially the customer comes in, browses the various products and services, then based upon that you will recommend, then the respective customer will see all the details, okay?

Then If they want to buy, they will add it to the cart and buy, or they want to have it later, they will save it. Then they will check out making the payment.

Okay, they will receive the order confirmation and the order would be supplied and it would be complete.

So on similar lines, the complete architecture.

Okay. And the schema, like what are the various products, customers, stores, products, recommendation.
 We have completed module two

Take out one more. One and two is done, right?

Next is module three.

So, this is the model machine learning flow model registry, how it should be. The milestone three, we are just dividing it and we are trying to have the code and execute it so that it will be easy. Right.

Objective by objective, that's all. So if machine learning flow is not there, you just install it. I think you should be knowing the command to install.

It is pip install what you follow to install any followed by that respective module.

then you need to track the inventory.

So you would have already already installed the machine learning flow library, you will import it. And then you will run the machine learning flow. This is with respect to the model registry, machine running from model registry.

Then you want to log the parameters for which you will make use of the random forest algorithm.

or any other suitable appropriately, but you need to justify why you are using that particular algorithm.

They may ask you why you have used this, why you have used that, what are the advantages, what are the parameters being considered.

Okay, and this is one basic structure what is being given which is mandatory to. Incorporate in your milestone.

You want to add any changes, modifications, additions that you are free to make. Next is to log the metrics in the accuracy.

Then you will save the model once you have developed it. Like you want to forecast the inventory and other things.

Save this inventory module And then you can close the run. Next is, from this you can have a model registry for the forecast.

Next is module four.
I will give you this module three.

matrix then you will save that particular.

model and then you can forecast it. That is the model registry.

I think there are another two steps.

The automation of the workflow pipeline.


Module 5 is the dashboard.

The various dashboards which you need to prepare.

These are our evaluation metrics.

This you can have it. These are the criteria which we need to meet. Okay, fine. So I will stop at this point.

So shall we start with module four? These are the expectations we have to satisfy this. The API response time, dashboard consistency, workflow success rate, forecasting accuracy, segmentation and recommendation relevance for which you need to perform the testing using postman or any other suitable tool. not going in detail because it is time consuming, it is very large.

So I want to give you the complete detail so that it is helpful and you can proceed with the implementation.

Wherever you have doubts, you please unmute and you ask it, okay?

So hoping you are able to follow till Whatever we have discussed, we will proceed further with module four which is automated workflow pipeline.

So you need to install the AP scheduler.

Using the pip install.

Then you need to have a code for the scheduler.

on a day basis.

So we'll perform some training and retraining.

So you will write Write the definition of the model for the retraining and once it is done, you will print the message as if the model has been retrained.

call the scheduler here So then you will run this job for every 2 hours.

You will start with the scheduler.

Once you start, this will perform the activities.

Okay. So, this is with respect to the module four. Next is module five. Module five is your intelligence dashboard.

We shall have the various dashboards.

First will be the admin dashboard.

So, You will import the streamlet and pandas which you have installed previously.

and you will configure the layout, the size, what it is required, the configuration.

set the title name. Then any KPIs like the revenue products, all those you need to display it, right?

So that you will have it. Then customer segmentation You can segment the customers.

You need to frequent buyers, non-frequent buyers, so you can decide the segmentation.

Then you can recommend the products.

Then after recommendation of the products for the inventory.

You can forecast that inventory required.

Then you can have the revenue visualization also. So any packages what are required, you will import those as required or if it is not there, you need to install.

Pi plot is for visualization.

Whatever the metrics you have found out in the previous, so here you are giving a suitable visualization in various chart, graph and so on. Yeah, so I think any other visualization metrics you want to add, you can add it. Basically all the visualization, you can try to have as many visualizations and analysis in the previous and here you can visualize those analysis.

So this is your module five. This is slightly big this particular milestone and hence.

Can we proceed further?

You want me to wait here for a couple of minutes or how?

So totally nine modules are there.

Can we proceed further?

I'll say this. Module six. So if this report lab package's library is not there, you need to install that. This is to generate the reports.

In the PDF form. So write a definition for the reports to save it in the PDF form which is preferable.

also on similar lines if you wanted in the excel form So, for the Excel you will make use of the pandas.

The form of rows and columns.

And you will and have the report in the form of the Excel.

So this is milestone six. So till here it is clear, able to follow or able to understand the flow of the topics.

I think all of you are aware, right?

It is the same meeting link for all the sessions on all the days Monday to Friday.

7, 8 and 9, we'll take it later or if time is there, we'll take it. So as of now, I will stop here.

---

## 4. MILESTONE 1 & 2 OVERVIEW MEETING TRANSCRIPT (Pasted text(3).txt)

Let's discuss what we can in brief.

So this is our title of our project, Shop Sense, Multivendor, E-commerce Analytics Platform.

Basically, we are going to develop a web page. and our complete project we are going to divide it into four modules.

So it is a shop sense multi vendor e-commerce analytics platform.

So, this is our project statement that we discussed in detail.

So this project statement is what is the company about, what it is going to perform, what are any issues, how it is going to solve.

So basically it is an e-commerce.

problem, okay?

So, wherein there are few issues.

We try to develop a platform, an e-commerce platform wherein there are various vendors.

The vendors come and register on the portal.

They will display their products and services on one side. On the other side, there are various users or customers who come to buy the various products and services.

So how is the demand being forecasted?

How are they going to manage the various orders?

What is the demand supply for which we are going to make use of a machine learning algorithm appropriately?

And we are going to use, you can use any of the open source.

platforms or applications that you want to place.

So here you are free to use any of the open source platforms, though there is no restriction on that. So basically here we try to understand what is the company working about, what are their issues and we try to solve it by developing a platform, use appropriate.

Techniques This is the project statement.

I will give you this letter go through and if any doubts you please ask because we need to proceed further.

Next is the outcomes, what we need to achieve.

There are a few outcomes.

So by the end of this particular internship project, we need to achieve these outcomes.

So this should be our objective.

Like maybe we have trying to have an appropriate focused model, predict it and so on. Okay. So how does the various vendors get onboarded on one side, the users on the other?

How are we going to predict the various products?

How are we going to forecast, understand the customer behavior?

So developing the dashboard.

So how are we going to analyze the data and so on. So all these are the outcomes.

So based on these outcomes we are going to divide our complete project into four milestones.

We divide it into four modules.

The first we want to start, it is the vendor management and marketplace onboarding any new vendor like they want to sign up on the portal.

So for that, we are having certain objectives.

So the vendor management and marketplace onboarding and how do they upload their products and services, how do we capture the information.

So all those things we try to accomplish here in this first.

module.

So there are four modules, each module will be having minimum four objectives.

So if we accomplish these four objectives, we try to achieve module one. All these four modules put together, we try to achieve our internship project.

So that is what. Finally, you will integrate everything and you will showcase.

So initially, when you will, you need to present the progress after each of these.

module.

So you will be having approximately one week to complete each module.

So after one week each of you independently you need to present the working demo, basically the web page, like how is the you are going to onboard, what is the login page. You will be having three modes.

One is the admin.

One is the vendor, another is the customer or the user. Three login pages we need to create.

That comes one by one. How are they going to upload their products?

How the user is going to create the profile?

Then how the admin is going to manage?

So all these things one by one comes up. Okay. So after this, then we have the second one which is the product and inventory analytics.

Then module three is with respect to the sales analytics and revenue intelligence.

So what I'll do, first I will give you in brief so that we'll get a complete overview of the project, then we'll take up one by one milestone and we will discuss how we will. the proceeding, right?

Next is with the customer behavior and analytics.

So here we will divide initially into six and then we will group it into four. So this is to analyze the behavior of the customer and analyze them and recommend suitable products and services customer retention.

Okay, so are you giving any offers, coupons, or something?

And so this is one basic structure which we intend to have, and in between maybe you want to add few other features so that you are free, but...

whatever this is given that is compulsory to implement.

Is that clear?

This is compulsory you want to add any other further innovation that you can add your own some objective something you want to add that you can do but whatever is present that compulsory needs to be done. reporting.

sound maatra haadkondu.

pipe. and all the working code you will be updating it in the GitHub.

One I will provide as optional last one. But dashboard you need to create that is compulsory.

Wherever if any number numerical comes, try as and when possible, try to have a pictorial graphical representation so it is easy to understand for the end user. And in between there will be some senior meters who will be coming and joining and they will ask you what is the progress and you need to show the working demo of the platform.

In between the sessions they would be coming in. Okay. Okay. So here there are approximately seven.

Dashboard is compulsory, right?

Sir will give you in the chat. You have a Word document and note it down. Because later it keeps on increasing at the time to give it is difficult.

Right?

It is your responsibility to note it down and carry it out. and execute and show the working demo. Okay. See this theory I'm not going much because as and when we find them we will discuss, we will directly take the first milestone and we will start so that you can work because in one week you need to complete this paper.

And all of you are receiving the mail for the session, right?

Yes, so maybe.

The session link, meeting link. So it is the same time and the same meeting link for all the days of the training.

There will be no change.

Although you will be getting it on a daily basis, but there will be no change in that. So, just in brief, so this Shopsense multi-vendor e-commerce analytics platform.

So this is our title.

It's got repeated a bit. So, we try to develop this particular web portal platform wherein we have divided it into six parts and again grouping it into four for our convenience.

So, this is our first milestone which is the marketplace foundation and vendor analytics.

This is our milestone and we have four objectives: implement the vendor onboarding, marketplace management, and product catalog modules.

So then design the database schema for vendors, products, transactions, and inventory management.

Build initial sales aggregation and reporting functionality.

Generate baseline marketplace analytics reports with revenue and product performance metrics.

So you are free to use any of the open source technologies and applications.

There is no restriction.

For example, for the database, you can make use of MySQL or any other suitable.

If you want any data, there are various places wherein you get the open source data which is going to meet our requirements.

Or you can generate the synthetic data, and maybe some 80% of the data you can make use of it for training and another 20% testing.

So for testing, you can make use of Postman.

Then you can make use of VS code for dashboard, you can make use of Streamlet, Power BI or Tabular programming, mainly Python.

is the focus which is most helpful.

You can interact, communicate, make use of various built-in packages and machine learning algorithms or any AI algorithms.

So first you concentrate on any machine learning algorithms, whichever is open source, you can take it for prediction, maintenance, scheduling of the products and so on. Any again open source artificial intelligence technique that you can make use of it appropriately.

You need to actively participate and work it out whatever is being guided that you need to follow and implement it, right?

So your 100% involvement is required.

Whatever we guide, you need to execute, implement, and carry out and then show it. then the expected output So this is the expected output what is required.

Okay. So till here it is clear, did you get an idea?

Few of you were not present yesterday.

Initially someone said not able to follow, is it?

Shweta, who is that?

Who was not able to fall?

Did you get an idea clear?

Yes, no, maybe, or Shreya.

So what about the get up thing that you said?

I wasn't present yesterday.

Okay, so each of you make sure that you have your individual GitHub link. If you do not have, you just create it and later on I will connect.

So in the GitHub link, whatever is the code of the complete project, you will be updating it in your Github profile, you create one folder.

In that folder, update the code in a systematic manner, the working code. Once you complete module by module.

Okay, and I will also be breaking it into groups.

So these groups are for you to facilitate and make sure like in case if you have any doubts and if you are not able to discuss any doubts in the session here, so you can feel free. to connect among yourself and you can discuss.

So the main objective is you should help out each other.

So for example, there is person A who knows some concept and person B who is finding it difficult to implement it, maybe you can help along each other.

So the main objective is like you can take help from anywhere.

But the final output which is the working demo individually, it has to be shown.

Is that clear?

Yes, no, maybe.

Yes, and For the there are various documentations to be done. Maybe the documentation you can do it as a group but later on you should not give reason that person A not working, person B not working for which I am not responsible, it is your responsibility but you can Work, the various documentation like various Word documents, PowerPoint presentation needs to be prepared.

You can prepare it in the group, but make sure that each one of you, you have that. Or you want to do it individually, you can do it. Okay, but I will create those groups in another few days and I will let you know, right?

Okay. So our milestone one is clear, the objectives are clear, what is the output is clear, right?

Next. Other objectives we'll see later.

Okay, I will give you the evaluation criteria.

Only for milestone one I will give you. Means what is expected?

How can we say that our milestone is okay?

So this is the evaluation criteria.

So vendor onboarding workflow successfully processes and validates the data of our vendor registration and it is 99% efficient.

Then there should be a sales analytics engine which is going to generate accurate revenue reports with 98% consistency.

Then, marketplace reporting dashboard successfully visualize the products and vendor performance metrics.

Okay, so from the first milestone itself, there should be a dashboard, right?

So this is the requirement expectation.

Only then we can say that our milestone is right.

These other milestones as and when required, I'll give you. Okay. I will give you one workflow diagram.

I think this should help you out. to understand the complete flow It is like a flowchart.

See, I think it is very much clear what should be the So initially we start, the vendors will register and the users will come and register.

The vendors will have a catalog, they will upload all their products and services.

And then the users they can search, recommend and various categories.

Then you can create the various views for the users also, for the vendors also to get the various details, price, inventory and You can have a wish list wherein the users can add the products to the wish list or they can add it to the cart and as per required they will check out, purchase that product, make the payment and after making the payment the order gets confirmed and the order fulfillment.

process will take place and deliver the order.

Okay, so this is the overall flowchart or the workflow diagram for our internship project, right?

Did you get an idea who were absent yesterday?

What is the overall flow?

So this we are dividing it appropriately.

Right?

Yes, no, maybe.

Okay, good. Next, we shall see architecture diagram.

See, this I'm giving it to you in brief, not elaborating much so that you will get a overall.

idea as to what we are performing, then you can concentrate on the execution of milestone one as and when you require, then we can discuss the concepts and you can work more with the hands-on part, right?

That is the overall idea. because one week approximately means you can keep sorry.

Approximately by 14 or 15 the milestone one needs to be complete so that's why. Next is the architecture diagram.

What is the overall architecture of our internship project?

I think this should be clear.

So initially there is a user or a shopper who wants to perform the shopping, they will come to the platform, search for the various product services, okay?

And there can be a AI recommendation system which is going to recommend.

suitable products.

Maybe there is a person who is searching for a television.

You may recommend a television stand to wall mount it. And you may want to personalize, you can personalize.

Maybe they want to purchase it from the laptop or from the mobile.

So if you want to develop an app, you can develop it. So the app as well, right?

Then you can develop a dashboard.

One dashboard for the user, one dashboard for the admin, and one dashboard for the Uh, vendor, then you can try to integrate any communication, then you may need to integrate it with the third party for the payment, so and so on, right?

So this is our architecture.

Next, the database which plays a very important part because we'll be having products, services, catalog, users.

various vendors and so on, right?

So this plays a very important part. Please by tomorrow try to design the database.

It would not take much time because you should be familiar, I think so. I'll give you the architecture for that. What should be the primary key, foreign key, what should be their relationship and so on, right?

Creation of various tables and the database.

See, you make a note of all this because this is going to help you in order to prepare all your documentation reports and the PowerPoint presentation.

You need not search at that time. Anyone can take. Now is it visible?

Anyone confirm?

Yes sir, it's visible.

Visible, no?

So this database, our complete first you create a database for our shop sense, give appropriate name and create the various tables.

The vendor, the user, products, catalogs.

Then for the payments, any wish list, various stores, brands, any recommendation, the user profile, vendor profile, okay, so all those and if you want to add any, you can, but these are few of the major things, right?

And what should be their primary key, what should be the foreign key, what should be their relationship.

So if it is a customer profile, the customer ID will be the primary.

The vendor profile, vendor ID. For the products, product ID. Correct.

So like those, use the IDs appropriately.

What should be the column names and the data types?

So all those, okay. I think you should be aware of this. Next, we'll move further.

Okay, I think for you this is fair enough.

These are few of the important.

Then, okay, then comes the rest of the milestones.

So now did you get an idea what we are going to perform?

showcase it. So how do we implement our first milestone?

Any idea anyone?

Please tell me here it is clear.

Yes sir. No doubts till here. Okay, just go through it. I will take the attendance in the meanwhile.

Hello Someone wanted to say something.

Yeah, for front end technologies, what technologies we want to use, sir?

See, one day any particular technologies.

There is no particular technology, you are free to make use of any of the open source platforms, applications, languages.

So as I said, for the dashboard you can use Streamlit, Power BI, Tableau.

Okay, then you can make use of VS code. Then for the database, you can make use of MySQL.

The programming language mainly you can make use of Python.

VS code for testing, you can make use of Postman.

Right, and there are various machine learning algorithms and AI algorithms which are open source that and again for deployment also there is one open source platform that you can use. So these are few of the major things.

Got it. Anything else in your mind?

If you answer your attendance, Ayushi, Amisha Singh, Rehan, Shri. Darshak.

Yes Sir. Darshak.

You can use HTML, CSS, React, anything you can use. Any open source, there is no restriction.

There Yasheka Yes sir Ashok Gayatri Unmute and answer, okay?

Imadullah.

---

## 5. MILESTONE 1 TRANSCRIPT / SPEC (transcript_step_0.txt)

<USER_REQUEST>
You are a senior Python full-stack engineer, software architect, database engineer, and UI/UX developer.



I am an Infosys Springboard intern building an academic project called:



# ShopSense – Multi-Vendor E-Commerce Analytics Platform



I have provided the official project transcript/specification. You must use that document as the primary source for understanding the project.



IMPORTANT:

I ONLY need to complete MILESTONE 1 (Weeks 1–2).



Do NOT implement later milestones or unnecessary AI/ML functionality.



The goal is to create a genuinely working, professional, demonstrable Milestone 1 application — not a static prototype.



============================================================

1. UNDERSTAND THE PROJECT

============================================================



ShopSense is a Multi-Vendor E-Commerce Analytics Platform.



The platform manages multiple vendors and their products while collecting transaction and inventory data and converting that data into marketplace analytics.



The overall project vision eventually includes advanced analytics, forecasting, recommendation systems, customer analytics, etc.



BUT MY CURRENT REQUIREMENT IS ONLY MILESTONE 1.



Milestone 1 focuses on:



- Vendor onboarding

- Marketplace management

- Product catalog

- Database design for vendors

- Database design for products

- Database design for transactions

- Database design for inventory

- Initial sales aggregation

- Sales reporting

- Baseline marketplace analytics

- Revenue metrics

- Product performance metrics

- Vendor performance visualization



Do not build the future modules.



============================================================

2. TECHNOLOGY REQUIREMENTS

============================================================



Use this technology stack:



BACKEND:

Python + FastAPI



FRONTEND / APPLICATION UI:

Streamlit



DATABASE:

MySQL



ORM / DATABASE ACCESS:

SQLAlchemy



DATA ANALYTICS:

Pandas



VISUALIZATION:

Plotly



VALIDATION:

Pydantic



AUTHENTICATION:

JWT-based authentication with secure password hashing



SERVER:

Uvicorn



TESTING:

Pytest



ENVIRONMENT CONFIGURATION:

python-dotenv



Do NOT use:

- PostgreSQL

- MongoDB

- SQLite as the main database

- React

- Flask



MySQL is the ONLY primary database.



============================================================

3. WHY FASTAPI

============================================================



The project transcript explicitly mentions REST APIs using FastAPI.



Therefore implement the backend as a proper FastAPI application.



FastAPI should provide REST APIs for:



- Authentication

- Vendor management

- Product management

- Inventory management

- Transactions

- Analytics



Streamlit should act as the user-facing dashboard/application interface.



The architecture should be:



User

  ↓

Streamlit UI

  ↓

FastAPI REST API

  ↓

SQLAlchemy

  ↓

MySQL



Analytics:



MySQL

  ↓

Python / Pandas

  ↓

Plotly

  ↓

Streamlit Dashboard



============================================================

4. AUTHENTICATION — VERY IMPORTANT

============================================================



The system must have proper authentication.



Do NOT create a fake login screen.



Implement actual authentication.



Create a users table.



Minimum user fields:



- user_id

- full_name

- email

- password_hash

- role

- is_active

- created_at



Roles:



ADMIN

VENDOR



Use secure password hashing.



Passwords must NEVER be stored as plain text.



Use JWT access tokens.



Implement:



POST /auth/register

POST /auth/login

GET /auth/me



Use OAuth2PasswordBearer or an equivalent FastAPI-compatible JWT implementation.



Protect all sensitive APIs using authentication.



Example:



Only authenticated users can access:

- dashboard

- vendors

- products

- inventory

- transactions

- analytics



Role-based access:



ADMIN:

- manage vendors

- manage products

- manage inventory

- view transactions

- view all analytics

- manage marketplace



VENDOR:

- view/update their own vendor information

- view their own products

- view their own inventory

- view their own sales/performance

- should NOT be able to access another vendor's private data



Make sure authorization is enforced in backend APIs, not only hidden in Streamlit.



============================================================

5. SECURITY REQUIREMENTS

============================================================



Implement basic production-style security:



- Password hashing

- JWT authentication

- Protected endpoints

- Role-based authorization

- Environment variables for secrets

- Never hardcode JWT secret

- Never hardcode database password

- Validate user input

- Validate email

- Prevent duplicate emails

- Proper HTTP status codes

- Avoid returning password hashes

- Handle authentication failures cleanly

- Handle unauthorized access with 401

- Handle forbidden access with 403



Create:



.env.example



Example:



DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/shopsense

SECRET_KEY=CHANGE_THIS_SECRET

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60



Never commit a real secret.



============================================================

6. MYSQL DATABASE

============================================================



Create MySQL database:



shopsense



Use SQLAlchemy ORM.



Use:



mysql+pymysql



Create these main tables:



1. users

2. vendors

3. products

4. inventory

5. transactions



You may add supporting tables only when genuinely necessary.



Do not overcomplicate the schema.



============================================================

7. DATABASE RELATIONSHIPS

============================================================



Use proper foreign keys.



Relationship:



User

  ↓

Vendor

  ↓

Products

  ↓

Inventory



Products + Vendors

  ↓

Transactions



Suggested relationships:



users:

user_id PK



vendors:

vendor_id PK

user_id FK → users.user_id where appropriate



products:

product_id PK

vendor_id FK → vendors.vendor_id



inventory:

inventory_id PK

product_id FK → products.product_id



transactions:

transaction_id PK

product_id FK → products.product_id

vendor_id FK → vendors.vendor_id



Use SQLAlchemy relationships where useful.



============================================================

8. VENDOR TABLE

============================================================



Vendor fields:



- vendor_id

- business_name

- owner_name

- email

- phone

- category

- commission_rate

- status

- created_at

- user_id if required for authentication



Status examples:



PENDING

ACTIVE

SUSPENDED



Implement proper vendor lifecycle handling.



============================================================

9. VENDOR ONBOARDING

============================================================



Implement real vendor onboarding.



Features:



- Vendor registration

- Validation

- Duplicate email prevention

- Vendor status

- Vendor profile

- Admin approval

- Activation/suspension



API endpoints:



POST /api/vendors

GET /api/vendors

GET /api/vendors/{vendor_id}

PUT /api/vendors/{vendor_id}

DELETE /api/vendors/{vendor_id}



Add appropriate role restrictions.



Vendor registration must validate:



- business name

- owner name

- email

- phone

- category



The implementation should support the milestone evaluation requirement of at least 99% successful validation.



Do not fake the 99%.



Actually implement strong validation and create tests demonstrating it.



============================================================

10. PRODUCT CATALOG

============================================================



Implement product management.



Product fields:



- product_id

- product_name

- category

- price

- stock

- vendor_id

- created_at



Features:



- Add product

- View products

- Update product

- Delete product

- Search

- Filter by category

- Filter by vendor



APIs:



POST /api/products

GET /api/products

GET /api/products/{product_id}

PUT /api/products/{product_id}

DELETE /api/products/{product_id}



Validation:



- product name required

- price > 0

- stock >= 0

- vendor must exist

- vendor must be authorized



============================================================

11. INVENTORY MANAGEMENT

============================================================



Create inventory table:



- inventory_id

- product_id

- current_stock

- warehouse

- reorder_level

- updated_at



Implement:



GET /api/inventory

GET /api/inventory/{product_id}

PUT /api/inventory/{product_id}



Inventory statuses:



IN STOCK

LOW STOCK

OUT OF STOCK



Logic:



if current_stock == 0:

    OUT OF STOCK



elif current_stock <= reorder_level:

    LOW STOCK



else:

    IN STOCK



Inventory must update when a transaction/sale occurs.



Never allow stock to become negative.



============================================================

12. TRANSACTION MANAGEMENT

============================================================



Create transactions table:



- transaction_id

- product_id

- vendor_id

- quantity

- amount

- transaction_date



Implement:



POST /api/transactions

GET /api/transactions

GET /api/transactions/{transaction_id}



When a transaction is created:



1. Verify product exists

2. Verify vendor exists

3. Verify available stock

4. Verify quantity > 0

5. Reduce inventory

6. Save transaction

7. Update analytics automatically through database data



The transaction and inventory update should be handled safely.



Do not allow:



quantity <= 0



or:



quantity > available_stock



============================================================

13. SALES AGGREGATION

============================================================



This is a core Milestone 1 requirement.



Use actual MySQL transaction data.



Calculate:



- Total Revenue

- Total Transactions

- Total Quantity Sold

- Revenue by Vendor

- Revenue by Product

- Revenue by Category

- Top Selling Product

- Top Performing Vendor

- Average Transaction Value

- Revenue by Date

- Revenue trend



Do NOT hardcode these metrics.



Whenever new transactions are added, dashboard analytics must reflect the new values.



============================================================

14. ANALYTICS ENGINE

============================================================



Use:



SQLAlchemy + Pandas + Plotly



Analytics should be generated from the database.



Create an analytics service/module rather than putting all calculations inside Streamlit.



Example functions:



get_total_revenue()

get_total_transactions()

get_total_quantity_sold()

get_vendor_revenue()

get_product_revenue()

get_top_products()

get_vendor_performance()

get_revenue_trend()



Create analytics APIs such as:



GET /api/analytics/summary

GET /api/analytics/vendor-performance

GET /api/analytics/product-performance

GET /api/analytics/revenue-trend



Protect analytics endpoints with authentication.



ADMIN can see marketplace-wide analytics.



VENDOR can see only their own authorized performance.



============================================================

15. STREAMLIT APPLICATION

============================================================



Build the complete user interface using Streamlit.



Do NOT make Streamlit just a static dashboard.



It must interact with the FastAPI backend.



Create:



dashboard/dashboard.py



The Streamlit application should contain:



LOGIN

DASHBOARD

VENDORS

PRODUCTS

INVENTORY

TRANSACTIONS

ANALYTICS

PROFILE / LOGOUT



Use sidebar navigation after login.



============================================================

16. LOGIN UI

============================================================



Create a professional login page.



Fields:



Email

Password



Buttons:



Login

Register



After successful login:



- receive JWT token

- maintain login session using Streamlit session state

- use token when calling protected FastAPI endpoints

- display user role

- redirect to dashboard



Implement logout.



Logout must clear the authentication state/token.



============================================================

17. ADMIN DASHBOARD

============================================================



Create a professional Admin Dashboard.



KPI cards:



Total Revenue

Total Vendors

Total Products

Total Transactions

Total Quantity Sold



Charts:



1. Revenue Trend

2. Revenue by Vendor

3. Product Performance

4. Top Selling Products

5. Inventory Status



Use Plotly.



Make it look like a real business analytics dashboard.



============================================================

18. VENDOR DASHBOARD

============================================================



When a vendor logs in, show only their authorized information.



Display:



- Vendor name

- Total revenue

- Products

- Transactions

- Quantity sold

- Top products

- Sales trend

- Inventory status



Do not expose another vendor's data.



============================================================

19. VENDOR MANAGEMENT UI

============================================================



Admin-only page.



Features:



- Add vendor

- View vendors

- Search vendors

- Filter vendors

- Update vendor

- Activate vendor

- Suspend vendor

- Delete vendor where appropriate



Display:



Business

Owner

Email

Phone

Category

Status

Created Date



============================================================

20. PRODUCT MANAGEMENT UI

============================================================



Features:



- Add product

- Edit product

- Delete product

- Search

- Filter

- Vendor filter

- Category filter



Display:



Product

Category

Vendor

Price

Stock

Status



============================================================

21. INVENTORY UI

============================================================



Display:



Product

Vendor

Current Stock

Reorder Level

Warehouse

Status



Use visual indicators for:



In Stock

Low Stock

Out of Stock



Allow authorized stock updates.



============================================================

22. TRANSACTIONS UI

============================================================



Display transaction history.



Columns:



Transaction ID

Product

Vendor

Quantity

Amount

Date



Admin can see marketplace transactions.



Vendor can see only their transactions.



Provide a transaction creation form for authorized users.



============================================================

23. ANALYTICS UI

============================================================



Create an Analytics page.



Filters:



- Date range

- Vendor

- Category

- Product



Metrics:



Revenue

Transactions

Quantity Sold

Average Transaction Value



Charts:



- Revenue trend

- Vendor performance

- Product perf

