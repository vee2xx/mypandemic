import numpy as np
import datetime
from dateutil import tz
from pytz import timezone
import math
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import messages.alerts
import admin.config as cfg
import models.user
import models.stat
import models.delta
import models.region


from dbaccess.bigqueryclient import BigQueryClient

utc = timezone('UTC')

#TODO: add unique constraint for day and region
def update_stats(country, start_date, end_date):
    max_date = models.stat.get_max_date()
    # Check to see if db is already up to date
    if max_date is not None:
        max_date = max_date.strftime("%Y-%m-%d") 
        if max_date >= end_date:
            return
        if max_date >= start_date:
            start_date = datetime.datetime.strptime(max_date, "%Y-%m-%d").date() + datetime.timedelta(1)
    stats = BigQueryClient().covid_stats_by_data_range(country, start_date, end_date)
    for i in range(len(stats)):
        stat = models.stat.Stat()
        stat.country = stats[i]['country']
        stat.region = stats[i]['region']
        stat.location = stats[i]['location']
        stat.date = stats[i]['date'] 
        stat.confirmed = stats[i]['confirmed']
        stat.deaths = stats[i]['deaths']
        stat.recovered = stats[i]['recovered']
        stat.active = stats[i]['active']
        stat.current_count = stats[i]['confirmed']

        stat.save()

#TODO: add unique constraint for day and region
def save_deltas(country, start_date, end_date):
    max_date = models.delta.get_max_date()
        # Check to see if db is already up to date
    if max_date is not None:
        max_date = max_date.strftime("%Y-%m-%d") 
        if max_date >= end_date:
            return
        if max_date >= start_date:
            start_date = datetime.datetime.strptime(max_date, "%Y-%m-%d").date() + datetime.timedelta(1)
    stats = models.stat.find_stats_by_date_range(country, start_date, end_date)
    for stat in stats:
        previous_day = (stat.date - datetime.timedelta(1)).strftime("%Y-%m-%d")
        previous_count = models.stat.get_count_by_region_and_date(stat.region, previous_day)

        new_cases = 0
        percent_delta = 0

        if previous_count is not None:
            new_cases = stat.confirmed - previous_count

        if new_cases > 0 and previous_count > 0:
            percent_delta = (new_cases / previous_count) * 100

        delta = models.delta.Delta()
        delta.country = stat.country
        delta.region = stat.region
        delta.date = stat.date
        delta.new_cases = new_cases
        delta.percent_delta = percent_delta

        delta.save()

def get_covid_count_by_date_range(days):
    start_date = (datetime.datetime.now(tz=utc) - datetime.timedelta(days)).strftime("%Y-%m-%d")
    counts = []
    #TODO: Get this from logged in user preferences
    country = 'Canada'
    regions = models.region.find_region_by_country('Canada')
    region_counts = {}
    for region in regions:
        stats = models.stat.find_stats_by_region_and_date_range(region.region, start_date, datetime.datetime.now(tz=utc))
        for stat in stats:
            if stat.region not in region_counts.keys():
                region_counts[stat.region] = []
            count_for_date = {'date': stat.date.strftime("%Y-%m-%d"),'count': stat.confirmed}
            region_counts[stat.region].append(count_for_date)

    for region in region_counts:
        counts.append({'region': region, 'counts': region_counts[region]})
    return counts

def get_new_cases_by_date_range(days):
    start_date = (datetime.datetime.now(tz=utc) - datetime.timedelta(days)).strftime("%Y-%m-%d")
    regions = models.region.find_region_by_country('Canada')
    new_cases = []
    region_new_cases = {}
    for region in regions:
        results = models.delta.find_deltas_by_date_range(region.region, start_date, datetime.date.today())
        for result in results:
            if result.region not in region_new_cases.keys():
                region_new_cases[result.region] = []
            new_cases_for_date = {'date': result.date.strftime("%Y-%m-%d"),'new_cases': result.new_cases}
            region_new_cases[result.region].append(new_cases_for_date)

    for region in region_new_cases:
        new_cases.append({'region': region, 'new_cases': region_new_cases[region]})
    return new_cases

def get_percent_delta_by_date_range(days):
    start_date = (datetime.datetime.now(tz=utc) - datetime.timedelta(days)).strftime("%Y-%m-%d")
    regions = models.region.find_region_by_country('Canada')
    percent_deltas = []
    region_percent_deltas = {}
    for region in regions:
        results = models.delta.find_deltas_by_date_range(region.region, start_date, datetime.date.today())
        for result in results:
            if result.region not in region_percent_deltas.keys():
                region_percent_deltas[result.region] = []
            percent_deltas_for_date = {'date': result.date.strftime("%Y-%m-%d"),'percent_delta': result.percent_delta}
            region_percent_deltas[result.region].append(percent_deltas_for_date)

    for region in region_percent_deltas:
        percent_deltas.append({'region': region, 'percent_deltas': region_percent_deltas[region]})
    return percent_deltas

def get_current_covid_stats():
    max_date = models.stat.get_max_date()
    date = (datetime.datetime.now(tz=utc) - datetime.timedelta(2))
    date = date.date()
    if max_date is not None:
        if max_date > date:
            date = max_date
    date = date.strftime("%Y-%m-%d")
    #TODO: Get this from logged in user preferences
    country = 'Canada'
    counts = []
    regions = models.region.find_region_by_country(country)
    for region in regions:
        result = models.delta.find_delta_by_region_and_date(region.region, date)
        if result is not None:
            stat_results = models.stat.find_stats_by_region_and_date(result.region, date)
            counts.append({'region': stat_results.region, 'count': stat_results.confirmed, 'new_cases': result.new_cases})
    return counts

def get_current_deltas_by_region(region):
    date = models.stat.get_max_date()
    if date is None:
        return {'date': (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d"), 'new_cases' : 0, 'percent_delta': 0} 
    
    delta = models.delta.find_delta_by_region_and_date(region, date)
    return {'date': delta.date, 'new_cases' : delta.new_cases, 'percent_delta': delta.percent_delta}


def get_current_count_by_region(region):
    date = models.stat.get_max_date()
    if date is None:
        return 0

    daily_count = models.stat.get_count_by_region_and_date(region, date)
    return daily_count


def send_alert():
    regions = models.region.find_region_by_country('Canada')
    for region  in regions:
        count = get_current_count_by_region(region.region)

        delta = get_current_deltas_by_region(region.region)
        percent_delta = delta['percent_delta']
        if math.isnan(percent_delta):
            percent_delta = 0.0
            
        new_cases = delta['new_cases']
        if math.isnan(new_cases):
            new_cases = 0
        users = models.user.find_users_by_region(region.region)
        latest_stats_date = delta['date']
        dashboard_url = "{}://{}/".format(cfg.get_config_value('dashboard', 'protocol'), cfg.get_config_value('dashboard', 'host'))
        message = "{}\nThe pandemic numbers in {} are: \n\tTotal cases: {}\n\tNew cases: {}\n\tPercent difference: {}\n\n\t{}".format(latest_stats_date, region.region, str(count), str(new_cases), str(percent_delta), dashboard_url)
        for user in users:
            messages.alerts.send_sms_message(message, user.phone_number)



#### For testing only ##### 
# start_date = (datetime.date.today() - datetime.timedelta(30)).strftime("%Y-%m-%d")
# end_date = datetime.date.today().strftime("%Y-%m-%d")  
# update_stats('Canada', start_date, end_date)
# save_deltas('Canada', start_date, end_date)
# print(get_covid_count_by_date_range(30))
# print(get_increases_by_date_range(30))
# print(get_current_increase_by_province('British Columbia'))
# print(get_daily_count_by_province('British Columbia'))
# send_alert()
# get_current_covid_stats()

# local_tz = timezone('America/Vancouver')
# utc = timezone('UTC')
# dt_utc = datetime.datetime(2020, 12, 13, 3, 37, 1, tzinfo=utc)
# dt_utc = datetime.datetime.utcnow()
# today_utc = datetime.datetime.utcnow()
# dt = local_tz.localize(dt_utc)
# fmt = '%Y-%m-%d %H:%M:%S %Z (%z)'
# dt = dt_utc.astimezone(local_tz)
# print(dt)
# print(datetime.datetime.utcnow())
# print(datetime.datetime.now(tz=utc))
# print(datetime.datetime.now().astimezone(local_tz))
# today_local = today_utc.astimezone()
# print(today_local)