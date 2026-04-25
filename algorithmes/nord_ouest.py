def nord_ouest_algo(cost_matrix, supply, demand):
    """"
    Application de l'algorithme Nord-Ouest : 
    - On créer un copie des matrices de provisions et demandes
    - En maximisant toujours le coin 'nord-ouest', on remplie la proposition de transport 
    - A chaque étape on décrémente les copies des provisions et demandes pour actualiser l'avancée de la proposition de transport
    - Si une ligne/colonne n'a plus de provisions/demandes, on passe à celle d'après
    """
    m, n = len(cost_matrix), len(cost_matrix[0])
    transport = [[0] * n for _ in range(m)]
    
    # Copies pour ne pas modifier les originaux
    s = supply[:]
    d = demand[:]
    
    # On part de (0, 0) => nord-ouest de la matrice
    i, j = 0, 0
    while i < m and j < n:
        # On prend le minimum entre les provisions et commandes de la case concerné
        qty = min(s[i], d[j])
        # On l'asigne à la case de la proposition
        transport[i][j] = qty
        # On enlève ce qu'on vient d'assigner de ce qu'il reste encore (en provision et commande)
        s[i] -= qty
        d[j] -= qty
        # Si la provision/commande est à 0, on passe à celle d'après
        if s[i] == 0 and d[j] == 0:
            i += 1
            j += 1
        elif s[i] == 0:
            i += 1
        else:
            j += 1
    
    return transport
