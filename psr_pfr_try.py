""" Combustion chamber modeled with one PSR and two PFRs """

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt


#####################################################################
#                Perfectly Stirred Reactor (PSR)
#####################################################################

AIR_MASS_FLOW = 20E-3                                               # in kg/s, total air mass flow
COMBUSTION_AIR_MASS_FLOW = 3.33E-3                                  # in kg/s, air mass flow used in the PSR
DILUTION_AIR_MASS_FLOW = AIR_MASS_FLOW - COMBUSTION_AIR_MASS_FLOW   # in kg/s, air mass flow used for dilution in PFRs
HYDROGEN_MASS_FLOW = 0.097E-3                                       # in kg/s
PRODUCTS_MASS_FLOW = COMBUSTION_AIR_MASS_FLOW + HYDROGEN_MASS_FLOW  # in kg/s

PHI = (1/0.42)/((COMBUSTION_AIR_MASS_FLOW/29)/(HYDROGEN_MASS_FLOW/2))
print("PHI  " + str(PHI))

gas = ct.Solution('gri30.yaml')
gas.TP = 700,3e5                                                    # compression outlet temperature and pressure 
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


""" Equilibrate instead of PSR in what follows """
gas.equilibrate('HP')



#######################################################################
#                    Plug Flow Reactors (PFRs)
#######################################################################

""" First mix: combustion products from the PSR with half of the dilution air mass flow (we want two PFRs) """

gas_a = gas                                                 # PSR outlet gas

gas_b = ct.Solution('gri30.yaml')                           # compressed air
gas_b.TPX = 700.0, 3*ct.one_atm, 'O2:0.21, N2:0.79'

LENGTH = 0.1                                                # total PFRs length [m]
AREA = 7.065e-4                                             # cross-sectional area [m**2]

u_0 = PRODUCTS_MASS_FLOW / (gas_a.density*AREA)             # combustion products velocity [m/s]

res_a = ct.Reservoir(gas_a)                                 # reservoir containing burned gas
res_b = ct.Reservoir(gas_b)                                 # reservoir containing compressed air
mixer = ct.IdealGasReactor(gas_a)                           # reactor mixing the gases

mfc_a = ct.MassFlowController(res_a, mixer, mdot=PRODUCTS_MASS_FLOW)        # combustion products mass flow controler 
mfc_b = ct.MassFlowController(res_b, mixer, mdot=DILUTION_AIR_MASS_FLOW/2)  # compressed air mass flow controler (divided by 2 as we want 2 PFRs)

downstream = ct.Reservoir(gas_a)                            # reservoir containing the mixture
outlet = ct.Valve(mixer, downstream, K=10.0)                # link the mixing reactor and the downstream reservoir

sim = ct.ReactorNet([mixer])                                # simulation of the mixer


# compute the first reaction
t_total = LENGTH / u_0                                      # the total simulation time depends on the length and inflow velocity
N_STEPS = 2000
dt = t_total/N_STEPS

t = (np.arange(N_STEPS) +1)*dt                              # array containing time
z = np.zeros_like(t)                                        # array containing space
u = np.zeros_like(t)                                        # array containing flow velocity 
states1 = ct.SolutionArray(mixer.thermo, extra=['space'])   # solution array containing thermodynamic state in mixer and space

for i in range (1, int(len(t)/2)):                          # for the first PFR, only half of the arrays is filled
    sim.advance(t[i])                                       # advance the simulation
    u[i] = PRODUCTS_MASS_FLOW / AREA / mixer.thermo.density # new flow velocity
    z[i] = z[i-1] + u[i]*dt                                 # advance in space
    states1.append(mixer.thermo.state, space = z[i])        # append the thermodynamic state in mixer and space
states = states1                                            # the final solution array containing states1 (solution array of the first PFR) and
                                                            #then states2 (solution array of the second PFR)



""" Second mix: previous mix with the remaining half of the dilution air mass flow """
gas_a2 = mixer.thermo                                                           # first PFR outlet gas

u_0 = PRODUCTS_MASS_FLOW + DILUTION_AIR_MASS_FLOW/2/ (gas_a2.density*AREA)      # first PFR outlet gas velocity 

res_a2 = downstream                                                             # reservoir containing the first PFR outlet gas
# res_b not changed
mixer2 = ct.IdealGasReactor(gas_a2)                                             # reactor mixing the two privious gases

mfc_a_2 = ct.MassFlowController(res_a2, mixer2, mdot=PRODUCTS_MASS_FLOW + DILUTION_AIR_MASS_FLOW/2)     # combustion chamber product mass flow 

downstream2 = ct.Reservoir(gas_a2)
outlet2 = ct.Valve(mixer2, downstream2, K=10.0)

sim2 = ct.ReactorNet([mixer2])


# compute the second reaction
states2 = ct.SolutionArray(mixer2.thermo, extra=['space'])

for i in range (int(len(t)/2), int(len(t))):                                    # for the second PFR, the remaining half of the arrays is filled
    sim.advance(t[i])
    u[i] = PRODUCTS_MASS_FLOW / AREA / mixer2.thermo.density
    z[i] = z[i -1] + u[i]*dt
    states.append(mixer2.thermo.state, space=z[i])                              # the final solution array already containing states1 and now
                                                                                # states of the second PFR


#######################################################################
#                    Displaying results
#######################################################################

plt.clf()

plt.subplot(2, 1, 1)
plt.plot(states.space, states.T)
plt.xlabel('Space [m]')
plt.ylabel('Temperature (K)')

# plt.subplot(2, 2, 2)
# plt.plot(states.space, states.X[:, gas_b.species_index('CO2')])
# plt.xlabel('Space [m]')
# plt.ylabel('CO2 Mole Fraction')

# plt.subplot(2, 2, 3)
# plt.plot(states.space, states.X[:, gas_b.species_index('NO2')])
# plt.xlabel('Space [m]')
# plt.ylabel('NO2 Mole Fraction')

# plt.subplot(2, 2, 4)
# plt.plot(states.space, states.X[:, gas_b.species_index('NO')])
# plt.xlabel('Space [m]')
# plt.ylabel('NO Mole Fraction')

plt.tight_layout()
plt.show()