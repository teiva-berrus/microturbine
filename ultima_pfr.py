""" Mixing + PFR """

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

#######################################################################
# Input Parameters
#######################################################################

T_0 = 700  # inlet temperature [K]
pressure = 3*ct.one_atm  # constant pressure [Pa]
gas1 = ct.Solution('gri30.yaml')
gas1.set_equivalence_ratio(1,'H2','O2:0.21,N2:0.79')
gas1.equilibrate('HP')
gas2 = ct.Solution('gri30.yaml')
gas2.TPX = 700,3e5,'O2:1,N2:3.76'

res_a = ct.Reservoir(gas1)
res_b = ct.Reservoir(gas2)
downstream = ct.Reservoir(gas2)
mixer = ct.IdealGasReactor(gas1)
mfc1 = ct.MassFlowController(res_a, mixer, mdot=3)
mfc2 = ct.MassFlowController(res_b, mixer, mdot=17)
outlet = ct.Valve(mixer, downstream, K=10.0)

sim = ct.ReactorNet([mixer])

sim.advance_to_steady_state()


