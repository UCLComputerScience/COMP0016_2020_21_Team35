from datetime import datetime, timedelta
import numpy as np
import os
import sys
import main_application.constants.asterisk_filepath_constants as asterisk_constants

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

def get_data(date):
    outcomes = [0] * 5
    time = [0] * 7
    redirect = {}
    config_file = os.path.join(application_path, asterisk_constants.MASTER_CSV_PATH)
    f = open(config_file, "r")
    lines = f.readlines()
    for line in reversed(lines):
        if date in line:
            if "ANSWERED" in line:
                outcomes[0] += 1
            if "NO ANSWER" in line:
                outcomes[1] += 1 
            if "BUSY" in line:
                outcomes[2] += 1
            if "FAILED" in line:
                outcomes[3] += 1
            if "ivr" in line:
                outcomes[4] += 1
            elif "from-phones" in line:
                position = line.find("PJSIP/+")
                if position > 0:
                    number = line[position+6:position+19]
                    if number in redirect:
                        redirect[number] += 1
                    else:
                        redirect[number] = 1
            position = line.find(date)
            hour = line[position+11:position+13]
            if hour[0] == '0':
                if hour[1] < '8':
                    time[0] += 1
                else: 
                    time[1] += 1
            elif hour[0] == '1':
                if hour[1] < '2':
                    time[2] += 1
                elif hour[1] < '4':
                    time[3] += 1
                elif hour[1] < '6':
                    time[4] += 1
                elif hour[1] < '8':
                    time[5] += 1
                else:
                    time[6] += 1
            else:
                time[6] += 1
    return outcomes, time, redirect

def return_daily_data(date):
    outcomes, time, redirect = get_data(date)
    return outcomes, time, redirect

def return_monthly_data(month):
    outcomes, time, redirect = get_data(month)
    return outcomes, time, redirect

def return_period_data(start, end):
    date = start
    outcomes = [0] * 5
    times = [0] * 7
    redirect = {}
    while date != end + timedelta(1):
        o, t, r = return_daily_data(date.strftime('%Y-%m-%d'))
        outcomes = np.add(outcomes, o) 
        times = np.add(times, t)
        for key in r:
            if key in redirect:
                redirect[key] += r.get(key)
            else:
                redirect[key] = r.get(key)
        date = date + timedelta(1)
    return outcomes, times, redirect