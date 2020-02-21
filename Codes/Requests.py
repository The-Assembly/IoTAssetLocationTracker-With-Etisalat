import serial
import time
import string
import pynmea2
import requests
import json

url = 'http://<server>/Thingworx'
headers = { 'Content-Type': 'application/json', 'appKey': '<appKey>','Accept': 'text/html'}
response = requests.put (url+'/Things/MyAsset_<userid>/Properties/*',json = {"GPS":{"longitude":35, "latitude":30.5, "elevation":0.5 , "units": "WGS84"}}, auth = (<username>,<password>) ,headers=headers, verify=False)