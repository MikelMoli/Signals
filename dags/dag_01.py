from datetime import timedelta
from email.charset import BASE64
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

import sys
sys.path.insert(0,"/opt/airflow/dags/functions")
from functions.extract import extract


dag = DAG(
    'ingest_data',
    description='ETL for historical stock data',
    schedule_interval = timedelta(days=7),
    start_date=days_ago(1)
)

check_wd = BashOperator(
    task_id='check',
    bash_command='echo -------------------------- EMPIEZA ------------------------',
    dag=dag
)

# add creation of venv and package installation if it is not created
extract_data_task = PythonOperator(
    task_id='extract_all_data',
    python_callable=extract,
    dag=dag
)

check_wd >> extract_data_task 