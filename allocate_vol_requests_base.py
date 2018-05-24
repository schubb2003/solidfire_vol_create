#!/usr/local/bin/python
# Author: Scott Chubb scott.chubb@netapp.com
# Written for Python 3.4 and above
# No warranty is offered, use at your own risk.  While these scripts have been tested in lab situations, all use cases cannot be accounted for.
# Date: 13-Feb-2018
# This scripts shows how to gather volume information on volumeID 1 using requests and web calls
# output is in JSON formatted text.  This can be modified to be used in a more iterative fashion 
#   by switching from web calls to python CLI parsing
import requests
import base64
import json
from solidfire.factory import ElementFactory
# QoS is a dataobject model and must be imported to set QoS
# it is not required to get/print QoS information
from solidfire.models import QoS

def main():
    # Web/REST auth credentials build authentication
    auth = ("admin:Netapp1!")
    encodeKey = base64.b64encode(auth.encode('utf-8'))
    basicAuth = bytes.decode(encodeKey)

    headers = {
        'Content-Type': "application/json",
        'Authorization': "Basic %s" % basicAuth,
        'Cache-Control': "no-cache",
        }

    # Be certain of your API version path here
    url = "https://sf-mvip/json-rpc/9.0"

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
                    "\n    \t\"name\": \"new-volume\"," + \
                    "\n    \t\"accountID\": 1," + \
                    "\n    \t\"totalSize\": 1073741824," + \
                    "\n    \t\"enable512e\": false," + \
                    "\n    \t\"attributes\": {}," + \
                    "\n    \t\"qos\": {" + \
                    "\n    \t    \"minIOPS\": 150," + \
                    "\n    \t    \"maxIOPS\": 350," + \
                    "\n    \t    \"burstIOPS\": 550," + \
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
