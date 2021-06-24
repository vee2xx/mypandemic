import os
import admin.config as cfg
from google.cloud import bigquery
import datetime


class BigQueryClient(object):
    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cfg.get_config_value('google', 'credentials')
        self.client = bigquery.Client()

    def daily_covid_stats(self):
        yesterday =(datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
        query_job = self.client.query(
            """
            SELECT province_state as province, location_geom as location,
            confirmed, deaths, recovered, active 
            FROM `bigquery-public-data.covid19_jhu_csse.summary` 
            where country_region = 'Canada' and date >= '{}'
            """.format(yesterday)
        )

        results = query_job.result() 

        stats = []

        for row in results:
            province = '' if row.province == None  else row.province
            location = '' if row.location == None  else row.location
            confirmed = 0 if row.confirmed == None else row.confirmed
            deaths = 0  if row.deaths == None else row.deaths
            recovered = 0  if row.recovered == None else  row.recovered
            active = 0 if row.active == None else row.active
            stats.append({'country': 'Canada', 'province': province, 'date': yesterday, 'location': location, 'confirmed': confirmed, 'deaths': deaths, 'recovered': recovered, 'active': active})
        return stats

    def covid_stats_by_data_range(self, country, start_date, end_date):
        query_job = self.client.query(
            """
            SELECT province_state as region, date, location_geom as location,
            confirmed, deaths, recovered, active 
            FROM `bigquery-public-data.covid19_jhu_csse.summary` 
            where country_region = '{}' and date >= '{}'  and date <= '{}'
            """.format(country, start_date, end_date)
        )

        results = query_job.result() 

        stats = []

        for row in results:
            region = '' if row.region == None  else row.region
            location = '' if row.location == None  else row.location
            confirmed = 0 if row.confirmed == None else row.confirmed
            deaths = 0  if row.deaths == None else row.deaths
            recovered = 0  if row.recovered == None else  row.recovered
            active = 0 if row.active == None else row.active
            stats.append({'country': 'Canada', 'region': region, 'date': row.date, 'location': location, 'confirmed': confirmed, 'deaths': deaths, 'recovered': recovered, 'active': active})
        return stats
#### TESTING ONLY
# bgClient = BigQueryClient()
# bgClient.daily_covid_stats()