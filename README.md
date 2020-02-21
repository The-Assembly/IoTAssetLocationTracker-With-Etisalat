# Build An IoT Asset Location Tracker With Etisalat
At this session, learn how to incorporate ​location tracking​ into your IoT solution, including how to: 
1. Set up GPS modules on remote edge devices & monitor location over the internet 
2. Sync and model location data streams for multiple assets to the cloud 
3. Build a consolidated web-based user interface using extensions to display maps & position simultaneously for all assets.

# Summary of steps
(Watch the live stream on http://www.facebook.com/makesmartthings)

## Get started on the Thingworx console
	1. Open up your web browser & navigate to http://<server IP Address>:<server port>/Thingworx/Composer/
	2. Set ProjectContext to 'AssemblyUsers'
	3. Create a new Application Key bound to your username and store the KeyID in a safe place

## Model your data
	1. Create a Thing Shape called LocationEnabled_<userid> (eg; LocationEnabled_01) with property GPS - with base type Location - select Persistent & Logged checkboxes
	2. Create a Thing called MyAsset_<userid> with base tempate GenericThing & add shape LocationEnabled
	3. Add 2 services to LocationEnabled called GetLatitude & GetLongitude (return type is NUMBER)
		- Code for GetLatitude: result = Me.GPS.latitude
		- Code for GetLongitude: result = Me.GPS.longitude
	4. (optional) Try property retrieval + service REST API calls in Postman (requires authentication in header)
		- get http://<server address with port>/Thingworx/Things/MyAsset_<userid>/Properties/GPS
		- post http://<server address with port>/Thingworx/Things/MyAsset_<userid>/Services/GetLatitude

## Build your mashup
	Mashup is a web application built on the Thingworx platform - drag and drop - no coding needed
	1. Create a new mashup called LocationTracker_<userid>
	2. Add labels for latitude, longitude & textbox for location
	3. In the Data tab, add MyAsset_<userid>->GetPropertyValues & GetLatitude & GetLongitude services - select OnMashupLoaded for all.
	4. Drag GetPropertyValues->AllData->GPS and drop on the textbox to bind.  Do the same for GetLatitude/GetLongitude->AllData->result & the two labels.
	5. Add Autorefresh widget - bind Refresh to GetPropertyValues, GetLatitude, GetLongitude (to refresh on a timer - set interval to 5 seconds)

## Add Google Maps Widget (server only)
	1. https://marketplace.ptc.com/apps/218633/google-maps-widget-303#!overview
	2. https://developer.thingworx.com/en/resources/guides/google-map-widget-how/configure-google-maps-widget-extension
	3. Get API key from Google Cloud Console for Maps Javascript API
	4. Edit PlatformSubsystem configuration in Thingworx to set the API key (as detailed above)

## Add maps to your mashup
	1. Select the newly available Google Maps & Location Picker widgets in your mashup
	2. Drag GetPropertyValues->AllData->GPS to the Maps widget->Selected Location
	3. In Maps widget properties, select ShowSelectionMarker
	4. Add a Button 'Set Location'
	5. Add SetProperties function from MyAsset_<userid> - bind Location Picker->Location to SetProperties->GPS
	6. Drag SetProperties to button->Clicked to bind
	7. Drag SetProperties->ServiceInvokedCompleted to GetPropertyValues (to refresh after setting)

## Add multi-asset location tracking to your mashup
	1. Duplicate the previous mashup to a new one if you'd like to preserve your work - we will be deleting the functionality
	2. Delete the GetLatitude/GetLongitude functions + the labels & text box - we won't need it any more
	3. Add a new list - select DropDown as the view
	4. Add LocationEnabled->GetImplementingThingsWithData in the Data Tab, bind GetImplementingThingsWithData->All Data to the list->Data
	5. Set DisplayField & ValueField in list properties to 'name'
	6. Add another service on the Data tab, select LocationEnabled again, however check 'Dynamic'
	7. Select GetPropertyValues & SetProperties services & add (do not select MashupLoaded this time)
	8. Drag/bind GetImplementingThingsWithData->SelectedRow->name to EntityName for DynamicThingShapes_LocationEnabled
	9. Repeat the binding steps in the previous section for the dynamic GetPropertyValues & SetProperties 
	10. Drag SetProperties->SelectedRowChanged to GetPropertyValues - this ensures when selection changes, new values retrieved
	
## Set up Thingworx Academic Simulator
	1. Install - 
		MAC - http://apps.ptc.com/schools/software/ThingWorxAcademicSimulatorSetup.dmg
		WINDOWS - http://apps.ptc.com/schools/software/ThingWorxAcademicSimulatorSetup.exe
	2. Start & select 'Simulate Device'
	3. Connect to your server with the address, application key and port
	4. Add Thing from left hand panel - Select MyAsset & connect
	5. Edit GPS under Properties 
	6. Select Random or Step - for Step, select Initial Latitude/Longitude (eg;25, 55) & Step Sizes (eg; 0.1)
	7. Set Refresh to 5 seconds, select Include In Simulation and save
	8. Hit the play button next to properties to begin simulation - return to your mashup to view changes - stop when done

## Set up value stream to view historical location values
	1. Duplicate mashup again - delete Location Picker, Set Location button & SetProperties service - only leave the dropdown list & the Maps widget
	2. Create a new Value Stream called VS_Location_<userid> in Thingworx with default properties (ThingworxPersistenceProvider already set)
	3. In the MyAsset thing, select VS_Location as your Value Stream (Ensure GPS property in LocationEnabled shape has 'Logged' selected)
	4. Re-run simulator to populate values
	5. From MyAsset->Services, filter QueryPropertyHistory service and run it - this should display the table of historic values
	6. In the mashup, add QueryPropertyHistory service from the Dynamic LocationEnabled entry in Data tab
	7. Bind All Data to the Data property for the Maps widget
	8. Select LocationField as GPS - view the mashup
	9. Change binding of QueryPropertyHistory->All Data to RouteData property of Maps widget
	10. Select RouteLocationField as GPS, select ShowRoute property & view mashup

## Connect the Pi & GPS module
	1. Connect pins on GPS module - VCC to 5V on Pi, TX with RX of Pi (GPS transmits, Pi receives), GND with GND of Pi, keep RX empty
	2. Insert SD card into Pi and power up
	3. Backup (optional) -
		sudo cp /boot/cmdline.txt /boot/cmdline_backup.txt
	4. Edit the file
		sudo nano /boot/cmdline.txt
	5. Replace content of file with 
		dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet splash plymouth.ignore-serial-consoles
	6. To save press ctrl-X, select y and enter
	7. Check whether LED on GPS module is blinking (indicates it's receiving coordinates) & reboot Pi (sudo reboot)
	8. Run command to see coordinates stream (ctrl C to stop) - 
		sudo cat /dev/ttyAMA0

## Send GPS data to Thingworx in Python
	1. Disable console as by default Pi uses serial port for console login but we need serial port for data from GPS module
		ls -l /dev
		sudo systemctl stop serial-getty@ttyAMA0.service
		sudo systemctl disable serial-getty@ttyAMA0.service
	2. Install Python library
		pip install pynmea2
	3. Code the following python script (replace <server>, <appKey>, <username>, <password>, <userid>) - 
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
        			response = requests.put (url+'/Things/MyAsset_<userid>/Properties/*',json = {"GPS":{"longitude":lng, "latitude":lat, "elevation":0.5 , "units": "WGS84"}}, auth = (<username>,<password>) ,headers=headers, verify=False)
	
	4. Run the script - this will send a stream of coordinates to Thingworx (adjust timeout as desired)
