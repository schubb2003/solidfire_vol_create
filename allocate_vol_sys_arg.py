#!/usr/local/bin/python
# Author: Scott Chubb scott.chubb@netapp.com
# Written for Python 3.4 and above
# No warranty is offered, use at your own risk.  While these scripts have been tested in lab situations, all use cases cannot be accounted for.
# It takes arguments from the command line to configure inputs
# usage: python allocate_vol_argument.py <MVIP> <USER> <PASSWORD> <ACCOUNT> <vol_name> <VOL_SIZE> <512enabled false|true> <MIN_QOS> <MAX_QOS> <BURST_QOS>
# This script looks for the provided account and creates a volume named <vol_name>
# It sets a size requested with 512 block emulation set based off the input
#     and then sets the QoS to a non-default value
# example python allocate_vol_argument.py sf-mvip admin Netapp1! account1 myvol1 1048576000 false 250 750 1000 

import sys
from solidfire.factory import ElementFactory
from solidfire.models import QoS

#Verify inputs using sys
if len(sys.argv) < 11:
    sys.exit("Insufficient arguments entered")
else:
    src_mvip = sys.argv[1]
    src_user = sys.argv[2]
    src_pass = sys.argv[3]
    vol_acct = sys.argv[4]
    vol_name = sys.argv[5]
    vol_size = sys.argv[6]
    vol_512e = sys.argv[7]
    min_qos = int(sys.argv[8])
    max_qos = int(sys.argv[9])
    burst_qos = int(sys.argv[10])

def main():
    # Create connection to SF Cluster
    sfe = ElementFactory.create(src_mvip, src_user, src_pass,print_ascii_art=False)

    # --------- EXAMPLE 1 - Existing ACCOUNT -----------
    # Send the request with required parameters and gather the result
    #	add_account_result = sfe.add_account(username="account1")
    list_accounts_result = sfe.list_accounts()

    # Pull the account ID from the result object
    for account in list_accounts_result.accounts:
        if account.username == vol_acct: 
            acc_id = account.account_id

    # --------- EXAMPLE 2 - CREATE A VOLUME -------------
    # Create a new QoS object for the volume
    qos = QoS(burst_iops=burst_qos, max_iops=max_qos, min_iops=min_qos)

    # Send the request with required parameters and gather the result
    create_volume_result = sfe.create_volume(name=vol_name,
                                             account_id=acc_id,
                                             total_size=vol_size,
                                             enable512e=enable_512e,
                                             qos=qos)

if __name__ == "__main__"
    main()
