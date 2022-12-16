import cantera as ct
import numpy as np
gas = ct.Solution('gri30.yaml')
gas.TPX = 300, ct.one_atm, 'H2:2, O2:1, N2:3.76'
gas.equilibrate('HP')
r = ct.IdealGasReactor(gas, volume=1.0)
sim = ct.ReactorNet([r])
# r.T = 300
# r.P = ct.one_atm
#r.u = 0
#gas.TPX = 300, ct.one
# Définir la durée de la simulation et le pas de temps
t_max = 1.0
dt = 1e-3

# Créer deux objets "PFR" et "PSR"
pfr = ct.ConstPressureReactor(gas, volume=1.0)
psr = ct.ConstPressureReactor(gas, volume = 1.0)

# Ajouter les objets "PFR" et "PSR" à l'objet "ReactorNet"
sim = ct.ReactorNet([pfr, psr])

# Définir un tableau pour enregistrer les résultats de la simulation
t_data = []
T_pfr = []
T_psr = []

# Exécuter la simulation en boucle jusqu'à ce que la durée de la simulation soit atteinte
while sim.time < t_max:
    # Faire avancer la simulation d'un pas de temps
    sim.advance(dt+sim.time)

    
    # Enregistrer les résultats de la simulation
    t_data.append(sim.time)
    T_pfr.append(pfr.T)
    T_psr.append(psr.T)

# Convertir les résultats en tableaux NumPy
t_data = np.array(t_data)
T_pfr = np.array(T_pfr)
T_psr = np.array(T_psr)
print(T_psr)