import stats.covidstats
import time
import logging
import logging.handlers
import json
import os
import concurrent.futures
import asyncio
import admin.config as cfg
import messages.alerts
import datetime
from dateutil import tz
from pytz import timezone
import bcrypt

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
import json
import uvicorn

from logging.handlers import RotatingFileHandler

import admin.utils
import models.user
import pkg_resources

app = FastAPI()
templates = Jinja2Templates(directory="resources/templates")
app.mount("/static", StaticFiles(directory=pkg_resources.resource_filename(__name__, 'resources/static/images')), name="static")

log_dir = cfg.get_config_value('logging', 'logdir')
max_size = cfg.get_config_value('logging', 'maxsize')

utc = timezone('UTC')

ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

handler = RotatingFileHandler(log_dir + '/mypandemic.log', maxBytes=int(max_size), backupCount=5)
formatter = logging.Formatter('%asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(cfg.get_config_value('logging', 'loglevel'))
root.addHandler(handler)

default_user = 'slugsy'

    
@app.get("/")
async def get_stats(request: Request):
    username = request.query_params.get('username')

    if username is None:
        user = models.user.find_by_username(default_user)
    else:
        user = models.user.find_by_username(username)

    currstats = stats.covidstats.get_current_covid_stats()
    today_utc = datetime.datetime.now(tz=tz.gettz('UTC'))
    today_local = today_utc.astimezone(tz.gettz(user.timezone))

    new_cases = stats.covidstats.get_new_cases_by_date_range(30)
    percent_deltas = stats.covidstats.get_percent_delta_by_date_range(30)
    counts = stats.covidstats.get_covid_count_by_date_range(30)
    return templates.TemplateResponse('covidstats/index.html', {'request':request,'currstats': currstats, 'today': today_local.strftime("%Y-%m-%d"), 'newcases': new_cases, 'percentdeltas': percent_deltas, 'counts': counts})

@app.post('/user/add')
def add_user(new_user: models.user.UserResponseModel, current_user: models.user.User = Depends(admin.utils.verify_token)):
    if current_user.role != 1:
        return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        )
    new_user.role = 0
    user_orm = models.user.user_model_to_orm(new_user)
    user_orm.save()
    return "User added"  

@app.post('/update_stats')
async def update_stats(days:Optional[int] = Query(..., gt=0, lt=31), current_user: models.user.User = Depends(admin.utils.verify_token)):
    if current_user.role != 1:
        return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        )
    
    start_date = (datetime.datetime.now(tz=utc)- datetime.timedelta(int(days))).strftime("%Y-%m-%d")
    end_date = datetime.datetime.now(tz=utc).strftime("%Y-%m-%d")     
    stats.covidstats.update_stats('Canada', start_date, end_date)
    stats.covidstats.save_deltas('Canada', start_date, end_date)
    return "Stats successfully updated"

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = models.user.find_by_username(username)
    is_authorized = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
    if user is None:
        raise HTTPException(status_code=400, detail="Username or password incorrect")
    else:
        if is_authorized is False:
            raise HTTPException(status_code=400, detail="Username or password incorrect")
        else:
            access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = admin.utils.create_access_token(data={"sub": user.username, 'iss': 'slugsy.me'}, expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "Bearer"}
    


def daily_covid_stats_job():
    start_date = (datetime.datetime.now(tz=utc)- datetime.timedelta(2)).strftime("%Y-%m-%d")
    end_date = datetime.datetime.now(tz=utc).strftime("%Y-%m-%d")     
    stats.covidstats.update_stats('Canada', start_date, end_date)
    stats.covidstats.save_deltas('Canada', start_date, end_date)

def send_stats_job():
    stats.covidstats.send_alert()

sched = BackgroundScheduler(daemon=True)
sched.add_job(daily_covid_stats_job,'cron',hour='08', minute='00')
sched.add_job(send_stats_job,'cron', hour='08', minute='30')
sched.start()

if __name__ == "__main__":
    uvicorn.run("dashboard:app")