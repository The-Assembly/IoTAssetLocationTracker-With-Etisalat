import serial
import time
import string
import pynmea2
import requests
import json

url = 'http://<server>/Thingworx'
headers = { 'Content-Type': 'application/json', 'appKey': '<appKey>','Accept': 'text/html'}

while True:
 	port="/dev/ttyAMA0"
	ser=serial.Serial(port, baudrate=9600, timeout=0.5)
	dataout = pynmea2.NMEAStreamReader()
	newdata=ser.readline()
	
	if newdata[0:6] == "$GPGLL":	
		newmsg=pynmea2.parse(newdata)		
		lat=newmsg.latitude
		lng=newmsg.longitude
		locstr = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
		print(locstr)
		response = requests.put (url+'/Things/MyAsset_<userid>/Properties/*',json = {"GPS":{"longitude":"{0:.4f}".format(lat), "latitude":"{0:.4f}".format(lng), "elevation":0 , "units": "WGS84"}}, auth = (<username>,<password>) ,headers=headers, verify=False)
		
