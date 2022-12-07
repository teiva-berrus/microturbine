""" PSF and PFR microturbine """

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

#######################################################################
# Perfectly Stirred Reactor (PSR)
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

#######################################################################
# Plug Flow Reactor (PFR)
#######################################################################

 # input parameters
T_0 = states.T[0]  # inlet temperature [K]
pressure = states.P[0]  # constant pressure [Pa]
gas1.TP = T_0, pressure

length = 1  # approximate PFR length [m]
PRODUCTS_MASS_FLOW = 20 - AIR_MASS_FLOW
area = 314e-6  # cross-sectional area [m**2]
u_0 = PRODUCTS_MASS_FLOW / (1*area) # inflow velocity [m/s]


# input file containing the reaction mechanism
# reaction_mechanism = 'gri30.yaml'

# Resolution: The PFR will be simulated by 'n_steps' time steps or by a chain
# of 'n_steps' stirred reactors.
n_steps = 2000


# # import the gas model and set the initial conditions
# gas1 = ct.Solution(reaction_mechanism)
# gas1.set_equivalence_ratio(phi = PHI, fuel = 'H2', oxidizer = 'O2: 0.21, N2: 0.79')
# gas1.TP = T_0, pressure
# mass_flow_rate1 = u_0 * gas1.density * area


# create a new reactor
reactor = ct.IdealGasConstPressureReactor(gas1)

# create a reactor network for performing time integration
sim = ct.ReactorNet([reactor])

# approximate a time step to achieve a similar resolution as in the next method
# t_total = length / u_0
t_total = 10
dt = t_total / n_steps

# define time, space, and other information vectors
t = (np.arange(n_steps) + 1) * dt
z = np.zeros_like(t)
u = np.zeros_like(t)
states = ct.SolutionArray(reactor.thermo)
# for n, t_i in enumerate(t):
#     # perform time integration
#     simadvance(t_i)
#     # compute velocity and transform into space
#     u[n] = mass_flow_rate1/ area / reactor.thermo.density
#     z[n] = z[n - 1] + u[n] * dt
#     states.append(reactor.thermo.state)





# # results
# plt.figure()
# plt.plot(z1, states1.T, label='Lagrangian Particle')
# plt.xlabel('$z$ [m]')
# plt.ylabel('$T$ [K]')
# plt.legend(loc=0)
# plt.show()
# #plt.savefig('pfr_T_z.png')

# plt.figure()
# plt.plot(t1, states1.X[:, gas1.species_index('H2')], label='H2')
# plt.plot(t1, states1.X[:, gas1.species_index('H2O')], label='H2O')
# plt.plot(t1, states1.X[:, gas1.species_index('O2')], label='O2')
# plt.plot(t1, states1.X[:, gas1.species_index('NO2')], label='NO2')
# plt.plot(t1, states1.X[:, gas1.species_index('N2')], label='N2')
# plt.xlabel('$t$ [s]')
# plt.ylabel('$X_{H_2}$ [-]')
# plt.legend(loc=0)
# plt.show()
# #plt.savefig('pfr_XH2_t.png')