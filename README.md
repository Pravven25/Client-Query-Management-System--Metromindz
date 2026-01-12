Client Query Management System

A Data-Driven Support Query Tracking Application

🔍 Project Overview

The Client Query Management System is a data-driven web application designed to organize, track, and close customer support queries efficiently.

This project simulates a real-world support system where:

Clients can submit queries in real time

Support teams can monitor and resolve queries

Managers can analyze query trends and service performance

The project focuses on Python, SQL, and Data Engineering fundamentals, with a simple and user-friendly interface built using Streamlit.

 Problem Statement

Many organizations struggle to manage customer queries due to:

Manual tracking

Delayed responses

Lack of clear query status

Poor data organization

This project solves the problem by:

Storing queries in a structured SQL database

Tracking query lifecycle (Open → Closed)

Measuring query resolution time

Improving service efficiency and customer satisfaction

 Business Use Cases

 Real-time client query submission

 Live dashboard for support teams

 Faster issue resolution

 Support workload monitoring

 Identification of common query types

 Data-backed service improvement

🛠️ Technologies Used
Programming & Tools

Python – Core logic and data processing

Pandas – Data loading and cleaning

Streamlit – Web dashboard and UI

MySQL / SQLite – Backend database

Libraries

pandas

datetime

mysql-connector-python

hashlib

 Dataset Description

The project uses a CSV file to simulate incoming client queries.

Dataset Columns:

query_id

mail_id

mobile_number

query_heading

query_description

status (Open / Closed)

query_created_time

query_closed_time

 Login & Security Features

Separate login for Client and Support Team

Passwords are hashed using SHA-256

No plain-text password storage

Role-based access control

Project Workflow

User registers and logs in

Client submits a support query

Query is stored in MySQL database

Support team views all queries

Support team closes resolved queries

System updates status and timestamps

Dashboard shows live query insights

 Key Features

 Live query intake

 Real-time query tracking dashboard

 Resolution time calculation

 Filter queries by status

 Clean and structured data storage

 SQL-based insert and update operations

 Insights Generated

Average query resolution time

Open vs closed query count

Support workload analysis

Query backlog tracking

Service performance evaluation

 Data Cleaning Steps

Removed empty or invalid records

Standardized query status values

Validated mobile number length

Handled NULL values for open queries

Ensured consistent timestamp format

 Project Architecture

Frontend: Streamlit

Backend: Python

Database: MySQL / SQLite

Data Source: CSV → SQL Database

📁 Project Structure
├── data/
│   └── client_queries.csv
├── database/
│   └── schema.sql
├── app.py
├── db_connection.py
├── utils.py
├── README.md

 How to Run the Project

Clone the repository

Install required libraries

pip install -r requirements.txt


Configure database connection

Run the Streamlit app

streamlit run app.py

Project Evaluation Highlights

✔ Clean and maintainable code

✔ Modular Python functions

✔ Proper SQL usage (No ORM)

✔ Clear documentation

✔ Real-world business relevance

✔ Interview-ready project

🎓 Skills Gained from This Project

Python programming

SQL query writing

Data cleaning and organization

Backend data handling

Dashboard development

Real-world data engineering mindset

 Future Enhancements

Cloud database integration

Advanced analytics charts

Email notifications

Admin-level reporting

Role-based permissions

📌 Final Note

This project demonstrates my ability to:

Work with structured data

Design SQL-based systems

Write clean and readable Python code

Build dashboards for business users

It reflects real-world data engineering and analytics use cases, not just academic concepts.
