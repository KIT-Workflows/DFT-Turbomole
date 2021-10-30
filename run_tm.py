import os,sys,yaml

import turbomole_functions as tm
import ase.io

#######################################################################
###                                                                 ###
### prerequisite files: rendered_wano.yml, initial_structure.xyz (coord_0) ###
###                                                                 ###
#######################################################################

def get_settings_from_rendered_wano(filename='rendered_wano.yml'):

    disp_dict={'None':'off','D2':'old','D3':'on','D3-BJ':'bj','D4':'d4'}

    settings=dict()
    with open(filename) as infile:
        wano_file = yaml.full_load(infile)
    
    settings['title']=wano_file['Title']
    settings['follow-up']=wano_file['Follow-up calculation']
    settings['int coord']=wano_file['Molecular structure']['Internal coordinates']
    settings['basis set']=wano_file['Basis set']['Basis set type']
    settings['use old mos']=wano_file['Initial guess']['Use old orbitals']
    settings['use old coord']=wano_file['Molecular structure']['Use old structure']
    settings['charge']=wano_file['Initial guess']['Charge']
    settings['multiplicity']=wano_file['Initial guess']['Multiplicity']
    settings['scf iter']=60
    settings['max scf iter']=wano_file['DFT options']['Max SCF iterations']
    settings['use ri']=wano_file['DFT options']['Use RI']
    settings['ricore']=wano_file['DFT options']['Memory for RI']
    settings['functional']=wano_file['DFT options']['Functional']
    settings['grid size']=wano_file['DFT options']['Integration grid']
    settings['disp']=disp_dict[wano_file['DFT options']['vdW correction']]
    settings['cosmo']=wano_file['DFT options']['COSMO calculation']
    settings['epsilon']=wano_file['DFT options']['Rel. permittivity']
    settings['opt']=wano_file['Type of calculation']['Structure optimisation']
    settings['opt cyc']=50
    settings['max opt cyc']=wano_file['Type of calculation']['Max optimization cycles']
    settings['freq']=wano_file['Type of calculation']['Frequency calculation']
    settings['tddft']=wano_file['Type of calculation']['Excited states calculation']
    settings['exc state type']=wano_file['Type of calculation']['TDDFT options']['Type of excited states']
    settings['num exc states']=wano_file['Type of calculation']['TDDFT options']['Number of excited states']
    settings['opt exc state']=wano_file['Type of calculation']['TDDFT options']['Optimised state']

    return settings

def sanitize_multiplicity(multi,n_el):

    multi_new=multi
    multi_min=n_el%2+1

    if multi < 1:
        print('Attention: a multiplicity of %i is not possible.'%(multi))

    elif n_el%2 and multi%2: 
        print('Attention: a multiplicity of %i is not possible for an odd number of electrons.'%(multi))
        multi_new-=1
    elif not n_el%2 and not multi%2: 
        print('Attention: a multiplicity of %i is not possible for an even number of electrons.'%(multi))
        multi_new-=1

    if multi_new < multi_min: multi_new=multi_min
    if multi != multi_new:
        print('The multiplicity was set to %i by default'%(multi_new))
        with open('rendered_wano.yml') as infile:
            wano_file=yaml.full_load(infile)
        wano_file['Initial guess']['Multiplicity']=int(multi_new)
        with open('rendered_wano.yml','w') as outfile: yaml.dump(wano_file,outfile)
    
    return multi_new

if __name__ == '__main__':
    
    coord_file='coord_0'
    settings=get_settings_from_rendered_wano()

    if settings['follow-up']: 
        os.system('mkdir old_results; tar -xf old_calc.tar.xz -C old_results')
        old_settings = get_settings_from_rendered_wano(filename='old_results/rendered_wano.yml')
        settings['title']=old_settings['title']
        if settings['use old mos']: settings['multiplicity']=old_settings['multiplicity']

    if settings['use old coord']: os.system('cp old_results/coord %s'%(coord_file))
    else: os.system('x2t initial_structure.xyz > %s'%(coord_file))

    if not settings['use old mos']:
        n_el=sum(ase.io.read(coord_file).numbers)-settings['charge']
        settings['multiplicity']=sanitize_multiplicity(settings['multiplicity'],n_el)

    tm.inputprep('define',tm.make_define_str(settings,coord_file))
    if settings['follow-up']: os.system('rm -rf old_results')

    if settings['cosmo']:
        if settings['follow-up']:
            if old_settings['cosmo']:
                tm.inputprep('cosmoprep','u\n%f\n\n\n\n\n\n\n\n\n\n\n*\n\n\n'%(settings['epsilon']))
            else: tm.inputprep('cosmoprep','%f\n\n\n\n\n\n\n\n\n\n\nr all b\n*\n\n\n'%(settings['epsilon']))
        else: tm.inputprep('cosmoprep','%f\n\n\n\n\n\n\n\n\n\n\nr all b\n*\n\n\n'%(settings['epsilon']))

    elif settings['follow-up'] and old_settings['cosmo']:
       for datagroup in ['cosmo','cosmo_atoms','cosmo_out']: os.system('kdg %s'%(datagroup))

    if settings['tddft'] and settings['opt']:
        if not settings['cosmo']: os.system('adg exopt %i'%(settings['opt exc state']))
        else:
            print('Excited state optimisations with COSMO not yet implemented in Turbomole\'s egrad - A single-point calculation is performed instead')
            settings['opt']=False

    tm.single_point_calc(settings)
    if settings['opt']: tm.jobex(settings)

    if settings['freq']:
        if settings['tddft']: 
            print('Frequency calculations for excited states not yet implemented')
            exit(0)
        else: tm.aoforce()

    results_dict={}
    results_dict['title']=settings['title']
    results_dict['energy_unit']='Hartree'

    with open('energy') as infile: results_dict['energy'] = float(infile.readlines()[-2].split()[1])
    with open('eiger.out') as infile: results_dict['homo-lumo gap'] = float(infile.readlines()[14].split()[2])

    if settings['tddft']:
        results_dict['exc_type']=settings['exc state type']
        exc_energies=[]
        with open('exspectrum') as infile:
            exc_lines=infile.readlines()[-settings['num exc states']:]
        for exc_line in exc_lines: exc_energies.append(float(exc_line.split()[2]))
        results_dict['exc_energies']=exc_energies
    elif settings['freq']:
        vib_freq=[]
        with open('aoforce.out') as infile:
            ao_lines=infile.readlines()
        for ao_line in ao_lines:
            if 'frequency  ' in ao_line:
                for freq in ao_line.split()[1:]:
                    if 'i' in freq: vib_freq.append(-float(freq.replace('i','')))
                    else: vib_freq.append(float(freq))
            if 'zero point' in ao_line: results_dict['ZPE']=float(ao_line.split()[6])
        results_dict['vibrational frequencies']=vib_freq

    with open('results.yml','w') as outfile: yaml.dump(results_dict,outfile)

    output_files=['alpha','auxbasis','basis','beta','control','coord','energy','forceapprox','gradient','hessapprox','mos','optinfo','rendered_wano.yml','sing_a','trip_a','unrs_a'] # implement symmetry: irrep names in [sing,trip,unrs]_irrep
    for filename in output_files:
        if not os.path.isfile(filename): output_files.remove(filename)

    os.system('tar -cf results.tar.xz %s'%(' '.join(output_files)))
