"""
generate_traces.py
------------------
Génère automatiquement les 24 fichiers de trace d'exécution :
  - 12 problèmes x 2 algorithmes (Nord-Ouest et Balas-Hammer)

Les fichiers sont sauvegardés dans le dossier 'traces/' à la racine du projet.
Nommage : {GROUPE}-{EQUIPE}-trace{N}-{no|bh}.txt

Usage : python generate_traces.py
"""

import os
import sys

# ================================================================
#  CONFIGURATION — À ADAPTER AVANT DE LANCER
# ================================================================
GROUPE = "7"   # Remplacer par votre numéro de groupe
EQUIPE = "1"   # Remplacer par votre numéro d'équipe
# ================================================================

from fonctions.load import load_transport_problem
from fonctions.print_matrix import print_matrix
from fonctions.total_cost import total_cost
from algorithmes.nord_ouest import nord_ouest_algo
from algorithmes.balas_hammer import balas_hammer_algo
from algorithmes.marche_pied_avec_potentiel import *


def resoudre_probleme(cost_matrix, supply, demand, initial_matrix, algo_name):
    """
    Exécute le marche-pied complet depuis une proposition initiale.
    Tous les prints vont dans le fichier de trace (stdout redirigé).
    """

    print(f"\nAvec l'algorithme {algo_name}, on obtient la proposition initiale suivante:\n")
    print_matrix(initial_matrix, supply, demand, "Proposition initiale")

    basis_matrix = [[1 if initial_matrix[i][j] > 0 else 0
                     for j in range(len(initial_matrix[0]))]
                     for i in range(len(initial_matrix))]

    print("\nMaintenant que nous avons la proposition de transport initiale, nous allons l'optimiser avec la méthode du marche-pied avec potentiels.")
    print("Pour cela, il faut que la proposition soit non-dégénérée. Vérifions si elle possède un cycle initialement :")

    one_step_matrix = initial_matrix
    acyclic, cycle = is_acyclic(basis_matrix)

    while not acyclic:
        print("Il y a un cycle dans la proposition de transport initiale. Maximisons-le.")
        one_step_matrix, basis_matrix, _ = maximize_cycle(one_step_matrix, basis_matrix, cycle, None, cost_matrix)
        print("Un cycle a été supprimé. Vérifions s'il n'en reste pas.")
        acyclic, cycle = is_acyclic(basis_matrix)

    print("\n=> La proposition de transport initiale est acyclique. Vérifions qu'elle est connexe :")

    best_proposition = False
    while not best_proposition:

        connected, composants = is_connected(basis_matrix)

        if not connected:
            two_step_matrix = one_step_matrix
            excluded_edges = []

            while not connected or not acyclic:
                basis_matrix, entering_edge = make_connected(basis_matrix, cost_matrix, composants, excluded_edges)

                print("Maintenant une arrête à été ajouté entre deux sous graphes.\nVérifions que cette étape n'a pas créée de cycle :")
                acyclic, cycle = is_acyclic(basis_matrix)

                if not acyclic:
                    print("Il y a un cycle dans la proposition de transport. Maximisons-le.")
                    three_step_matrix, basis_matrix, degenerate = maximize_cycle(two_step_matrix, basis_matrix, cycle, entering_edge, None)

                    if degenerate:
                        excluded_edges.append(entering_edge)
                        basis_matrix[entering_edge[0]][entering_edge[1]] = 0
                    else:
                        print("Désormais la proposition de transport est acyclique. Vérifions qu'elle est connexe :")
                        excluded_edges = []
                        connected, composants = is_connected(basis_matrix)
                        if not connected:
                            two_step_matrix = three_step_matrix
                        else:
                            break
                else:
                    print("\n=> La proposition de transport est acyclique (l'ajout d'une arrête n'a pas créé de cycle).\nVérifons qu'elle est connexe")
                    connected, composants = is_connected(basis_matrix)
                    if connected:
                        three_step_matrix = two_step_matrix
                        break
        else:
            three_step_matrix = one_step_matrix
            print("La proposition de transport est connexe et acyclique. Son graphe biparti associé est donc un arbre.")

        E_sources, E_targets = compute_potentials(basis_matrix, cost_matrix)
        best_edge = compute_and_print_marginal_costs(cost_matrix, basis_matrix, E_sources, E_targets, supply, demand)

        if best_edge is None:
            print("\nA l'aide de la méthode du marche-pied avec potentiels, nous avons donc :\n")
            print_matrix(three_step_matrix, supply, demand, "Proposition optimale")
            print("\nLe cout total de cette proposition de transport est : ", float(total_cost(cost_matrix, three_step_matrix)))
            best_proposition = True
        else:
            basis_matrix = add_entering_edge(basis_matrix, best_edge)
            acyclic, cycle = is_acyclic(basis_matrix)
            one_step_matrix, basis_matrix, _ = maximize_cycle(three_step_matrix, basis_matrix, cycle, best_edge, None)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ressources_dir = os.path.join(base_dir, "ressources")
    output_dir = os.path.join(base_dir, "traces")
    os.makedirs(output_dir, exist_ok=True)

    algos = [
        (1, "Nord-Ouest", "no"),
        (2, "Balas-Hammer", "bh"),
    ]

    for probleme in range(1, 13):
        file = os.path.join(ressources_dir, f"proposition_{probleme}.txt")
        cost_matrix, supply, demand = load_transport_problem(file)

        for algo_num, algo_name, suffix in algos:
            nom_fichier = f"{GROUPE}-{EQUIPE}-trace{probleme}-{suffix}.txt"
            chemin = os.path.join(output_dir, nom_fichier)

            print(f"Génération de {nom_fichier}...")

            with open(chemin, "w", encoding="utf-8") as f:
                old_stdout = sys.stdout
                sys.stdout = f

                print(f"Voici la matrice des couts initiaux du problème {probleme} :")
                print_matrix(cost_matrix, supply, demand, "Matrice des couts")

                if algo_num == 1:
                    initial_matrix = nord_ouest_algo(cost_matrix, supply, demand)
                else:
                    initial_matrix = balas_hammer_algo(cost_matrix, supply, demand)

                resoudre_probleme(cost_matrix, supply, demand, initial_matrix, algo_name)

                sys.stdout = old_stdout

            print(f"  => Sauvegardé : {chemin}")

    print(f"\n✓ Toutes les traces ont été générées dans le dossier '{output_dir}/'")


if __name__ == "__main__":
    main()