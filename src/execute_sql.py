import pandas as pd
import sqlite3
connection = sqlite3.connect('../Proyecto1/data/maintenance.db')

with open('../Proyecto1/sql/analytical_queries.sql', 'r') as file:
    sql_script = file.read()
query = sql_script.split(';')

# We will use some of the queries to create tables for the notebook, so we will execute them individually.
# Query 1: Average days since last failure by machine model and age
avg_days = pd.read_sql_query(query[0], connection)
with open('reports/avg_days_tab.md', 'w', encoding='utf-8') as f:
    f.write(avg_days.to_markdown(index=False))

# Query 2 and 3: Average and standard deviation of telemetry data in the 24 hours before a failure
avg_stddev_24 = pd.read_sql_query(query[1], connection)
avg_stddev = pd.read_sql_query(query[2], connection)
avg_stddev['failure'] = 'Total'
avg_stddev_total = pd.concat([avg_stddev_24, avg_stddev], ignore_index=True)
with open('reports/avg_stddev_tab.md', 'w', encoding='utf-8') as f:
    f.write(avg_stddev_total.to_markdown(index=False))

# Query 4: Percentage of times there is an error and has a failure in less than 48h
percentage_with_error = pd.read_sql_query(query[3], connection)
with open('reports/percentage_with_error_tab.md', 'w', encoding='utf-8') as f:
    f.write(percentage_with_error.to_markdown(index=False))

connection.close()