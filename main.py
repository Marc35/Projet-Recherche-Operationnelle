import os
from fonctions.load import load_transport_problem
from fonctions.print_matrix import print_matrix
from algorithmes.nord_ouest import nord_ouest_algo

def main():
    run = True
    while run:


        dir = "ressources"
        found = False
        while not found:
            try:
                problem_number = input("Choisir le numéro du problème à tester : ")
                problem_number = str(int(problem_number.strip()))
                file = os.path.join(dir, f"proposition_{problem_number}.txt")
                cost_matrix, supply, demand = load_transport_problem(file)
                found = True
            except FileNotFoundError:
                print(f"Le problème de transport numéro '{problem_number}' n'a pas été trouvé dans le dossier '{dir}'. Veuillez réessayer.")
            except ValueError:
                print("Erreur : veuillez entrer un numéro valide.")


            print("\n\nVoici la matrice des couts initiaux du problème choisis :")
            print_matrix(cost_matrix, supply, demand, "Matrice des couts")
                
            print("\n\nQuel algorithme voulez-vous exécuter pour avoir une proposition initiale ? \n1 - Algorithme Nord-Ouest\n2 - Algorithme Balas-Hammer")
            while True:
                try:    
                    algo_initial_proposition = int(input("Algorithme n° : ").strip())
                    if (algo_initial_proposition not in [1, 2]):
                        print(f"Numéro invalide. Choisir entre 1 (Nord-Ouest) et 2 (Balas-Hammer)")
                        continue
                    break
                except ValueError:
                    print("Erreur : veuillez entrer un numéro valide.")

            if(algo_initial_proposition == 1):
                initial_matrix = nord_ouest_algo(cost_matrix, supply, demand)
                print("\n\nAvec l'algorithme Nord-Ouest, on obtient la proposition initiale suivante:\n")
                print_matrix(initial_matrix, supply, demand, "Proposition initiale")






        print("\n\nVoulez-vous tester un  autre problème de transport ? (oui/non) : ", end="")
        if input().lower() != "non":
            run = True
        else:
            run = False
    


if __name__ == "__main__" :
    main()