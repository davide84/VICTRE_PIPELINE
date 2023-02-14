#!/bin/python
import os

def extract_dose_from_file(filepath, fatness, volume):
    if not os.path.exists(filepath):
        return
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
        scan_type = None
        file_data = None
        file_summ = None
        for line in f:
            if 'Simulating a 0 degree projection' in line:
                scan_type = 'sing'
            elif 'Simulating tomographic' in line:
                scan_type = 'tomo'
            if 'Total number of simulated x rays' in line:
                hist_num = int(line.split(' ')[-1])
            if '[MAT]' in line:
                file_data = open('data_output.csv', 'a')
                file_summ = open('data_summary.csv', 'a')
                dose_summ = 0.0
                dose_temp = 0.0
                mass_summ = 0.0
                vol3_summ = 0.0
                continue
            if file_data is not None and '================' not in line:
                line = line[:-1].replace(',', '').replace('  ', ',').replace('\t\t', '\t').replace('\t', ',')[1:]
                if 'MAT' not in line:
                    line = '{},{},{},{}'.format(volume, float(fatness[3:]) / 10.0, scan_type, line)
                elif scan_type == 'tomo':
                    continue
                if 'air' not in line and 'polystyrene' not in line:
                    file_data.write(line.split('_')[0] + '\n')
                    cell = line.split(',')
                    dose = float(cell[-3])
                    mass = float(cell[-2])
                    vol3 = mass / density[int(cell[3])]
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
            if file_data is not None and 'polystyrene__5-120keV.mcgpu.gz' in line:
                file_data.close()
                file_data = None
                file_summ.write('{},{},{},{},{},{},{}\n'.format(volume, float(fatness[3:]) / 10.0,
                                scan_type, hist_num, dose_summ, dose_temp / vol3_summ, mgd))
                file_summ.close()
                file_summ = None
                print('{},{},{},{:.1f},{:.1f},{:.3f},{:.1f},{:.1f},{:.1f},{:.1f}'.format(
                    volume, fatness, scan_type, mass_summ, vol3_summ, mass_summ / vol3_summ,
                    (100 * mass_adip / mass_summ), (100 * vol3_adip / vol3_summ),
                    (100 * mass_glan / mass_summ), (100 * vol3_glan / vol3_summ)))


def main():
    file_dest = open('data_output.csv', 'w')
    file_dest.write('Size,Fatness,Scan,MAT,DOSE eV/g/hist,2*std_dev,Rel_error 2*std_dev %,E_dep eV/hist,DOSE mGy,Material mass g,Material\n')
    file_dest.close()
    file_dest = open('data_summary.csv', 'w')
    file_dest.write('Size,Fatness,Scan,Histories,Total Dose,Avg.Abs.Dose,MGD\n')
    file_dest.close()
    for fatness in ['fat125', 'fat375', 'fat625', 'fat875']:
        for seed in [8, 12, 15]:
            volume = 'sma' if seed == 8 else ('med' if seed == 12 else 'big')
            extract_dose_from_file('{}/{}/output_projection.out'.format(fatness, seed), fatness, volume)


if __name__ == '__main__':
    main()
