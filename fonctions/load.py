def load_transport_problem(filename):

    with open(filename, "r", encoding="utf-8") as f: 
        lines = f.read().splitlines()
    m, n = map(int, lines[0].split())

    cost_matrix = []
    supply = []

    for i in range(1, m + 1):
        values = list(map(int, lines[i].split()))
        cost_matrix.append(values[:n])   # les n premiers = coûts
        supply.append(values[n])         # le dernier = contrainte provision

    # Contraintes de commandes
    demand = list(map(int, lines[m + 1].split()))

    return cost_matrix, supply, demand


