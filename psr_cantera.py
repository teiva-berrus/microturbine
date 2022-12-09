""" PSR by Cantera """

import numpy as np
import matplotlib.pyplot as plt
import cantera as ct

# Use reaction mechanism GRI-Mech 3.0. For 0-D simulations,
# no transport model is necessary.
gas = ct.Solution('gri30.yaml')

# Create a Reservoir for the inlet, set to a methane/air mixture at a specified
# equivalence ratio
equiv_ratio = 0.17  # lean combustion
gas.TP = 700,3E5
gas.set_equivalence_ratio(equiv_ratio, 'H2', 'O2:1.0, N2:3.76')
inlet = ct.Reservoir(gas)

# Create the combustor, and fill it initially with a mixture consisting of the
# equilibrium products of the inlet mixture. This state corresponds to the state
# the reactor would reach with infinite residence time, and thus provides a good
# initial condition from which to reach a steady-state solution on the reacting
# branch.
gas.equilibrate('HP')
combustor = ct.IdealGasReactor(gas)
combustor.volume = 1.0

# Create a reservoir for the exhaust
exhaust = ct.Reservoir(gas)

# Use a variable mass flow rate to keep the residence time in the reactor
# constant (residence_time = mass / mass_flow_rate). The mass flow rate function
# can access variables defined in the calling scope, including state variables
# of the Reactor object (combustor) itself.


def mdot(t):
    return combustor.mass / residence_time


inlet_mfc = ct.MassFlowController(inlet, combustor, mdot=mdot)

# A PressureController has a baseline mass flow rate matching the 'master'
# MassFlowController, with an additional pressure-dependent term. By explicitly
# including the upstream mass flow rate, the pressure is kept constant without
# needing to use a large value for 'K', which can introduce undesired stiffness.
outlet_mfc = ct.PressureController(combustor, exhaust, master=inlet_mfc, K=0.01)

# the simulation only contains one reactor
sim = ct.ReactorNet([combustor])

# Run a loop over decreasing residence times, until the reactor is extinguished,
# saving the state after each iteration.
states = ct.SolutionArray(gas, extra=['tres'])

residence_time = 0.1  # starting residence time
while combustor.T > 1000:
    sim.set_initial_time(0.0)  # reset the integrator
    sim.advance_to_steady_state()
    print('tres = {:.2e}; T = {:.1f}'.format(residence_time, combustor.T))
    states.append(combustor.thermo.state, tres=residence_time)
    residence_time *= 0.9  # decrease the residence time for the next iteration

# Plot results
f, ax1 = plt.subplots(1, 1)
ax1.plot(states.tres, states.heat_release_rate, '.-', color='C0')
ax2 = ax1.twinx()
ax2.plot(states.tres[:-1], states.T[:-1], '.-', color='C1')

ax1.set_xlabel('residence time [s]')
ax1.set_ylabel('heat release rate [W/m$^3$]', color='C0')
ax2.set_ylabel('temperature [K]', color='C1')

f.tight_layout()
plt.show()


#######################################################################
# Perfectly Stirred Reactor (PSR) in the microturbine code
#######################################################################

# Input parameters 
T_0 = 700  # inlet temperature [K]
pressure = 3E5  # constant pressure [Pa]
AIR_MASS_FLOW = 2.5          # in g/s
HYDROGEN_MASS_FLOW = 0.097  #in g/s
PHI = (1/0.42)/((AIR_MASS_FLOW/29)/(HYDROGEN_MASS_FLOW/2))
print("PHI : " + str(round(PHI,2)))


# Set the gas model with the initial conditions
gas1 = ct.Solution('gri30.yaml')
gas1.set_equivalence_ratio(phi = PHI, fuel = 'H2', oxidizer = 'O2: 0.21, N2: 0.79')
gas1.TP = T_0, pressure


# Create the combustor, and fill it initially with a mixture consisting of the equilibrium products
# Create the inlet and the outlet reservoirs of the combustor
inlet = ct.Reservoir(gas1)

gas1.equilibrate('HP')
combustor = ct.IdealGasReactor(gas1)
combustor.volume = 1.0

exhaust = ct.Reservoir(gas1)


# Use a variable mass flow rate to keep the residence time constant in the reactor
# The master flow controler is installed in the inlet of the combustor (MassFlowController)
# and the corresponding flow controler is installed in the outlet of the reactor (PressureControler)
def mdot(t):
    return combustor.mass / residence_time      #residence time = mass / mass_flow_rate

inlet_mfc = ct.MassFlowController(inlet, combustor, mdot=mdot)
outlet_mfc = ct.PressureController(combustor, exhaust, master=inlet_mfc, K=0.01)


# The simulation only contains one reactor
sim = ct.ReactorNet([combustor])


# Run a loop over decreasing residence times, until the reactor is extinguished, saving the state after each iteration
states = ct.SolutionArray(gas1, extra=['tres'])

residence_time = 0.1
while combustor.T > 700:
    sim.set_initial_time(0.0)  # reset the integrator
    sim.advance_to_steady_state()
    print('tres = {:.2e}; T = {:.1f}'.format(residence_time, combustor.T))
    states.append(combustor.thermo.state, tres=residence_time)
    residence_time *= 0.9  # decrease the residence time for the next iteration

# Plot results
# plt.plot(states.tres[:-1], states.T[:-1], '.-', color='C1')
# plt.xlabel('residence time [s]')
# plt.ylabel('temperature [K]')
# plt.show()

f, ax1 = plt.subplots(1, 1)
ax1.plot(states.tres, states.heat_release_rate, '.-', color='C0')
ax2 = ax1.twinx()
ax2.plot(states.tres[:-1], states.T[:-1], '.-', color='C1')
ax1.set_xlabel('residence time [s]')
ax1.set_ylabel('heat release rate [W/m$^3$]', color='C0')
ax2.set_ylabel('temperature [K]', color='C1')
f.tight_layout()
plt.show()