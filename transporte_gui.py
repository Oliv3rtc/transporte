#!/usr/bin/python3
import copy
import tkinter as tk
import tkinter.ttk as ttk

import numpy as np

from transporte import Transporte


class App:
    def __init__(self, master=None):
        master.title("Problema do Transporte")

        style = ttk.Style(master)
        master.tk.call("source", "forest-light.tcl")
        style.theme_use("forest-light")
        master.resizable(0, 0)

        self.main = ttk.Frame(master)
        self.main.configure(height=500, width=500)
        self.main.grid(column=0, row=0)
        self.mainwindow = self.main

        self.n = 3
        self.m = 3

        self.t = None
        self.sbf = None
        self.custo_total = None

        self.left = None
        self.definir_frame = None
        self.n_spinbox = None
        self.m_spinbox = None
        self.definir_bt = None
        self.dados_frame = None
        self.custos_frame = None
        self.custos_entries = []
        self.ofertas_frame = None
        self.ofertas_entries = []
        self.demandas_frame = None
        self.demandas_entries = []
        self.enviar_bt = None
        self.spinbox_frame = None
        self.left_frame_config()

        self.right_frame = None
        self.sbf_frame = None
        self.sbf_texts = []
        self.metodos_frame = None
        self.no_bt = None
        self.minc_bt = None
        self.vogel_bt = None
        self.otimizar_bt = None
        self.tmp_label = None
        self.right_frame_config()

    def left_frame_config(self):
        self.left = ttk.Frame(self.main)
        self.left.grid(column=0, padx=5, pady=5, row=0)
        self.left.configure(height=200, width=200)

        self.definir_frame_config()
        self.dados_frame_config()

    def definir_frame_config(self):
        self.definir_frame = ttk.Labelframe(self.left)
        self.definir_frame.configure(height=200, text="Defir tamanho", width=200)
        self.definir_frame.pack()

        self.spinbox_frame = ttk.Frame(self.definir_frame)
        self.spinbox_frame.configure(height=200, width=200)
        self.spinbox_frame.grid(column=0, row=1)

        self.n_spinbox = ttk.Spinbox(self.spinbox_frame)
        self.n_spinbox.insert(0, str(self.n))
        self.n_spinbox.configure(from_=2, to=20, width=5)
        self.n_spinbox.grid(column=0, padx=5, pady=5, row=0)

        self.m_spinbox = ttk.Spinbox(self.spinbox_frame)
        self.m_spinbox.insert(0, str(self.m))
        self.m_spinbox.configure(from_=2, to=20, width=5)
        self.m_spinbox.grid(column=1, padx=5, pady=5, row=0)

        definir_bt_frame = ttk.Frame(self.definir_frame)
        definir_bt_frame.configure(height=200, width=200)
        definir_bt_frame.grid(column=0, row=2)

        self.definir_bt = ttk.Button(definir_bt_frame, command=self.definir_tamanho)
        self.definir_bt.configure(text="Definir", width=15)
        self.definir_bt.pack(pady=5, side="top")

    def dados_frame_config(self):
        self.dados_frame = ttk.Labelframe(self.left)
        self.dados_frame.configure(height=200, text="Inserir Dados", width=200)
        self.dados_frame.pack()

        self.custos_frame_config()

        self.ofertas_frame_config()

        self.demandas_frame_config()

        self.gerar_entries()

        dados_bt_frame = ttk.Frame(self.dados_frame)
        dados_bt_frame.configure(height=200, width=200)
        dados_bt_frame.grid(column=0, columnspan=2, padx=5, pady=5, row=2)

        self.enviar_bt = ttk.Button(dados_bt_frame, command=self.ler_entries)
        self.enviar_bt.configure(text="Definir", width=15)
        self.enviar_bt.grid(column=0, row=0, padx=5, pady=5)

        self.clear_bt = ttk.Button(dados_bt_frame, command=self.clear_left_side)
        self.clear_bt.configure(text="Limpar", width=15)
        self.clear_bt.grid(column=1, row=0, padx=5, pady=5)

    def custos_frame_config(self):
        self.custos_frame = ttk.Frame(self.dados_frame)
        self.custos_frame.configure(height=200, width=200)
        self.custos_frame.grid(column=0, pady=5, row=0)

    def ofertas_frame_config(self):
        self.ofertas_frame = ttk.Frame(self.dados_frame)
        self.ofertas_frame.grid(column=1, pady=5, padx=5, row=0)

    def demandas_frame_config(self):
        self.demandas_frame = ttk.Frame(self.dados_frame)
        self.demandas_frame.configure(height=200, width=200)
        self.demandas_frame.grid(column=0, padx=5, pady=5, row=1)

    def gerar_entries(self):
        self.custos_entries = []
        self.ofertas_entries = []
        self.demandas_entries = []

        for i in range(self.n):
            for j in range(self.m):
                tmp = ttk.Entry(self.custos_frame)
                tmp.configure(width=5)
                tmp.grid(column=j, row=i)
                self.custos_entries.append(tmp)

        for i in range(self.n):
            tmp = ttk.Entry(self.ofertas_frame)
            tmp.configure(width=5)
            tmp.pack()
            self.ofertas_entries.append(tmp)

        for i in range(self.m):
            tmp = ttk.Entry(self.demandas_frame)
            tmp.configure(width=5)
            tmp.grid(column=i, row=0)
            self.demandas_entries.append(tmp)

    def clear_left_side(self):
        for entry in self.custos_entries:
            entry.destroy()
        self.custos_entries.clear()

        for entry in self.ofertas_entries:
            entry.destroy()
        self.ofertas_entries.clear()

        for entry in self.demandas_entries:
            entry.destroy()
        self.demandas_entries.clear()

        self.gerar_entries()

    def definir_tamanho(self):
        self.n = int(self.n_spinbox.get())
        self.m = int(self.m_spinbox.get())

        self.n_spinbox = ttk.Spinbox(self.spinbox_frame)
        self.n_spinbox.insert(0, str(self.n))
        self.n_spinbox.configure(from_=2, to=20, width=5)
        self.n_spinbox.grid(column=0, padx=5, pady=5, row=0)

        self.m_spinbox = ttk.Spinbox(self.spinbox_frame)
        self.m_spinbox.insert(0, str(self.m))
        self.m_spinbox.configure(from_=2, to=20, width=5)
        self.m_spinbox.grid(column=1, padx=5, pady=5, row=0)

        self.clear_left_side()
        self.clear_right_side()

    def ler_entries(self):
        ofertas = []
        demandas = []
        custos = []

        for i in range(self.n):
            tmp = []
            for j in range(self.m):
                tmp.append(int(self.custos_entries[i * self.m + j].get()))
            custos.append(tmp)

        for i in range(self.n):
            ofertas.append(int(self.ofertas_entries[i].get()))

        for j in range(self.m):
            demandas.append(int(self.demandas_entries[j].get()))

        self.t = Transporte(custos, ofertas, demandas)

        self.clear_right_side()

    def clear_right_side(self):
        for label in self.sbf_texts:
            label.destroy()
        self.sbf_texts.clear()

        self.gerar_label_sbf()

    def right_frame_config(self):
        self.right_frame = ttk.Labelframe(self.main)
        self.right_frame.configure(height=200, text="Resultado", width=200)
        self.right_frame.grid(column=1, padx=5, pady=5, row=0, sticky="nw")

        self.sbf_frame_config()

        self.metodos_frame = ttk.Frame(self.right_frame)
        self.metodos_frame.configure(height=200, width=200)
        self.metodos_frame.grid(column=0, padx=5, pady=5, row=2)

        self.no_bt = ttk.Button(self.metodos_frame, command=self.canto_no)
        self.no_bt.configure(text="Canto Noroeste")
        self.no_bt.grid(column=0, row=0, padx=5, pady=5)

        self.minc_bt = ttk.Button(self.metodos_frame, command=self.minimo_custo)
        self.minc_bt.configure(text="Minimo dos Custos")
        self.minc_bt.grid(column=1, row=0, padx=5, pady=5)

        self.vogel_bt = ttk.Button(self.metodos_frame, command=self.vogel)
        self.vogel_bt.configure(text="Vogel")
        self.vogel_bt.grid(column=2, row=0, padx=5, pady=5)

        self.otimizar_bt = ttk.Button(self.right_frame, command=self.otimizar)
        self.otimizar_bt.configure(text="Otimizar")
        self.otimizar_bt.grid(column=0, padx=5, pady=5, row=3)

    def sbf_frame_config(self):
        self.sbf_frame = ttk.Frame(self.right_frame)
        self.sbf_frame.configure(height=200, width=200)
        self.sbf_frame.grid(column=0, padx=5, pady=5, row=1)

        self.gerar_label_sbf()

    def gerar_label_sbf(self):
        if self.tmp_label != None:
            self.tmp_label.destroy()

        mensagem = "Defina o problema ao lado"

        if self.t != None:
            mensagem = "Escolha um método abaixo"

        if self.sbf == None:
            self.tmp_label = tk.Label(self.sbf_frame, text=mensagem)
            self.tmp_label.grid(row=0, column=0, sticky="nesw")
            return

        for i in range(self.n):
            for j in range(self.m):
                tmp = tk.Label(
                    self.sbf_frame,
                    text="0" if np.isnan(self.sbf[i][j]) else str(self.sbf[i][j]),
                )
                tmp.configure(height=2, width=6)
                tmp.grid(column=j, row=i, sticky="nw")
                self.sbf_texts.append(tmp)

        self.custo_total_label = ttk.Label(
            self.right_frame, text=f"Custo = {self.custo_total}"
        )
        self.custo_total_label.grid(row=0, column=0, padx=5, pady=5)

    def canto_no(self):
        if self.t == None:
            return

        self.sbf, self.custo_total = self.t.canto_noroeste()
        self.n = len(self.sbf)
        self.m = len(self.sbf[0])
        self.clear_right_side()

    def minimo_custo(self):
        if self.t == None:
            return
        self.sbf, self.custo_total = self.t.minimo_dos_custos()
        self.n = len(self.sbf)
        self.m = len(self.sbf[0])
        self.clear_right_side()

    def vogel(self):
        if self.t == None:
            return
        self.sbf, self.custo_total = self.t.vogel()
        self.n = len(self.sbf)
        self.m = len(self.sbf[0])
        self.clear_right_side()

    def otimizar(self):
        if self.t == None or self.sbf == None:
            return

        self.custo_total = self.t.obter_otimo(self.sbf)
        self.clear_right_side()

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.run()
