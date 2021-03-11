import datetime
from datetime import datetime, timedelta
import numpy as np
import os

OUTCOMES = 4

dirname = os.path.dirname(__file__)

def get_dates(days):
    date_today = datetime.today()
    dates = [""] * days
    for i in range(days):
        new_date = date_today - timedelta(i)
        dates[i] = new_date.strftime('%Y-%m-%d')
    return dates


def get_daily_call_outcomes(dates, days):
    all_calls_outcome = [0] * days
    config_location = os.path.join(dirname, "../asterisk_docker/conf/asterisk-build/Master.csv")
    f = open(config_location, "r")
    lines = f.readlines()
    d = 0
    for day in dates:
        daily_outcomes = [0] * OUTCOMES
        for line in reversed(lines):
            if day in line:
                if "ANSWERED" in line:
                    daily_outcomes[0] += 1
                if "NO ANSWER" in line:
                    daily_outcomes[1] += 1
                if "BUSY" in line:
                    daily_outcomes[2] += 1
                if "FAILED" in line:
                    daily_outcomes[3] += 1
        all_calls_outcome[d] = daily_outcomes
        d += 1

    all_calls_outcome = np.array(all_calls_outcome).T
    return all_calls_outcome


def return_daily_data(days):
    dates = get_dates(days)
    daily_calls_outcomes = get_daily_call_outcomes(dates, days)
    dates = format_dates_as_days(dates)
    return dates, daily_calls_outcomes


def return_weekly_data(weeks):
    dates = get_dates(7 * weeks)
    daily_calls_outcome = get_daily_call_outcomes(dates, 7 * weeks)
    weekly_calls_outcome = split_into_weeks(daily_calls_outcome, weeks)
    weekly_calls_outcome = np.array(weekly_calls_outcome).T
    dates = format_dates_as_weeks(dates, weeks)
    return dates, weekly_calls_outcome


def split_into_weeks(outcome, weeks):
    weekly_calls_outcome = [0] * weeks
    for i in range(weeks):
        calls_outcome = [0] * OUTCOMES
        for j in range(i * 7, i * 7 + 7):
            for k in range(4):
                calls_outcome[k] += outcome[k][j]
        weekly_calls_outcome[i] = calls_outcome
    return weekly_calls_outcome


def format_dates_as_weeks(dates, w):
    dates = format_dates_as_days(dates)
    weeks = [""] * w
    for i in range(w):
        end = dates[7 * i]
        start = dates[7 * i + 6]
        if start[6:] == end[6:]:
            start = start[:-5]
            if start[3:] == end[3:6]:
                start = start[:-4]
        weeks[i] = start + " - " + end
    return weeks


def format_dates_as_days(dates):
    for i in range(len(dates)):
        date = dates[i]
        year = date[:4]
        day = date[8:]
        date = date.replace(year, day)
        date = date[:-2] + year
        if date[3] == '0':
            if date[4] == '1':
                date = date.replace(date[2:6], " Jan ")
            if date[4] == '2':
                date = date.replace(date[2:6], " Feb ")
            if date[4] == '3':
                date = date.replace(date[2:6], " Mar ")
            if date[4] == '4':
                date = date.replace(date[2:6], " Apr ")
            if date[4] == '5':
                date = date.replace(date[2:6], " May ")
            if date[4] == '6':
                date = date.replace(date[2:6], " Jun ")
            if date[4] == '7':
                date = date.replace(date[2:6], " Jul ")
            if date[4] == '8':
                date = date.replace(date[2:6], " Aug ")
            if date[4] == '9':
                date = date.replace(date[2:6], " Sep ")
        if date[3] == '1':
            if date[4] == '0':
                date = date.replace(date[2:6], " Oct ")
            if date[4] == '1':
                date = date.replace(date[2:6], " Nov ")
            if date[4] == '2':
                date = date.replace(date[2:6], " Dec ")
        dates[i] = date
    return dates