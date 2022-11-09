import cantera as ct
import numpy as np
import matplotlib.pyplot as plt



# Intake air

INTAKE_TEMP = 293   # in Kelvin
INTAKE_PRES = 1E5   # in Pa
AIR_MASS_FLOW = 20 # in g/s
HYDROGEN_MASS_FLOW = 0.097 #in g/s
DILUTION_RATIO = AIR_MASS_FLOW/HYDROGEN_MASS_FLOW
RICHESSE = 34/DILUTION_RATIO
GAMMA = 1.4
gas = ct.Solution('gri30.yaml')
gas.TPX = INTAKE_TEMP, INTAKE_PRES, 'N2:{0}, O2:{1}'.format(0.8,0.2)

INTAKE_ENTALPY = gas.h
# Compression

COMPRESSION_RATIO = 3
P3 = COMPRESSION_RATIO*INTAKE_PRES
T3 = INTAKE_TEMP*(INTAKE_PRES/P3)**((1-GAMMA)/GAMMA)
print(T3)
gas.TP = T3,P3
COMPRESSION_POWER = (gas.h - INTAKE_ENTALPY)*AIR_MASS_FLOW*1E-3
print(COMPRESSION_POWER)


# Combustion

gas.set_equivalence_ratio(phi = RICHESSE, fuel = 'H2', oxidizer = 'O2: 0.2, N2: 0.8')
gas.equilibrate('HP')

T4 = gas.T
P4 = gas.P
H4 = gas.h

# Turbine

P5 = INTAKE_PRES
T5 = T4*(P4/P5)**((1-GAMMA)/GAMMA)
gas.TP = T5,P5
H5 = gas.h
TURBINE_POWER = (H4-H5)*AIR_MASS_FLOW*1E-3
print(TURBINE_POWER)
print(TURBINE_POWER-COMPRESSION_POWER)




