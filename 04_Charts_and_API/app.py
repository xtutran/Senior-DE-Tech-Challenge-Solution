# -*- coding: utf-8 -*-
"""
Covid19 Dashboard
"""
from __future__ import print_function
from datetime import date, timedelta
import requests
import streamlit as st
import pandas as pd
import numpy as np


class Dashboard(object):

    def __init__(self, title):
        self.title = title

    @staticmethod
    @st.cache_data
    def load_data(country: str, start_date: str, end_date: str):

        url = f'https://api.covid19api.com/country/{country}/status/confirmed?from={start_date}&to={end_date}'
        resp = requests.get(url)
        if resp.status_code == 200:
            return pd.json_normalize(resp.json())
        else:
            return pd.DataFrame()

    @staticmethod
    @st.cache_data
    def process_data(df: pd.DataFrame):
        # data = df.groupby(['Country', 'Date']).sum().reset_index()
        data = df.copy()
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.sort_values('Date').set_index('Date')
        data['NewCases'] = data['Cases'].diff().fillna(method='backfill')
        return data[['Cases', 'NewCases', 'Status']]

    def layout(self):
        st.title(self.title)

        start_date = st.date_input('Start Date', value=date.today() - timedelta(days=30))
        end_date = st.date_input('End Date')

        with st.spinner('Requesting Covid-19 cases data in Singapore...'):
            data = self.load_data('singapore', start_date.strftime("%Y-%m-%dT00:00:00Z"), end_date.strftime("%Y-%m-%dT00:00:00Z"))

        if st.checkbox('Show raw data'):
            st.subheader('Covid-19 cases data in Singapore')
            st.write(data)

        with st.spinner('Processing data ...'):
            agg_data = self.process_data(data)

        if st.checkbox('Show processed data'):
            st.subheader('Confirmed cases in Singapore')
            st.write(agg_data)

        if len(agg_data) > 0:
            st.subheader(f'Number of new cases in Singapore')
            st.bar_chart(agg_data[['NewCases']])


def main():
    dashboard = Dashboard("Covid19 Cases")
    dashboard.layout()


if __name__ == '__main__':
    main()


