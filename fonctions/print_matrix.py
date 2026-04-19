def print_matrix(matrix, supply, demand, title):
    m, n = len(matrix), len(demand)
    col_w = 9
    table_w = col_w * n + n + 1

    # Titre
    print(" " *col_w + f"{title:^{table_w}}")

    # En-tête
    print(" "*(col_w+1) + "".join(f"{'D'+str(j+1):^{col_w}} " for j in range(n)))

    # Matrice
    sep = " "*col_w + "+" + (("-" * col_w + "+") * n)
    print(sep)

    for i in range(m):
        row = f"S{i+1} |" + "".join(f"{matrix[i][j]:^{col_w}}|" for j in range(n))
        print(" " * (col_w-3) + f"{row}  {supply[i]}")

    print(sep)
    print(" "*col_w + "".join(f" {demand[j]:^{col_w}}" for j in range(n)))


