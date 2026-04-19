def nord_ouest_algo(cost_matrix, supply, demand):
    m, n = len(cost_matrix), len(cost_matrix[0])
    transport = [[0] * n for _ in range(m)]
    
    # Copies pour ne pas modifier les originaux
    s = supply[:]
    d = demand[:]
    
    i, j = 0, 0
    while i < m and j < n:
        qty = min(s[i], d[j])
        transport[i][j] = qty
        s[i] -= qty
        d[j] -= qty
        
        if s[i] == 0 and d[j] == 0:
            i += 1
            j += 1
        elif s[i] == 0:
            i += 1
        else:
            j += 1
    
    return transport