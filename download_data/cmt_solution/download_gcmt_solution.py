#!/usr/bin/env python
"""
This script is used to download global cmt solution files.
"""
import argparse
import sh
import sys
from loguru import logger
import requests
from dotmap import DotMap
from bs4 import BeautifulSoup
from lxml import etree
import re
import pandas as pd

# * reference url: https://www.globalcmt.org/cgi-bin/globalcmt-cgi-bin/CMT5/form?itype=ymd&yr=2012&mo=12&day=13&oyr=1976&omo=1&oday=1&jyr=1976&jday=1&ojyr=1976&ojday=1&otype=nd&nday=1&lmw=4.6&umw=10&lms=0&ums=10&lmb=0&umb=10&llat=-90&ulat=90&llon=-180&ulon=180&lhd=0&uhd=1000&lts=-9999&uts=9999&lpe1=0&upe1=90&lpe2=0&upe2=90&list=4


class COUNT():
    SUCCESS_N = 0
    FAIL_N = 0
    TOTAL_N = 0


def parser(event_information):
    baseurl = "https://www.globalcmt.org/cgi-bin/globalcmt-cgi-bin/CMT5/form"
    args = {
        "itype": "ymd",
        "yr": event_information.year,
        "mo": event_information.month,
        "day": event_information.day,
        "oyr": 1976,
        "omo": 1,
        "oday": 1,
        "jyr": 1976,
        "jday": 1,
        "ojyr": 1976,
        "ojday": 1,
        "otype": "nd",
        "nday": 1,
        "lmw": event_information.magnitude,
        "umw": 10,
        "lms": 0,
        "ums": 10,
        "lmb": 0,
        "umb": 10,
        "llat": -90,
        "ulat": 90,
        "llon": -180,
        "ulon": 180,
        "lhd": 0,
        "uhd": 1000,
        "lts": -9999,
        "uts": 9999,
        "lpe1": 0,
        "upe1": 90,
        "lpe2": 0,
        "upe2": 90,
        "list": 4
    }

    response = requests.get(baseurl, params=args)
    selector = etree.HTML(response.text)
    selectedinfo = selector.xpath('/html/body/pre[2]/text()')[0]
    regex = re.compile(
        f"(\sPDEW.*\n.*\n.*\n.*\nlatitude:.*?{event_information.latitude}.*?\nlongitude:.*?{event_information.longitude}.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?)\n")
    find_result = regex.findall(selectedinfo)
    if(find_result == []):
        COUNT.SUCCESS_N += 1
        logger.error(
            f"[{COUNT.SUCCESS_N+COUNT.FAIL_N}:{COUNT.SUCCESS_N}:{COUNT.FAIL_N}]{event_information.name} couldn't find cmt solution file!")

    else:
        COUNT.FAIL_N += 1
        logger.info(
            f"[{COUNT.SUCCESS_N+COUNT.FAIL_N}:{COUNT.SUCCESS_N}:{COUNT.FAIL_N}]{event_information.name} found event!")
        find_result = find_result[0]
        find_result = "PDEW "+find_result[5:]
        with open(f"./cmts/{event_information.name}", "w") as f:
            f.write(find_result)


def read_event_information():
    data = pd.read_pickle("./event_info.pkl")
    return data


if __name__ == "__main__":
    logger.info("start to parse")
    sh.mkdir("-p", "cmts")

    event_information = read_event_information()
    for i in event_information.values:
        event_information = DotMap()
        event_information.name = i[0]
        event_information.year = i[0][:4]
        event_information.month = i[0][4:6]
        event_information.day = i[0][6:8]
        event_information.magnitude = f"{round(i[4],1):.1f}"
        event_information.latitude = f"{round(i[2],2):.2f}"
        event_information.longitude = f"{round(i[3],2):.2f}"
        parser(event_information)
