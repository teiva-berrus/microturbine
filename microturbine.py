import cantera as ct
import numpy as np
import matplotlib.pyplot as plt


# Intake air

INTAKE_TEMP = 293           # in Kelvin
INTAKE_PRES = 1E5           # in Pa
AIR_MASS_FLOW = 20          # in g/s
HYDROGEN_MASS_FLOW = 0.097  #in g/s
RICHESSE = (1/0.42)/((AIR_MASS_FLOW/29)/(HYDROGEN_MASS_FLOW/2))

print("Richesse : " + str(round(RICHESSE,2)))
GAMMA = 1.4
gas = ct.Solution('gri30.yaml')
gas.TPX = INTAKE_TEMP, INTAKE_PRES, 'N2:{0}, O2:{1}'.format(0.8,0.2)
INTAKE_ENTALPY = gas.h

pressure = [INTAKE_PRES]
temperature = [INTAKE_TEMP]
enthalpy = [INTAKE_ENTALPY]
entropy = [gas.s]
DISCRETISATION = 50        # number of step in each part of engine

""" Compressor """

COMPRESSION_RATIO = 3
for i in range (DISCRETISATION):
    pressure.append(pressure[0]*(1+COMPRESSION_RATIO*(i+1)/DISCRETISATION))
    temperature.append(temperature[i]*(pressure[i]/pressure[i+1])**((1-GAMMA)/GAMMA))
    gas.TP = temperature[i], pressure[i]
    enthalpy.append(gas.h)
    entropy.append(gas.s)
P3 = pressure[-1]
T3_IS = temperature[-1]
H3_IS = enthalpy[-1]


plt.plot(entropy, enthalpy)

print("Compressor outlet pressure = " + str(P3*1E-5) + " bar")
gas.TP = T3_IS,P3

COMPRESSION_POWER_ISENTROPIC = (gas.h - INTAKE_ENTALPY)*AIR_MASS_FLOW*1E-3
COMPRESSION_POWER = COMPRESSION_POWER_ISENTROPIC/0.66
print("Compression power isentropic= " + str(int(COMPRESSION_POWER_ISENTROPIC)) + " W")
print("Compression power = " + str(int(COMPRESSION_POWER)) + " W")
T3 = INTAKE_TEMP+COMPRESSION_POWER/(gas.cp*AIR_MASS_FLOW*1E-3)
print("Compressor outlet temperature (isentropic) = " + str(int(T3_IS)) + " K")
print("Compressor outlet temperature = " + str(int(T3)) + " K")
gas.TP = T3,P3




""" Combustion chamber"""

gas.set_equivalence_ratio(phi = RICHESSE, fuel = 'H2', oxidizer = 'O2: 0.21, N2: 0.79')
gas.equilibrate('HP')

T4 = gas.T
P4 = gas.P
H4 = gas.h
temperature.append(T4)
pressure.append(P4)
enthalpy.append(H4)
entropy.append(gas.s)

print("Flamme temperature = " + str(int(T4)) + " K")


""" Turbine """

EXPANSION_RATIO = P4/INTAKE_PRES
end = len(pressure)-1


for i in range (DISCRETISATION):
    pressure.append(INTAKE_PRES*(1+EXPANSION_RATIO*(DISCRETISATION-i)/DISCRETISATION))
    temperature.append(temperature[end+i]*(pressure[end+i]/pressure[end+i+1])**((1-GAMMA)/GAMMA))
    gas.TP = temperature[i],pressure[i]
    enthalpy.append(gas.h)
    entropy.append(gas.s)

plt.plot(entropy[end+1:],enthalpy[end+1:])
P5 = INTAKE_PRES
T5_IS = T4*(P4/P5)**((1-GAMMA)/GAMMA)
gas.TP = T5_IS,P5
H5 = gas.h
TURBINE_POWER_ISENTROPIC = (H4-H5)*AIR_MASS_FLOW*1E-3
TURBINE_POWER = TURBINE_POWER_ISENTROPIC*0.73
T5 = T4 + TURBINE_POWER/(gas.cp*AIR_MASS_FLOW*1E-3)
print("Turbine power (isentropic) = " + str(int(TURBINE_POWER_ISENTROPIC)) + " W")
print("Turbine power = " + str(int(TURBINE_POWER)) + " W")
print("Available power = " + str(int(TURBINE_POWER-COMPRESSION_POWER)) + " W")
#plt.show()
print(T5)

# Rendement

EFFICENCY = (TURBINE_POWER-COMPRESSION_POWER)/(143E6*HYDROGEN_MASS_FLOW*1E-3)
print("Rendement = " + str(EFFICENCY*100) + " %")
