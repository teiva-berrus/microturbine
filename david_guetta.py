""" Mixing """

import cantera as ct

gas = ct.Solution('gri30.yaml')

# Stream A (air)
A = ct.Quantity(gas, constant='HP')
A.TPX = 700.0, 3E5, 'O2:0.21, N2:0.79'

# Stream B (methane)
B = ct.Quantity(gas, constant='HP')
B.TPX = 2000.0, ct.one_atm, 'N2:0.67, H2O:0.27, OH:0.2, O2:0.01'

# Set the molar flow rates corresponding to stoichiometric reaction,
# CH4 + 2 O2 -> CO2 + 2 H2O
A.mass = 18

B.mass = 2

# Compute the mixed state
M = A + B
print(M.T)

