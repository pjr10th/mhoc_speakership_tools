#!/usr/bin/env python3
#Fetches voting data from the MHOC vote counting API.

import json
import requests

def lords(bill_url):
    request_url = 'https://api.mhoc.co.uk/api/votecount/mhol'
    key = {'bill_url': bill_url}

    call = requests.post(request_url, data = key)
    
    if call.ok:
        response = call.json()
        response_dict = json.loads(response)
        return response_dict
    else:
        status_code = call.status_code
        status_code_key = requests.status_codes._codes[status_code]
        raise Exception('API returned non-okay code', status_code, status_code_key)
        