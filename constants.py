#!/bin/python

from Victre import Constants


VALUES_SIZE = ['small', 'medium', 'large']
VALUES_FATNESS_PC = [12.5, 37.5, 62.5, 87.5]
PHANTOM_DEFAULTS = {
    12.5: Constants.VICTRE_DENSE,
    37.5: Constants.VICTRE_DENSE,  # Constants.VICTRE_HETERO,
    62.5: Constants.VICTRE_HETERO,  # Constants.VICTRE_SCATTERED,
    87.5: Constants.VICTRE_SCATTERED  # Constants.VICTRE_FATTY
}

params_common = {
    'imgRes': 0.2,
}

params_phantom = {
    'small': {
        'thickness_mm': 53,
        'scaling_factor': 1.12
    },
    'medium': {
        'thickness_mm': 57,
        'scaling_factor': 1.51
    },
    'large': {
        'thickness_mm': 61,
        'scaling_factor': 1.78
    }
}

# 'mcgpu' is not yet fully understood and used. Davide 09.02.2023
params_simulation = {
    'small': {
        'mAs': {
            12.5: 222,
            37.5: 152,
            62.5: 122,
            87.5: 76
        },
        'mcgpu': {
            'roi_voxel_dose_x': [220, 220],
            'roi_voxel_dose_y': [250, 250],
            'roi_voxel_dose_z': [290, 290]
        }
    },
    'medium': {
        'mAs': {
            12.5: 263,
            37.5: 212,
            62.5: 142,
            87.5: 79
        },
        'mcgpu': {
            'roi_voxel_dose_x': [320, 320],
            'roi_voxel_dose_y': [382, 382],
            'roi_voxel_dose_z': [482, 482]
        }
    },
    'large': {
        'mAs': {
            12.5: 300,
            37.5: 206,
            62.5: 166,
            87.5: 105
        },
        'mcgpu': {
            'roi_voxel_dose_x': [150, 150],
            'roi_voxel_dose_y': [150, 150],
            'roi_voxel_dose_z': [150, 150]
        }
    }
}

