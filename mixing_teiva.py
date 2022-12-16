""" Mixing two streams """

""" First method """
import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
# Use air for stream a.
gas_a = ct.Solution('gri30.yaml')
gas_a.TPX = 700.0, 3*ct.one_atm, 'O2:0.21, N2:0.79'



# Use GRI-Mech 3.0 for stream b (methane) and for the mixer. If it is desired
# to have a pure mixer, with no chemistry, use instead a reaction mechanism
# for gas_b that has no reactions.
gas_b = ct.Solution('gri30.yaml')
gas_b.TP = 700,3E5
gas_b.set_equivalence_ratio(1,'H2','O2:1,N2:3.76')
gas_b.equilibrate('HP')


# Create reservoirs for the two inlet streams and for the outlet stream.  The
# upsteam reservoirs could be replaced by reactors, which might themselves be
# connected to reactors further upstream. The outlet reservoir could be
# replaced with a reactor with no outlet, if it is desired to integrate the
# composition leaving the mixer in time, or by an arbitrary network of
# downstream reactors.
res_a = ct.Reservoir(gas_a)
res_b = ct.Reservoir(gas_b)
downstream = ct.Reservoir(gas_b)

# Create a reactor for the mixer. A reactor is required instead of a
# reservoir, since the state will change with time if the inlet mass flow
# rates change or if there is chemistry occurring.
# gas_a.TPX = 1000.0, ct.one_atm, 'O2:0.21, N2:0.78, AR:0.01'
gas_c = ct.Solution('gri30.yaml')
gas_c.TP = 1200,3E5
mixer = ct.IdealGasReactor(gas_c)

# create two mass flow controllers connecting the upstream reservoirs to the
# mixer, and set their mass flow rates to values corresponding to
# stoichiometric combustion.

mfc2 = ct.MassFlowController(res_b, mixer, mdot=4)

# connect the mixer to the downstream reservoir with a valve.
outlet = ct.Valve(mixer, downstream, K=10.0)

sim = ct.ReactorNet([mixer])


# Since the mixer is a reactor, we need to integrate in time to reach steady
# state
t_max = 20
n = 3
dt = t_max/n
t=0
temp = []
time = []

for i in np.arange(0,t_max,3):
    mfc1 = ct.MassFlowController(res_a, mixer, mdot=0.1)
    sim = ct.ReactorNet([mixer])
    for x in np.arange(0,t_max,100):
        sim.advance(t_max/100)
        temp.append(mixer.thermo.state.T[0])
        
        time.append(t)
        t+=1
# 
# view the state of the gas in the mixer
print(mixer.thermo.report())
plt.plot(time,temp)
plt.show()


""" Second method """
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