import cantera as ct
import matplotlib.pyplot as plt
import numpy as np

gas = ct.Solution('gri30.yaml')

# Stream A (air)
A = ct.Quantity(gas, constant='HP')
A.TPX = 700.0, 3*ct.one_atm, 'O2:0.21, N2:0.79'

# Stream B (methane)
gas_b = ct.Solution('gri30.yaml')
gas_b.set_equivalence_ratio(1,'H2', 'O2:1,N2:3.76')
gas_b.TP = 700,3E3
gas_b.equilibrate('HP')
B = ct.Quantity(gas_b, constant='HP')

# Set the molar flow rates corresponding to stoichiometric reaction,
# CH4 + 2 O2 -> CO2 + 2 H2O

t_max = 1
n = 1
dt = t_max/n

AIR_MASS_FLOW = 17
BURNED_GAS_MASS_FLOW = 3

A.mass = AIR_MASS_FLOW*dt

B.mass = BURNED_GAS_MASS_FLOW*t_max

M = A+B
print(M.report())
