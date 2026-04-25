import os
from fonctions.load import load_transport_problem
from fonctions.print_matrix import print_matrix
from fonctions.total_cost import total_cost
from algorithmes.nord_ouest import nord_ouest_algo
from algorithmes.balas_hammer import balas_hammer_algo
from algorithmes.marche_pied_avec_potentiel import *

def main():
    run = True
    base_dir = os.path.dirname(os.path.abspath(__file__))

    while run:


        dir = os.path.join(base_dir, "ressources")  
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

        elif(algo_initial_proposition == 2):
            initial_matrix = balas_hammer_algo(cost_matrix, supply, demand)
            print("\n\nAvec l'algorithme Balais-Hammer, on obtient la proposition initiale suivante:\n")
            print_matrix(initial_matrix, supply, demand, "Proposition initiale")

        # On utilisera une matrice "brouillon" pour guider nos ajouts/supression d'arrêtes
        basis_matrix = [[1 if initial_matrix[i][j] > 0 else 0 for j in range(len(initial_matrix[0]))] for i in range(len(initial_matrix))]
        
        # On vérifie qu'il n'y a pas de cycle déja présent dans la proposition de transport initiale

        print("\nMaintenant que nous avons la proposition de transport initiale, nous allons l'optimiser avec la méthode du marche-pied avec potentiels.")
        print("Pour cela, il faut que la proposition soit non-dégénérée. Vérifions si elle possède un cycle initialement :")

        one_step_matrix = initial_matrix
        acyclic, cycle = is_acyclic(basis_matrix)

        while not acyclic:
            # Si la proposition initiale possède un cycle, on le maximise
            print("Il y a un cycle dans la proposition de transport initiale. Maximisons-le.")
            one_step_matrix, basis_matrix, _ = maximize_cycle(one_step_matrix, basis_matrix, cycle, None, cost_matrix)
            print("Un cycle a été supprimé. Vérifions s'il n'en reste pas.")
            acyclic, cycle = is_acyclic(basis_matrix)
        

        # Maintenant la proposition initiale est acyclique, on peu directement passer à l'étape suivante
        print("\n=> La proposition de transport initiale est acyclique. Vérifions qu'elle est connexe :")

        best_proposition = False
        while not best_proposition:

            # On vérifie si la proposition de transport est connexe

            connected, composants = is_connected(basis_matrix)

            # Si elle n'est pas connexe, il faut lui rajouter un certain nombre d'arrêtes
            if not connected:
                two_step_matrix = one_step_matrix
                excluded_edges = []

                # Pour chaque étape, on vérifie à la fois que la proposition est connexe et acyclique. On sort de la boucle seulement si les deux conditions sont vérifiées. 
                while not connected or not acyclic:
                    # On rend la proposition connexe
                    basis_matrix, entering_edge = make_connected(basis_matrix, cost_matrix, composants, excluded_edges)
                    
                    print("Maintenant une arrête à été ajouté entre deux sous graphes.\nVérifions que cette étape n'a pas créée de cycle :")
                    # On vérifie que la proposition est bien acyclique
                    acyclic, cycle = is_acyclic(basis_matrix)

                    if not acyclic:
                        print("Il y a un cycle dans la proposition de transport. Maximisons-le.")
                        # On enlève le cycle créé
                        three_step_matrix, basis_matrix, degenerate = maximize_cycle(two_step_matrix, basis_matrix, cycle, entering_edge, None)

                        # Si ce dernier cycle venait de l'arrête ajouté juste avant par make_connected, on backliste l'arrête et on l'enlêve de la proposition 
                        if degenerate:
                            excluded_edges.append(entering_edge)  # on blackliste
                            basis_matrix[entering_edge[0]][entering_edge[1]] = 0 
                        # Sinon, c'est que l'arrête ajouté a permise de faire avancer l'algorithme : on la garde et passe à l'étape suivante
                        else:
                            print("Désormais la proposition de transport est acyclique. Vérifions qu'elle est connexe :")
                            excluded_edges = []
                            connected, composants = is_connected(basis_matrix)
                            # Si la proposition n'est plus connexe on reboucle les algorithmes
                            if not connected:
                                two_step_matrix = three_step_matrix
                            else:
                                break

                    # Après avoir rajouté une arrête, on a vérifié que cet ajout n'avait pas créé de cycle. Ici c'est qu'il n'en a pas créé
                    else:
                        print("\n=> La proposition de transport est acyclique (l'ajout d'une arrête n'a pas créé de cycle).\nVérifons qu'elle est connexe")
                        connected, composants = is_connected(basis_matrix)
                        # Si la proposition est connexe et acyclique, on peu sortir du while (=> le graphe associé à la proposition est un arbre)
                        if connected:
                            three_step_matrix = two_step_matrix
                            break

            # On avait rendu la proposition acyclique. Si elle est déja connexe, on peu directement passer à l'étape des potentiels. 
            else:
                three_step_matrix = one_step_matrix
                print("La proposition de transport est connexe et acyclique. Son graphe biparti associé est donc un arbre.")

            # On calcul les coûts potentiels de chaque source et destinataire
            E_sources, E_targets = compute_potentials(basis_matrix, cost_matrix)

            # On calcul puis affiche les tables des coûts potentiels et marginaux.
            # Si coût marginal négatif il y a, alors le plus faible constitue l'arrête à ajouter 'best_edge' 
            best_edge = compute_and_print_marginal_costs(cost_matrix, basis_matrix, E_sources, E_targets, supply, demand)

            if best_edge == None:
                # Si aucune arrête améliorante existe, on a la proposition optimales ; on l'affiche
                print("\nA l'aide de la méthode du marche-pied avec potentiels, nous avons donc :\n")
                print_matrix(three_step_matrix, supply, demand, "Propostion optimale")
                print("\nLe cout total de cette proposition de transport est : ", float(total_cost(cost_matrix, three_step_matrix)))
                best_proposition = True
            
            else:
                # On ajoute l'arrête améliorante à la proposition de transport
                basis_matrix = add_entering_edge(basis_matrix, best_edge)
                # Comme la proposition de transport formait un arbre, cet ajout a forcément créé un cycle. On l'identifie.
                acyclic, cycle = is_acyclic(basis_matrix)
                # On maximise le cycle pour rendre la proposition de transport acyclique
                one_step_matrix, basis_matrix, _ = maximize_cycle(three_step_matrix, basis_matrix, cycle, best_edge, None)
                # Maintenant, on reboucle ces quelques dernière ligne : rendre la proposition non-dégénérée, puis calcul des coûts potentiels et marginaux. 
                




        answere = False
        while(not answere):
            user_said = input("\n\nVoulez-vous tester un  autre problème de transport ? (oui/non) : ")
            if user_said.lower() == "non":
                run = False
                answere = True
            elif user_said.lower() == "oui":
                answere = True
            else:
                print("Veuillez entrer une réponse valide !")
        
    


if __name__ == "__main__" :
    main()
