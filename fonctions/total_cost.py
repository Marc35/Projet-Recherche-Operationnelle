def total_cost(cost_matrix, transport_proposition):
    """
    Calcul le cout total d'une proposition de transport, avec la matrice de la proposition et la matrice des couts
    """
    return sum(
        cost_matrix[i][j] * transport_proposition[i][j]
        for i in range(len(cost_matrix))
        for j in range(len(cost_matrix[0]))
    )
