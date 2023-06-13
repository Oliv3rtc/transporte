import numpy as np
import copy
from collections import Counter

INF = 10**3


def findDiff(grid):
    rowDiff = []
    colDiff = []
    for i in range(len(grid)):
        arr = grid[i][:]
        arr.sort()
        rowDiff.append(arr[1] - arr[0])
    col = 0
    while col < len(grid[0]):
        arr = []
        for i in range(len(grid)):
            arr.append(grid[i][col])
        arr.sort()
        col += 1
        colDiff.append(arr[1] - arr[0])
    return rowDiff, colDiff


def minGrid(grid, ignored_row, ignored_col):
    minValue = INF
    minPos = (0, 0)

    for i in range(0, len(grid)):
        if i in ignored_row:
            continue
        for j in range(0, len(grid[i])):
            if j in ignored_col:
                continue

            if grid[i][j] < minValue:
                minValue = grid[i][j]
                minPos = (i, j)

    return minPos


class Transporte:
    def __init__(self, grid, supply, demand):
        t_supply = sum(supply)
        t_demand = sum(demand)

        if t_supply < t_demand:
            supply.append(t_demand - t_supply)
            grid.append([0] * len(demand))
        elif t_demand < t_supply:
            demand.append(t_supply - t_demand)
            for row in grid:
                row.append(0)

        self.grid = grid[:]
        self.supply = supply[:]
        self.demand = demand[:]
        self.bfs = []

        self.bfs = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]

    def northwestCorner(self):
        startR = 0  # start row
        startC = 0  # start col
        ans = 0

        while startR != len(self.grid) and startC != len(self.grid[0]):
            if self.supply[startR] <= self.demand[startC]:
                self.bfs[startR][startC] = self.supply[startR]
                ans += self.supply[startR] * self.grid[startR][startC]
                self.demand[startC] -= self.supply[startR]
                startR += 1
            else:
                self.bfs[startR][startC] = self.demand[startC]
                ans += self.demand[startC] * self.grid[startR][startC]
                self.supply[startR] -= self.demand[startC]
                startC += 1
        print("Solucao inicial factivel \n", np.matrix(self.bfs), ans)

    def leastCost(self):
        ignored_row = []
        ignored_col = []
        ans = 0
        cloneSupply = self.supply
        cloneDemand = self.demand

        while len(ignored_row) != len(self.supply) and len(ignored_col) != len(
            self.demand
        ):
            minPos = minGrid(self.grid, ignored_row, ignored_col)

            tmpSupply = cloneSupply[minPos[0]]
            tmpDemand = cloneDemand[minPos[1]]

            min_ = min(tmpSupply, tmpDemand)

            self.bfs[minPos[0]][minPos[1]] = min_
            cloneSupply[minPos[0]] -= min_
            cloneDemand[minPos[1]] -= min_

            ans += min_ * self.grid[minPos[0]][minPos[1]]

            if cloneSupply[minPos[0]] == 0:
                ignored_row.append(minPos[0])

            if cloneDemand[minPos[1]] == 0:
                ignored_col.append(minPos[1])

        print("Solucao inicial factivel \n", np.matrix(self.bfs), ans)

    def vogel(self):
        grid_bkp = copy.deepcopy(self.grid)
        demand_bkp = copy.deepcopy(self.demand)
        supply_bkp = copy.deepcopy(self.supply)

        n = len(self.grid)
        m = len(self.grid[0])
        ans = 0

        while max(self.supply) != 0 or max(self.demand) != 0:
            row, col = findDiff(self.grid)
            maxi1 = max(row)
            maxi2 = max(col)

            if maxi1 >= maxi2:
                for ind, val in enumerate(row):
                    if val == maxi1:
                        mini1 = min(self.grid[ind])
                        for ind2, val2 in enumerate(self.grid[ind]):
                            if val2 == mini1:
                                mini2 = min(self.supply[ind], self.demand[ind2])
                                self.bfs[ind][ind2] = mini2
                                ans += mini2 * mini1
                                self.supply[ind] -= mini2
                                self.demand[ind2] -= mini2
                                if self.demand[ind2] == 0:
                                    for r in range(n):
                                        self.grid[r][ind2] = INF
                                else:
                                    self.grid[ind] = [INF for i in range(m)]
                                break
                        break
            else:
                for ind, val in enumerate(col):
                    if val == maxi2:
                        mini1 = INF
                        for j in range(n):
                            mini1 = min(mini1, self.grid[j][ind])

                        for ind2 in range(n):
                            val2 = self.grid[ind2][ind]
                            if val2 == mini1:
                                mini2 = min(self.supply[ind2], self.demand[ind])
                                self.bfs[ind2][ind] = mini2
                                ans += mini2 * mini1
                                self.supply[ind2] -= mini2
                                self.demand[ind] -= mini2
                                if self.demand[ind] == 0:
                                    for r in range(n):
                                        self.grid[r][ind] = INF
                                else:
                                    self.grid[ind2] = [INF for i in range(m)]
                                break
                        break

        self.grid = grid_bkp
        self.supply = supply_bkp
        self.demand = demand_bkp
        print("Solucao inicial factivel \n", np.matrix(self.bfs), ans)

    def findOptimal(self):
        C = np.copy(self.grid)
        X = np.copy(self.bfs)

        n, m = C.shape

        while True:
            u = np.array([np.nan] * n)
            v = np.array([np.nan] * m)
            S = np.zeros((n, m))

            _x, _y = np.where(X > 0)
            nonzero = list(zip(_x, _y))
            f = nonzero[0][0]
            u[f] = 0

            while any(np.isnan(u)) or any(np.isnan(v)):
                for i, j in nonzero:
                    if np.isnan(u[i]) and not np.isnan(v[j]):
                        u[i] = C[i, j] - v[j]
                    elif not np.isnan(u[i]) and np.isnan(v[j]):
                        v[j] = C[i, j] - u[i]
                    else:
                        continue

            for i in range(n):
                for j in range(m):
                    S[i, j] = C[i, j] - u[i] - v[j]

            s = np.min(S)
            if s >= 0:
                break

            i, j = np.argwhere(S == s)[0]
            start = (i, j)

            T = np.copy(X)
            T[start] = 1
            while True:
                _xs, _ys = np.nonzero(T)
                xcount, ycount = Counter(_xs), Counter(_ys)

                for x, count in xcount.items():
                    if count <= 1:
                        T[x, :] = 0
                for y, count in ycount.items():
                    if count <= 1:
                        T[:, y] = 0

                if all(x > 1 for x in xcount.values()) and all(
                    y > 1 for y in ycount.values()
                ):
                    break

            dist = lambda p1, p2: abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
            fringe = set(tuple(p) for p in np.argwhere(T > 0))

            size = len(fringe)

            path = [start]
            while len(path) < size:
                last = path[-1]
                if last in fringe:
                    fringe.remove(last)
                next_ = min(fringe, key=lambda point: dist(last, point))
                path.append(next_)

            neg = path[1::2]
            pos = path[::2]
            q = min(X[tuple(zip(*neg))])
            X[tuple(zip(*neg))] -= q
            X[tuple(zip(*pos))] += q

        print(
            "Solucao final otima é  \n",
            np.matrix(X),
            np.sum(X * C),
        )


def get_input(prompt):
    while True:
        try:
            user_input = input(prompt).split(" ")
            return user_input
        except ValueError:
            print("Entrada inválida. Tente novamente.")


def main():
    print("Programa de Resolução do Problema do Transporte")

    supply = get_input("Digite as ofertas: ")
    supply = list(map(int, supply))
    demand = get_input("Digite as demandas: ")
    demand = list(map(int, demand))

    num_rows = len(supply)
    num_cols = len(demand)

    costs = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
    print("Digite os custos:")
    for i in range(num_rows):
        for j in range(num_cols):
            costs[i][j] = int(
                get_input(f"Custo para a origem {i+1} e destino {j+1}: ")[0]
            )

    t = Transporte(copy.copy(costs), supply, demand)

    menu = 1
    while True:
        if menu == 1:
            print("\nOpções:")
            print("1. Método do Canto Noroeste")
            print("2. Método do Mínimo dos Custos")
            print("3. Método de Vogel")
            print("0. Sair")

            choice = int(get_input("Digite o número da opção desejada: ")[0])

            if choice == 1:
                t.northwestCorner()
                menu = 2
            elif choice == 2:
                t.leastCost()
                menu = 2
            elif choice == 3:
                t.vogel()
                menu = 2
            elif choice == 0:
                print("Programa encerrado.")
                break
            else:
                print("Opção inválida. Tente novamente.")
        elif menu == 2:
            print("\nOpções:")
            print("1. Otimizar")
            print("0. Sair")

            choice = int(get_input("Digite o número da opção desejada: ")[0])

            if choice == 1:
                t.findOptimal()
                break
            elif choice == 0:
                print("Programa encerrado.")
                break
            else:
                print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
