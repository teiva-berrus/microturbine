# -*- coding: utf-8 -*-
"""
This example solves a plug-flow reactor problem of hydrogen-oxygen combustion.
The PFR is computed by two approaches: The simulation of a Lagrangian fluid
particle, and the simulation of a chain of reactors.

Requires: cantera >= 2.5.0, matplotlib >= 2.0
Keywords: combustion, reactor network, plug flow reactor
"""

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

#######################################################################
# Input Parameters
#######################################################################

T_0 = 700  # inlet temperature [K]
pressure = 3E5  # constant pressure [Pa]
length = 80000  # *approximate* PFR length [m]
u_0 = 53  # inflow velocity [m/s]
area = 314e-6  # cross-sectional area [m**2]
PHI = 0.17

# input file containing the reaction mechanism
reaction_mechanism = 'gri30.yaml'

# Resolution: The PFR will be simulated by 'n_steps' time steps or by a chain
# of 'n_steps' stirred reactors.
n_steps = 2000
#####################################################################


#####################################################################
# Method 1: Lagrangian Particle Simulation
#####################################################################
# A Lagrangian particle is considered which travels through the PFR. Its
# state change is computed by upwind time stepping. The PFR result is produced
# by transforming the temporal resolution into spatial locations.
# The spatial discretization is therefore not provided a priori but is instead
# a result of the transformation.

# import the gas model and set the initial conditions
gas1 = ct.Solution(reaction_mechanism)
gas1.set_equivalence_ratio(phi = PHI, fuel = 'H2', oxidizer = 'O2: 0.21, N2: 0.79')
gas1.TP = T_0, pressure
mass_flow_rate1 = u_0 * gas1.density * area
print(mass_flow_rate1)

# create a new reactor
r1 = ct.IdealGasConstPressureReactor(gas1)
# create a reactor network for performing time integration
sim1 = ct.ReactorNet([r1])

# approximate a time step to achieve a similar resolution as in the next method
t_total = length / u_0
dt = t_total / n_steps

# define time, space, and other information vectors
t1 = (np.arange(n_steps) + 1) * dt
z1 = np.zeros_like(t1)
u1 = np.zeros_like(t1)
states1 = ct.SolutionArray(r1.thermo)
for n1, t_i in enumerate(t1):
    # perform time integration
    sim1.advance(t_i)
    # compute velocity and transform into space
    u1[n1] = mass_flow_rate1 / area / r1.thermo.density
    z1[n1] = z1[n1 - 1] + u1[n1] * dt
    states1.append(r1.thermo.state)

# results
plt.figure()
plt.plot(z1, states1.T, label='Lagrangian Particle')
plt.xlabel('$z$ [m]')
plt.ylabel('$T$ [K]')
plt.legend(loc=0)
plt.show()
#plt.savefig('pfr_T_z.png')

plt.figure()
plt.plot(t1, states1.X[:, gas1.species_index('H2')], label='H2')
plt.plot(t1, states1.X[:, gas1.species_index('H2O')], label='H2O')
plt.plot(t1, states1.X[:, gas1.species_index('O2')], label='O2')
plt.plot(t1, states1.X[:, gas1.species_index('NO2')], label='NO2')
plt.plot(t1, states1.X[:, gas1.species_index('N2')], label='N2')
plt.xlabel('$t$ [s]')
plt.ylabel('$X_{H_2}$ [-]')
plt.legend(loc=0)
plt.show()
#plt.savefig('pfr_XH2_t.png')