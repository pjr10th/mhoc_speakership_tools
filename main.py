#!/usr/bin/env python3
#Main script for speakership tools

import csv
from praw.models import MoreComments
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#import time
from googleapiclient import discovery
#from array import *
import lib.countAPI as countAPI
from urllib.parse import urlparse

__author__ = "pjr10th, Zygark"
__license__ = "MIT License"

#Initialises connection with Google Sheets
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('mySecret.json', scope)
client = gspread.authorize(creds)
service = discovery.build('sheets', 'v4', credentials=creds)

#Fetches the votes from an MHOL division and returns them in the correct order.
def count_lords(url):
    lords_speaker = 'CountBrandenburg'
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1PXj_4LMRKuiUPDLlTx6ZrBKlFOS60V7T3dHxa7yNg1Q/edit').worksheet("L: 13th Term Voting Record") #Opens Lords' voting sheet
    result = countAPI.lords(url)

    print("Please resolve the following duplicate votes:", result["duplicates"])

    #fetches list of current peers from sheet
    lords_names = sheet.col_values(3)
    lords = list()
    for voter in lords_names:
        if voter == '':
            continue
        elif voter == lords_speaker: #Ends at Lords Speaker - final voting lord
            break
        else:
            lords.append(voter.lower())
        
    votes = result["votes"] #fetches votes from API response
    
    #Sorts votes into the same order as the lords on the sheet
    ordered_votes = list() 
    for lord in lords:
        if lord in votes:
            ordered_votes.append(votes[lord])
        else:
            ordered_votes.append("DNV")
    
    return ordered_votes

#Takes a list of votes from Commons/Lords and writes them to the master sheet.
def write_to_sheet(url, vote_results):
    if urlparse(url).path[6] == 'L':
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1PXj_4LMRKuiUPDLlTx6ZrBKlFOS60V7T3dHxa7yNg1Q/edit').worksheet("L: 13th Term Voting Record") #Opens Lords' voting sheet
        chosen_column = input('Enter the column code (letters) of the next empty column on the Voting Record:') #Selects next clear column manually

        #Writes to sheet
        UpSheet_range = "'"+ "L: 13th Term Voting Record" + "'!" + chosen_column + ":" + chosen_column
        