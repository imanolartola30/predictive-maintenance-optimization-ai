import pandas as pd
import sqlite3
connection = sqlite3.connect('../Proyecto1/data/maintenance.db')

errors = pd.read_csv('../Proyecto1/data/errors.csv')
failures = pd.read_csv('../Proyecto1/data/failures.csv')
machines = pd.read_csv('../Proyecto1/data/machines.csv')
maint = pd.read_csv('../Proyecto1/data/maint.csv')
telemetry = pd.read_csv('../Proyecto1/data/telemetry.csv')

errors['datetime'] = pd.to_datetime(errors['datetime'])
failures['datetime'] = pd.to_datetime(failures['datetime'])
maint['datetime'] = pd.to_datetime(maint['datetime'])
telemetry['datetime'] = pd.to_datetime(telemetry['datetime'])

errors.to_sql('errors', connection, if_exists='replace', index=False)
failures.to_sql('failures', connection, if_exists='replace', index=False)
machines.to_sql('machines', connection, if_exists='replace', index=False)
maint.to_sql('maint', connection, if_exists='replace', index=False)
telemetry.to_sql('telemetry', connection, if_exists='replace', index=False)



connection.close()