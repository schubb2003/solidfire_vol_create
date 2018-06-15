# !/usr/bin/python
# Author: Scott Chubb scott.chubb@netapp.com
# Written for Python 3.4 and above
# No warranty is offered, use at your own risk.  While these scripts have been tested in lab situations, all use cases cannot be accounted for.
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

def enforceVolNaming(vol_name):
    try:
        return re.match("^[a-zA-Z1-9][a-zA-Z1-9-]{1,63}[a-zA-Z1-9]$", vol_name).group(0)
    except:
        raise argparse.ArgumentTypeError("\nString {} does not match required format, ensure there are no special characters,"
                                         " that it is between 1 and 64 characters in length, and that no '-' exists at the start"
                                         " or end of the volume".format(vol_name,))

# Set vars for connectivity using argparse
parser = argparse.ArgumentParser()
parser.add_argument('-sm', type=str,
                    required=True,
                    metavar='mvip',
                    help='MVIP/node name or IP')
parser.add_argument('-su', type=str,
                    required=True,
                    metavar='username',
                    help='username to connect with')
parser.add_argument('-sp', type=str,
                    required=True,
                    metavar='password',
                    help='password for user')
parser.add_argument('-v', type=enforceVolNaming,
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
src_mvip = args.sm
src_user = args.su
src_pass = args.sp
vol_name = args.v
vol_acct = args.a
vol_size = args.s
vol_512e = args.e

# QoS, if requested
if args.q == "custom":
    minQoS = args.n
    maxQoS = args.x
    burstQoS = args.b
    qos = QoS(burst_iops=burstQoS,
              max_iops=maxQoS,
              min_iops=minQoS)

# Verify all variable inputs are valid and within boundaries
if len(vol_name) > 64:
    fh.write("Vol name exceeds character limit of 64. "
             "\n\tRequested length is %d" % len(vol_name))
    fh.close()
    sys.exit(1)

def main():
    # Connect to SF cluster
    sfe = ElementFactory.create(src_mvip, src_user, src_pass)

    # Verify account exists
    check_account = sfe.list_accounts(vol_acct)
    if len(check_account.accounts) == 0:
        fh.write("Submitted account ID does not exist")
        fh.close()
        sys.exit(1)

    # Check for duplicate volume name
    vol_check = sfe.list_volumes()
    for vol in vol_check.volumes:
        if vol.name == vol_name:
            fh.write("duplicate volume name detected, script will exit")
            fh.close()
            sys.exit(1)

    # Actually do the work
    if args.q == "custom":
        sfe.create_volume(vol_name,
                          vol_acct,
                          vol_size,
                          vol_512e,
                          qos=qos)
    elif args.q == "default":
        sfe.create_volume(vol_name,
                          vol_acct,
                          vol_size,
                          vol_512e)
    else:
        fh.write("Unhandled exception has occurred.")
        fh.close()
        sys.exit(1)

if __name__ == "__main__":
    main()
