#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import tkinter as tk
from tkinter import messagebox

# ---------------- Configurações ----------------
BANCA_INICIAL = 500
MULTIPLOS_BARALHOS = 1
PAGAMENTO_BLACKJACK = 1.5  # 3:2

NAIPES = ['♠', '♥', '♦', '♣']
VALORES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

CARD_W, CARD_H = 70, 100
GAP = 18
MARGEM_X = 20
MARGEM_Y = 30

# ---------------- Utilidades de jogo ----------------
def criar_baralho(qtd_baralhos=1):
    baralho = [(v, n) for v in VALORES for n in NAIPES] * qtd_baralhos
    random.shuffle(baralho)
    return baralho

def valor_mao(cartas):
    """Retorna (total, eh_blackjack, eh_soft)."""
    valores = []
    ases = 0
    for v, _ in cartas:
        if v == 'A':
            ases += 1
            valores.append(11)
        elif v in ('J', 'Q', 'K'):
            valores.append(10)
        else:
            valores.append(int(v))
    total = sum(valores)
    while total > 21 and ases > 0:
        total -= 10
        ases -= 1
    # soft se algum Ás ainda conta como 11
    soma_bruta = sum(11 if v=='A' else (10 if v in ('J','Q','K') else int(v)) for v,_ in cartas)
    eh_soft = any(v=='A' for v,_ in cartas) and total <= 21 and soma_bruta != total
    eh_blackjack = (len(cartas) == 2) and total == 21
    return total, eh_blackjack, eh_soft

def texto_mao(cartas, ocultar_primeira=False):
    if ocultar_primeira and cartas:
        return "[??] " + " ".join(f"[{v}{n}]" for v,n in cartas[1:])
    return " ".join(f"[{v}{n}]" for v,n in cartas)

# ---------------- Interface / App ----------------
class BlackjackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack (Tkinter)")
        self.resizable(False, False)
        random.seed()

        # Estado do jogo
        self.baralho = criar_baralho(MULTIPLOS_BARALHOS)
        self.banca = BANCA_INICIAL
        self.aposta = 0
        self.mao_jog = []
        self.mao_dealer = []
        self.round_ativo = False
        self.dealer_oculto = True

        # Layout
        self._build_top()
        self._build_canvas()
        self._build_bottom()

        self._update_info("Bem-vindo! Faça sua aposta e clique em 'Dar as Cartas'.")

    # ----- UI builders -----
    def _build_top(self):
        frm = tk.Frame(self, padx=10, pady=8)
        frm.pack(fill="x")
        self.lbl_banca = tk.Label(frm, text=f"Banca: ${self.banca}", font=("TkDefaultFont", 11, "bold"))
        self.lbl_banca.pack(side="left")

        tk.Label(frm, text="Aposta:").pack(side="left", padx=(20, 5))
        self.ent_aposta = tk.Entry(frm, width=7, justify="right")
        self.ent_aposta.insert(0, "10")
        self.ent_aposta.pack(side="left")

        self.btn_deal = tk.Button(frm, text="Dar as Cartas", command=self.iniciar_rodada)
        self.btn_deal.pack(side="left", padx=10)

        self.lbl_status = tk.Label(frm, text="", fg="#555")
        self.lbl_status.pack(side="right")

    def _build_canvas(self):
        self.canvas = tk.Canvas(self, width=820, height=360, bg="#0B6A3A")  # verde feltro :)
        self.canvas.pack(padx=10, pady=5)
        # Títulos de áreas
        self.canvas.create_text(10, 18, anchor="w", fill="white",
                                font=("TkDefaultFont", 12, "bold"), text="Dealer")
        self.canvas.create_text(10, 190, anchor="w", fill="white",
                                font=("TkDefaultFont", 12, "bold"), text="Você")

    def _build_bottom(self):
        frm = tk.Frame(self, padx=10, pady=10)
        frm.pack(fill="x")

        self.btn_hit = tk.Button(frm, text="Hit (Comprar)", width=15, command=self.acao_hit, state="disabled")
        self.btn_stand = tk.Button(frm, text="Stand (Parar)", width=15, command=self.acao_stand, state="disabled")
        self.btn_double = tk.Button(frm, text="Double (Dobrar)", width=15, command=self.acao_double, state="disabled")
        self.btn_nova = tk.Button(frm, text="Nova Rodada", width=15, command=self.reset_rodada, state="disabled")

        self.btn_hit.pack(side="left")
        self.btn_stand.pack(side="left", padx=6)
        self.btn_double.pack(side="left")
        self.btn_nova.pack(side="right")

    # ----- Fluxo do jogo -----
    def iniciar_rodada(self):
        if self.round_ativo:
            return
        # valida aposta
        try:
            aposta = int(self.ent_aposta.get())
        except ValueError:
            messagebox.showwarning("Aposta inválida", "Digite um número inteiro para a aposta.")
            return
        if aposta <= 0 or aposta > self.banca:
            messagebox.showwarning("Aposta inválida", "Aposta deve ser positiva e não pode exceder a banca.")
            return

        self.aposta = aposta
        self.round_ativo = True
        self.dealer_oculto = True
        self.mao_jog, self.mao_dealer = [], []

        if len(self.baralho) < 15:
            self.baralho = criar_baralho(MULTIPLOS_BARALHOS)

        # Distribuição inicial
        self.mao_jog.append(self.baralho.pop())
        self.mao_dealer.append(self.baralho.pop())
        self.mao_jog.append(self.baralho.pop())
        self.mao_dealer.append(self.baralho.pop())

        self._desenhar_mesa()

        # Verificar blackjacks
        tot_j, bj_j, _ = valor_mao(self.mao_jog)
        tot_d, bj_d, _ = valor_mao(self.mao_dealer)

        if bj_j or bj_d:
            self.dealer_oculto = False
            self._desenhar_mesa()
            if bj_j and bj_d:
                self._fim_de_rodada("Empate com Blackjacks. Aposta devolvida.", push=True)
                return
            if bj_j:
                ganho = int(self.aposta * PAGAMENTO_BLACKJACK)
                self.banca += ganho
                self._fim_de_rodada(f"Blackjack! Você ganha ${ganho}.")
                return
            # Dealer tem BJ
            self.banca -= self.aposta
            self._fim_de_rodada(f"Dealer tem Blackjack. Você perde ${self.aposta}.")
            return

        # Habilita ações
        self._toggle_botoes(jogar=True)
        self._update_info(f"Suas cartas: {texto_mao(self.mao_jog)}  (total {tot_j})")

    def acao_hit(self):
        if not self.round_ativo:
            return
        self.mao_jog.append(self.baralho.pop())
        tot_j, _, _ = valor_mao(self.mao_jog)
        self._desenhar_mesa()
        if tot_j > 21:
            self.banca -= self.aposta
            self._fim_de_rodada("Você estourou!")
        else:
            self._update_info(f"Comprou carta. Total: {tot_j}")

    def acao_double(self):
        if not self.round_ativo:
            return
        # Só permite dobrar nas duas primeiras cartas e com saldo
        if len(self.mao_jog) != 2:
            self._update_info("Não é possível dobrar agora.")
            return
        if self.banca < self.aposta * 2:
            self._update_info("Banca insuficiente para dobrar.")
            return
        self.aposta *= 2
        self.mao_jog.append(self.baralho.pop())
        tot_j, _, _ = valor_mao(self.mao_jog)
        self._desenhar_mesa()
        if tot_j > 21:
            self.banca -= self.aposta
            self._fim_de_rodada("Você estourou após dobrar!")
        else:
            # passa a vez imediatamente
            self._dealer_turn()

    def acao_stand(self):
        if not self.round_ativo:
            return
        self._dealer_turn()

    def _dealer_turn(self):
        self.dealer_oculto = False
        self._desenhar_mesa()
        tot_d, _, _ = valor_mao(self.mao_dealer)
        # Dealer compra até 17 (inclui soft 17)
        while True:
            tot_d, _, soft = valor_mao(self.mao_dealer)
            if tot_d < 17 or (tot_d == 17 and soft):
                self.after(350, self._dealer_hit)  # animação leve
                return
            break
        self._resolver_maos()

    def _dealer_hit(self):
        self.mao_dealer.append(self.baralho.pop())
        self._desenhar_mesa()
        tot_d, _, soft = valor_mao(self.mao_dealer)
        if tot_d < 17 or (tot_d == 17 and soft):
            self.after(350, self._dealer_hit)
        else:
            self._resolver_maos()

    def _resolver_maos(self):
        tot_j, _, _ = valor_mao(self.mao_jog)
        tot_d, _, _ = valor_mao(self.mao_dealer)
        self._desenhar_mesa()

        if tot_d > 21:
            self.banca += self.aposta
            self._fim_de_rodada(f"Dealer estourou! Você ganha ${self.aposta}.")
            return
        if tot_j > tot_d:
            self.banca += self.aposta
            self._fim_de_rodada(f"Você venceu! Você ganha ${self.aposta}.")
            return
        if tot_j < tot_d:
            self.banca -= self.aposta
            self._fim_de_rodada(f"Você perdeu ${self.aposta}.")
            return
        self._fim_de_rodada("Empate (push). Aposta devolvida.", push=True)

    def _fim_de_rodada(self, msg, push=False):
        self.round_ativo = False
        self._toggle_botoes(jogar=False)
        self._update_banca()
        self._update_info(msg)
        self.btn_nova.configure(state="normal")

    def reset_rodada(self):
        self.mao_jog.clear()
        self.mao_dealer.clear()
        self.aposta = 0
        self.dealer_oculto = True
        self._desenhar_mesa()
        self._toggle_botoes(jogar=False)
        self.btn_nova.configure(state="disabled")
        if self.banca <= 0:
            messagebox.showinfo("Fim de jogo", "Você ficou sem fichas!")
        else:
            self._update_info("Faça sua aposta e clique em 'Dar as Cartas'.")

    # ----- Desenho / UI helpers -----
    def _toggle_botoes(self, jogar):
        self.btn_hit.configure(state="normal" if jogar else "disabled")
        self.btn_stand.configure(state="normal" if jogar else "disabled")
        # Double só nas duas primeiras cartas
        pode_double = jogar and len(self.mao_jog) == 2 and self.banca >= self.aposta * 2
        self.btn_double.configure(state="normal" if pode_double else "disabled")
        self.btn_deal.configure(state="disabled" if jogar else "normal")

    def _update_banca(self):
        self.lbl_banca.configure(text=f"Banca: ${self.banca}")

    def _update_info(self, txt):
        self.lbl_status.configure(text=txt)

    def _desenhar_mesa(self):
        self.canvas.delete("card")
        # Dealer
        self._desenhar_mao(self.mao_dealer, y=MARGEM_Y, ocultar_primeira=self.dealer_oculto)
        tot_d, _, _ = valor_mao(self.mao_dealer)
        label_d = "??" if self.dealer_oculto else str(tot_d)
        self._draw_total(label=f"Total: {label_d}", x=700, y=MARGEM_Y + CARD_H + 10)

        # Jogador
        self._desenhar_mao(self.mao_jog, y=180, ocultar_primeira=False)
        tot_j, _, _ = valor_mao(self.mao_jog)
        self._draw_total(label=f"Total: {tot_j if self.mao_jog else 0}", x=700, y=180 + CARD_H + 10)

        # Atualiza botões (para o caso de já ter 3ª carta etc.)
        if self.round_ativo:
            self._toggle_botoes(jogar=True)

    def _draw_total(self, label, x, y):
        self.canvas.create_text(x, y, anchor="w", fill="white",
                                font=("TkDefaultFont", 12, "bold"), text=label, tags="card")

    def _desenhar_mao(self, cartas, y, ocultar_primeira=False):
        x = MARGEM_X
        for idx, (v, n) in enumerate(cartas):
            if idx == 0 and ocultar_primeira:
                self._desenhar_carta_oculta(x, y)
            else:
                self._desenhar_carta(x, y, v, n)
            x += CARD_W + GAP

    def _desenhar_carta(self, x, y, valor, naipe):
        # Cor vermelha para ♥ ♦
        cor = "#D32F2F" if naipe in ('♥', '♦') else "black"
        # Moldura
        self.canvas.create_rectangle(x, y, x+CARD_W, y+CARD_H, fill="white", outline="#333", width=2, tags="card")
        # Valor topo-esq
        self.canvas.create_text(x+8, y+12, anchor="nw", text=valor, fill=cor, font=("TkDefaultFont", 12, "bold"), tags="card")
        # Naipe centro
        self.canvas.create_text(x+CARD_W/2, y+CARD_H/2, text=naipe, fill=cor, font=("TkDefaultFont", 28), tags="card")
        # Valor base-dir
        self.canvas.create_text(x+CARD_W-8, y+CARD_H-12, anchor="se", text=valor, fill=cor, font=("TkDefaultFont", 12, "bold"), tags="card")

    def _desenhar_carta_oculta(self, x, y):
        self.canvas.create_rectangle(x, y, x+CARD_W, y+CARD_H, fill="#1E88E5", outline="#333", width=2, tags="card")
        # padrão simples
        for i in range(6):
            self.canvas.create_line(x+6, y+10+i*15, x+CARD_W-6, y+10+i*15, fill="white", tags="card")

if __name__ == "__main__":
    app = BlackjackApp()
    app.mainloop()
