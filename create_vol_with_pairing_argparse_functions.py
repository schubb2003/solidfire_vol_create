#!/bin/bash/python
# create a series of volumes and pair them

from solidfire.factory import ElementFactory
import time
import sys
import argparse
import re

def connect_src():
    print("-----Source connect called-----")
    argv = parse_inputs()
    src_mvip = argv.sm
    src_user = argv.su
    src_pass = argv.sp

    global sfe_src
    sfe_src = ElementFactory.create(src_mvip,
                                    src_user,
                                    src_pass,
                                    print_ascii_art=False)

def connect_dst():
    print("-----Destination connect called-----")
    argv = parse_inputs()
    dst_mvip = argv.dm
    dst_user = argv.du
    dst_pass = argv.dp

    global sfe_dst    
    sfe_dst = ElementFactory.create(dst_mvip,
                                    dst_user,
                                    dst_pass,
                                    print_ascii_art=False)


def create_src_vol(new_vol, vol_acct, vol_size, vol_512e):
    """
    This function creates the source volumes from the arguments supplied
    outputs src_vol_id for use in pairing functions
    """
    print("-----Create source vol called-----")
    src_vol = sfe_src.create_volume(new_vol,
                                    account_id=vol_acct,
                                    total_size=vol_size,
                                    enable512e=vol_512e)

    global src_vol_id
    src_vol_id = src_vol.volume_id
    


def create_dst_vol(new_vol, vol_acct, vol_size, vol_512e):
    """
    This function creates the destination volumes from the arguments supplied
    outputs dst_vol_id for use in pairing functions
    """
    print("-----Create destination vol called-----")
    dst_vol = sfe_dst.create_volume(new_vol,
                                    account_id=vol_acct,
                                    total_size=vol_size,
                                    enable512e=vol_512e)
    global dst_vol_id
    dst_vol_id = dst_vol.volume_id

def modify_dest_vol(dst_vol_id):
    """
    This function sets the destination volumes to replicationTarget for
        replication.  It cannot be set until the pairing is configured.
     """
    print("-----Modify destination vol called-----")
    sfe_dst.modify_volume(dst_vol_id,
                          access="replicationTarget")


def start_pair_vols(src_vol_id, vol_repl):
    """
    This function starts the pairing process
    It configures the source and sets the pairing key to the
        variable pair_key for use in the complete_pair_vols function
    """
    print("-----Create pair vol called-----")
    key = sfe_src.start_volume_pairing(src_vol_id,
                                       mode=vol_repl)
    global pair_key
    pair_key = key.volume_pairing_key
    
def complete_pair_vols(pair_key, dst_vol_id):
    """
    This function completes the pairing process
    """
    print("-----Complete pair vol called-----")
    sfe_dst.complete_volume_pairing(pair_key,
                                    dst_vol_id)


def remove_vol_pair(src_vol_id):
    """
    This function is only used in the exception statements
    When a DBVersion mismatch is detected attempting to re-pair will not work
    Therefore we have to remove the pair on the source and attempt again.
    """
    print("-----remove pair vol called-----")
    sfe_src.remove_volume_pair(src_vol_id)


def check_repl_status():
    """
    This function is a debug fucntion that is being used to test timings.  It
        is designed to watch for new volumes that start as PausedMisconfigured
        for longer than two minutes on replication initialization.
        Two minutes is the target as there is a source/target sync
        state that can take up to 60 seconds per side to stabilize and
        for transfer operations to start.
    """
    print("-----Check repl status called-----")
    vols = sfe_src.list_active_paired_volumes()
    status = []
    t = 0
    bad_state = "PausedMisconfigured"
    for vol in vols.volumes:
        for v in vol.volume_pairs:
            if bad_state in v.remote_replication.state:
                status.append(v.remote_replication.state)
                while bad_state in status:
                    status.clear()
                    vols = sfe_src.list_active_paired_volumes()
                    for vol in vols.volumes:
                        for v in vol.volume_pairs:
                            if bad_state in v.remote_replication.state:
                                if bad_state not in status:
                                    status.append(v.remote_replication.state)
                                t = t + 1
                                time.sleep(1)
                                print(status)
                min = t // 60
                sec = t % 60
                print("{} minutes and {} seconds elapsed, "
                      "\n\ttotal seconds were {}".format(min, sec, t))

def enforceVolNaming(vol_name):
    try:
        return re.match("^[a-zA-Z1-9][a-zA-Z1-9-]{1,62}$", vol_name).group(0)
    except:
        raise argparse.ArgumentTypeError("\nVolume {} does not match required"
                                         " name format, ensure there are "
                                         "no special characters,"
                                         " that it is between 1 and 64 "
                                         "characters in length, and that no "
                                         "'-' exists at the start"
                                         " of the volume".format(vol_name,))

def parse_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-sm', type=str,
                        required=True,
                        metavar='smvip',
                        help='Source MVIP name or IP')
    parser.add_argument('-su', type=str,
                        required=True,
                        metavar='susername',
                        help='Source username to connect with')
    parser.add_argument('-sp', type=str,
                        required=True,
                        metavar='spassword',
                        help='Source password for user')
    parser.add_argument('-dm', type=str,
                        required=True,
                        metavar='dmvip',
                        help='Destination MVIP name or IP')
    parser.add_argument('-du', type=str,
                        required=True,
                        metavar='dusername',
                        help='Desitnation username to connect with')
    parser.add_argument('-dp', type=str,
                        required=True,
                        metavar='dpassword',
                        help='Destinationpassword for user')
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
    parser.add_argument('-r', type=str,
                        required=True,
                        metavar='repl',
                        choices=['sync', 'async', 'snap'],
                        help='Replication type - sync/async/snap')
    parser.add_argument('-c', type=int,
                        required=True,
                        metavar='vol count',
                        help='number of volumes to create')
    args = parser.parse_args()
    return args

def main():
    """
    This function does the work, creates both sides, pairs the vols and
        adjusts pairing in the even of a DBVersionMismatch error
    """
    argv = parse_inputs()
    rep_mode = argv.r
    vol_count = argv.c
    vol_512e = argv.e
    vol_size = argv.s
    vol_acct = argv.a
    vol_name = argv.v
    
    sfe_src = connect_src()
    sfe_dst = connect_dst()
    
    # set replication mode based off of inputs
    if rep_mode == "sync":
        vol_repl = "Sync"
    elif rep_mode == "async":
        vol_repl = "Async"
    elif rep_mode == "snap":
        vol_repl = "SnapshotsOnly"
    else:
        sys.exit("Argparse should prevent this from ever being seen"
                 "script will exit with unexpected replication mode submitted")

    try:
        i = 1
        while i < vol_count + 1:
            new_vol = vol_name + str(i)

            create_src_vol(new_vol, vol_acct, vol_size, vol_512e)
            create_dst_vol(new_vol, vol_acct, vol_size, vol_512e)
            modify_dest_vol(dst_vol_id)

            try:
                start_pair_vols(src_vol_id, vol_repl)
                print("Volume pairing key is: {}".format(pair_key))

            # Catches exceptions on start pairing process
            except Exception as e:
                if "xDBVersionMismatch" in str(e):
                    while "xDBVersionMismatch" in str(e):
                        e = ""
                        print("##########\n"
                              "DBVersionMismatch encountered, "
                              "retrying pair start"
                              "\n##########")
                        start_pair_vols(src_vol_id, vol_repl)

                else:
                    print(e)
                    sys.exit("Unhandled exception, script will exit")

            try:
                complete_pair_vols(pair_key, dst_vol_id)

            # Catches exceptions in the complete pairing process
            # We must remove pairing, start pairing and complete pairing
            #   when this error occurs here as the key cannot be re-used
            except Exception as e:
                if "xDBVersionMismatch" in str(e):
                    while "xDBVersionMismatch" in str(e):
                        e = ""
                        print("##########\n"
                              "DBVersionMismatch encountered, "
                              "retrying pair completion"
                              "\n##########")
                        remove_vol_pair(src_vol_id)
                        start_pair_vols(src_vol_id, vol_repl)
                        complete_pair_vols(pair_key, dst_vol_id)

                else:
                    print(e)
                    sys.exit("Unhandled exception, script will exit")
            i = i + 1

    except Exception as e:
        print(e)

    finally:
        time.sleep(120)
        check_repl_status()
        print("Script complete")

if __name__ == "__main__":
    main()
