import os

def analyze_sim_output(filepath):
    density = {
        2: 0.92,
        3: 1.09,
        4: 1.06,
        5: 1.12,
        6: 1.05,
        7: 1.06
    }
    vol_cm3 = {
        'sma': 247,
        'med': 640,
        'big': 1085
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
                    dose_temp += dose * vol3
                    mass_summ += mass
                    vol3_summ += vol3
                    if 'glandular' in cell[-1]:
                        vol3_glan = vol3
                        mass_glan = vol3
                        mgd = dose
                    elif 'adipose' in cell[-1]:
                        vol3_adip = vol3
                        mass_adip = vol3
            if flag_data and 'polystyrene__5-120keV.mcgpu.gz' in line:
                flag_data = False
                data[scan_type] = {
                    'histories': hist_num,
                    'volume_cm3': vol3_summ,
                    'dose_total': dose_summ,
                    'dose_avg': dose_temp / vol3_summ,
                    'dose_mgd': mgd
                }
    data['summ'] = {
        'aad': data['sing']['dose_avg'] + data['tomo']['dose_avg'],
        'mgd': data['sing']['dose_mgd'] + data['tomo']['dose_mgd']
    }
    return data
