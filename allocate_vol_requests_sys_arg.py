#!/usr/local/bin/python
# Author: Scott Chubb scott.chubb@netapp.com
# Written for Python 3.4 and above
# No warranty is offered, use at your own risk.  While these scripts have been tested in lab situations, all use cases cannot be accounted for.
# Date: 13-Feb-2018
# This scripts shows how to gather volume information on volumeID 1 using requests and web calls
# output is in JSON formatted text.  This can be modified to be used in a more iterative fashion 
#   by switching from web calls to python CLI parsing
import sys
import requests
import base64
import json
from solidfire.factory import ElementFactory
# QoS is a dataobject model and must be imported to set QoS
# it is not required to get/print QoS information
from solidfire.models import QoS

if len(sys.argv) < 11:
    print("Insufficient arguments entered:\n"
          "Usage: python <script> <cluster> <username> <password>"
          "<volume_name> <account_id> <volume_size> <enable512emulation true|false>"
          "<min_QoS> <max_QoS> <burst_QoS>")

mvip_ip = sys.argv[1]
user_name = sys.argv[2]
user_pass = sys.argv[3]
vol_name = sys.argv[4]
acct_id = sys.argv[5]
vol_size = sys.argv[6]
enable512e = (sys.argv[7]).lower()
min_qos = sys.argv[8]
max_qos = sys.argv[9]
burst_qos = sys.argv[10]

def main():
    try:
        vol_size = int(vol_size)
    except:
        sys.exit("Volume size is not a number")
    if vol_size < 1000000000 or vol_size > 8796093022208:
        sys.exit("volume size is either less than 1GB or more than 8TiB")

    if enable512e != "true" and enable512e != "false":
        sys.exit("512 emulation must be either true or false")

    try:
        max_qos = int(max_qos)
    except:
        sys.exit("Script exited due to incorrect max QoS information")
    if max_qos > 15000 or max_qos < 100 or max_qos < min_qos:
        sys.exit("Maximum QoS is out of bounds, max QoS is valid between 100 and 15000, or less than minimum QoS submitted was %s" % max_qos)

    try:
        min_qos = int(min_qos)
    except:
        sys.exit("Script exited due to incorrect min QoS information")
    if min_qos < 50 or min_qos > 15000:
        sys.exit("Minimum QoS is out of bounds, min QoS must be between 50 and 15000 submitted was %s" % min_qos)

    try:
        burst_qos = int(burst_qos)
    except:
        sys.exit("Script exited due to incorrect burst QoS information")
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

if __name__ == "__main__"
    main()
