import time
import random
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from algorithmes.nord_ouest import nord_ouest_algo
from algorithmes.balas_hammer import balas_hammer_algo
from algorithmes.marche_pied_avec_potentiel import *
import matplotlib.pyplot as plt
import numpy as np

def generate_random_problem(n):
    """
    Génère un problème de transport aléatoire de taille n x n.
    
    - Les coûts a[i][j] sont des entiers aléatoires entre 1 et 100.
    - Une matrice temp[i][j] de taille n x n est générée avec des entiers
      aléatoires entre 1 et 100, puis :
        Pi  = somme des temp[i][j] sur j  (provisions)
        Cj  = somme des temp[i][j] sur i  (commandes)
    Ainsi sum(Pi) = sum(Cj) = sum(temp) : le problème est toujours équilibré.
    """

    # Matrice des coûts : entiers aléatoires entre 1 et 100
    cost_matrix = [
        [random.randint(1, 100) for _ in range(n)]
        for _ in range(n)
    ]

    # Matrice temp pour générer provisions et commandes équilibrées
    temp = [
        [random.randint(1, 100) for _ in range(n)]
        for _ in range(n)
    ]

    # Pi = somme de la ligne i de temp
    supply = [sum(temp[i]) for i in range(n)]

    # Cj = somme de la colonne j de temp
    demand = [sum(temp[i][j] for i in range(n)) for j in range(n)]

    return cost_matrix, supply, demand



def run_marche_pied(initial_matrix, cost_matrix):
    """
    Exécute le marche-pied avec potentiel sans aucun print.
    Retourne la matrice optimale.
    """
    basis_matrix = [[1 if initial_matrix[i][j] > 0 else 0
                     for j in range(len(initial_matrix[0]))]
                     for i in range(len(initial_matrix))]

    one_step_matrix = initial_matrix
    acyclic, cycle = is_acyclic(basis_matrix)
    while not acyclic:
        one_step_matrix, basis_matrix, _ = maximize_cycle(one_step_matrix, basis_matrix, cycle, None, cost_matrix)
        acyclic, cycle = is_acyclic(basis_matrix)

    best_proposition = False
    while not best_proposition:
        connected, composants = is_connected(basis_matrix)

        if not connected:
            two_step_matrix = one_step_matrix
            excluded_edges = []
            while not connected or not acyclic:
                basis_matrix, entering_edge = make_connected(basis_matrix, cost_matrix, composants, excluded_edges)
                acyclic, cycle = is_acyclic(basis_matrix)
                if not acyclic:
                    three_step_matrix, basis_matrix, degenerate = maximize_cycle(two_step_matrix, basis_matrix, cycle, entering_edge, None)
                    if degenerate:
                        excluded_edges.append(entering_edge)
                        basis_matrix[entering_edge[0]][entering_edge[1]] = 0
                    else:
                        excluded_edges = []
                        connected, composants = is_connected(basis_matrix)
                        if not connected:
                            two_step_matrix = three_step_matrix
                        else:
                            break
                else:
                    connected, composants = is_connected(basis_matrix)
                    if connected:
                        three_step_matrix = two_step_matrix
                        break
        else:
            three_step_matrix = one_step_matrix

        E_sources, E_targets = compute_potentials(basis_matrix, cost_matrix)
        best_edge = compute_and_print_marginal_costs(cost_matrix, basis_matrix, E_sources, E_targets,
                                                      [0]*len(cost_matrix), [0]*len(cost_matrix[0]))

        if best_edge is None:
            best_proposition = True
        else:
            basis_matrix = add_entering_edge(basis_matrix, best_edge)
            acyclic, cycle = is_acyclic(basis_matrix)
            one_step_matrix, basis_matrix, _ = maximize_cycle(three_step_matrix, basis_matrix, cycle, best_edge, None)

    return three_step_matrix


def mesure_temps(n_values, nb_repetitions=100):
    """
    Pour chaque n dans n_values, répète nb_repetitions fois la mesure de :
    - theta_NO : temps de Nord-Ouest
    - theta_BH : temps de Balas-Hammer
    - t_NO     : temps du marche-pied depuis Nord-Ouest
    - t_BH     : temps du marche-pied depuis Balas-Hammer
    Retourne un dictionnaire de résultats.
    """
    resultats = {n: {"theta_NO": [], "theta_BH": [], "t_NO": [], "t_BH": []} for n in n_values}

    for n in n_values:
        print(f"\n=== n = {n} ===")
        for rep in range(nb_repetitions):
            if rep % 10 == 0:
                print(f"  Répétition {rep+1}/{nb_repetitions}...")

            cost_matrix, supply, demand = generate_random_problem(n)

            # --- Mesure theta_NO ---
            t0 = time.perf_counter()
            initial_NO = nord_ouest_algo(cost_matrix, supply, demand)
            theta_NO = time.perf_counter() - t0

            # --- Mesure theta_BH ---
            t0 = time.perf_counter()
            initial_BH = balas_hammer_algo(cost_matrix, supply, demand)
            theta_BH = time.perf_counter() - t0

            # --- Mesure t_NO ---
            t0 = time.perf_counter()
            run_marche_pied_silencieux(initial_NO, cost_matrix)
            t_NO = time.perf_counter() - t0

            # --- Mesure t_BH ---
            t0 = time.perf_counter()
            run_marche_pied_silencieux(initial_BH, cost_matrix)
            t_BH = time.perf_counter() - t0

            resultats[n]["theta_NO"].append(theta_NO)
            resultats[n]["theta_BH"].append(theta_BH)
            resultats[n]["t_NO"].append(t_NO)
            resultats[n]["t_BH"].append(t_BH)

    return resultats



def run_marche_pied_silencieux(initial_matrix, cost_matrix):
    """Redirige stdout vers /dev/null pendant l'exécution pour supprimer les prints."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            result = run_marche_pied(initial_matrix, cost_matrix)
        finally:
            sys.stdout = old_stdout
    return result




def tracer_graphiques(resultats, n_values):
    """
    Trace les 6 nuages de points demandés + les enveloppes supérieures.
    """

    # Préparation des données
    theta_NO_max, theta_BH_max = [], []
    t_NO_max,     t_BH_max     = [], []
    sum_NO_max,   sum_BH_max   = [], []

    for n in n_values:
        theta_NO = resultats[n]["theta_NO"]
        theta_BH = resultats[n]["theta_BH"]
        t_NO     = resultats[n]["t_NO"]
        t_BH     = resultats[n]["t_BH"]
        sum_NO   = [theta_NO[k] + t_NO[k] for k in range(len(theta_NO))]
        sum_BH   = [theta_BH[k] + t_BH[k] for k in range(len(theta_BH))]

        theta_NO_max.append(max(theta_NO))
        theta_BH_max.append(max(theta_BH))
        t_NO_max.append(max(t_NO))
        t_BH_max.append(max(t_BH))
        sum_NO_max.append(max(sum_NO))
        sum_BH_max.append(max(sum_BH))

    configs = [
        ("theta_NO(n) — Nord-Ouest",         "theta_NO", None,      "blue"),
        ("theta_BH(n) — Balas-Hammer",        "theta_BH", None,      "orange"),
        ("t_NO(n) — Marche-pied depuis NO",   "t_NO",     None,      "green"),
        ("t_BH(n) — Marche-pied depuis BH",   "t_BH",     None,      "red"),
        ("(theta_NO + t_NO)(n)",              "theta_NO", "t_NO",    "purple"),
        ("(theta_BH + t_BH)(n)",              "theta_BH", "t_BH",    "brown"),
    ]
    maxs = [theta_NO_max, theta_BH_max, t_NO_max, t_BH_max, sum_NO_max, sum_BH_max]

    fig, axes = plt.subplots(3, 2, figsize=(14, 16))
    axes = axes.flatten()

    for idx, ((titre, key1, key2, couleur), enveloppe) in enumerate(zip(configs, maxs)):
        ax = axes[idx]

        # Nuage de points
        for n in n_values:
            vals1 = resultats[n][key1]
            if key2 is not None:
                vals2 = resultats[n][key2]
                valeurs = [vals1[k] + vals2[k] for k in range(len(vals1))]
            else:
                valeurs = vals1
            ax.scatter([n] * len(valeurs), valeurs, color=couleur, alpha=0.3, s=8)

        # Enveloppe supérieure
        ax.plot(n_values, enveloppe, color="black", linewidth=2, label="Enveloppe supérieure")

        ax.set_title(titre, fontsize=11)
        ax.set_xlabel("n")
        ax.set_ylabel("Temps (s)")
        ax.legend()
        ax.set_xscale("log")   # échelle log sur x pour mieux voir les grandes valeurs
        ax.set_yscale("log")   # échelle log sur y pour identifier le type de complexité

    plt.tight_layout()
    plt.savefig("complexite_nuages.png", dpi=150)
    plt.show()
    print("Graphique sauvegardé : complexite_nuages.png")


def tracer_comparaison(resultats, n_values):
    """
    Trace le rapport (theta_NO + t_NO) / (theta_BH + t_BH) en fonction de n.
    """
    ratios_max = []

    for n in n_values:
        theta_NO = resultats[n]["theta_NO"]
        theta_BH = resultats[n]["theta_BH"]
        t_NO     = resultats[n]["t_NO"]
        t_BH     = resultats[n]["t_BH"]

        ratios = [
            (theta_NO[k] + t_NO[k]) / (theta_BH[k] + t_BH[k])
            for k in range(len(theta_NO))
        ]
        ratios_max.append(max(ratios))

        plt.scatter([n] * len(ratios), ratios, color="blue", alpha=0.3, s=8)

    plt.plot(n_values, ratios_max, color="black", linewidth=2, label="Maximum")
    plt.axhline(y=1, color="red", linestyle="--", label="Ratio = 1 (égalité)")
    plt.xscale("log")
    plt.xlabel("n")
    plt.ylabel("(θNO + tNO) / (θBH + tBH)")
    plt.title("Comparaison NO vs BH dans le pire des cas")
    plt.legend()
    plt.tight_layout()
    plt.savefig("complexite_comparaison.png", dpi=150)
    plt.show()
    print("Graphique sauvegardé : complexite_comparaison.png")