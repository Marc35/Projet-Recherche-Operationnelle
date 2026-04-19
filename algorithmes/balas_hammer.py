def balas_hammer_algo(cost_matrix, supply, demand):
    m, n = len(cost_matrix), len(cost_matrix[0])
    transport = [[0] * n for _ in range(m)]

    s = supply[:]
    d = demand[:]

    rows_done = [False] * m
    cols_done = [False] * n

    def get_penalty_row(i):
        costs = sorted(cost_matrix[i][j] for j in range(n) if not cols_done[j])
        if len(costs) >= 2:
            return costs[1] - costs[0]
        return costs[0] if costs else -1

    def get_penalty_col(j):
        costs = sorted(cost_matrix[i][j] for i in range(m) if not rows_done[i])
        if len(costs) >= 2:
            return costs[1] - costs[0]
        return costs[0] if costs else -1

    while True:
        # Vérifier s'il reste des lignes et colonnes actives
        active_rows = [i for i in range(m) if not rows_done[i]]
        active_cols = [j for j in range(n) if not cols_done[j]]
        if not active_rows or not active_cols:
            break

        # Calcul des pénalités
        row_penalties = {i: get_penalty_row(i) for i in active_rows}
        col_penalties = {j: get_penalty_col(j) for j in active_cols}

        max_row_penalty = max(row_penalties.values())
        max_col_penalty = max(col_penalties.values())

        # Affichage des pénalités maximales
        max_rows = [i for i, p in row_penalties.items() if p == max_row_penalty]
        max_cols = [j for j, p in col_penalties.items() if p == max_col_penalty]

        print(f"Pénalités lignes  : { {f'S{i+1}': row_penalties[i] for i in active_rows} }")
        print(f"Pénalités colonnes: { {f'D{j+1}': col_penalties[j] for j in active_cols} }")
        if max_row_penalty >= max_col_penalty:
            print(f"Pénalité max : lignes {[f'S{i+1}' for i in max_rows]} avec {max_row_penalty}")
        else:
            print(f"Pénalité max : colonnes {[f'D{j+1}' for j in max_cols]} avec {max_col_penalty}")

        # Choix de l'arête à remplir
        if max_row_penalty >= max_col_penalty:
            i = max_rows[0]
            # Coût minimal sur la ligne i
            j = min(active_cols, key=lambda j: cost_matrix[i][j])
        else:
            j = max_cols[0]
            # Coût minimal sur la colonne j
            i = min(active_rows, key=lambda i: cost_matrix[i][j])

        # Allocation
        qty = min(s[i], d[j])
        transport[i][j] = qty
        s[i] -= qty
        d[j] -= qty

        print(f"Arête choisie : P{i+1} -> C{j+1} = {qty}\n")

        # Désactiver ligne ou colonne épuisée
        if s[i] == 0:
            rows_done[i] = True
        if d[j] == 0:
            cols_done[j] = True

    return transport