# imports praw (reddit API), gspread (GSheets API) -  ensure installed via 
import praw
import csv
from praw.models import MoreComments
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from googleapiclient import discovery
from array import *

# does Google-y stuff to get the OAuth info. Ensure your own API key is stored in the same folder as this bot as "mySecret.json". Please ask if unsure what to do.
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('mySecret.json', scope)
client = gspread.authorize(creds)
service = discovery.build('sheets', 'v4', credentials=creds)

# This can be changed for a relevant sheet. Specifies spreadsheet and the sheet. Your secret key should be invited to the sheet. Its email adress can be found by accesing mySecret.json next to client_email. 
mySheet = "L: 13th Term Voting Record"
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1PXj_4LMRKuiUPDLlTx6ZrBKlFOS60V7T3dHxa7yNg1Q/edit').worksheet(mySheet)

text_list = ''
nolist = ''

# Praw Setup
r = praw.Reddit(client_id='75ilRvcoBvTHlw',
                     client_secret='a9c_l6qxhUcKDvAVSxPX5_IqFAY',
                     user_agent='my user agent')

# Do not remove credit without author's permission.
print("This bot was coded by pjr10th and Zygark.")

def count():
    global submissionnum
    submission = r.submission(url=input("Enter Bill: ")) #User input of Bill URL
    res_list = list()
    author_list = list()
    listtotal = list() #establishes lists

    #splits title to get Bill Number for  filename
    submissionnum = submission.title.split(' - ')[0]

    # retrieves each second level comment by Automoderator and extracts the vote, then appends the voters u/ with a #.
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments): #ensures that Hidden comments are included
            continue
        else:
            for second_level_comment in top_level_comment.replies:
                # removes fluff from automod comment.
                if second_level_comment.author == 'AutoModerator':
                    comment_text = second_level_comment.body.lower()
                    comment_text_stage1 = comment_text.replace('/u/', '')
                    comment_text_stage2 = comment_text_stage1.replace(' voted as below', '')
                    comment_text_stage3 = comment_text_stage2.replace('\n\n*i am a bot, and this action was performed automatically. please [contact the moderators of this subreddit](/message/compose/?to=/r/mholvote) if you have any questions or concerns.*', '')
                    comment_text_split = comment_text_stage3.split(''':
> ''')
                    for listitem in author_list:
                        if comment_text_split[0] == listitem:
                            print(comment_text_split[0] + ' has voted more than once. Please verify.')
                    try:
                        valfor_reslist = str((comment_text_split[0]) + "#" + (comment_text_split[1]))
                        author_list.append(comment_text_split[0])
                    except:
                        continue
                    res_list.append(valfor_reslist)

    # Checks for proxies
    for listitem in res_list:
        try:
            if 'PROXY' in listitem.upper():
                lowerlistitem = listitem.lower()
                proxyinfo = lowerlistitem.split('#')[1]
                if lowerlistitem.split('#')[0] != 'automoderator':
                    new_proxyinfo = proxyinfo.replace('proxy for /u/', '')
                    splitlist = new_proxyinfo.split(" = ")
                    listtotal.append({'mp': splitlist[0], 'vote': splitlist[1]})
                    print('MP ' + splitlist[0] + ' CHECK PROXY VOTE')
            else:
                splitlist = listitem.split('#')
                #print(listitem)
                #translates vote contents to 
                if splitlist[1] == "content":
                    splitlist[1] = "CON"
                elif splitlist[1] == "not content":
                    splitlist[1] = "NOT"
                elif splitlist[1] == "present":
                    splitlist[1] = "PRE"
                
                listtotal.append({'mp': splitlist[0], 'vote': splitlist[1]})
        except:
            print('Error: ' + listitem + '. If this is an illegal proxy, please inform the proxyer of the correct format.')

    # Sets file name for export
    filename = "#" + submissionnum + ".csv"

    # Tries to output if no file with existing name exists.
    try:
        with open(filename, "w", newline='') as output:
            fieldnames = ['mp', 'vote']
            writer = csv.DictWriter(output, fieldnames=fieldnames)

            writer.writeheader()
            for val in listtotal:
                writer.writerow(val)
        print(submissionnum + " has been counted. Result file in result folder.")
    except:
        print('Sorry there has been an error. Please delete the CSV with name ' + filename + ' in the folder and try again.')
        cont = input('Ready? Click any key: ')
        with open(filename, "w", newline='') as output:
            fieldnames = ['mp', 'vote']
            writer = csv.DictWriter(output, fieldnames=fieldnames)

            writer.writeheader()
            for val in listtotal:
                writer.writerow(val)
        print(submissionnum + " has been counted. Result file in result folder.")

    return filename

filename = count()

with open(filename) as f:
    a = [{k:v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]

# accesses the third column (with the list of lords)
lordsNames = sheet.col_values(3)

# creates a list
lordslist = list()

# goes through the list of lords between the first lord and the Lords Speaker
for voter in lordsNames:
    if voter == '':
        continue
    elif voter == 'CountBrandenburg': # Change for Lords Speaker of the time
        break
    else:
        lordslist.append(voter.lower())

# Array called VotesList. Adds all Lords Votes to VotesList which is the array used by the bot on the google sheet.
VotesList = [[''], [submissionnum], ['']]
found = False
with open(filename, "w+", newline='') as file:
    writer = csv.writer(file)
    for lord in lordslist:
        for vote in a:
            if vote["mp"] == lord:
                this_lord = lord
                this_vote = vote["vote"]
                writer.writerow([this_lord, this_vote])
                VotesList.append([this_vote])
                found = True
                    
        if not found:
            this_lord = lord
            this_vote = "DNV"
            writer.writerow([this_lord, this_vote])
            VotesList.append([this_vote])
        found = False


# Asks user to enter chosen column for the output.
chosenColumn = input('Enter the column code (letters) of the next empty column on the Voting Record:')

# Updates the chosen range on the sheet
UpSheet_range = "'"+ mySheet + "'!" + chosenColumn + ":" + chosenColumn        
UpSheet_body = {
    'values': VotesList,
}
UpSheet_result = service.spreadsheets().values().update(spreadsheetId='1PXj_4LMRKuiUPDLlTx6ZrBKlFOS60V7T3dHxa7yNg1Q',range=UpSheet_range,valueInputOption='RAW',body=UpSheet_body).execute()
print('Cells updated on Master Spreadsheet. Please verify for errors.')

# This bot was coded by pjr10th and Zygark.
