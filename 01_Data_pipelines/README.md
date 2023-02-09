# Data Pipeline using PySpark & Airflow as job scheduler

## 1. Code structure
```
.
├── Makefile   # SIMPLE Makefile TO RUN THE JOB LOCALLY
├── README.md  # DOCUMENTATION
├── airflow_dag.py # SIMPLE DAG TO SCHEDULE JOB IN AIRFLOW
├── data       # INPUT DATA
│   ├── applications_dataset_1.csv
│   └── applications_dataset_2.csv
├── main.py
├── module  # MAIN SOURCE CODE
│   ├── __init__.py
│   ├── helper.py
│   └── transformer.py
├── output  # OUTPUT 
│   ├── failed
│   ├── stats
│   └── succeed
├── requirements.txt
├── run.log # JOB LOG
├── test    # UNIT TEST
    ├── __init__.py
    ├── pytest.ini
    └── test_helper.py
```


## 2. Local Running &  Testing

- Creating a virtual environment
```bash
make venv
```

- Run `unit test`
```bash
make run_unit_test
```

- Expected output of `pytest`
```
======================================================================================= test session starts =======================================================================================
platform darwin -- Python 3.9.12, pytest-7.2.1, pluggy-1.0.0
rootdir: /Users/txuantu/Documents/Projects/Interview_2023/GovTech/01_Tech_Assignment/Senior-DE-Tech-Challenge-Solution/01_Data_pipelines/test, configfile: pytest.ini
plugins: anyio-3.6.2
collected 6 items                                                                                                                                                                                 

test_helper.py::test_is_valid_email PASSED                                                                                                                                                  [ 16%]
test_helper.py::test_clean_birthday PASSED                                                                                                                                                  [ 33%]
test_helper.py::test_gen_membership_id PASSED                                                                                                                                               [ 50%]
test_helper.py::test_clean_mobile_number PASSED                                                                                                                                             [ 66%]
test_helper.py::test_is_valid_mobile_number PASSED                                                                                                                                          [ 83%]
test_helper.py::test_split_fullname PASSED                                                                                                                                                  [100%]

======================================================================================== 6 passed in 0.07s ========================================================================================
(venv) ╭─txuantu@Trans-MBP-3 ~/Documents/Projects/Interview_2023/GovTech/01_Tech_Assignmen
```

- Run the job locally

``` 
usage: main.py [-h] --input INPUT --output OUTPUT [--format FORMAT] [--stats STATS] [--etl-time ETL_TIME]

optional arguments:
  -h, --help           show this help message and exit
  --input INPUT        Raw application data
  --output OUTPUT      Output directory
  --format FORMAT      Input data format
  --stats STATS        True to generate statistic data
  --etl-time ETL_TIME  ETL run time, format: YYYYmmdddHHMMSS

```

- Run the job using sample input in `data` folder

```bash
make run_local
```

- Output log would be store in `run.log`, example (truncated)
```
etting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
23/02/09 18:03:30 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
23/02/09 18:03:31 WARN Utils: Service 'SparkUI' could not bind on port 4040. Attempting port 4041.
23/02/09 18:03:31 INFO SharedState: Setting hive.metastore.warehouse.dir ('null') to the value of spark.sql.warehouse.dir.
23/02/09 18:03:31 INFO SharedState: Warehouse path is 'file:/Users/txuantu/Documents/Projects/Interview_2023/GovTech/01_Tech_Assignment/Senior-DE-Tech-Challenge-Solution/01_Data_pipelines/spark-warehouse'.
23/02/09 18:03:32 INFO InMemoryFileIndex: It took 29 ms to list leaf files for 1 paths.
23/02/09 18:03:32 INFO InMemoryFileIndex: It took 2 ms to list leaf files for 2 paths.
23/02/09 18:03:34 INFO FileSourceStrategy: Pushed Filters: 
23/02/09 18:03:34 INFO FileSourceStrategy: Post-Scan Filters: (length(trim(value#0, None)) > 0)
23/02/09 18:03:34 INFO FileSourceStrategy: Output Data Schema: struct<value: string>
23/02/09 18:03:34 INFO CodeGenerator: Code generated in 132.06732 ms
23/02/09 18:03:34 INFO MemoryStore: Block broadcast_0 stored as values in memory (estimated size 200.1 KiB, free 434.2 MiB)
23/02/09 18:03:34 INFO MemoryStore: Block broadcast_0_piece0 stored as bytes in memory (estimated size 34.4 KiB, free 434.2 MiB)
23/02/09 18:03:34 INFO BlockManagerInfo: Added broadcast_0_piece0 in memory on trans-mbp-3:54189 (size: 34.4 KiB, free: 434.4 MiB)
23/02/09 18:03:34 INFO SparkContext: Created broadcast 0 from csv at NativeMethodAccessorImpl.java:0
23/02/09 18:03:34 INFO FileSourceScanExec: Planning scan with bin packing, max size: 4194304 bytes, open cost is considered as scanning 4194304 bytes.
23/02/09 18:03:34 INFO SparkContext: Starting job: csv at NativeMethodAccessorImpl.java:0
23/02/09 18:03:34 INFO DAGScheduler: Got job 0 (csv at NativeMethodAccessorImpl.java:0) with 1 output partitions
23/02/09 18:03:34 INFO DAGScheduler: Final stage: ResultStage 0 (csv at NativeMethodAccessorImpl.java:0)
23/02/09 18:03:34 INFO DAGScheduler: Parents of final stage: List()
23/02/09 18:03:34 INFO DAGScheduler: Missing parents: List()
...
```

## 3. Job scheduling
- Use a simple dag which would be deployed into any Apache Airflow scheduler.
- Simply copy the dag: `ariflow_dag.py`, `module` & `main.py` to the `dags` folder of Airflow
- The job will be scheduled to run every hour start at `2023-02-09 23:59:29`, next run would be `2023-02-10 00:59:59` ...
- This DAG should only use for development and proof of concept only since this is just a spark job in standalone cluster mode
- For production, the DAG should use a Spark operator or `spark-submit` to send the job to production cluster (for example, using AWS EMR or on-premise Hadoop cluster ...) 

```python
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

```