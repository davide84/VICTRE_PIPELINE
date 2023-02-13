#!/bin/python

import os
from constants import *
from Victre import Pipeline
import argparse
from datetime import date


parser = argparse.ArgumentParser(description='Starts the simulation for one or more sizes on a given GPU.')
parser.add_argument('-s', '--size', required=False, action='append', choices=VALUES_SIZE, help='Breast size')
parser.add_argument('-f', '--fatness', required=False, action='append', type=float, choices=VALUES_FATNESS_PC, help='Fat content in percentage')
parser.add_argument('-g', '--gpu', required=False, action='store', type=int, choices=[0, 1], default=0, help='GPU index')
parser.add_argument('--speedup', action='store', type=int, default=1, help='Scaling factor (2 means 1/2 of histories')
parser.add_argument('--nosim', action='count', default=0, help='Only generate phantoms, no simulations')
parser.add_argument('-r', '--randomseed', required=False, type=int, default=1, help='First seed to be used in the repeated simulations')
parser.add_argument('-n', '--numsims', required=False, type=int, default=1, help='Numer of random repeated simulations')
parser.add_argument('-p', '--basepath', required=False, default='.', help='Absolute path where to crreate output folders')
args = parser.parse_args()

def hash_params(size, fatness, params):
    all_params = params.copy()
    all_params['size'] = size
    all_params['fatness'] = fatness
    return hashlib.sha1(json.dumps(all_params, sort_keys=True).encode('utf-8')).hexdigest()

def phantom_uid(size, fatness, params):
    return '{}_fat{}pc_{}cm'.format(size[:3], fatness, params['compressionThickness'])

for breast_size in args.size if args.size else VALUES_SIZE:
    thickness = params_phantom[breast_size]['thickness_mm']
    fatness_pc_list = args.fatness if args.fatness else VALUES_FATNESS_PC
    for fatness_pc in fatness_pc_list:
        params_gen = PHANTOM_DEFAULTS[fatness_pc]
        params_gen['imgRes'] = params_common['imgRes']
        params_gen['targetFatFrac'] = fatness_pc / 100.0
        params_gen['compressionThickness'] = thickness
        params_gen['surface_a1t'] = params_phantom[breast_size]['scaling_factor']
        params_gen['surface_a1b'] = params_gen['surface_a1t']
        params_gen['surface_a2l'] = params_gen['surface_a1t']
        params_gen['surface_a2r'] = params_gen['surface_a1t']
        params_gen['surface_a3'] = 1.48 * params_gen['surface_a1t']
        mas = params_simulation[breast_size]['mAs'][fatness_pc]
        params_sim = {'selected_gpu': args.gpu,
                      'number_histories': 4e9 * mas / 25.0 * 1.5 * (1/args.speedup), 'tally_voxel_dose': 'NO'}
        params_sim.update(params_simulation[breast_size]['mcgpu'])
        phuid = phantom_uid(breast_size, fatness_pc, params_gen)

        results_folder='{}/results/{}'.format(args.basepath, phuid)

        for seed in [args.randomseed + i for i in range(args.numsims)]:
            print('=== Size={}, seed={}, fatness={:.1f}%, mAs={}, thickness={}, speedup={}x\n    dest={}'.format(
                breast_size, seed, fatness_pc, mas, thickness, args.speedup, results_folder))
            print('    Phantom UID: {}'.format(phuid))

            # phantom generation if needed
            phantom_folder = '{}/phantoms/{}'.format(args.basepath, phuid)
            os.makedirs(phantom_folder, exist_ok=True)
            if not os.path.exists('{}/{}/pc_{}_crop.mhd'.format(phantom_folder, seed, seed)):
                pline = Pipeline(seed=seed, arguments_generation=params_gen, results_folder=phantom_folder)
                pline.generate_phantom()
                pline.compress_phantom(thickness=thickness)
                pline.crop()
            else:
                print('Found existing cropped phantom.')

            # exit if simulation not needed
            if args.nosim:
                continue

            # linking (cropped) phantom files into simulation folder
            print('Ensuring cropped phantom links into simulation folder...')
            simulation_folder = '{}/{}'.format(results_folder, seed)
            os.makedirs(simulation_folder, exist_ok=True)
            for ext in ['loc', 'mhd', 'raw.gz']:
                filepath = '{}/{}/pc_{}_crop.{}'.format(phantom_folder, seed, seed, ext)
                linkpath = '{}/pc_{}_crop.{}'.format(simulation_folder, seed, ext)
                if not os.path.exists(linkpath):
                    os.symlink(filepath, linkpath)
                    print('Symlinked {} to {}', filepath, linkpath)

            # simulation
            pline = Pipeline(seed=seed, arguments_generation=params_gen,
                             arguments_mcgpu=params_sim, results_folder=results_folder)
            pline.project()
            # pline.reconstruct()
            # pline.save_DICOM("dbt")
            # pline.save_DICOM("dm")

        # analyze results
        # TODO




