import cantera as ct
import numpy as np

epsilon = 0.01
T3 = 500 # K
P3 = 300000
PHI = 0.17
T4_stab = [1000]
P0 = 100000
GAMMA = 1.4
T4_lim = 1200
epsilon_spacing = 0.01

while T4_stab[-1] < T4_lim :
    T5 = [770]
    T35 = []
    T4 = []
    P4 = []
    for k in range (10):
        T35.append(T3+epsilon*(T5[k]-T3))

        gas = ct.Solution('gri30.yaml')
        gas.TP = T35[k], P3
        gas.set_equivalence_ratio(phi = PHI, fuel = 'H2', oxidizer = 'O2: 0.21, N2: 0.79')
        gas.equilibrate('HP')
        T4.append(gas.T)
        P4.append(gas.T)
        gas.TP = T4[-1],P4[-1]
        H4 = gas.h

        P5 = P0
        T5.append(T4[-1]*(P4[-1]/P5)**((1-GAMMA)/GAMMA))
        gas.TP = T5[-1],P5
    epsilon += epsilon_spacing
    T4_stab.append(T4[-1])
    
print("T4 = " + str(T4_stab[-2]))
print("epsilon = " + str(epsilon-epsilon_spacing))