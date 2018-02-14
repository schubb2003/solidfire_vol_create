#!/usr/local/bin/python
# Author: Scott Chubb scott.chubb@netapp.com
# Written for Python 3.4 and above
# No warranty is offered, use at your own risk.  While these scripts have been tested in lab situations, all use cases cannot be accounted for.
# Date: 13-Feb-2018
# This scripts shows how to gather volume information on volumeID 1 using requests and web calls
# output is in JSON formatted text.  This can be modified to be used in a more iterative fashion 
#   by switching from web calls to python CLI parsing
import sys
import argparse
import requests
import base64
import json
from solidfire.factory import ElementFactory
# QoS is a dataobject model and must be imported to set QoS
# it is not required to get/print QoS information
from solidfire.models import QoS

parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str,
                    required=True,
                    metavar='mvip',
                    help='MVIP/node name or IP')
parser.add_argument('-u', type=str,
                    required=True,
                    metavar='username',
                    help='username to connect with')
parser.add_argument('-p', type=str,
                    required=True,
                    metavar='password',
                    help='password for user')
parser.add_argument('-v', type=str,
                    required=True,
                    metavar='vol_name',
                    help='volume name')
parser.add_argument('-i', type=int,
                    required=True,
                    metavar='acct_id',
                    help='account ID to attach')
parser.add_argument('-s', type=int,
                    required=True,
                    metavar='vol_size',
                    help='volume size')
parser.add_argument('-e', type=str,
                    required=True,
                    choices=['true', 'false'],
                    metavar='enable512e',
                    help='enable 512 block emulation')
parser.add_argument('-n', type=int,
                    choices=range(50, 15001),
                    required=True,
                    metavar='min_qos',
                    help='minimum QoS, between 50 and 15,000')
parser.add_argument('-x', type=int,
                    choices=range(100, 200001),
                    required=True,
                    metavar='max_qos',
                    help='maximum QoS, between 100, and 15,000')
parser.add_argument('-b', type=int,
                    choices=range(100, 200001),
                    required=True,
                    metavar='burst_qos',
                    help='burst QoS, between max and 200,000')
args = parser.parse_args()

mvip_ip = args.m
user_name = args.u
user_pass = args.p
vol_name = args.v
acct_id = args.i
vol_size = args.s
enable512e = (args.e).lower()
min_qos = args.n
max_qos = args.x
burst_qos = args.b

if vol_size < 1000000000 or vol_size > 8796093022208:
	sys.exit("volume size is either less than 1GB or more than 8TiB")

if enable512e != "true" and enable512e != "false":
    sys.exit("512 emulation must be either true or false")

if max_qos > 15000 or max_qos < 100:
	sys.exit("Maximum QoS is out of bounds, max QoS is valid between 100 and 15000, submitted was %s" % max_qos)

if min_qos < 50 or min_qos > 15000:
	sys.exit("Minimum QoS is out of bounds, min QoS must be between 50 and 15000 submitted was %s" % min_qos)

if burst_qos > 200000 or burst_qos < max_qos:
	sys.exit("Burst QoS is out of bounds, it must be below 200,000 and equal to or greater than max QoS.\n"
		  "Current QoS is set to %s" % burst_qos)
    
# Web/REST auth credentials build authentication
auth = (user_name + ":" + user_pass)
encodeKey = base64.b64encode(auth.encode('utf-8'))
basicAuth = bytes.decode(encodeKey)

headers = {
    'Content-Type': "application/json",
    'Authorization': "Basic %s" % basicAuth,
    'Cache-Control': "no-cache",
    }

# Be certain of your API version path here
url = "https://" + mvip_ip + "/json-rpc/9.0"

# Various payload params in one liner
# payload = "{\r    \"method\": \"CreateVolume\",\r    
#               \"params\": {\r        \"name\": \"<Volume Name>\",\r        
#               \"accountID\": <Account ID>,\r        \"totalSize\": <Volume Size in Bytes>,\r        
#               \"enable512e\": <Optional Boolean true or false>,\r        \"attributes\": {},\r        
#               \"qos\": {\r            \"minIOPS\": <Optional Minimum IOPS>,\r        
#               \"maxIOPS\": <Optional Maximum IOPS>,\r            \"burstIOPS\": <Optional Burst IOPS>,\r        
#               \"burstTime\": 60\r        }\r    },\r    \"id\": 1\r}"
# payload in JSON multi-line
payload = "{" + \
                "\n  \"method\": \"CreateVolume\"," + \
                "\n    \"params\": {" + \
                "\n    \t\"name\": \"" + str(vol_name) + "\"," + \
                "\n    \t\"accountID\": \"" + str(acct_id) + "\"," + \
                "\n    \t\"totalSize\": " + str(vol_size) + "," + \
                "\n    \t\"enable512e\": \"" + str(enable512e) + "\"," + \
                "\n    \t\"attributes\": {}," + \
                "\n    \t\"qos\": {" + \
                "\n    \t    \"minIOPS\": " + str(min_qos) + "," + \
                "\n    \t    \"maxIOPS\": " + str(max_qos) + "," + \
                "\n    \t    \"burstIOPS\": " + str(burst_qos) + "," + \
                "\n    \t    \"burstTime\": 60" + \
                "\n    \t}" +\
                "\n    }," + \
                "\n    \"id\": 1" + \
            "\n}"

response = requests.request("POST", url, data=payload, headers=headers, verify=False)

raw = json.loads(response.text)

print(json.dumps(raw, indent=4, sort_keys=True))