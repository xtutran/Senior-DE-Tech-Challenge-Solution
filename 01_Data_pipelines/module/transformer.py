# -*- coding: utf-8 -*-

"""
Main PySpark driver to process the application data. The main logic will be inside the Transformer class
"""
from __future__ import print_function

import logging
import os
from datetime import datetime

import pyspark.sql.functions as F
from pyspark.sql import SparkSession, DataFrame, Column
from pyspark.sql.types import StringType, IntegerType, ArrayType, DateType, BooleanType

from module import helper


class Transformer(object):
    """
    The main ETL logic in PySpark
    """

    def __init__(self, input_path: str, output_path: str, etl_time: str = None, file_fmt: str = "csv"):
        """
        Constructor method to initialize a Transformer

        :param input_path: the raw input path
        :param output_path: the output directory
        :param etl_time: ETL run time, if None current timestamp will be used. This could be used to backfill the pipeline in case of failed job
        :param file_fmt: input data format which support csv, json, parquet, csv is by default
        """

        if etl_time is None:
            self.etl_time = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        else:
            self.etl_time = etl_time

        self.input_path = input_path
        self.out_path = output_path
        self.file_fmt = file_fmt
        assert file_fmt is not None and file_fmt.lower() in ["csv", "json",
                                                             "parquet"], "Only support file format as CSV or JSON or PARQUET"

        self.spark = SparkSession \
            .builder \
            .getOrCreate()

        self.input_data: DataFrame = None
        self.output_data: DataFrame = None
        self.stats_data: DataFrame = None

        sc = self.spark.sparkContext
        sc.setLogLevel("INFO")

        self.logger = sc._jvm.org.apache.log4j.LogManager.getLogger(Transformer.__name__)
        self.spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
        sc._jsc.hadoopConfiguration().set('mapreduce.fileoutputcommitter.marksuccessfuljobs', 'false')
        sc._jsc.hadoopConfiguration().set('parquet.enable.summary-metadata', 'false')

    def load(self):
        """
        Load method to read data from folder and store Spark SQL DataFrame to `input_data`
        :return:
        """

        if self.file_fmt.lower() == "csv":
            reader = self.spark.read.option("header", "true").option("inferSchema", "false").csv
        elif self.file_fmt.lower() == "parquet":
            reader = self.spark.read.parquet
        else:
            reader = self.spark.read.json

        self.input_data = reader(self.input_path)

        return self

    def transform(self):
        """
        Transform method - main ETL logic will be implemented here. This method will clean & transform the input_data and store to `output_data`
        :return:
        """

        if self.input_data is None or len(self.input_data.head(1)) == 0:
            self.logger.warn("Input data is missing or empty!!!")
            return

        # user define function
        clean_mobile_number_udf = F.udf(helper.clean_mobile_number, IntegerType())
        clean_birthday_udf = F.udf(helper.clean_birthday, DateType())
        is_over_18_udf = F.udf(helper.is_over_18, BooleanType())
        is_valid_email_udf = F.udf(helper.is_valid_email, BooleanType())
        is_valid_mobile_number_udf = F.udf(helper.is_valid_mobile_number, BooleanType())
        split_fullname_udf = F.udf(helper.split_fullname, ArrayType(StringType()))
        gen_membership_id_udf = F.udf(helper.gen_membership_id, StringType())
        valid_name: Column = F.col("name").isNotNull() & (F.col("name") != '')

        trim_cols = [F.trim(F.col(c)).alias(c) for c in self.input_data.columns]
        transformed_data = self.input_data.select(*trim_cols) \
            .withColumn("mobile_no", clean_mobile_number_udf(F.col('mobile_no'))) \
            .withColumn("date_of_birth", clean_birthday_udf(F.col('date_of_birth'))) \
            .withColumn("is_valid_email", is_valid_email_udf(F.col("email"))) \
            .withColumn("is_valid_mobile_number", is_valid_mobile_number_udf(F.col("mobile_no"))) \
            .withColumn("over_18", is_over_18_udf(F.col("date_of_birth"))) \
            .withColumn("is_succeed", F.col("is_valid_email") & F.col("is_valid_mobile_number") & F.col("over_18") & valid_name) \
            .withColumn("date_of_birth", F.date_format(F.col("date_of_birth"), "yyyyMMdd")) \
            .withColumn("fullname", split_fullname_udf(F.col("name"))) \
            .withColumn("first_name", F.col("fullname").getItem(0)) \
            .withColumn("last_name", F.col("fullname").getItem(1)) \
            .withColumn("membership_id", F.when(F.col("is_succeed"), gen_membership_id_udf(F.col("last_name"), F.col("date_of_birth"))).otherwise(F.lit(None))) \
            .withColumn("etl_time", F.lit(self.etl_time))

        self.output_data = transformed_data
        return self

    def stats(self):
        """
        This method to used to compute data statistic and store to `stats_data`. This stats data will be helpful to assess data quality and troubleshoot the etl job
        :return:
        """

        if self.output_data is None:
            self.logger.warn("Output data is missing or empty!!! No action for running data stats")
            return

        stats_data = self.output_data.groupBy("etl_time").agg(
            F.count("name").alias("nb_rows"),
            F.round(F.mean(F.col("is_valid_email").cast(IntegerType())), 4).alias("percent_valid_email"),
            F.round(F.mean(F.col("is_valid_mobile_number").cast(IntegerType())), 4).alias("percent_valid_mobile_number"),
            F.round(F.mean(F.col("over_18").cast(IntegerType())), 4).alias("percent_over_18"),
            F.round(F.mean(F.col("is_succeed").cast(IntegerType())), 4).alias("percent_succeed_application")
        ).withColumn("input_path", F.lit(self.input_path))
        self.stats_data = stats_data

        return self

    def store(self):
        """
        This method to save the data back to `output_path`.
        There are 3 possible output: `succeed` for successful applications, `failed` for unsuccessful applications, `stats` for data stats summary
        :return:
        """

        if self.output_data is None:
            self.logger.warn("Output data is missing or empty!!! No action for storing output")

            return

        select_cols = ['name', 'first_name', 'last_name', 'email', 'mobile_no', 'date_of_birth', 'over_18',
                       'membership_id', 'etl_time']

        succeed_applications = self.output_data.where(F.col("is_succeed")).select(*select_cols)
        succeed_path = os.path.join(self.out_path, "succeed")
        succeed_applications.write \
            .option("partitionOverwriteMode", "dynamic") \
            .partitionBy("etl_time").mode("overwrite").parquet(succeed_path)

        failed_applications = self.output_data.where(~F.col("is_succeed")).select(*select_cols)
        failed_path = os.path.join(self.out_path, "failed")
        failed_applications.write \
            .option("partitionOverwriteMode", "dynamic") \
            .partitionBy("etl_time").mode("overwrite").parquet(failed_path)

        if self.stats_data is not None:
            stats_path = os.path.join(self.out_path, "stats")
            # combine to one file since the stats data is just one row
            self.stats_data.coalesce(1).write.mode("append").csv(stats_path)
