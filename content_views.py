#!/usr/bin/python
# This script reads a list of channel names from a csv file
# and re-creates them as content views on a satellite 6
# server

from __main__ import *
import pprint
import csv
import sys
import datetime
import os
import simplejson as json
from time import sleep
try:
        import requests
except ImportError:
        print "Please install the python-requests module."
        sys.exit(-1)

try:
        import getpass
except ImportError:
        print "Please install the getpass module."
        sys.exit(-1)


# URL to the Satellite 6 server
URL = "https://satellite.hostname.example.com"
# URL for the API for Satellite 6 server
global KAT_API, KAT_API_URL, SAT_API, SAT_API_URL
global org_id
KAT_API = "%s/katello/api/v2/" % URL
SAT_API = "%s/api/v2/" % URL
# Katello-specific API
POST_HEADERS = {'Content-Type': 'application/json'}
# Default credentials to login to Satellite 6
#USERNAME = os.environ.get('USER')
USERNAME = "admin"
# Ignore SSL for now
SSL_VERIFY = False

# Organization name
ORG_NAME = 'My Organization name'

# Path to CSV File
CSV_FILE = "channels.csv"

def get_json(location):
    """
    Performs a GET using the passed URL location
    """

    r = requests.get(location, auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)

    return r.json()
    
def post_json(location, json_data):
    """
    Performs a POST and passes the data to the URL location
    """

    result = requests.post(
        location,
        data=json_data,
        auth=(USERNAME, PASSWORD),
        verify=SSL_VERIFY,
        headers=POST_HEADERS)

    return result.json()

def put_json(location, json_data):
    """
    Performs a POST and passes the data to the URL location
    """

    result = requests.put(
        location,
        data=json_data,
        auth=(USERNAME, PASSWORD),
        verify=SSL_VERIFY,
        headers=POST_HEADERS)

    return result.json()

def test_login():
        org = get_json(KAT_API + "organizations/" + ORG_NAME)
        if org.get('error', None):
                print "Invalid Credentials. Please verify and try again"

def get_content_views():
        cvlist = []
        cv_list = get_json(KAT_API_URL + "/content_views/")
        for cv in cv_list['results']:
            cvl = {}
            cvl['id'] = cv.get('id')
            cvl['name'] = cv.get('name')
            cvlist.append(cvl)
        return cvlist

def create_content_view(cv_name,cv_label):
    rinfo = post_json(
                KAT_API + "/content_views/" ,
                   json.dumps(
                        {
                                "organization_id": org_id,
                                "name": cv_name,
                                "label": cv_label,
                                "description": '',
                                "composite": False,
                                "repository_ids": []
                        }
                        )
                  )

    return rinfo
    
# Prompt for the users credentials
PASSWORD = getpass.getpass(prompt='Enter your Satellite 6 Password to continue:')

# Verify login
print "Verify login..."
test_login()

# Test out the Organization to make sure we can connect and we're working with the right one.
print "Verify organization..."
org = get_json(KAT_API + "organizations/" + ORG_NAME)

if org.get('error', None):
        print 'Orgnanization ' + ORG_NAME + ' not found.  Please double check'
        sys.exit(-1)
else:
        org_id = org['id']
        print "Organization " + ORG_NAME + " exists with id " + str(org_id)
        KAT_API_URL = KAT_API + "organizations/" + str(org_id) + "/"
        SAT_API_URL = SAT_API + "organizations/" + str(org_id) + "/"

# Get list of existing content views
print "List of existing content views..."
cvlist = get_content_views()
print pprint.pprint(cvlist)

# Import list of channels to be created from the CSV file
print "Importing CSV..."
with open( CSV_FILE, 'r') as f:
    reader = csv.reader(f)
    channel_list = list(reader)

# loop through the list and create each as content view
for channel in channel_list:
    print "Creating content view %s.." %channel[2]

    cv_name = str(channel[2])
    cv_label = str(channel[1]) 
    cvtask = create_content_view(cv_name, cv_label)

    print json.dumps(cvtask, indent=1)
