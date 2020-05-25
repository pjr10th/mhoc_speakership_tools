#!/usr/bin/env python3
#Main script for speakership tools

import csv
from praw.models import MoreComments
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from googleapiclient import discovery
from array import *
import lib.countAPI

__author__ = "pjr10th, Zygark"
__license__ = "MIT License"

#Initialises connection with Google Sheets
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('mySecret.json', scope)
client = gspread.authorize(creds)
service = discovery.build('sheets', 'v4', credentials=creds)

def count_lords(url):
    