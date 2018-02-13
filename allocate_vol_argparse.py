# !/usr/bin/python
# author: Scott Chubb
# date: 20-Dec-2017
# PEP8 compliance reviewed 22-Jan-2018
# This script is a volume allocation script for automation of volume
# ----creation on SolidFire storage systems using EOS 10.0
# sys is needed to manage exit codes
# argparse is needed to accept arguments
# datetime is used to write the log file to a timecode indicator
# ElementFactory is used to connect SolidFire
# QoS is needed to set specific QoS on the volume

import sys
import argparse
import datetime
from solidfire.factory import ElementFactory
from solidfire.models import QoS

# Build time vars for file output
rawtime = datetime.datetime.now().isoformat()
mediumtime = rawtime.replace(':', '_')
cookedtime = mediumtime.replace('-', '_')

# Open output file
fh = open(cookedtime, "w")

# Set vars for connectivity using argparse
parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str,
                    required=True,
                    metavar='mvip',
                    help='MVIP name or IP')
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
                    metavar='volume',
                    help='volume name, no "_", 1 to 64 characters in length')
parser.add_argument('-a', type=int,
                    required=True,
                    metavar='chap account',
                    help='account to use for CHAP exchange')
parser.add_argument('-s', type=int,
                    required=True,
                    metavar='volume size',
                    help='volume size between 1,000,000,000'
                    'and 8,796,093,022,208')
parser.add_argument('-e', type=bool,
                    required=True,
                    metavar='512e',
                    help='True/False enable 512 block emulation')
parser.add_argument('-q', type=str,
                    choices=['custom', 'default'],
                    required=True,
                    metavar='QoS style',
                    help='custom/default use custom or default qos settings')
parser.add_argument('-n', type=int,
                    choices=range(50, 15001),
                    required=False,
                    metavar='min QoS',
                    help='min QoS between 50 and 15000')
parser.add_argument('-x', type=int,
                    choices=range(100, 200001),
                    required=False,
                    metavar='max QoS',
                    help='max QoS between 100 and 200000')
parser.add_argument('-b', type=int,
                    choices=range(100, 200001),
                    required=False,
                    metavar='burst QoS',
                    help='burst QoS between 100 and 200000')
args = parser.parse_args()

# Write the submitted info out to the file
fh.write(args)

# Take input and create new vars
sfMVIP = args.m
sfUser = args.u
sfPass = args.p
volName = args.v
acct_ID = args.a
vol_size = args.s
enable512e = args.e

# QoS, if requested
if args.q == "custom":
    minQoS = args.n
    maxQoS = args.x
    burstQoS = args.b
    qos = QoS(burst_iops=burstQoS,
              max_iops=maxQoS,
              min_iops=minQoS)

# Verify all variable inputs are valid and within boundaries
if len(volName) > 64:
    fh.write("Vol name exceeds character limit of 64. "
             "\n\tRequested length is %d" % len(volName))
    fh.close()
    sys.exit(1)

# Connect to SF cluster
sfe = ElementFactory.create(sfMVIP, sfUser, sfPass)

# Verify account exists
check_account = sfe.list_accounts(acct_ID)
if len(check_account.accounts) == 0:
    fh.write("Submitted account ID does not exist")
    fh.close()
    sys.exit(1)

# Check for duplicate volume name
vol_check = sfe.list_volumes()
for vol in vol_check.volumes:
    if vol.name == volName:
        fh.write("duplicate volume name detected, script will exit")
        fh.close()
        sys.exit(1)

# Actually do the work
if args.q == "custom":
    sfe.create_volume(volName,
                      acct_ID,
                      vol_size,
                      enable512e,
                      qos=qos)
elif args.q == "default":
    sfe.create_volume(volName,
                      acct_ID,
                      vol_size,
                      enable512e)
else:
    fh.write("Unhandled exception has occurred.")
    fh.close()
    sys.exit(1)
