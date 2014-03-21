#!/usr/bin/env python

import sys, argparse

import logging
logging.basicConfig(level=logging.DEBUG)

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

from drive_test_analysis import trace_loader as tl
from drive_test_analysis import nemo_trace_processor as ntp
from drive_test_analysis import data_plotter as dpl

def setup_args():
    parser = argparse.ArgumentParser(description='Plot drive test data.')
    parser.add_argument('-l','--list', action='store_true', help='List all data-set.')
    parser.add_argument('-s','--static', action='store_true', help='Keep samples with zero velocity.')
    parser.add_argument('-d','--select', type=int,
                        help='Select a particular data-set to display')
    parser.add_argument('library',type=str,
                        help='Select a particular library to pull data from')
    parser.add_argument('-u','--ue',type=str, default='e398',
                        help='What UE was used [e398|e3276]. Default is e398 ')
    parser.add_argument('--print', type=str, help='Print figure to file.')  # nargs='+'
    args   = parser.parse_args()
    return args


def main(args):
    data_file_list = tl.get_data_file_list(args.library)
    if args.list:
        tl.print_list(data_file_list)
        sys.exit(0)
    data = tl.load_data_file(data_file_list,args.select)

    if not args.static:
        logging.debug('Remove non-zero velocity samples')
        data = ntp.remove_non_positive_velocity_samples(data)

    if args.ue == 'e398':
        # Rename MAC downlink throughput in Application downlink throughput if need be
        ntp.process_data(data,ntp.process_lte_rename_mac_to_app)

    # Get basic data
    ntp.process_data(data,ntp.process_lte_app_bw_prb_util)
    ntp.process_data(data,ntp.process_lte_app_bw_prb_util_bw20)
    ntp.process_data(data,ntp.process_lte_app_bw_prb_util_bw10)
    ntp.process_data(data,ntp.process_lte_app_bw_prb_util_bw15)

    column_list = ['Application throughput downlink',
                   'Application throughput downlink 10',
                   'Application throughput downlink 15',
                   'Application throughput downlink 20']
    if args.select is None:
        df = tl.concat_pandas_data([df[column_list] for df in data ])
    else:
        df = data

    print(df['Application throughput downlink'].describe())
    print(df['Application throughput downlink 10'].describe())
    print(df['Application throughput downlink 15'].describe())
    print(df['Application throughput downlink 20'].describe())

    # Normalize
    f_norm = lambda x: x/1e6

    plt.ion()
    plt.figure()
    plt.subplot2grid((2,3), (0,0),colspan=3)
    x = np.arange(0,120,1)
    dpl.plot_ecdf_triplet(df['Application throughput downlink 10'].dropna().apply(f_norm),
                          df['Application throughput downlink'].dropna().apply(f_norm),
                          df['Application throughput downlink 15'].dropna().apply(f_norm),x,
                          'Application th. (10 MHz)',
                          'Application th.',
                          'Application th. (15 MHz)',
                          'Mbit/s')
    plt.legend(loc=0,prop={'size':10})
    plt.subplot2grid((2,3), (1,0),colspan=1)
    dpl.plot_density(df['Application throughput downlink'].dropna().apply(f_norm),x,
                     'App. th.','Mbit/s')
    plt.subplot2grid((2,3), (1,1),colspan=1)
    dpl.plot_density(df['Application throughput downlink 10'].dropna().apply(f_norm),x,
                     'App. th. 10 MHz','Mbit/s')
    plt.subplot2grid((2,3), (1,2),colspan=1)
    dpl.plot_density(df['Application throughput downlink 15'].dropna().apply(f_norm),x,
                     'App. th. 15 MHz','Mbit/s')

    if args.print:
        plt.savefig(args.print,dpi=300,bbox_inches='tight')

    input('Press any key')
    

if __name__ == "__main__":
    args = setup_args()
    main(args)
