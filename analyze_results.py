#!/bin/python

import argparse
from pathlib import Path
from helpers import analyze_sim_output


parser = argparse.ArgumentParser(description='Starts the analysis of a give folder')
parser.add_argument('-p', '--datapath', required=True, help='Absolute path of the simulation output')
parser.add_argument('--speedup', action='store', type=int, default=0, help='Scaling factor. Not used = autodetect from folder name')
args = parser.parse_args()


def params_from_dirname(dirname):
    return dirname[0:3], float(dirname[7:11]), int(dirname[14:16])


def main():
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
        for path_seed in path_params.glob('*'):
            if not path_params.is_dir():
                continue
            seed = int(path_seed.name)
            values = analyze_sim_output(path_seed / 'output_projection.out')
            print('{} {} {} {} {:.4f} {:.4f}'.format(size, fatness_pc, thickness_cm, seed,
                  values['summ']['aad'] * speedup, values['summ']['mgd'] * speedup))

            # TODO DEBUG for now we stop at first folder
#            exit(0)




if __name__ == '__main__':
    main()

