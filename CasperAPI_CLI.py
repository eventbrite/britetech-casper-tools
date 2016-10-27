#!/usr/bin/python
# Casper API Tools version 0.1.2
## Import libraries for basic command line functions
import sys
import getpass
import argparse

import datetime
from datetime import datetime
from datetime import date

import csv
import os, inspect

import urllib2
import base64
import xml.etree.ElementTree as etree

from xml.etree import ElementTree
from xml.dom import minidom

import subprocess

# prettify function from https://pymotw.com/2/xml/etree/ElementTree/create.html
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


### Core Functions

def getJSS_API_URL():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	jss_api_url_Location = scriptPath + '/.jssURL'

	if os.path.isfile(jss_api_url_Location):
		
		with open (jss_api_url_Location) as jssURLfile:
			jssURL = jssURLfile.read().replace('\n','')
			jss_api_url = jssURL + '/JSSResource'
			return jss_api_url

## Base URLs
#jss_api_base_url = getJSS_API_URL()

# Keys Location
#keysfile = '/Volumes/Keys'

def getKeysFile():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	keysFile = scriptPath + '/.keysfile'

	if os.path.isfile(keysFile):
		
		with open (keysFile) as keyLocationFile:
			keysfileLoc = keyLocationFile.read().replace('\n','')
			return keysfileLoc

## Configuration Functions

def resetCLI_Settings():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	encryptedPW_Location = scriptPath + '/.jsspwencrypted'

	if os.path.isfile(encryptedPW_Location):
		os.remove(encryptedPW_Location)
		print "Deleted encrypted password file at " + encryptedPW_Location
	else:
		print "No cached encrypted password file found"

## Functions

def sendAPIRequest(reqStr, username, password, method, XML=''):

	errorMsg_401 = 'Authentication failed. Check your JSS credentials.'
	errorMsg_404 = 'The JSS could not find the resource you were requesting. Check the URL to the resource you are using.'

	request = urllib2.Request(reqStr)
	request.add_header('Authorization', 'Basic ' + base64.b64encode(username + ':' + password))

	if method == "GET":
		# GET
		try:
			request.add_header('Accept', 'application/xml')
			response = urllib2.urlopen(request)
			return response
		except urllib2.HTTPError, e:
			print 'Request failed with error code - %s.' % e.code

			if e.code == 401:
				print errorMsg_401
			elif e.code == 404:
				print errorMsg_404

			return -1
	elif method == "POST":
		# POST
		request.add_header('Content-Type', 'text/xml')
		request.get_method = lambda: 'POST'
		response = urllib2.urlopen(request, XML)
	elif method == "PUT":
		# PUT
		request.add_header('Content-Type', 'text/xml')
		request.get_method = lambda: 'PUT'
		try:
			response = urllib2.urlopen(request, XML)	
			return response
		except urllib2.HTTPError, e:
			print 'Request failed with error code - %s.' % e.code

			if e.code == 401:
				print errorMsg_401
			elif e.code == 404:
				print errorMsg_404

			return -1
	elif method == "DELETE":
		# DELETE
		request.get_method = lambda: 'DELETE'
		try:
			response = urllib2.urlopen(request)
			return response
		except urllib2.HTTPError, e:
			print 'Request failed with error code - %s.' % e.code

			if e.code == 401:
				print errorMsg_401
			elif e.code == 404:
				print errorMsg_404

			return -1
	else:
		print 'Unknown method.'
		return -1

def setBase_URL():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	orgFileLocation = scriptPath + '/.jssorg'

	if os.path.isfile(orgFileLocation):
		with open (orgFileLocation) as orgFile:
			crowdOrg = orgFile.read().replace('\n','')
	else:
		#No okta org config file found, request JSS org name from user
		crowdOrg = raw_input('Please enter your JSS org URL, in the form company.okta.com: ')
		orgFile = open(orgFileLocation, 'a+')
		orgFile.write(jssOrg)

	## Base URLs
	print api_base_url

	return api_base_url

def getJSSpw():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	apikeyLocation = scriptPath + '/.jsspw'
	#print apikeyLocation

	if os.path.isfile(apikeyLocation):
		#print "api key file exists, here's the key!"
		
		#print "Path: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		with open (apikeyLocation) as apikeyfile:
			api_key = apikeyfile.read().replace('\n','')
			return api_key

	else:
		print "JSS credentials do not exist, prompting..."

		try:
			jss_pw = getpass.getpass('Enter JSS Password:')
			return api_key
		except:
			print "\nCtrl-C detected, exiting..."
			raise SystemExit

def decryptString(inputString, salt, passphrase):
    '''Usage: >>> DecryptString("Encrypted String", "Salt", "Passphrase")'''
    p = subprocess.Popen(['/usr/bin/openssl', 'enc', '-aes256', '-d', '-a', '-A', '-S', salt, '-k', passphrase], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    return p.communicate(inputString)[0]

def getSalt():
	keysfile = getKeysFile()
	saltFileLocation = keysfile + '/.jsssalt'

	if os.path.isfile(saltFileLocation):
		with open (saltFileLocation) as saltFile:
			salt = saltFile.read().replace('\n','')
		return salt
	else:
		print 'No keys file available.'
		raise SystemExit

def getPassphrase():
	keysfile = getKeysFile()
	passphraseFileLocation = keysfile + '/.jsspassphrase'

	if os.path.isfile(passphraseFileLocation):
		with open (passphraseFileLocation) as passphraseFile:
			passphrase = passphraseFile.read().replace('\n','')
		return passphrase
	else:
		print 'No keys file available.'
		raise SystemExit

def getEncryptedJSSpw():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	encryptedPWLocation = scriptPath + '/.jsspwencrypted'

	salt = getSalt()
	passphrase = getPassphrase()

	if os.path.isfile(encryptedPWLocation):
		#print "api key file exists, here's the key!"
		
		#print "Path: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		with open (encryptedPWLocation) as encryptedPWfile:
			encryptedPW = encryptedPWfile.read().replace('\n','')
	
		decryptedPW = decryptString(encryptedPW, salt, passphrase)
		return decryptedPW

	else:
		print "JSS credentials do not exist, prompting..."

		try:
			jss_pw = getpass.getpass('Enter JSS Password:')
			return jss_pw
		except:
			print "\nCtrl-C detected, exiting..."
			raise SystemExit

## Accounts

def getAccounts(username, password):
	reqStr = jss_api_base_url + '/accounts'

	r = sendAPIRequest(reqStr, username, password, 'GET')

	responseCode = r.code
	responseXml = etree.fromstring(r.read())

	print etree.tostring(responseXml)

	#print 'Root: ' + str(responseXml.tag)

	for users in responseXml.findall('users'):
		for user in users:
			#print "here?"
			name = user.find('name').text
			print name
			#uObj = user.find('user')
			#name = uObj.find('name').text
			#print name


## Computer Functions

def getComputer(computerName, username, password, detail):
	reqStr = jss_api_base_url + '/computers/match/' + computerName
	#print reqStr
	#print detail

	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return

	#responseCode = r.code
	baseXml = r.read()
	#print baseXml
	responseXml = etree.fromstring(baseXml)

	#print prettify(responseXml)
	#print etree.tostring(responseXml)

	#print 'Response Code: ' + str(responseCode)
	#print 'Root: ' + str(responseXml.tag)
	#print 'Attr: ' + str(responseXml.attrib)

	#for child in responseXml:
	#	print child.tag, child.attrib

	#for computer in responseXml.iter('computer'):
	#	print computer.attrib

	print 'All computers with ' + computerName + ' as part of the computer information:\n'

	for computer in responseXml.findall('computer'):
		name = computer.find('name').text
		asset_tag = computer.find('asset_tag').text
		sn = computer.find('serial_number').text
		mac_addr = computer.find('mac_address').text
		jssID = computer.find('id').text
		#fv2status = computer.find('filevault2_status').text
		
		#print 'FileVault2 Status: ' + fv2status + '\n'

		if detail == 'yes':
			getComputerByID(jssID, username, password)
		else:
			print 'Computer Name: ' + name
			print 'Asset Number: ' + str(asset_tag)
			print 'Serial Number: ' + sn
			print 'Mac Address: ' + str(mac_addr)
			print 'JSS Computer ID: ' + jssID + '\n'

def getComputerId(computerSearch, username, password):
	computerSearch_normalized = urllib2.quote(computerSearch)

	reqStr = jss_api_base_url + '/computers/match/' + computerSearch_normalized

	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return -1

	#responseCode = r.code
	baseXml = r.read()
	#print baseXml
	responseXml = etree.fromstring(baseXml)

	response_size = responseXml.find('size').text

	if response_size == '0':
		#print 'Mobile Device not found, please search again.'
		return -1
	elif response_size == '1':
		return responseXml.find('computer/id').text
	else:
		#print 'Too many results, narrow your search paramaters.'
		return -2


def getComputerByID(compID, username, password):
	print "Getting computer with JSS ID " + compID + "..."
	reqStr = jss_api_base_url + '/computers/id/' + compID

	#print reqStr

	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		responseCode = r.code

		#print 'Response Code: ' + str(responseCode)

		baseXml = r.read()
		#print baseXml
		responseXml = etree.fromstring(baseXml)

		#print responseXml.tag

		general = responseXml.find('general')
		name = general.find('name').text
		jssID = general.find('id').text
		asset_tag = general.find('asset_tag').text
		sn = general.find('serial_number').text
		mac_addr = general.find('mac_address').text
		last_contact_time = responseXml.find('general/last_contact_time').text
		report_time = responseXml.find('general/report_date').text
		remote_management = general.find('remote_management')
		managed = remote_management.find('managed').text
		
		print '\nGENERAL INFORMATION:'
		print 'Computer Name: ' + name
		print 'Asset Number: ' + str(asset_tag)
		print 'JSS Computer ID: ' + jssID
		print 'Serial Number: ' + sn
		print 'Mac Address: ' + mac_addr 
		print 'Managed: ' + managed
		print 'Last Check-In: ' + last_contact_time
		print 'Last Inventory Update: ' + report_time

		assigned_user = responseXml.find('location/username').text
		real_name = responseXml.find('location/real_name').text
		email_address = responseXml.find('location/email_address').text
		position = responseXml.find('location/position').text
		phone = responseXml.find('location/phone').text
		department = responseXml.find('location/department').text
		building = responseXml.find('location/building').text
		room = responseXml.find('location/room').text

		print '\nUSER AND LOCATION:'
		print 'Username: ' + str(assigned_user)
		print 'Real Name: ' + str(real_name)
		print 'Email: ' + str(email_address)
		print 'Position: ' + str(position)
		print 'Phone: ' + str(phone)
		print 'Department: ' + str(department)
		print 'Building: ' + str(building)
		print 'Room: ' + str(room)


		hardware = responseXml.find('hardware')
		model = hardware.find('model').text
		modelid = hardware.find('model_identifier').text
		ram = hardware.find('total_ram').text
		ram_gb = int(ram) / 1000
		os_version = hardware.find('os_version').text
		processor_type = hardware.find('processor_type').text
		processor_speed = hardware.find('processor_speed').text

		storage = hardware.find('storage')
		device = storage.find('device')
		disk_size = device.find('size').text
		disk_size_gb = int(disk_size) / 1000
		partition = device.find('partition')
		fv2status = partition.find('filevault2_status').text

		print '\nHARDWARE INFORMATION:'
		print 'Model: ' + model
		print 'Model ID: ' + modelid
		print 'OS X Version: ' + os_version
		print 'Processor: ' + processor_type + ' ' + processor_speed + ' MHz'
		print 'RAM: ' + str(ram_gb) + ' GB'
		print 'Disk Size: ' + str(disk_size_gb) + ' GB'
		print 'FileVault2 Status: ' + str(fv2status)

		extension_attributes = responseXml.find('extension_attributes')
		eas = []

		print '\nEXTENSION ATTRIBUTES:'

		for ea in extension_attributes.findall('extension_attribute'):
			eaName = ea.find('name').text
			eaValue = ea.find('value').text
			eaPair = str(eaName) + ': ' + str(eaValue)
			eas += [ eaPair ]

		print '\n'.join (sorted (eas))


		groups_accounts = responseXml.find('groups_accounts')
		computer_group_memberships = groups_accounts.find('computer_group_memberships')
		#print computer_group_memberships

		groups = []
		for group in computer_group_memberships.findall('group'):
			groupName = group.text
			groups += [ groupName ]
			#print groupName
		print '\nGROUPS: '
		print '\n'.join (sorted (groups))

		
		local_accounts = groups_accounts.find('local_accounts')
		localusers = []
		for user in local_accounts.findall('user'):
			username = user.find('name').text
			localusers += [ username ]

		print '\nUSERS: '
		print '\n'.join (sorted (localusers))

		print '\n'
		#print prettify(responseXml)

		#print etree.tostring(responseXml)
	else:
		print 'Failed to find computer with JSS ID ' + compID

## Add the named computer to the specified computer group. If either the computer or the computer_group results in zero or multiple matches, the call will fail and exit.
def addComputerToGroup(computer, computer_group, username, password):
	# Find computer JSS ID
	computer_id = getComputerId(computer, username, password)

	if str(computer_id) == '-1':
		print 'Computer ' + computer + ' not found, please try again.'
		return
	elif str(computer_id) == '-2':
		print 'More than one computer found matching search string ' + computer + ', please try again.'
		return

	# Find computer group JSS ID
	computer_group_id = getComputerGroupId(computer_group, username, password)
	if str(computer_group_id) == '-1':
		print 'Computer group ' + computer_group + ' not found, please try again.'
		return

	print 'Adding computer id ' + str(computer_id) + ' to computer group id ' + str(computer_group_id)

	putStr = jss_api_base_url + '/computergroups/id/' + str(computer_group_id)
	putXML = '<computer_group><computer_additions><computer><id>' + str(computer_id) + '</id></computer></computer_additions></computer_group>'

	#print putStr
	#print putXML
	#return

	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to add computer ' + computer + ' to group, see error above.'
		return
	else:
		print 'Successfully added computer ' + computer + ' to group ' + computer_group + '.'

def removeComputerFromGroup(computer, computer_group, username, password):
	# Find computer JSS ID
	computer_id = getComputerId(computer, username, password)

	if str(computer_id) == '-1':
		print 'Computer ' + computer + ' not found, please try again.'
		return
	elif str(computer_id) == '-2':
		print 'More than one computer found matching search string ' + computer + ', please try again.'
		return

	# Find computer group JSS ID
	computer_group_id = getComputerGroupId(computer_group, username, password)
	if str(computer_group_id) == '-1':
		print 'Computer group ' + computer_group + ' not found, please try again.'
		return

	print 'Removing computer id ' + str(computer_id) + ' from computer group id ' + str(computer_group_id)

	putStr = jss_api_base_url + '/computergroups/id/' + str(computer_group_id)
	putXML = '<computer_group><computer_deletions><computer><id>' + str(computer_id) + '</id></computer></computer_deletions></computer_group>'

	#print putStr
	#print putXML
	#return

	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to remove computer ' + computer + ' from group, see error above.'
		return
	else:
		print 'Successfully removed computer ' + computer + ' from group ' + computer_group + '.'

## MOBILE DEVICE FUNCTIONS

def getMobileDevice(mobileDeviceName, username, password, detail):
	mobileDeviceName_normalized = urllib2.quote(mobileDeviceName)
	reqStr = jss_api_base_url + '/mobiledevices/match/' + mobileDeviceName_normalized
	#print reqStr
	#print detail

	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return

	#responseCode = r.code
	baseXml = r.read()
	#print baseXml
	responseXml = etree.fromstring(baseXml)

	print 'All mobile devices with ' + mobileDeviceName + ' as part of the device information:\n'

	for mobile_device in responseXml.findall('mobile_device'):
		name = mobile_device.find('name').text
		sn = mobile_device.find('serial_number').text
		mac_addr = mobile_device.find('mac_address').text
		jssID = mobile_device.find('id').text

		if detail == 'yes':
			getMobileDeviceByID(jssID, username, password)
		else:
			print 'Mobile Device Name: ' + name
			print 'Serial Number: ' + sn
			print 'Mac Address: ' + str(mac_addr)
			print 'JSS Mobile Device ID: ' + jssID + '\n'

## Get single mobile device Id. If no results, return -1, if more than one result, return -2, if exactly one result, return mobile device id.
def getMobileDeviceId(mobileDeviceName, username, password):
	mobileDeviceName_normalized = urllib2.quote(mobileDeviceName)
	reqStr = jss_api_base_url + '/mobiledevices/match/' + mobileDeviceName_normalized

	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return -1

	#responseCode = r.code
	baseXml = r.read()
	#print baseXml
	responseXml = etree.fromstring(baseXml)

	response_size = responseXml.find('size').text

	if response_size == '0':
		#print 'Mobile Device not found, please search again.'
		return -1
	elif response_size == '1':
		return responseXml.find('mobile_device/id').text
	else:
		#print 'Too many results, narrow your search paramaters.'
		return -2

def getMobileDeviceByID(mobileID, username, password):
	print "Getting mobile device with JSS ID " + mobileID + "..."
	reqStr = jss_api_base_url + '/mobiledevices/id/' + mobileID

	#print reqStr

	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		responseCode = r.code

		#print 'Response Code: ' + str(responseCode)

		baseXml = r.read()
		#print baseXml
		responseXml = etree.fromstring(baseXml)

		#print responseXml.tag
		
		general = responseXml.find('general')
		jssID = general.find('id').text
		name = general.find('name').text
		model = general.find('model').text
		last_inventory_update = general.find('last_inventory_update').text
		asset_tag = general.find('asset_tag').text
		os_version = general.find('os_version').text
		sn = general.find('serial_number').text
		mac_addr = general.find('wifi_mac_address').text
		ip_addr = general.find('ip_address').text
		managed = general.find('managed').text
		supervised = general.find('supervised').text
		
		print '\nGENERAL INFORMATION:'
		print 'JSS Mobile Device ID: ' + jssID
		print 'Mobile Name: ' + name
		print 'Model: ' + model
		print 'Last Inventory Update: ' + last_inventory_update
		print 'Asset Number: ' + str(asset_tag)
		print 'OS Version: ' + os_version
		print 'Serial Number: ' + sn
		print 'Mac Address: ' + mac_addr 
		print 'IP Address: ' + ip_addr
		print 'Managed: ' + managed
		print 'Supervised: ' + supervised
		

		assigned_user = responseXml.find('location/username').text
		real_name = responseXml.find('location/real_name').text
		email_address = responseXml.find('location/email_address').text
		position = responseXml.find('location/position').text
		phone = responseXml.find('location/phone').text
		department = responseXml.find('location/department').text
		building = responseXml.find('location/building').text
		room = responseXml.find('location/room').text

		print '\nUSER AND LOCATION:'
		print 'Username: ' + str(assigned_user)
		print 'Real Name: ' + str(real_name)
		print 'Email: ' + str(email_address)
		print 'Position: ' + str(position)
		print 'Phone: ' + str(phone)
		print 'Department: ' + str(department)
		print 'Building: ' + str(building)
		print 'Room: ' + str(room)

		mobile_device_groups = responseXml.find('mobile_device_groups')

		groups = []
		for group in mobile_device_groups.findall('mobile_device_group'):
			groupId = group.find('id').text
			groupName = group.find('name').text
			groupPair = str(groupId) + ': ' + str(groupName)
			groups += [ groupPair ]
			#print groupName
		print '\nMOBILE DEVICE GROUPS: '
		print '\n'.join (sorted (groups))

		print '\n'
		#print prettify(responseXml)

		#print etree.tostring(responseXml)
	else:
		print 'Failed to find mobile device with JSS ID ' + mobileID

def getMobileDeviceGroup(mobile_device_group_name, username, password):
	print 'Getting mobile device group named: ' + mobile_device_group_name + '...'
	mobile_device_group_name_normalized = urllib2.quote(mobile_device_group_name)

	reqStr = jss_api_base_url + '/mobiledevicegroups/name/' + mobile_device_group_name_normalized


	#print reqStr

	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		responseCode = r.code

		#print 'Response Code: ' + str(responseCode)

		baseXml = r.read()
		responseXml = etree.fromstring(baseXml)

		mobileDeviceGroupId = responseXml.find('id').text
		mobileDeviceGroupSize = responseXml.find('criteria/size').text

		if mobileDeviceGroupSize == '0':
			print 'No devices in this group'
			return mobileDeviceGroupId

		print 'Group ID: ' + mobileDeviceGroupId
		#print prettify(responseXml)
		mobiledevicemembers = responseXml.find('mobile_devices')

		mobiledevices = []
		for mobiledevice in mobiledevicemembers.findall('mobile_device'):
			mobiledevicename = mobiledevice.find('name').text
			mobiledeviceid = mobiledevice.find('id').text
			mobiledeviceserial = mobiledevice.find('serial_number').text
			mobiledeviceinfo = str(mobiledevicename) + ', ' + str(mobiledeviceid) + ', ' + str(mobiledeviceserial)
			mobiledevices += [ mobiledeviceinfo ]
		print 'All devices in group ' + mobile_device_group_name + ' [name, jss_id, serial_no]:\n'
		print '\n'.join (sorted (mobiledevices))
		print '\nTotal Devices: ' + str(len(mobiledevices))
		return mobileDeviceGroupId
	else:
		print 'Failed to find mobile device group with name ' + mobile_device_group_name
		return -1

def addMobileDeviceToGroup(mobile_device, mobile_device_group, username, password):
	# Find mobile device JSS ID
	mobile_device_id = getMobileDeviceId(mobile_device, username, password)
	if str(mobile_device_id) == '-1':
		print 'Mobile device ' + mobile_device + ' not found, please try again.'
		return
	elif str(mobile_device_id) == '-2':
		print 'More than one mobile device found matching search string ' + mobile_device + ', please try again.'
		return

	# Find mobile device group ID
	mobile_device_group_id = getMobileDeviceGroup(mobile_device_group, username, password)
	if str(mobile_device_group_id) == '-1':
		print 'Mobile device group ' + mobile_device_group + ' not found, please try again.'
		return

	print 'Adding mobile device id ' + str(mobile_device_id) + ' to group id ' + str(mobile_device_group_id)

	putStr = jss_api_base_url + '/mobiledevicegroups/id/' + str(mobile_device_group_id)
	putXML = '<mobile_device_group><mobile_device_additions><mobile_device><id>' + str(mobile_device_id) + '</id></mobile_device></mobile_device_additions></mobile_device_group>'

	#print putStr
	#print putXML
	#return

	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to add mobile device ' + mobile_device + ' to group, see error above.'
		return
	else:
		print 'Successfully added mobile device ' + mobile_device + ' to group ' + mobile_device_group + '.'


def removeMobileDeviceFromGroup(mobile_device, mobile_device_group, username, password):
	# Find mobile device JSS ID
	mobile_device_id = getMobileDeviceId(mobile_device, username, password)
	if str(mobile_device_id) == '-1':
		print 'Mobile device ' + mobile_device + ' not found, please try again.'
		return
	elif str(mobile_device_id) == '-2':
		print 'More than one mobile device matching search string ' + mobile_device + ', please try again.'
		return

	# Find mobile device group ID
	mobile_device_group_id = getMobileDeviceGroup(mobile_device_group, username, password)
	if str(mobile_device_group_id) == '-1':
		print 'Mobile device group ' + mobile_device_group + ' not found, please try again.'
		return

	print 'Removing mobile device id ' + str(mobile_device_id) + ' from group id ' + str(mobile_device_group_id)

	putStr = jss_api_base_url + '/mobiledevicegroups/id/' + str(mobile_device_group_id)
	putXML = '<mobile_device_group><mobile_device_deletions><mobile_device><id>' + str(mobile_device_id) + '</id></mobile_device></mobile_device_deletions></mobile_device_group>'

	#print putStr
	#print putXML
	#return

	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to remove mobile device ' + mobile_device + ' to group, see error above.'
		return
	else:
		print 'Successfully remove mobile device ' + mobile_device + ' to group ' + mobile_device_group + '.'

## Find Mobile Device using search string using name, serial number, asset tag, etc. 
## Name, mac address, etc. to filter by. Match uses the same format as the general search in the JSS. For instance, admin* can be used to match mobile device names that begin with admin

def findMobileDeviceId(searchString, username, password):
	#print 'Searching for mobile device with string ' + searchString
	searchString_normalized = urllib2.quote(searchString)

	reqStr = jss_api_base_url + '/mobiledevices/match/' + searchString_normalized
	#print reqStr
	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		responseCode = r.code
		baseXml = r.read()
		responseXml = etree.fromstring(baseXml)
		#print prettify(responseXml)
		#return

		#mobiledevicemembers = responseXml.find('mobile_devices')
		#print mobiledevicemembers
		#return
		result_size = responseXml.find('size').text
		#print 'hello' + str(result_size)

		if result_size == '0':
			print 'No matches found.'
			return -1
		elif result_size == '1':
			#print 'Single match found'
			mobile_device_id = responseXml.find('mobile_device/id').text
			print mobile_device_id
			return mobile_device_id
			#print prettify(responseXml)
		else:
			print 'Multiple matches found, please narrow your search.'
			return -1
	else:
		print 'Error'

def updateMobileAssetTag(mobileSearch, asset_tag, username, password):
	print 'Updating asset tag for mobile device ' + mobileSearch + ' with asset tag ' + asset_tag + '...'
	mobile_id = getMobileDeviceId(mobileSearch, username, password)
	if str(mobile_id) == '-1':
		print 'Mobile device ' + mobileSearch + ' not found, please try again.'
		return
	elif str(mobile_id) == '-2':
		print 'More than one mobile device matching search string ' + str(mobileSearch) + ', please try again.'
		return

	putStr = jss_api_base_url + '/mobiledevices/id/' + mobile_id
	#print putStr

	putXML = "<mobile_device><general><asset_tag>" + asset_tag + "</asset_tag></general></mobile_device>"
	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to update asset tag for mobile device ' + mobileSearch + ', see error above.'
		return
	else:
		print 'Successfully updated asset tag for mobile device ' + mobileSearch + '.'

## GROUPS

def GetAllComputerGroups(resource, username, password):
	reqStr = jss_api_base_url + '/computergroups'

	try:
		response = sendAPIRequest(reqStr, username, password, 'GET')
		xmlstring = response.read()
		print str(xmlstring)

		responseCode = str(response.code)
		print responseCode
		#print response.read()

		if '200' in str(responseCode):
			print "Successful API call, printing XML results"
			xml = etree.fromstring(xmlstring)
			#print xml.tag
			#print xml.attrib

			#print etree.tostring(xml)

			print prettify(xml)

			for computer_group in xml.findall('computer_group'):
				name = computer_group.find('name').text
				groupId = computer_group.find('id').text
				is_smart = computer_group.find('is_smart').text
				print name + ' [id: ' + groupId + ', smart: ' + is_smart + ']'
		elif '401' in str(responseCode):
			print "Authorization failed"
	except urllib2.HTTPError, err:
		if '401' in str(err):
			print 'Authorization failed, goodbye.'

def getComputerGroupId(groupSearch, username, password):
	groupSearch_normalized = urllib2.quote(groupSearch)

	reqStr = jss_api_base_url + '/computergroups/name/' + groupSearch_normalized

	r = sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		responseCode = r.code
		#print 'Response Code: ' + str(responseCode)

		baseXml = r.read()
		responseXml = etree.fromstring(baseXml)

		computerGroupId = responseXml.find('id').text
		print computerGroupId
		return computerGroupId
	else:
		#print 'Group not found.'
		return -1


def getSerialNumber():
	print 'test'

def unmanageComputer(comp_id, username, password):
	print "Unmanaging computer " + comp_id + "..."
	
	#reqStr = jss_api_base_url + '/computercommands/command/UnmanageDevice'
	#print reqStr

	putStr = jss_api_base_url + '/computers/id/' + comp_id
	#print putStr

	#postXML = "<computers><computer><general><id>" + comp_id + "</id><remote_management><managed>false</managed></remote_management></general></computer></computers>"

	putXML = "<computer><general><remote_management><managed>false</managed></remote_management></general></computer>"
	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to unmanage computer ID ' + comp_id + '. Make sure the computer actually exists in the JSS.'
	else:
		responseCode = str(response.code)
		#print 'Response Code: ' + responseCode
		if responseCode == '201':
			print 'Successfully unmanaged computer ID ' + comp_id + '...'
			
		
		## Uncomment this part to see the xml response
		#xmlstring = response.read()
		#xml = etree.fromstring(xmlstring)
		#print prettify(xml)

def updateAssetTag(comp_id, asset_tag, username, password):
	print 'Updating asset tag for computer ID ' + comp_id + ' with asset tag ' + asset_tag + '...'

	putStr = jss_api_base_url + '/computers/id/' + comp_id
	#print putStr

	putXML = "<computer><general><asset_tag>" + asset_tag + "</asset_tag></general></computer>"
	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to update asset tag for computer ' + comp_id + ', see error above.'
		return
	else:
		print 'Successfully updated asset tag for computer ' + comp_id + '.'

def updateComputerUserInfo(comp_id, username, real_name, email_address, position, phone, department, building, room, overwrite, jssuser, jsspassword):
	
	
	putStr = jss_api_base_url + '/computers/id/' + comp_id
	if overwrite == 'y':
		print 'Overwriting all existing user and location info for computer ID ' + comp_id + ' with the following:\n' + '\n  Username: ' + username + '\n  Full Name: ' + real_name + '\n  Email: ' + email_address + '\n  Position: ' + position + '\n  Phone: ' + str(phone) + '\n  Department: ' + department + '\n  Building: ' + building + '\n  Room: ' + room + '\n'
		putXML = "<computer><location><username>" + username + "</username><real_name>" + real_name + "</real_name><email_address>" + email_address + "</email_address><position>" + position + "</position><phone>" + str(phone) + "</phone><department>" + department + "</department><building>" + building + "</building><room>" + room + "</room></location></computer>"
	else:
		updateStr = 'Updating user and location info for computer ID ' + comp_id + ' with the following:\n'
		putXML = "<computer><location>"
		updateCount = 0

		if username != '':
			putXML += '<username>' + username + '</username>'
			updateStr += '\n  Username : ' + username
			updateCount += 1

		if real_name != '':
			putXML += '<real_name>' + real_name + '</real_name>'
			updateStr += '\n Full Name: ' + real_name
			updateCount += 1

		if email_address != '':
			putXML += '<email_address>' + email_address + '</email_address>'
			updateStr += '\n  Email: ' + email_address
			updateCount += 1

		if position != '':
			putXML += '<position>' + position + '</position>'
			updateStr += '\n  Position: ' + position
			updateCount += 1

		if phone != '':
			putXML += '<phone>' + str(phone) + '</phone>'
			updateStr += '\n  Phone: ' + str(phone)
			updateCount += 1

		if department != '':
			putXML += '<department>' + department + '</department>'
			updateStr += '\n  Department: ' + department
			updateCount += 1

		if building != '':
			putXML += '<building>' + building + '</building>'
			updateStr += '\n  Building: ' + building
			updateCount += 1

		if room != '':
			putXML += '<room>' + room + '</room>'
			updateStr += '\n  Room: ' + room
			updateCount += 1

		putXML += "</location></computer>"

		if updateCount == 0:
			# Nothing to update
			print "Nothing to update."
			return


	#print putXML

	response = sendAPIRequest(putStr, jssuser, jsspassword, 'PUT', putXML)

	if response == -1:
		print 'Failed to update user and location info for computer ' + comp_id + ', see error above.'
		return
	else:
		print 'Successfully updated user and location info for computer ' + comp_id + '.'

def updateMobileDeviceUserInfo(mobile_id, username, real_name, email_address, position, phone, department, building, room, overwrite, jssuser, jsspassword):
	
	
	putStr = jss_api_base_url + '/mobiledevices/id/' + mobile_id
	if overwrite == 'y':
		print 'Overwriting all existing user and location info for mobile device ID ' + mobile_id + ' with the following:\n' + '\n  Username: ' + username + '\n  Full Name: ' + real_name + '\n  Email: ' + email_address + '\n  Position: ' + position + '\n  Phone: ' + str(phone) + '\n  Department: ' + department + '\n  Building: ' + building + '\n  Room: ' + room + '\n'
		putXML = "<mobile_device><location><username>" + username + "</username><real_name>" + real_name + "</real_name><email_address>" + email_address + "</email_address><position>" + position + "</position><phone>" + str(phone) + "</phone><department>" + department + "</department><building>" + building + "</building><room>" + room + "</room></location></mobile_device>"
	else:
		updateStr = 'Updating user and location info for mobile device id ID ' + mobile_id + ' with the following:\n'
		putXML = "<mobile_device><location>"
		updateCount = 0

		if username != '':
			putXML += '<username>' + username + '</username>'
			updateStr += '\n  Username : ' + username
			updateCount += 1

		if real_name != '':
			putXML += '<real_name>' + real_name + '</real_name>'
			updateStr += '\n Full Name: ' + real_name
			updateCount += 1

		if email_address != '':
			putXML += '<email_address>' + email_address + '</email_address>'
			updateStr += '\n  Email: ' + email_address
			updateCount += 1

		if position != '':
			putXML += '<position>' + position + '</position>'
			updateStr += '\n  Position: ' + position
			updateCount += 1

		if phone != '':
			putXML += '<phone>' + str(phone) + '</phone>'
			updateStr += '\n  Phone: ' + str(phone)
			updateCount += 1

		if department != '':
			putXML += '<department>' + department + '</department>'
			updateStr += '\n  Department: ' + department
			updateCount += 1

		if building != '':
			putXML += '<building>' + building + '</building>'
			updateStr += '\n  Building: ' + building
			updateCount += 1

		if room != '':
			putXML += '<room>' + room + '</room>'
			updateStr += '\n  Room: ' + room
			updateCount += 1

		putXML += "</location></mobile_device>"

		if updateCount == 0:
			# Nothing to update
			print "Nothing to update."
			return


	#print putXML
	response = sendAPIRequest(putStr, jssuser, jsspassword, 'PUT', putXML)

	if response == -1:
		print 'Failed to update user and location info for mobile device ' + mobile_id + ', see error above.'
		return
	else:
		print 'Successfully updated user and location info for mobile device ' + mobile_id + '.'

def updateComputerUserInfoFromCSV(computersCSV, username, password):

	# CSV File with 9 columns: JSS Computer ID, Username, Full Name, Email, Position, Phone, Department, Building, Room, Overwrite

	with open (computersCSV, 'rU') as csvfile:
		computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		#Skip the header row
		next(computerreader, None)

		for row in computerreader:
			compID = row[0].replace('"', '').strip()
			uName = row[1].replace('"', '').strip()
			fullName = row[2].replace('"', '').strip()
			email = row[3].replace('"', '').strip()
			position = row[4].replace('"', '').strip()
			phone = row[5].replace('"', '').strip()
			department = row[6].replace('"', '').strip()
			building = row[7].replace('"', '').strip()
			room = row[8].replace('"', '').strip()
			overwrite = row[9].replace('"', '').strip()

			print 'Update computer user info with ' + 'JSS ID: ' + compID + ' Username: ' + uName + ' Full Name: ' + fullName + ' Email: ' + email + ' Position: ' + position + ' Phone: ' + str(phone) + ' Dept: ' + department + 'Bldg: ' + building + ' Room: ' + room + ' Overwrite: ' + overwrite
			updateComputerUserInfo(compID, uName, fullName, email, position, phone, department, building, room, overwrite, username, password)
	return

def updateMobileDeviceUserInfoFromCSV(mobiledevicesCSV, username, password):

	# CSV File with 9 columns: JSS Mobile Device ID, Username, Full Name, Email, Position, Phone, Department, Building, Room, Overwrite

	with open (mobiledevicesCSV, 'rU') as csvfile:
		mobiledevicesreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		#Skip the header row
		next(mobiledevicesreader, None)

		for row in mobiledevicesreader:
			mobileDeviceID = row[0].replace('"', '').strip()
			uName = row[1].replace('"', '').strip()
			fullName = row[2].replace('"', '').strip()
			email = row[3].replace('"', '').strip()
			position = row[4].replace('"', '').strip()
			phone = row[5].replace('"', '').strip()
			department = row[6].replace('"', '').strip()
			building = row[7].replace('"', '').strip()
			room = row[8].replace('"', '').strip()
			overwrite = row[9].replace('"', '').strip()

			print 'Update mobile device user info with ' + 'JSS ID: ' + mobileDeviceID + ' Username: ' + uName + ' Full Name: ' + fullName + ' Email: ' + email + ' Position: ' + position + ' Phone: ' + str(phone) + ' Dept: ' + department + 'Bldg: ' + building + ' Room: ' + room + ' Overwrite: ' + overwrite
			updateMobileDeviceUserInfo(mobileDeviceID, uName, fullName, email, position, phone, department, building, room, overwrite, username, password)
	return


def unmanageComputerIDsFromCSV(computersCSV, username, password):

	# CSV file with one column, just JSS computer IDs

	with open (computersCSV, 'rU') as csvfile:
		computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		#Skip the header row
		next(computerreader, None)

		for row in computerreader:
			compID = row[0].replace('"', '').strip()
			#print 'Test Run: Unmanage computer ID ' + compID
			unmanageComputer(compID, username, password)

def deleteComputerByID(comp_id, username, password):
	
	getComputerByID(comp_id, username, password)

	sure = raw_input('Are you sure you want to delete the computer above from the JSS? (y/n): ')

	if sure == 'y':	
		print "Deleting computer " + comp_id + "..."

		delStr = jss_api_base_url + '/computers/id/' + comp_id
		#print delStr
		response = sendAPIRequest(delStr, username, password, 'DELETE')

		if response == -1:
			print 'Failed to delete computer. See errors above.'
		else:
			print 'Successfully deleted computer ' + comp_id

	else:
		print 'Aborting request to delete computer ' + comp_id

		## Uncomment this part to see the xml response
		#xmlstring = response.read()
		#xml = etree.fromstring(xmlstring)
		#print prettify(xml)

		#responseCode = str(response.code)
		#print 'Response Code: ' + responseCode

def deleteComputerIDsFromCSV(computersCSV, username, password):

	# CSV file with one column, just JSS computer IDs

	with open (computersCSV, 'rU') as csvfile:
		computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		#Skip the header row
		next(computerreader, None)

		for row in computerreader:
			compID = row[0].replace('"', '').strip()
			print 'Test Run: Delete computer ID ' + compID
			deleteComputerByID(compID, username, password)


def getComputerCommands(username, password):
	print "Getting computer commands..."
	reqStr = jss_api_base_url + '/computercommands'
	#print reqStr

	r = sendAPIRequest(reqStr, username, password, 'GET')
	print r

	responseCode = r.code
	print 'Response code: ' + str(responseCode)

	responseXml = etree.fromstring(r.read())

	print etree.tostring(responseXml)

	#responseXml = etree.fromstring(r.read())
	#print prettify(responseXml)
	#print etree.tostring(responseXml)

def getJSSUsername():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	jssusernameLocation = scriptPath + '/.jssusername'
	#print apikeyLocation

	if os.path.isfile(jssusernameLocation):
		#print "api key file exists, here's the key!"
		
		#print "Path: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		with open (jssusernameLocation) as jssusernamefile:
			jss_username = jssusernamefile.read().replace('\n','')
			return jss_username

	else:
		print "JSS Username does not exist, prompting for JSS username"

		try:
			jss_username = raw_input('JSS Username: ')
			return jss_username
		except:
			print "\nCtrl-C detected, exiting..."
			raise SystemExit

def getJSSPassword():
	## This method supports a plaintext password stored in the file .jsspassword existing in the same directory
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	jsspasswordLocation = scriptPath + '/.jsspassword'
	#print apikeyLocation

	if os.path.isfile(jsspasswordLocation):
		#print "api key file exists, here's the key!"
		
		#print "Path: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		with open (jsspasswordLocation) as jsspasswordfile:
			jss_password = jsspasswordfile.read().replace('\n','')
			return jss_password

	else:
		print "JSS Password does not exist, prompting for key"

		try:
			jss_password = getpass.getpass('JSS Password: ')
			return jss_password
		except:
			print "\nCtrl-C detected, exiting..."
			raise SystemExit

def main():

	### Start here
	#user = raw_input('JSS Username: ')
	#password = getpass.getpass('Password: ')

	user = getJSSUsername()
	#password = getJSSPassword()
	password = getEncryptedJSSpw()



	unmanageComputerHelp = 'JSS Computer ID'

	parser = argparse.ArgumentParser(description='Interact with the Casper JSS API')
	subparsers = parser.add_subparsers(help='Enter command with -h for help on each particular command')
	'''
	parser_config = subparsers.add_parser('config', help='Casper CLI Configuration options')
	parser_config.set_defaults(which='config')
	parser_config.add_argument('-o', '--option', metavar='', choices=['Reset', 'Setup'], help='Enter Reset to reset the CLI to default settings, enter Setup to configure the Casper CLI')
	'''

	parser_addcomputertogroup = subparsers.add_parser('addcomputertogroup', help='Add computer to group')
	parser_addcomputertogroup.set_defaults(cmd='addcomputertogroup')
	parser_addcomputertogroup.add_argument('computerSearch', help='Computer to add')
	parser_addcomputertogroup.add_argument('computerGroupSearch', help='Computer group to add computer to')

	parser_addmobiledevicetogroup = subparsers.add_parser('addmobiledevicetogroup', help='Add mobile device to group')
	parser_addmobiledevicetogroup.set_defaults(cmd='addmobiledevicetogroup')
	parser_addmobiledevicetogroup.add_argument('mobileSearch', help='Mobile Device to add')
	parser_addmobiledevicetogroup.add_argument('mobileGroupSearch', help='Mobile Device group to add device to')

	parser_deletecomputerbyid = subparsers.add_parser('deletecomputerbyid', help='Delete computer by JSS ID')
	parser_deletecomputerbyid.set_defaults(cmd='deletecomputerbyid')
	parser_deletecomputerbyid.add_argument('computerID', help=unmanageComputerHelp)
	
	parser_deletecomputeridsfromcsv = subparsers.add_parser('deletecomputeridsfromcsv', help='Delete computers from JSS IDs in CSV file')
	parser_deletecomputeridsfromcsv.set_defaults(cmd='deletecomputeridsfromcsv')
	parser_deletecomputeridsfromcsv.add_argument('csvfile', help='Full path to CSV file with one column containing JSS computer IDs to delete')
	
	parser_findmobiledeviceid = subparsers.add_parser('findmobiledeviceid', help='Find mobile device JSS ID using search string')
	parser_findmobiledeviceid.set_defaults(cmd='findmobiledeviceid')
	parser_findmobiledeviceid.add_argument('searchString', help='String to search for, followed by * for wildcard')

	parser_getcomputer = subparsers.add_parser('getcomputer', help='Search for a computer')
	parser_getcomputer.set_defaults(cmd='getcomputer')
	parser_getcomputer.add_argument('compsearch', help='Search string for computer')
	parser_getcomputer.add_argument('-d', '--detail', default='no', help='Print detailed computer info')
	parser_getcomputerbyid = subparsers.add_parser('getcomputerbyid', help='Get computer by ID')
	parser_getcomputerbyid.set_defaults(cmd='getcomputerbyid')
	parser_getcomputerbyid.add_argument('computerID', help=unmanageComputerHelp)

	parser_getcomputergroupid = subparsers.add_parser('getcomputergroupid', help='Get computer group JSS ID')
	parser_getcomputergroupid.set_defaults(cmd='getcomputergroupid')
	parser_getcomputergroupid.add_argument('groupsearch', help='Search string for computer group')

	parser_getmobiledevice = subparsers.add_parser('getmobiledevice', help='Search for a mobile device')
	parser_getmobiledevice.set_defaults(cmd='getmobiledevice')
	parser_getmobiledevice.add_argument('mobilesearch', help='Search string for mobile device')
	parser_getmobiledevice.add_argument('-d', '--detail', default='no', help='Print detailed mobile device info')
	parser_getmobiledevicebyid = subparsers.add_parser('getmobiledevicebyid', help='Get mobile device by ID')
	parser_getmobiledevicebyid.set_defaults(cmd='getmobiledevicebyid')
	parser_getmobiledevicebyid.add_argument('mobileDeviceID', help='Mobile Device JSS ID')
	parser_getmobiledevicegroup = subparsers.add_parser('getmobiledevicegroup', help='Search for a mobile device group')
	parser_getmobiledevicegroup.set_defaults(cmd='getmobiledevicegroup')
	parser_getmobiledevicegroup.add_argument('mobilegroupsearch', help='Search string for mobile device group')

	parser_removecomputerfromgroup = subparsers.add_parser('removecomputerfromgroup', help='Remove a computer from a group')
	parser_removecomputerfromgroup.set_defaults(cmd='removecomputerfromgroup')
	parser_removecomputerfromgroup.add_argument('computerSearch', help='Computer to remove')
	parser_removecomputerfromgroup.add_argument('computerGroupSearch', help='Computer group to remove computer from')

	parser_removemobiledevicefromgroup = subparsers.add_parser('removemobiledevicefromgroup', help='Remove a mobile device from a group')
	parser_removemobiledevicefromgroup.set_defaults(cmd='removemobiledevicefromgroup')
	parser_removemobiledevicefromgroup.add_argument('mobileSearch', help='Mobile Device to remove')
	parser_removemobiledevicefromgroup.add_argument('mobileGroupSearch', help='Mobile Device group to remove device from')

	parser_unmanagecomputer = subparsers.add_parser('unmanagecomputer', help='Get user object')
	parser_unmanagecomputer.set_defaults(cmd='unmanagecomputer')
	parser_unmanagecomputer.add_argument('computerID', help=unmanageComputerHelp)
	parser_unmanagecomputeridsfromcsv = subparsers.add_parser('unmanagecomputeridsfromcsv', help='Unmanage computers from JSS IDs in CSV file')
	parser_unmanagecomputeridsfromcsv.set_defaults(cmd='unmanagecomputeridsfromcsv')
	parser_unmanagecomputeridsfromcsv.add_argument('csvfile', help='Full path to CSV file with one column containing JSS computer IDs to unmanage')
	parser_updateassettag = subparsers.add_parser('updateassettag', help='Update Asset Tag')
	parser_updateassettag.set_defaults(cmd='updateassettag')
	parser_updateassettag.add_argument('computerID', help='JSS Computer ID')
	parser_updateassettag.add_argument('assetTag', help='Asset Tag')
	parser_updatecomputeruserinfo = subparsers.add_parser('updatecomputeruserinfo', help='Update User and Location Info')
	parser_updatecomputeruserinfo.set_defaults(cmd='updatecomputeruserinfo')
	parser_updatecomputeruserinfo.add_argument('computerID', help='JSS Computer ID')
	parser_updatecomputeruserinfo.add_argument('-u', '--username', default='', help='Username')
	parser_updatecomputeruserinfo.add_argument('-n', '--real_name', default='', help='Real Name')
	parser_updatecomputeruserinfo.add_argument('-e', '--email_address', default='', help='Email Address')
	parser_updatecomputeruserinfo.add_argument('-p', '--position', default='', help='Position')
	parser_updatecomputeruserinfo.add_argument('-t', '--phone', default='', help='Phone Number')
	parser_updatecomputeruserinfo.add_argument('-d', '--department', default='', help='Department')
	parser_updatecomputeruserinfo.add_argument('-b', '--building', default='', help='Building')
	parser_updatecomputeruserinfo.add_argument('-r', '--room', default='', help='Room')
	parser_updatecomputeruserinfo.add_argument('-o', '--overwrite', default='n', help='Overwrite all existing values [y] or update only [n]. Default is no')
	parser_updatecomputeruserinfofromcsv = subparsers.add_parser('updatecomputeruserinfofromcsv', help='Update Computer User and Location Info from JSS IDs in CSV file')
	parser_updatecomputeruserinfofromcsv.set_defaults(cmd='updatecomputeruserinfofromcsv')
	parser_updatecomputeruserinfofromcsv.add_argument('csvfile', help='Full path to CSV File with 9 columns: JSS Computer ID, Username, Full Name, Email, Position, Phone, Department, Building, Room, Overwrite')

	parser_updatemobileassettag = subparsers.add_parser('updatemobileassettag', help='Update Mobile Asset Tag')
	parser_updatemobileassettag.set_defaults(cmd='updatemobileassettag')
	parser_updatemobileassettag.add_argument('mobileSearch', help='Mobile Device to add asset tag to')
	parser_updatemobileassettag.add_argument('assetTag', help='Asset Tag')

	parser_updatemobiledeviceuserinfo = subparsers.add_parser('updatemobiledeviceuserinfo', help='Update User and Location Info')
	parser_updatemobiledeviceuserinfo.set_defaults(cmd='updatemobiledeviceuserinfo')
	parser_updatemobiledeviceuserinfo.add_argument('mobileDeviceID', help='JSS Mobile Device ID')
	parser_updatemobiledeviceuserinfo.add_argument('-u', '--username', default='', help='Username')
	parser_updatemobiledeviceuserinfo.add_argument('-n', '--real_name', default='', help='Real Name')
	parser_updatemobiledeviceuserinfo.add_argument('-e', '--email_address', default='', help='Email Address')
	parser_updatemobiledeviceuserinfo.add_argument('-p', '--position', default='', help='Position')
	parser_updatemobiledeviceuserinfo.add_argument('-t', '--phone', default='', help='Phone Number')
	parser_updatemobiledeviceuserinfo.add_argument('-d', '--department', default='', help='Department')
	parser_updatemobiledeviceuserinfo.add_argument('-b', '--building', default='', help='Building')
	parser_updatemobiledeviceuserinfo.add_argument('-r', '--room', default='', help='Room')
	parser_updatemobiledeviceuserinfo.add_argument('-o', '--overwrite', default='n', help='Overwrite all existing values [y] or update only [n]. Default is no')
	parser_updatemobiledeviceuserinfofromcsv = subparsers.add_parser('updatemobiledeviceuserinfofromcsv', help='Update Mobile Device User and Location Info from JSS IDs in CSV file')
	parser_updatemobiledeviceuserinfofromcsv.set_defaults(cmd='updatemobiledeviceuserinfofromcsv')
	parser_updatemobiledeviceuserinfofromcsv.add_argument('csvfile', help='Full path to CSV File with 9 columns: JSS Mobile Device ID, Username, Full Name, Email, Position, Phone, Department, Building, Room, Overwrite')


	args = parser.parse_args()

	APIcommand = args.cmd

	#print parser.parse_args()
	#print "Script: " + __file__
	scriptName = inspect.getfile(inspect.currentframe())
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

	## CONFIGURATION SETTINGS

	'''if APIcommand == 'config':
		option = args.option
		if str(option) == 'Reset':
			resetCLI_Settings()
			raise SystemExit
		elif option == 'Setup':
			setupCasperCLI()
			print 'Setup complete.'
			raise SystemExit'''


	## MAIN BODY

	if APIcommand == 'addcomputertogroup':
		computerSearch = args.computerSearch
		computerGroupSearch = args.computerGroupSearch
		addComputerToGroup(computerSearch, computerGroupSearch, user, password)
	elif APIcommand == 'addmobiledevicetogroup':
		mobileSearch = args.mobileSearch
		mobileGroupSearch = args.mobileGroupSearch
		addMobileDeviceToGroup(mobileSearch, mobileGroupSearch, user, password) 
	elif APIcommand == 'deletecomputerbyid':
		computerID = args.computerID
		deleteComputerByID(computerID, user, password)
	elif APIcommand == 'deletecomputeridsfromcsv':
		computersCSV = args.csvfile
		deleteComputerIDsFromCSV(computersCSV, user, password)
	elif APIcommand == 'findmobiledeviceid':
		searchString = args.searchString
		findMobileDeviceId(searchString, user, password)
	elif APIcommand == 'getcomputer':
		compSearch = args.compsearch
		detail = args.detail
		getComputer(compSearch, user, password, detail)
	elif APIcommand == 'getcomputerbyid':
		computerID = args.computerID
		getComputerByID(computerID, user, password)
	elif APIcommand == 'getcomputergroupid':
		groupSearch = args.groupsearch
		getComputerGroupId(groupSearch, user, password)
	elif APIcommand == 'getmobiledevice':
		mobilesearch = args.mobilesearch
		detail = args.detail
		getMobileDevice(mobilesearch, user, password, detail)
	elif APIcommand == 'getmobiledevicebyid':
		mobileDeviceID = args.mobileDeviceID
		getMobileDeviceByID(mobileDeviceID, user, password)
	elif APIcommand == 'getmobiledevicegroup':
		mobileDeviceGroup = args.mobilegroupsearch
		getMobileDeviceGroup(mobileDeviceGroup, user, password)
	elif APIcommand == 'removecomputerfromgroup':
		computerSearch = args.computerSearch
		computerGroupSearch = args.computerGroupSearch
		removeComputerFromGroup(computerSearch, computerGroupSearch, user, password)
	elif APIcommand == 'removemobiledevicefromgroup':
		mobileSearch = args.mobileSearch
		mobileGroupSearch = args.mobileGroupSearch
		removeMobileDeviceFromGroup(mobileSearch, mobileGroupSearch, user, password)
	elif APIcommand == "unmanagecomputer":
		computerID = args.computerID
		unmanageComputer(computerID, user, password)
	elif APIcommand == 'unmanagecomputeridsfromcsv':
		computersCSV = args.csvfile
		unmanageComputerIDsFromCSV(computersCSV, user, password)
	elif APIcommand == 'updateassettag':
		computerID = args.computerID
		assetTag = args.assetTag
		updateAssetTag(computerID, assetTag, user, password)
	elif APIcommand == 'updatecomputeruserinfo':
		computerID = args.computerID
		username = args.username
		real_name = args.real_name
		email_address = args.email_address
		position = args.position
		phone = args.phone
		department = args.department
		building = args.building
		room = args.room
		overwrite = args.overwrite
		updateComputerUserInfo(computerID, username, real_name, email_address, position, phone, department, building, room, overwrite, user, password)
	elif APIcommand == 'updatecomputeruserinfofromcsv':
		computersCSV = args.csvfile
		updateComputerUserInfoFromCSV(computersCSV, user, password)
	elif APIcommand == 'updatemobileassettag':
		mobileSearch = args.mobileSearch
		assetTag = args.assetTag
		updateMobileAssetTag(mobileSearch, assetTag, user, password)
	elif APIcommand == 'updatemobiledeviceuserinfo':
		mobileDeviceID = args.mobileDeviceID
		username = args.username
		real_name = args.real_name
		email_address = args.email_address
		position = args.position
		phone = args.phone
		department = args.department
		building = args.building
		room = args.room
		overwrite = args.overwrite
		updateMobileDeviceUserInfo(mobileDeviceID, username, real_name, email_address, position, phone, department, building, room, overwrite, user, password)
	elif APIcommand == 'updatemobiledeviceuserinfofromcsv':
		mobileDevicesCSV = args.csvfile
		updateMobileDeviceUserInfoFromCSV(mobileDevicesCSV, user, password)
	else:
		print 'Unknown command.'

if __name__ == '__main__':
	## Set the JSS API URL
	jss_api_base_url = getJSS_API_URL()

	## Run the main parser and command line interface
	main()
