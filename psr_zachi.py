""" PSR by Zacharia """

import sys
import cantera as ct

gas = ct.Solution('gri30.yaml')
gas.TP = 700,3e5
gas.set_equivalence_ratio(1, fuel='H2', oxidizer='O2:1, N2:3.76')


r = ct.IdealGasConstPressureReactor(gas)

sim = ct.ReactorNet([r])
sim.verbose = True

# limit advance when temperature difference is exceeded
delta_T_max = 20
r.set_advance_limit('temperature', delta_T_max)

dt_max = 1E-2
t_end = 400
states = ct.SolutionArray(gas, extra=['t'])

print('{:10s} {:10s} {:10s} {:14s}'.format(
     't [s]', 'T [K]', 'P [Pa]', 'u [J/kg]'))
while sim.time < t_end:
    if sim.time < 380:
        dt_max = 1
    else:
        dt_max = 1E-4
    sim.advance(sim.time + dt_max)
    states.append(r.thermo.state, t=sim.time*1e3)
    print('{:10.3e} {:10.3f} {:10.3f} {:14.6f}'.format(
          sim.time, r.T, r.thermo.P, r.thermo.u))


import matplotlib.pyplot as plt
plt.clf()

plt.subplot(2, 2, 1)
plt.plot(states.t, states.T)
plt.xlabel('Time (ms)')
plt.ylabel('Temperature (K)')

plt.subplot(2, 2, 2)
plt.plot(states.t, states.X[:, gas.species_index('CO2')])
plt.xlabel('Time (ms)')
plt.ylabel('CO2 Mole Fraction')

plt.subplot(2, 2, 3)
plt.plot(states.t, states.X[:, gas.species_index('NO2')])
plt.xlabel('Time (ms)')
plt.ylabel('NO2 Mole Fraction')

plt.subplot(2, 2, 4)
plt.plot(states.t, states.X[:, gas.species_index('NO')])
plt.xlabel('Time (ms)')
plt.ylabel('NO Mole Fraction')

plt.tight_layout()
plt.show()
