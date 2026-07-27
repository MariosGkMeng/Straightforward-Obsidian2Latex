import numpy as np
import sys
import os
from get_parameters import *
from path_searching import *

PARS = get_parameters()


list_notes = '''
[[sim 404 parameters]]
[[SIMULATION_LOG]]
[[SIMULATION_LOG__sim_373]]
[[SIMULATION_LOG__sim_374]]
[[SIMULATION_LOG__sim_375]]
[[SIMULATION_LOG__sim_376]]
[[SIMULATION_LOG__sim_377]]
[[SIMULATION_LOG__sim_378]]
[[SIMULATION_LOG__sim_379]]
[[SIMULATION_LOG__sim_380]]
[[SIMULATION_LOG__sim_381]]
[[SIMULATION_LOG__sim_382]]
[[SIMULATION_LOG__sim_383]]
[[SIMULATION_LOG__sim_384]]
[[SIMULATION_LOG__sim_385]]
[[SIMULATION_LOG__sim_386]]
[[SIMULATION_LOG__sim_387]]
[[SIMULATION_LOG__sim_388]]
[[SIMULATION_LOG__sim_389]]
[[SIMULATION_LOG__sim_390]]
[[SIMULATION_LOG__sim_391]]
[[SIMULATION_LOG__sim_393]]
[[SIMULATION_LOG__sim_394]]
[[SIMULATION_LOG__sim_395]]
[[SIMULATION_LOG__sim_396]]
[[SIMULATION_LOG__sim_397]]
[[SIMULATION_LOG__sim_398]]
[[SIMULATION_LOG__sim_399]]
[[SIMULATION_LOG__sim_400]]
[[SIMULATION_LOG__sim_401]]
[[SIMULATION_LOG__sim_402]]
[[SIMULATION_LOG__sim_403]]
[[SIMULATION_LOG__sim_404]]
[[SIMULATION_LOG__sim_405]]
[[SIMULATION_LOG__sim_406]]
[[SIMULATION_LOG__sim_407]]
[[SIMULATION_LOG__sim_408]]
[[SIMULATION_LOG__sim_409]]
[[SIMULATION_LOG__sim_410]]
[[SIMULATION_LOG__sim_411]]
[[SIMULATION_LOG__sim_412]]
[[SIMULATION_LOG__sim_413]]
[[SIMULATION_LOG__sim_414]]
[[SIMULATION_LOG__sim_415]]
[[SIMULATION_LOG__sim_416]]
[[SIMULATION_LOG__sim_417]]
[[SIMULATION_LOG__sim_418]]
[[SIMULATION_LOG__sim_419]]
[[SIMULATION_LOG__sim_420]]
[[SIMULATION_LOG__sim_421]]
[[SIMULATION_LOG__sim_423]]
[[SIMULATION_LOG__sim_424]]
[[SIMULATION_LOG__sim_425]]
[[SIMULATION_LOG__sim_427]]
[[SIMULATION_LOG__sim_428]]
'''


list_notes = list_notes.split('\n')
for note in list_notes:
    try:
        path_note = get_embedded_reference_path(note, PARS)
        with open(path_note, 'r', encoding='utf8') as f:
            lines = f.readlines()
        lines = ['[[MTL_PINN__dynamic_data]]'] + lines
        with open(path_note, 'w', encoding='utf8') as f:
            f.writelines(lines)
    except:
        print('Could not handle note ' + note)

        # print('d')

