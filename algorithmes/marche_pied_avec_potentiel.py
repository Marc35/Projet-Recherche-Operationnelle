from collections import deque

def is_acyclic(transport_matrix):
    """
    A l'aide d'un parcours en largeur (BFS), on vérifie qu'il n'y a pas de cycle dans la proposition
    S'il y a un cycle, le parcours s'arrête et le cycle est retourné
    """
    rows = len(transport_matrix)
    cols = len(transport_matrix[0])

    # Construction du graphe
    graph = {}
    for i in range(rows):
        for j in range(cols):
            if transport_matrix[i][j] > 0:
                u = (0, i)  # noeud offre
                v = (1, j)  # noeud demande
                graph.setdefault(u, []).append(v)
                graph.setdefault(v, []).append(u)

    visited = {}  # noeud => parent

    # BFS
    queue = deque()
    start = list(graph.keys())[0]
    queue.append(start)
    visited[start] = None  # le noeud de départ n'a pas de parent

    while queue:
        node = queue.popleft()

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                # Voisin non visité : on le marque et on retient son parent
                visited[neighbor] = node
                queue.append(neighbor)
            elif visited[node] != neighbor:
                # Voisin déjà visité et ce n'est pas le parent : il y a donc un cycle
                # On remonte le chemin pour reconstruire le cycle
                cycle = [node, neighbor]
                current = node
                while visited[current] is not None and visited[current] != neighbor:
                    current = visited[current]
                    cycle.append(current)
                cycle.reverse()

                readable = ["O"+str(n[1]+1) if n[0]==0 else "D"+str(n[1]+1) for n in cycle]
                print(f"Cycle détecté : {' -> '.join(readable)}")
                return False, cycle

    return True, []



def maximize_cycle(transport_matrix, cycle, entering_edge=None, cost_matrix=None):
    """
    Maximise le transport sur un cycle détecté.
    - entering_edge : arête ajoutée lors du marche-pied (toujours en "+")
    - cost_matrix   : utilisée pour choisir le bon sens sur un cycle initial (Proposition 1.1)
    """
    matrix = [row[:] for row in transport_matrix]

    # Reconstruction des arêtes du cycle avec leur signe
    edges = []
    for k in range(len(cycle) - 1):
        u = cycle[k]
        v = cycle[k + 1]
        i = u[1] if u[0] == 0 else v[1]
        j = v[1] if v[0] == 1 else u[1]
        sign = "+" if k % 2 == 0 else "-"
        edges.append((i, j, sign))

    if entering_edge is not None:
        # Cas marche-pied : la proposition de transport est cyclique après qu'une arrête est été rajouté
        # L'arrête entrant est toujours en "+"
        ei, ej = entering_edge
        for i, j, sign in edges:
            if i == ei and j == ej and sign == "-":
                edges = [(i, j, "-" if sign == "+" else "+") for i, j, sign in edges]
                break

    elif cost_matrix is not None:
        # Cas initiale : la proposition initiale de transport est cyclcique
        # On procède selon le signe du cout associé au cycle (Proposition 1.1)
        cout_cycle = sum(
            cost_matrix[i][j] * (1 if sign == "+" else -1)
            for i, j, sign in edges
        )
        print(f"\nCoût du cycle (sens actuel) = {cout_cycle}")
        if cout_cycle > 0:
            edges = [(i, j, "-" if sign == "+" else "+") for i, j, sign in edges]
            print("Sens inversé pour minimiser le coût total.")

    # Affichage des conditions
    print("\nConditions pour chaque case du cycle :")
    for i, j, sign in edges:
        print(f"  Case ({i+1}, {j+1}) [{sign}] : valeur actuelle = {matrix[i][j]}")

    # Theta = minimum des cases "-"
    minus_edges = [(i, j) for i, j, sign in edges if sign == "-"]
    theta = min(matrix[i][j] for i, j in minus_edges)
    print(f"\nTheta (valeur maximale transférable) = {theta}")

    # Application du theta
    for i, j, sign in edges:
        if sign == "+":
            matrix[i][j] += theta
        else:
            matrix[i][j] -= theta

    # Arêtes supprimées
    removed = [(i, j) for i, j, sign in edges if sign == "-" and matrix[i][j] == 0]
    print(f"\nArête(s) supprimée(s) : {['('+str(i+1)+', '+str(j+1)+')' for i, j in removed]}")

    degenerate = theta <= 1e-9
    return matrix, degenerate


def is_connected(transport_matrix):
    """
    A l'aide d'un parcours en largeur (BFS), test si la proposition est connexe
    """
    rows = len(transport_matrix)
    cols = len(transport_matrix[0])

    # Construction du graphe
    graph = {}
    for i in range(rows):
        for j in range(cols):
            if transport_matrix[i][j] > 0:
                u, v = (0, i), (1, j)
                graph.setdefault(u, []).append(v)
                graph.setdefault(v, []).append(u)

    visited = set()
    composantes = []

    # Parcours en largeur sur toutes les sommets
    for start in graph:
        # Si le sommets est déja dans ceux visité on le saute ; il fait déja partie d'un (sous) graphe 
        if start in visited:
            continue

        # On explore tout le chemin possible depuis la composante
        composante = []
        queue = deque([start])
        visited.add(start)

        while queue:
            node = queue.popleft()
            composante.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        composantes.append(composante)

    # S'il n'y a qu'un sous graphe, c'est donc qu'il n'y a qu'un seul graphe 
    if len(composantes) == 1:
        print("\n=> a proposition est connexe")
        return True, composantes
    else:
    # Sinon c'est qu'il y a plusieurs sous graphes (inaccessibles entre eux)
        print(f"\nLa proposition est non connexe ({len(composantes)} sous-graphes)\n")
        for k, comp in enumerate(composantes):
            offres   = ["O"+str(n[1]+1) for n in comp if n[0] == 0]
            demandes = ["D"+str(n[1]+1) for n in comp if n[0] == 1]
            print(f"  Sous-graphe {k+1} : Offres {offres} | Demandes {demandes}")
        return False, composantes
    



def make_connected(transport_matrix, cost_matrix, composantes, excluded_edges=[]):
    """
    Ajoute une seule arête epsilon reliant les deux composantes
    les moins chères à relier parmi toutes les paires possibles.
    Retourne (matrix, (i, j)) : la matrice modifiée et l'arête ajoutée.
    """
    matrix = [row[:] for row in transport_matrix]
    EPSILON = 1e-9

    best = None  # (coût, i, j, idx_a, idx_b)

    # On cherche le meilleur lien global entre toutes les paires de composantes
    for a in range(len(composantes)):
        for b in range(a + 1, len(composantes)):
            comp_a = composantes[a]
            comp_b = composantes[b]

            offres_a   = [n[1] for n in comp_a if n[0] == 0]
            demandes_a = [n[1] for n in comp_a if n[0] == 1]
            offres_b   = [n[1] for n in comp_b if n[0] == 0]
            demandes_b = [n[1] for n in comp_b if n[0] == 1]

            for i in offres_a:
                for j in demandes_b:
                    cout = cost_matrix[i][j]
                    if (i, j) not in excluded_edges:
                        if best is None or cout < best[0]:
                            best = (cout, i, j, a + 1, b + 1)

            for i in offres_b:
                for j in demandes_a:
                    cout = cost_matrix[i][j]
                    if (i, j) not in excluded_edges:
                        if best is None or cout < best[0]:
                            best = (cout, i, j, a + 1, b + 1)

    _, i, j, idx_a, idx_b = best
    matrix[i][j] = EPSILON
    print(f"\n=> Epsilon ajouté en case ({i+1}, {j+1}) [coût = {cost_matrix[i][j]}] pour relier les sous-graphes {idx_a} et {idx_b}")

    return matrix, (i, j)




def compute_potentials(transport_matrix, cost_matrix):
    """
    Calcule les potentiels de chaque sommet.
    On fixe arbitrairement E(S1) = 0 (le premier noeud offre).
    Pour chaque arête (i,j) utilisée : E(i) - E(j) = c(i,j)
    """
    rows = len(transport_matrix)
    cols = len(transport_matrix[0])

    # Initialisation : None => potentiel pas encore calculé
    E_sources = [None] * rows   # E(Si)
    E_targets = [None] * cols   # E(Cj)

    # On fixe arbitrairement E(S1) = 0
    E_sources[0] = 0

    # On parcours et reparcours la table tant qu'il y a des choses à calculer
    # Si une itération ne change rien, on sort du while : c'est que tout les potentiels possible de calculer ont été calculés
    changed = True
    while changed:
        changed = False
        for i in range(rows):
            for j in range(cols):
                # On calcul les potentiels à partir du graphe associé à la proposition de transport 
                if transport_matrix[i][j] > 0:
                    # On utilse la formule E(i) - E(j) = c(i,j)
                    if E_sources[i] is not None and E_targets[j] is None:
                        E_targets[j] = E_sources[i] - cost_matrix[i][j]
                        changed = True
                    elif E_targets[j] is not None and E_sources[i] is None:
                        E_sources[i] = E_targets[j] + cost_matrix[i][j]
                        changed = True

    # Affichage des potentiels précédemment calculés
    print("\nPotentiels calculés (avec E(S1) = 0) :")
    for i in range(rows):
        print(f"  E(S{i+1}) = {E_sources[i]}")
    for j in range(cols):
        print(f"  E(C{j+1}) = {E_targets[j]}")

    return E_sources, E_targets




def compute_and_print_marginal_costs(cost_matrix, transport_matrix, E_sources, E_targets, supply, demand):
    """
    Calcule et affiche les coûts potentiels et marginaux.
    Retourne la meilleure arête améliorante (coût marginal le plus négatif) ou None.
    """
    rows = len(cost_matrix)
    cols = len(cost_matrix[0])
    col_w = 9
    EPSILON = 1e-9

    # Calcul de la table des coûts potentiels : E(i) - E(j)
    potential_costs = [[E_sources[i] - E_targets[j] for j in range(cols)] for i in range(rows)]

    # Calcul de la table des coûts marginaux : c(i,j) - (E(i) - E(j))
    marginal_costs = [[cost_matrix[i][j] - potential_costs[i][j] for j in range(cols)] for i in range(rows)]

    # Affichage des coûts potentiels
    table_w = col_w * cols + cols + 1
    print()
    print(" " * col_w + f"{'Coûts potentiels':^{table_w}}")
    print(" " * (col_w + 1) + "".join(f"{'D'+str(j+1):^{col_w}} " for j in range(cols)))
    sep = " " * col_w + "+" + (("-" * col_w + "+") * cols)
    print(sep)
    for i in range(rows):
        row = f"S{i+1} |" + "".join(f"{potential_costs[i][j]:^{col_w}}|" for j in range(cols))
        print(" " * (col_w - 3) + f"{row}  {supply[i]}")
    print(sep)
    print(" " * col_w + "".join(f" {demand[j]:^{col_w}}" for j in range(cols)))

    print()

    # Affichage des coûts marginaux
    print(" " * col_w + f"{'Coûts marginaux':^{table_w}}")
    print(" " * (col_w + 1) + "".join(f"{'D'+str(j+1):^{col_w}} " for j in range(cols)))
    print(sep)
    for i in range(rows):
        row = f"S{i+1} |" + "".join(f"{marginal_costs[i][j]:^{col_w}}|" for j in range(cols))
        print(" " * (col_w - 3) + f"{row}  {supply[i]}")
    print(sep)
    print(" " * col_w + "".join(f" {demand[j]:^{col_w}}" for j in range(cols)))

    # Détection de la meilleure arête améliorante (coût marginal le plus négatif)
    # On ignore les arêtes déjà utilisées dans la proposition (coût marginal = 0 par définition)
    best = None
    best_cost = 0  # on cherche strictement négatif
    for i in range(rows):
        for j in range(cols):
            if transport_matrix[i][j] <= EPSILON and marginal_costs[i][j] < best_cost:
                best_cost = marginal_costs[i][j]
                best = (i, j)

    if best is not None:
        print(f"\nMeilleure arête améliorante : (S{best[0]+1}, D{best[1]+1}) [coût marginal = {best_cost}]")
    else:
        print("\n=> Tous les coûts marginaux sont positifs : la proposition est optimale")

    return best



def add_entering_edge(transport_matrix, entering_edge):
    """
    Ajoute l'arête améliorante à la proposition de transport
    Cet ajout se fait à l'aide du quantité très faible epsilon (temporaire)
    Grâce à celui-ci, l'arrête ajouté fera forcément un cycle, qui sera donc détecté par is_acyclic
    """
    EPSILON = 1e-9
    matrix = [row[:] for row in transport_matrix]
    i, j = entering_edge
    if matrix[i][j] != 0:
        print(f"Attention : l'arête ({i+1}, {j+1}) est déjà utilisée.")
    else:
        matrix[i][j] = EPSILON
        print(f"Arête ajoutée : (S{i+1}, D{j+1})")
    return matrix
