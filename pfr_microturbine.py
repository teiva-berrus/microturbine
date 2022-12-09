""" PSR (Zacharia) and PFR microturbine """

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
import sys


#######################################################################
#          Perfectly Stirred Reactor (PSR) by Zacharia
#######################################################################

COMBUSTION_AIR_MASS_FLOW = 3.33
AIR_MASS_FLOW = 20-COMBUSTION_AIR_MASS_FLOW      # in g/s
HYDROGEN_MASS_FLOW = 0.097  #in g/s
PRODUCTS_MASS_FLOW = COMBUSTION_AIR_MASS_FLOW+HYDROGEN_MASS_FLOW
PHI = (1/0.42)/((COMBUSTION_AIR_MASS_FLOW/29)/(HYDROGEN_MASS_FLOW/2))
print("PHI  " + str(PHI))
print("PRODUCT MASS FLOW  "+str(PRODUCTS_MASS_FLOW))
gas = ct.Solution('gri30.yaml')
gas.TP = 700,3e5
gas.set_equivalence_ratio(PHI, fuel='H2', oxidizer='O2:0.21, N2:0.79')

# r = ct.IdealGasConstPressureReactor(gas)

# sim = ct.ReactorNet([r])
# sim.verbose = True

# # limit advance when temperature difference is exceeded
# delta_T_max = 20
# r.set_advance_limit('temperature', delta_T_max)

# dt_max = 1E-2
# t_end = 385.19

# states = ct.SolutionArray(gas, extra=['t'])

# while sim.time < t_end:
#     if sim.time < 380:
#         dt_max = 1
#     else:
#         dt_max = 1E-2
#     sim.advance(sim.time + dt_max)
#     states.append(r.thermo.state, t=sim.time*1e3)

# plt.clf()

# plt.subplot(2, 2, 1)
# plt.plot(states.t, states.T)
# plt.xlabel('Time (ms)')
# plt.ylabel('Temperature (K)')

# plt.subplot(2, 2, 2)
# plt.plot(states.t, states.X[:, gas.species_index('CO2')])
# plt.xlabel('Time (ms)')
# plt.ylabel('CO2 Mole Fraction')

# plt.subplot(2, 2, 3)
# plt.plot(states.t, states.X[:, gas.species_index('NO2')])
# plt.xlabel('Time (ms)')
# plt.ylabel('NO2 Mole Fraction')

# plt.subplot(2, 2, 4)
# plt.plot(states.t, states.X[:, gas.species_index('NO')])
# plt.xlabel('Time (ms)')
# plt.ylabel('NO Mole Fraction')

# plt.tight_layout()
# plt.show()


""" Equilibrate instead of PSR in follows """
gas.equilibrate('HP')


#######################################################################
#                    Plug Flow Reactor (PFR)
#######################################################################

gas1 = gas
gas2 = ct.Solution('gri30.yaml')
gas2.TPX = 700.0, 3*ct.one_atm, 'O2:0.21, N2:0.79'

length = 0.05  # approximate PFR length [m]
area = 7.065e-4  # cross-sectional area [m**2]
#PRODUCTS_MASS_FLOW = 1
#AIR_MASS_FLOW = 19
u_0 = PRODUCTS_MASS_FLOW*E-3 / (gas1.density*area) # inflow velocity [m/s]
print(u_0)

res_a = ct.Reservoir(gas1)
res_b = ct.Reservoir(gas2)

downstream = ct.Reservoir(gas1)
mixer = ct.IdealGasReactor(gas1)

mfc1 = ct.MassFlowController(res_a, mixer, mdot=PRODUCTS_MASS_FLOW)
mfc2 = ct.MassFlowController(res_b, mixer, mdot=AIR_MASS_FLOW)

outlet = ct.Valve(mixer, downstream, K=10.0)

sim = ct.ReactorNet([mixer])


""" One PFR by Cantera """
# n_steps = 2000
# t_total = length/u_0
# dt = t_total / n_steps

# t = (np.arange(n_steps)+1) * dt
# z = np.zeros_like(t)
# u = np.zeros_like(t)

# states = ct.SolutionArray(gas,extra=['space'])

# for n,t_i in enumerate(t):
#     sim.advance(t_i)
#     # compute velocity and transform into space
#     u[n] = PRODUCTS_MASS_FLOW*10E-3 / (mixer.thermo.density*area)
#     z[n] = z[n - 1] + u[n] * dt
#     states.append(mixer.thermo.state,space=z[n])


plt.clf()

plt.subplot(2, 2, 1)
plt.plot(states.space, states.T)
plt.xlabel('Space [m]')
plt.ylabel('Temperature (K)')

plt.subplot(2, 2, 2)
plt.plot(states.space, states.X[:, gas1.species_index('CO2')])
plt.xlabel('Space [m]')
plt.ylabel('CO2 Mole Fraction')

plt.subplot(2, 2, 3)
plt.plot(states.space, states.X[:, gas1.species_index('NO2')])
plt.xlabel('Space [m]')
plt.ylabel('NO2 Mole Fraction')

plt.subplot(2, 2, 4)
plt.plot(states.space, states.X[:, gas1.species_index('NO')])
plt.xlabel('Space [m]')
plt.ylabel('NO Mole Fraction')

plt.tight_layout()
plt.show()