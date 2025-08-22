# app_paradoxo_aniversario.py
# Aplicativo desktop (Tkinter) para simular o Paradoxo do Aniversário sem abrir navegador.

import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import Counter
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")  # backend GUI
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --------------------- LÓGICA ---------------------

def gerar_aniversarios(num_pessoas, dias_no_ano=365):
    """Gera uma lista de aniversários aleatórios para num_pessoas pessoas."""
    return [random.randint(1, dias_no_ano) for _ in range(num_pessoas)]

def contar_aniversarios(aniversarios):
    """Conta quantas pessoas fazem aniversário em cada dia."""
    return Counter(aniversarios)

def simular(num_pessoas, num_simulacoes, dias_no_ano=365):
    """Simula o paradoxo do aniversário num_simulacoes vezes."""
    duplicados = 0
    for _ in range(num_simulacoes):
        aniversarios = gerar_aniversarios(num_pessoas, dias_no_ano=dias_no_ano)
        if len(aniversarios) != len(set(aniversarios)):
            duplicados += 1
    return duplicados / max(1, num_simulacoes)

def preparar_tabelas(contagens, dias_no_ano):
    dias = list(range(1, dias_no_ano + 1))
    valores = [contagens.get(d, 0) for d in dias]
    df_contagens = pd.DataFrame({"Dia do Ano": dias, "Pessoas": valores})
    dias_duplicados = sorted([d for d, c in contagens.items() if c > 1])
    df_duplicatas = pd.DataFrame({
        "Dia do Ano": dias_duplicados,
        "Quantidade": [contagens[d] for d in dias_duplicados]
    })
    return df_contagens, df_duplicatas

# --------------------- UI ---------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Paradoxo do Aniversário — App Desktop (Tkinter)")
        self.geometry("1000x650")

        # Estado
        self.df_contagens = None
        self.df_duplicatas = None
        self.ultimo_titulo = ""
        self.fig = None
        self.canvas = None

        # Controles (inputs)
        frm_inputs = ttk.Frame(self, padding=10)
        frm_inputs.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frm_inputs, text="Número de pessoas:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.var_pessoas = tk.StringVar(value="50")
        ttk.Entry(frm_inputs, width=10, textvariable=self.var_pessoas).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frm_inputs, text="Número de simulações:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.var_sims = tk.StringVar(value="20000")
        ttk.Entry(frm_inputs, width=12, textvariable=self.var_sims).grid(row=0, column=3, padx=5, pady=5)

        self.var_bissexto = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_inputs, text="Ano bissexto (366 dias)", variable=self.var_bissexto).grid(row=0, column=4, padx=10, pady=5)

        self.var_seed = tk.StringVar(value="")
        ttk.Label(frm_inputs, text="Seed (opcional):").grid(row=0, column=5, sticky="e", padx=5, pady=5)
        ttk.Entry(frm_inputs, width=10, textvariable=self.var_seed).grid(row=0, column=6, padx=5, pady=5)

        # Botões
        frm_btns = ttk.Frame(self, padding=(10, 0))
        frm_btns.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(frm_btns, text="Gerar & Plotar", command=self.rodar_e_plotar).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frm_btns, text="Salvar CSVs", command=self.salvar_csvs).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frm_btns, text="Copiar Resultado", command=self.copiar_resultado).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frm_btns, text="Limpar", command=self.limpar).pack(side=tk.LEFT, padx=5, pady=5)

        # Área do gráfico
        self.frm_plot = ttk.Frame(self, padding=10)
        self.frm_plot.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Resultado textual
        self.texto_resultado = tk.Text(self, height=6, wrap="word")
        self.texto_resultado.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0,10))
        self.texto_resultado.insert("1.0", "Bem-vindo! Preencha os campos acima e clique em 'Gerar & Plotar'.")

        # Tema básico (opcional)
        try:
            self.style = ttk.Style(self)
            if "vista" in self.style.theme_names():
                self.style.theme_use("vista")
        except Exception:
            pass

    def rodar_e_plotar(self):
        # Valida entradas
        try:
            n = int(self.var_pessoas.get())
            sims = int(self.var_sims.get())
            if n <= 0 or sims <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Insira valores inteiros positivos para pessoas e simulações.")
            return

        dias_no_ano = 366 if self.var_bissexto.get() else 365

        # Seed opcional
        seed_txt = self.var_seed.get().strip()
        if seed_txt:
            try:
                random.seed(int(seed_txt))
            except ValueError:
                random.seed(seed_txt)  # aceita string como seed

        # Gera amostra e contagens
        aniversarios = gerar_aniversarios(n, dias_no_ano)
        contagens = contar_aniversarios(aniversarios)
        df_contagens, df_duplicatas = preparar_tabelas(contagens, dias_no_ano)

        # Guarda para salvar depois
        self.df_contagens = df_contagens
        self.df_duplicatas = df_duplicatas

        # Monte Carlo
        prob = simular(n, sims, dias_no_ano)

        # Texto de resultado
        dias_dup = list(df_duplicatas["Dia do Ano"]) if not df_duplicatas.empty else []
        self.texto_resultado.delete("1.0", tk.END)
        self.texto_resultado.insert(tk.END,
            f"Grupo: {n} pessoa(s)\n"
            f"Simulações: {sims}\n"
            f"Dias no ano: {dias_no_ano}\n"
            f"Probabilidade de ao menos um aniversário compartilhado: {prob:.2%}\n"
            f"Dias com duplicatas nesta amostra: {dias_dup if dias_dup else 'nenhum'}"
        )

        self.ultimo_titulo = f"Paradoxo do Aniversário — {n} pessoas ({dias_no_ano} dias)"

        # Plot
        self.plotar_barras(contagens, dias_no_ano)

    def plotar_barras(self, contagens, dias_no_ano):
        # Destroi gráfico antigo se existir
        for child in self.frm_plot.winfo_children():
            child.destroy()

        dias = list(range(1, dias_no_ano + 1))
        valores = [contagens.get(d, 0) for d in dias]

        # Cores: vermelho (>1), azul (=1), cinza (=0)
        cores = []
        for v in valores:
            if v > 1:
                cores.append("red")
            elif v == 1:
                cores.append("blue")
            else:
                cores.append("lightgrey")

        self.fig = plt.Figure(figsize=(11, 3.8))
        ax = self.fig.add_subplot(111)
        ax.bar(dias, valores, color=cores)
        ax.set_title(self.ultimo_titulo)
        ax.set_xlabel("Dia do Ano")
        ax.set_ylabel("Número de Pessoas")
        step = 30 if dias_no_ano == 365 else 31
        ax.set_xticks(list(range(0, dias_no_ano + 1, step)))
        ax.set_yticks(list(range(0, max(valores + [1]) + 1)))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frm_plot)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def salvar_csvs(self):
        if self.df_contagens is None:
            messagebox.showwarning("Atenção", "Nada para salvar. Clique em 'Gerar & Plotar' primeiro.")
            return

        # Escolhe pasta
        pasta = filedialog.askdirectory(title="Escolha a pasta para salvar os CSVs")
        if not pasta:
            return

        try:
            caminho_contagens = f"{pasta}/contagem_aniversarios.csv"
            caminho_duplicatas = f"{pasta}/dias_duplicatas.csv"
            self.df_contagens.to_csv(caminho_contagens, index=False)
            (self.df_duplicatas if self.df_duplicatas is not None else pd.DataFrame(columns=["Dia do Ano","Quantidade"])) \
                .to_csv(caminho_duplicatas, index=False)
            messagebox.showinfo("Sucesso", f"Arquivos salvos:\n- {caminho_contagens}\n- {caminho_duplicatas}")
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))

    def copiar_resultado(self):
        texto = self.texto_resultado.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(texto)
        messagebox.showinfo("Copiado", "Resultado copiado para a área de transferência.")

    def limpar(self):
        self.texto_resultado.delete("1.0", tk.END)
        self.texto_resultado.insert("1.0", "Limpo. Ajuste os parâmetros e rode novamente.")
        for child in self.frm_plot.winfo_children():
            child.destroy()
        self.df_contagens = None
        self.df_duplicatas = None
        self.ultimo_titulo = ""
        self.fig = None
        self.canvas = None

if __name__ == "__main__":
    app = App()
    app.mainloop()
