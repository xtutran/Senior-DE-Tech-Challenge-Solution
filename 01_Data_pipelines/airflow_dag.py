from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
        'govtech_de_tech_assessment',
        schedule_interval='0 * * * *',
        default_args={'retries': 1},
        tags=[""],
        start_date=datetime(2023, 2, 9, 23, 59, 59),
) as dag:
    etl_job = BashOperator(
        task_id='process_membership_application',
        bash_command='python main.py --input data/{{ ts_nodash }} --output output --stats True --etl-time {{ ts_nodash }}',
    )

if __name__ == '__main__':
    dag.cli()
