import cantera as ct
import numpy as np
import matplotlib.pyplot as plt


# Intake air

T0 = 293           # in Kelvin
P0 = 1E5           # in Pa
AIR_MASS_FLOW = 20          # in g/s
HYDROGEN_MASS_FLOW = 0.097  #in g/s
PHI = (1/0.42)/((AIR_MASS_FLOW/29)/(HYDROGEN_MASS_FLOW/2))
print("PHI : " + str(round(PHI,2)))
GAMMA = 1.4
COMPRESSION_EFFICIENCY = 0.66
TURBINE_EFFICIENCY = 0.73
gas = ct.Solution('gri30.yaml')
gas.TPX = T0, P0, 'N2:0.79, O2:0.21'
H0 = gas.h
# S0 = gas.s

# temperature = [T0]
# pressure = [P0]
# enthalpy = [H0]
# entropy = [S0]
# DISCRETISATION = 50        # number of step in each part of engine



""" Compressor """

COMPRESSION_RATIO = 3

# for i in range (DISCRETISATION):
#     pressure.append(pressure[0]*(1+COMPRESSION_RATIO*(i+1)/DISCRETISATION))
#     temperature.append(temperature[i]*(pressure[i]/pressure[i+1])**((1-GAMMA)/GAMMA))
#     gas.TP = temperature[i], pressure[i]
#     enthalpy.append(gas.h)
#     entropy.append(gas.s)
# P3 = pressure[-1]
# T3_IS = temperature[-1]
# gas.TP = T3_IS,P3
# H3_IS = enthalpy[-1]

# plt.plot(entropy, enthalpy)

P3 = P0*COMPRESSION_RATIO
T3_IS = T0*(P0/P3)**((1-GAMMA)/GAMMA)
gas.TP = T3_IS,P3
H3_IS = gas.h

print("Compressor outlet pressure = " + str(P3*1E-5) + " bar")

ISENTROPIC_COMPRESSION_POWER = (H3_IS - H0)*AIR_MASS_FLOW*1E-3
COMPRESSION_POWER = ISENTROPIC_COMPRESSION_POWER/COMPRESSION_EFFICIENCY
print("Isentropic compression power = " + str(int(ISENTROPIC_COMPRESSION_POWER)) + " W")
print("Compression power = " + str(int(COMPRESSION_POWER)) + " W")

T3 = T0+COMPRESSION_POWER/(gas.cp*AIR_MASS_FLOW*1E-3)
gas.TP = T3,P3
print("Compressor outlet temperature (isentropic) = " + str(int(T3_IS)) + " K")
print("Compressor outlet temperature = " + str(int(T3)) + " K")



""" Combustion chamber"""

gas.set_equivalence_ratio(phi = PHI, fuel = 'H2', oxidizer = 'O2: 0.21, N2: 0.79')
gas.equilibrate('HP')

T4 = gas.T
P4 = gas.P
H4 = gas.h

# S4 = gas.s
# temperature.append(T4)
# pressure.append(P4)
# enthalpy.append(H4)
# entropy.append(S4)

print("Flame temperature = " + str(int(T4)) + " K")



""" Turbine """

# EXPANSION_RATIO = P4/P0
# end = len(pressure)-1

# for i in range (DISCRETISATION+1):
#     pressure.append(P0*(1+EXPANSION_RATIO*(DISCRETISATION-i)/DISCRETISATION))
#     temperature.append(temperature[end+i]*(pressure[end+i]/pressure[end+i+1])**((1-GAMMA)/GAMMA))
#     gas.TP = temperature[i],pressure[i]
#     enthalpy.append(gas.h)
#     entropy.append(gas.s)
    
# P5 = pressure[-1]
# T5_IS = temperature[-1]
# gas.TP = T5_IS,P5
# H5_IS = enthalpy[-1]

# plt.plot(entropy[end+1:],enthalpy[end+1:])

P5 = P0
T5_IS = T4*(P4/P5)**((1-GAMMA)/GAMMA)
gas.TP = T5_IS,P5
H5_IS = gas.h

ISENTROPIC_TURBINE_POWER = (H4-H5_IS)*AIR_MASS_FLOW*1E-3
TURBINE_POWER = ISENTROPIC_TURBINE_POWER*TURBINE_EFFICIENCY
T5 = T4 - TURBINE_POWER/(gas.cp*AIR_MASS_FLOW*1E-3)
print("Isentropic turbine power = " + str(int(ISENTROPIC_TURBINE_POWER)) + " W")
print("Turbine power = " + str(int(TURBINE_POWER)) + " W")

print("Available power = " + str(int(TURBINE_POWER-COMPRESSION_POWER)) + " W")
#plt.show()
print(T5)

# Rendement
THERMAL_POWER = 143E6*HYDROGEN_MASS_FLOW*1E-3
EFFICENCY = (TURBINE_POWER-COMPRESSION_POWER)/THERMAL_POWER
print("Rendement = " + str(EFFICENCY*100) + " %")