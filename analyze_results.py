#!/bin/python

import argparse
import numpy as np
import pandas as pd
from pathlib import Path


parser = argparse.ArgumentParser(description='Starts the analysis of a give folder')
parser.add_argument('-p', '--datapath', required=True, help='Absolute path of the simulation output')
parser.add_argument('--speedup', action='store', type=int, default=0, help='Scaling factor. Not used = autodetect from folder name')
args = parser.parse_args()


def params_from_dirname(dirname):
    return dirname[0:3], float(dirname[7:11]), int(dirname[14:16])


def analyze_sim_output(filepath):
    density = {
        2: 0.92,
        3: 1.09,
        4: 1.06,
        5: 1.12,
        6: 1.05,
        7: 1.06
    }
    with open(filepath, 'r') as f:
        data = {}
        scan_type = None
        flag_data = False
        for line in f:
            if 'Simulating a 0 degree projection' in line:
                scan_type = 'sing'
            elif 'Simulating tomographic' in line:
                scan_type = 'tomo'
            if 'Total number of simulated x rays' in line:
                hist_num = int(line.split(' ')[-1])
            if '[MAT]' in line:
                flag_data = True
                dose_summ = 0.0
                dose_temp = 0.0
                mass_summ = 0.0
                vol3_summ = 0.0
                continue
            if flag_data and '================' not in line:
                line = line[:-1].replace(',', '').replace('  ', ',').replace('\t\t', '\t').replace('\t', ',')[1:]
                if 'MAT' in line and scan_type == 'tomo':
                    continue
                if 'air' not in line and 'polystyrene' not in line:
                    cell = line.split(',')
                    dose = float(cell[-3])
                    mass = float(cell[-2])
                    vol3 = mass / density[int(cell[0])]
                    dose_summ += dose
                    dose_temp += dose * mass
                    mass_summ += mass
                    vol3_summ += vol3
                    if 'glandular' in cell[-1]:
                        vol3_glan = vol3
                        mass_glan = mass
                        mgd = dose
                    elif 'adipose' in cell[-1]:
                        vol3_adip = vol3
                        mass_adip = mass
            if flag_data and 'polystyrene__5-120keV.mcgpu.gz' in line:
                flag_data = False
                data[scan_type] = {
                    'histories': hist_num,
                    'vol_cm3': vol3_summ,
                    'dose_total': dose_summ,
                    'dose_avg': dose_temp / mass_summ,
                    'dose_mgd': mgd,
                    'glandularity': vol3_glan / vol3_summ * 100,
                    'fatness': vol3_adip / vol3_summ * 100
                }
    data['summ'] = {
        'aad': data['sing']['dose_avg'] + data['tomo']['dose_avg'],
        'mgd': data['sing']['dose_mgd'] + data['tomo']['dose_mgd']
    }
    return data


def main():
    # preparing the dataframe
    columns=['Size', 'Volume', 'Thickness', 'Fatness', 'ActualFat', 'ActualGland', 'Histories', 'AAD', 'AAD_std', 'MGD', 'MGD_std']
    df = pd.DataFrame()

    # get the speed scaling factor
    speedup = args.speedup if args.speedup > 0 else int(args.datapath.split('-')[-1][:-2])

    # open results folder and loop over subfolders
    # expected format: results-{speedup}x/{size}_fat{fatness}pc_{thickness}cm/{seed}
    path_results = Path(args.datapath)
    if not path_results.is_dir():
        print(path_results, 'is not a valid folder')
        exit(1)
    for path_params in path_results.glob('*'):
        if not path_params.is_dir():
            continue
        size, fatness_pc, thickness_cm = params_from_dirname(path_params.name)
        aad = []
        mgd = []
        gpc = 0.0
        fat = 0.0
        his = 0
        for path_seed in path_params.glob('*'):
            if not path_params.is_dir():
                continue
            seed = int(path_seed.name)
            values = analyze_sim_output(path_seed / 'output_projection.out')
            aad.append(values['summ']['aad'] * speedup)
            mgd.append(values['summ']['mgd'] * speedup)
            gpc = values['sing']['glandularity']
            fpc = values['sing']['fatness']
            cm3 = values['sing']['vol_cm3']
            his = (values['sing']['histories'] + values['tomo']['histories']) * speedup
        # averaging values for different seeds
        aad_avg = np.mean(aad)
        aad_std = np.std(aad)
        mgd_avg = np.mean(mgd)
        mgd_std = np.std(mgd)

        df2 = pd.DataFrame([[size, cm3, thickness_cm, fatness_pc, fpc, gpc, his, aad_avg, aad_std, mgd_avg, mgd_std]], columns=columns)
        df = df.append(df2)

    df.sort_values(by=['Fatness','Size'], ascending=[True,False], inplace=True)
    print(df.to_csv(index=False))





if __name__ == '__main__':
    main()

