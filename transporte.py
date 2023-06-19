from collections import deque
import tkinter
import numpy as np
from networkx import DiGraph, find_cycle
import copy


class Transporte:
    def __init__(self, custos, oferta, demanda):
        self.custos = copy.deepcopy(custos)
        self.oferta = oferta[:]
        self.demanda = demanda[:]

        dif_oferta_demanda = int(np.nansum(self.oferta) - np.nansum(self.demanda))

        if dif_oferta_demanda < 0:
            self.oferta.append(abs(dif_oferta_demanda))
            self.custos.append([0] * len(self.demanda))
        elif dif_oferta_demanda > 0:
            self.demanda.append(abs(dif_oferta_demanda))
            for linha in self.custos:
                linha.append(0)

        if np.nan in self.oferta or np.nan in self.demanda:
            soma = int(np.nansum(self.oferta))
            for i in range(len(self.oferta)):
                if np.isnan(self.oferta[i]):
                    self.oferta[i] = soma

            for i in range(len(self.demanda)):
                if np.isnan(self.demanda[i]):
                    self.demanda[i] = soma

    def canto_noroeste(self):
        bfs = [
            [np.nan for _ in range(len(self.custos[0]))]
            for _ in range(len(self.custos))
        ]
        custo_total = 0
        i = 0
        j = 0

        oferta = self.oferta[:]
        demanda = self.demanda[:]

        while i < len(self.custos) and j < len(self.custos[0]):
            max_disponivel = min(oferta[i], demanda[j])

            bfs[i][j] = max_disponivel
            custo_total += max_disponivel * self.custos[i][j]
            oferta[i] -= max_disponivel
            demanda[j] -= max_disponivel

            if oferta[i] == 0:
                i += 1
            elif demanda[j] == 0:
                j += 1

        return bfs, custo_total

    def minimo_dos_custos(self):
        bfs = [
            [np.nan for _ in range(len(self.custos[0]))]
            for _ in range(len(self.custos))
        ]
        custo_total = 0

        oferta = self.oferta[:]
        demanda = self.demanda[:]
        custos = copy.deepcopy(self.custos)

        while max(oferta) != 0 or max(demanda) != 0:
            i, j = np.argwhere(custos == np.min(custos))[0]

            max_disponivel = min(oferta[i], demanda[j])

            bfs[i][j] = max_disponivel
            custo_total += max_disponivel * self.custos[i][j]
            oferta[i] -= max_disponivel
            demanda[j] -= max_disponivel

            if oferta[i] == 0:
                custos[i] = [np.inf for _ in range(len(custos[i]))]
            elif demanda[j] == 0:
                for linha in custos:
                    linha[j] = np.inf

        return bfs, custo_total

    def vogel(self):
        bfs = [
            [np.nan for _ in range(len(self.custos[0]))]
            for _ in range(len(self.custos))
        ]
        custo_total = 0

        oferta = self.oferta[:]
        demanda = self.demanda[:]
        custos = copy.deepcopy(self.custos)

        while max(oferta) != 0 or max(demanda) != 0:
            dif_linhas, dif_colunas = dif_minimos(custos)

            max_dif_linhas = np.max(dif_linhas)
            max_dif_colunas = np.max(dif_colunas)

            i = -1
            j = -1

            if max_dif_linhas >= max_dif_colunas:
                i = np.argwhere(dif_linhas == max_dif_linhas)[0][0]
                j = np.argwhere(custos[i] == np.min(custos[i]))[0][0]
            else:
                j = np.argwhere(dif_colunas == max_dif_colunas)[0][0]
                col = [x[j] for x in custos]
                i = np.argwhere(col == np.min(col))[0][0]

            max_disponivel = min(oferta[i], demanda[j])

            bfs[i][j] = max_disponivel
            custo_total += max_disponivel * self.custos[i][j]
            oferta[i] -= max_disponivel
            demanda[j] -= max_disponivel

            if oferta[i] == 0:
                custos[i] = [np.inf for _ in range(len(custos[i]))]
            elif demanda[j] == 0:
                for dif_linhas in custos:
                    dif_linhas[j] = np.inf

        return bfs, custo_total

    def obter_dual(self, sbf):
        u = [np.nan for _ in self.oferta]
        v = [np.nan for _ in self.demanda]

        index_basicas = list(np.argwhere(np.asarray(sbf) >= 0))
        u[index_basicas[0][0]] = 0

        while any(np.isnan(u)) or any(np.isnan(v)):
            for i, j in index_basicas:
                if np.isnan(u[i]) and not np.isnan(v[j]):
                    u[i] = self.custos[i][j] - v[j]
                elif not np.isnan(u[i]) and np.isnan(v[j]):
                    v[j] = self.custos[i][j] - u[i]
                else:
                    continue

        return u, v

    def obter_otimo(self, sbf):
        while True:
            n_basicas = (len(sbf) * len(sbf[0])) - np.count_nonzero(np.isnan(sbf))

            if n_basicas != len(self.demanda) + len(self.oferta) - 1:
                for i in range(len(self.oferta)):
                    for j in range(len(self.demanda)):
                        coluna = [x[j] for x in sbf]
                        if np.count_nonzero(np.isnan(sbf[i])) == 1 and np.count_nonzero(
                            np.isnan(coluna)
                        ):
                            x, y = np.argwhere(coluna == np.nan)[0]
                            sbf[x][y] = 0

            u, v = self.obter_dual(sbf)

            custos_reduzidos = [[0 for _ in self.demanda] for _ in self.oferta]

            for i in range(len(self.oferta)):
                for j in range(len(self.demanda)):
                    custos_reduzidos[i][j] = self.custos[i][j] - u[i] - v[j]

            min_custo = np.min(custos_reduzidos)
            if min_custo >= 0:
                break

            i, j = np.argwhere(custos_reduzidos == min_custo)[0]
            sbf[i][j] = np.inf

            ciclo = encontrar_ciclo(sbf, i, j)

            sub = [ciclo[x] for x in range(len(ciclo)) if x % 2 != 0]
            sai = min([sbf[x][y] for x, y in sub])
            sbf[ciclo[0][0]][ciclo[0][1]] = sai

            ciclo.pop(0)
            ciclo.pop()
            t = -1

            for i, j in ciclo:
                if sbf[i][j] == sai and t < 0:
                    sbf[i][j] = np.nan
                else:
                    sbf[i][j] += sai * t
                t = -t

        return np.nansum(np.asarray([sbf]) * np.asanyarray(self.custos))


def encontrar_ciclo(matriz, i_inicial, j_inicial):
    g = DiGraph()
    fila = deque()

    fila.append(((i_inicial, j_inicial), False))

    while len(fila) > 0:
        no = fila.popleft()

        if no[1] == False:
            j = no[0][1]
            coluna = [linha[j] for linha in matriz]
            for i in range(len(coluna)):
                if i == no[0][0] or g.has_node((i, j)) or np.isnan(coluna[i]):
                    continue

                g.add_edge(no[0], (i, j))
                fila.append(((i, j), not no[1]))
        elif no[1] == True:
            i = no[0][0]
            linha = matriz[i]
            for j in range(len(linha)):
                if (i, j) == (i_inicial, j_inicial):
                    g.add_edge(no[0], (i, j))
                    break

                if j == no[0][1] or g.has_node((i, j)) or np.isnan(linha[j]):
                    continue

                g.add_edge(no[0], (i, j))
                fila.append(((i, j), not no[1]))

    ciclo = find_cycle(g, (i_inicial, j_inicial))
    return [(i_inicial, j_inicial)] + [n[1] for n in ciclo]


def dif_minimos(matriz):
    dif_colunas = []
    dif_linhas = []

    dif_linhas = [sorted(linha)[:2] for linha in matriz]
    for i, d in enumerate(dif_linhas):
        if d[1] != np.inf:
            dif_linhas[i] = d[1] - d[0]
        else:
            dif_linhas[i] = -min(d)

    dif_colunas = [sorted(coluna)[:2] for coluna in zip(*matriz)]
    for i, d in enumerate(dif_colunas):
        if d[1] != np.inf:
            dif_colunas[i] = d[1] - d[0]
        else:
            dif_colunas[i] = -min(d)

    return [dif_linhas, dif_colunas]


def min_matriz(matriz, linhas_ignoradas, colunas_ignoradas):
    valor_min = np.inf
    pos_min = (0, 0)

    for i in range(0, len(matriz)):
        if i in linhas_ignoradas:
            continue
        for j in range(0, len(matriz[i])):
            if j in colunas_ignoradas:
                continue

            if matriz[i][j] < valor_min:
                valor_min = matriz[i][j]
                pos_min = (i, j)

    return pos_min


def get_input(prompt):
    while True:
        try:
            user_input = input(prompt).split(" ")
            return user_input
        except ValueError:
            print("Entrada inválida. Tente novamente.")


def test():
    print("Programa de Resolução do Problema do Transporte")

    t = Transporte(
        [[2, 3, 4, 5], [3, 2, 5, 2], [4, 1, 2, 3]],
        [15, 20, 25],
        [8, 10, 12, 15],
    )

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
                sbf, custo = t.canto_noroeste()
                print(sbf)
                print(custo)
                custo = t.obter_otimo(sbf)
                print(sbf)
                print(custo)

            elif choice == 2:
                sbf, custo = t.minimo_dos_custos()
                print(sbf)
                print(custo)
                custo = t.obter_otimo(sbf)
                print(sbf)
                print(custo)

            elif choice == 3:
                sbf, custo = t.vogel()
                print(sbf)
                print(custo)
                custo = t.obter_otimo(sbf)
                print(sbf)
                print(custo)
            elif choice == 0:
                print("Programa encerrado.")
                break
            else:
                print("Opção inválida. Tente novamente.")
