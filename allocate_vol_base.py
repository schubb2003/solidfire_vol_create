#!/usr/local/bin/python
# This script assumes that an account named account1 exists
# It finds said account and creates a volume named account1-volume1
# It sets a size of 1GB not 1GiB with 512 block emulation disabled
#     and sets the QoS to a non-default value

from solidfire.factory import ElementFactory
from solidfire.models import QoS

# Create connection to SF Cluster
sfe = ElementFactory.create("sf-mvip", "admin", "Netapp1!")

# --------- EXAMPLE 1 - Existing ACCOUNT -----------
# Send the request with required parameters and gather the result
#	add_account_result = sfe.add_account(username="account1")
list_accounts_result = sfe.list_accounts()

# Pull the account ID from the result object
for account in list_accounts_result.accounts:
    if account.username == 'account1': 
        acc_id = account.account_id

# --------- EXAMPLE 2 - CREATE A VOLUME -------------
# Create a new QoS object for the volume
qos = QoS(burst_iops=5000, max_iops=1000, min_iops=500)

# Send the request with required parameters and gather the result
create_volume_result = sfe.create_volume(name="account1-volume1",
                                         account_id=acc_id,
                                         total_size=1000000000,
                                         enable512e=False,
                                         qos=qos)
