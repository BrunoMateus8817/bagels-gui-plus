# bagels_gui_plus.py
# Jogo "Bagels" com interface gráfica (Tkinter) + teclado na tela,
# modo fácil (revela posições fixas) e animação de confete ao vencer.
#
# Regras das dicas:
# - "Certo": dígito correto na posição correta
# - "Quase": dígito correto, mas na posição errada
# - "Nada": nenhum dígito correto
#
# Python 3.8+

import random
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional

APP_TITLE = "Bagels — Jogo de Lógica"
PAD = 10


class BagelsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(False, False)

        # Estado do jogo
        self.secret: str = ""
        self.num_digitos = tk.IntVar(value=3)
        self.max_tentativas = tk.IntVar(value=10)
        self.modo_facil = tk.BooleanVar(value=False)
        self.revelados: Dict[int, str] = {}  # índice -> dígito revelado (0-based)
        self.tentativa_atual = 0
        self.jogo_ativo = False

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        container = ttk.Frame(self, padding=PAD)
        container.grid(row=0, column=0, sticky="nsew")

        # Título / instruções
        lbl_title = ttk.Label(
            container,
            text="Adivinhe o número secreto (sem dígitos repetidos).",
            font=("TkDefaultFont", 11, "bold")
        )
        lbl_title.grid(row=0, column=0, columnspan=4, sticky="w")

        lbl_rules = ttk.Label(
            container,
            text="Dicas:  Certo → posição certa  |  Quase → posição errada  |  Nada → nenhum dígito"
        )
        lbl_rules.grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, PAD))

        # Configurações (antes de iniciar)
        cfg = ttk.LabelFrame(container, text="Configurações")
        cfg.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, PAD))

        ttk.Label(cfg, text="Dígitos:").grid(row=0, column=0, padx=(PAD, 4), pady=6, sticky="e")
        sp_digits = ttk.Spinbox(cfg, from_=2, to=8, width=5, textvariable=self.num_digitos, state="readonly")
        sp_digits.grid(row=0, column=1, padx=(0, PAD), pady=6, sticky="w")

        ttk.Label(cfg, text="Tentativas:").grid(row=0, column=2, padx=(PAD, 4), pady=6, sticky="e")
        sp_tries = ttk.Spinbox(cfg, from_=3, to=20, width=5, textvariable=self.max_tentativas, state="readonly")
        sp_tries.grid(row=0, column=3, padx=(0, PAD), pady=6, sticky="w")

        chk_facil = ttk.Checkbutton(cfg, text="Modo fácil (revelar algumas posições)", variable=self.modo_facil)
        chk_facil.grid(row=0, column=4, padx=(PAD, PAD), pady=6, sticky="w")

        self.btn_novo = ttk.Button(cfg, text="Novo jogo", command=self.novo_jogo)
        self.btn_novo.grid(row=0, column=5, padx=(PAD, PAD), pady=6)

        # Dicas do modo fácil
        self.lbl_facil = ttk.Label(container, text="", foreground="#6b6b6b")
        self.lbl_facil.grid(row=3, column=0, columnspan=4, sticky="w", pady=(0, PAD))

        # Histórico
        hist_frame = ttk.LabelFrame(container, text="Histórico")
        hist_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")

        self.txt_hist = tk.Text(hist_frame, width=58, height=12, state="disabled", wrap="none")
        self.txt_hist.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(hist_frame, orient="vertical", command=self.txt_hist.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.txt_hist.configure(yscrollcommand=scroll.set)

        # Tags de cor
        self.txt_hist.tag_configure("guess", font=("TkDefaultFont", 10, "bold"))
        self.txt_hist.tag_configure("Certo", foreground="#1b8a1b")   # verde
        self.txt_hist.tag_configure("Quase", foreground="#b36b00")   # laranja
        self.txt_hist.tag_configure("Nada", foreground="#6b6b6b")    # cinza
        self.txt_hist.tag_configure("info", foreground="#004a77")

        # Entrada e ações
        ttk.Label(container, text="Seu palpite:").grid(row=5, column=0, sticky="w", pady=(PAD, 0))
        self.entry = ttk.Entry(container, width=20, justify="center", font=("TkDefaultFont", 11))
        self.entry.grid(row=5, column=1, sticky="w", pady=(PAD, 0))
        self.entry.bind("<Return>", lambda e: self.chutar())

        self.btn_chutar = ttk.Button(container, text="Chutar (Enter)", command=self.chutar, state="disabled")
        self.btn_chutar.grid(row=5, column=2, sticky="w", padx=(PAD, 0), pady=(PAD, 0))

        self.btn_limpar = ttk.Button(container, text="Limpar", command=self.key_clear, state="disabled")
        self.btn_limpar.grid(row=5, column=3, sticky="w", padx=(PAD, 0), pady=(PAD, 0))

        # Teclado numérico
        kb_frame = ttk.LabelFrame(container, text="Teclado")
        kb_frame.grid(row=6, column=0, columnspan=4, sticky="ew", pady=(PAD, PAD))

        self._build_keypad(kb_frame)

        # Status
        self.lbl_status = ttk.Label(container, text="Clique em 'Novo jogo' para começar.", foreground="#004a77")
        self.lbl_status.grid(row=7, column=0, columnspan=4, sticky="w", pady=(PAD, 0))

        # Menu
        self._build_menu()

        # Canvas de confete (criado sob demanda)
        self.confetti_canvas: Optional[tk.Canvas] = None
        self.confetti_items: List[int] = []

    def _build_menu(self):
        menubar = tk.Menu(self)
        jogo = tk.Menu(menubar, tearoff=False)
        jogo.add_command(label="Novo jogo", command=self.novo_jogo)
        jogo.add_separator()
        jogo.add_command(label="Sair", command=self.quit)
        menubar.add_cascade(label="Jogo", menu=jogo)

        ajuda = tk.Menu(menubar, tearoff=False)
        ajuda.add_command(label="Sobre", command=self._sobre)
        menubar.add_cascade(label="Ajuda", menu=ajuda)

        self.config(menu=menubar)

    def _build_keypad(self, parent):
        # Layout 1-9 em 3x3, depois 0, backspace, enter
        btn_cfg = dict(width=4)
        rows = [
            ("1", "2", "3"),
            ("4", "5", "6"),
            ("7", "8", "9"),
        ]
        for r, row in enumerate(rows):
            for c, label in enumerate(row):
                b = ttk.Button(parent, text=label, command=lambda d=label: self.key_digit(d), state="disabled")
                b.grid(row=r, column=c, padx=4, pady=4)
                setattr(self, f"btn_{label}", b)

        # Linha final: 0, backspace, enter
        self.btn_0 = ttk.Button(parent, text="0", command=lambda: self.key_digit("0"), state="disabled")
        self.btn_0.grid(row=3, column=0, padx=4, pady=4)

        self.btn_back = ttk.Button(parent, text="⌫", command=self.key_backspace, state="disabled")
        self.btn_back.grid(row=3, column=1, padx=4, pady=4)

        self.btn_enter = ttk.Button(parent, text="Enter", command=self.chutar, state="disabled")
        self.btn_enter.grid(row=3, column=2, padx=4, pady=4)

    def _set_keypad_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for d in "0123456789":
            getattr(self, f"btn_{d}").config(state=state)
        self.btn_back.config(state=state)
        self.btn_enter.config(state=state)
        self.btn_limpar.config(state=state)

    # ---------- Lógica ----------
    def novo_jogo(self):
        n = self.num_digitos.get()
        if n > 10:
            messagebox.showwarning("Configuração inválida", "Número máximo de dígitos é 10.")
            return

        self.secret = self._gerar_secreto(n)
        self.tentativa_atual = 1
        self.jogo_ativo = True
        self.revelados.clear()
        self._clear_hist()
        self._set_keypad_state(True)
        self.btn_chutar.config(state="normal")
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.focus()

        # Se modo fácil, revelar ~1/3 das posições (ao menos 1)
        if self.modo_facil.get():
            qnt = max(1, n // 3)
            idxs = list(range(n))
            random.shuffle(idxs)
            idxs = sorted(idxs[:qnt])  # ordena só para exibir bonito
            for i in idxs:
                self.revelados[i] = self.secret[i]
            texto = "Modo fácil: posições reveladas → " + ", ".join(
                [f"{i+1}={self.revelados[i]}" for i in idxs]
            )
            self.lbl_facil.config(text=texto)
            self._append_hist(texto + "\n", "info")
        else:
            self.lbl_facil.config(text="")

        self._append_hist(f"Início de jogo — número com {n} dígitos, sem repetição.\n", "info")
        self._update_status()

        # Remove confete, se estava ativo
        self._stop_confetti()

    def chutar(self):
        if not self.jogo_ativo:
            messagebox.showinfo("Bagels", "Clique em 'Novo jogo' para começar.")
            return

        guess = self.entry.get().strip()
        n = self.num_digitos.get()

        # Validação
        if len(guess) != n or not guess.isdecimal():
            messagebox.showwarning("Palpite inválido", f"Digite exatamente {n} dígitos (0–9).")
            return
        if len(set(guess)) != len(guess):
            messagebox.showwarning("Palpite inválido", "Os dígitos não podem se repetir.")
            return

        # Checagem do modo fácil: posições reveladas devem bater
        if self.revelados:
            erros = [str(i+1) for i, d in self.revelados.items() if guess[i] != d]
            if erros:
                pos_str = ", ".join(erros)
                messagebox.showwarning(
                    "Modo fácil",
                    f"No modo fácil, as posições {pos_str} devem ser os dígitos revelados."
                )
                return

        dicas = self._gerar_dicas(guess, self.secret)
        self._mostrar_tentativa(guess, dicas)

        if guess == self.secret:
            self._append_hist("\nVocê acertou! 🎉\n", "info")
            self._fim_de_jogo(vitoria=True)
            self._start_confetti()
            return

        if self.tentativa_atual >= self.max_tentativas.get():
            self._append_hist(f"\nAcabaram-se as tentativas. O número era {self.secret}.\n", "info")
            self._fim_de_jogo(vitoria=False)
            return

        # Preparar próxima jogada
        self.tentativa_atual += 1
        self._update_status()
        self.entry.delete(0, tk.END)
        self.entry.focus()

    def _fim_de_jogo(self, vitoria: bool):
        self.jogo_ativo = False
        self.btn_chutar.config(state="disabled")
        self.entry.config(state="disabled")
        self._set_keypad_state(False)
        if vitoria:
            self.lbl_status.config(text=f"Parabéns! Você venceu em {self.tentativa_atual} tentativa(s).")
        else:
            self.lbl_status.config(text="Fim de jogo. Clique em 'Novo jogo' para tentar novamente.")

    def _mostrar_tentativa(self, guess: str, dicas: List[str]):
        self._append_hist(f"Tentativa #{self.tentativa_atual}  ", "info")
        self._append_hist(f"{guess}\n", "guess")
        if not dicas:
            dicas = ["Nada"]
        # Ordena para não vazar posição real
        dicas_ordenadas = sorted(dicas)
        # Escreve com tags de cor por palavra
        self._append_hist("Dicas: ")
        for i, palavra in enumerate(dicas_ordenadas):
            self._append_hist(palavra, palavra)
            if i < len(dicas_ordenadas) - 1:
                self._append_hist(" ")
        self._append_hist("\n")

    def _update_status(self):
        restantes = self.max_tentativas.get() - self.tentativa_atual + 1
        self.lbl_status.config(
            text=f"Tentativa {self.tentativa_atual}/{self.max_tentativas.get()}  •  Restantes: {restantes}"
        )

    def _clear_hist(self):
        self.txt_hist.config(state="normal")
        self.txt_hist.delete("1.0", tk.END)
        self.txt_hist.config(state="disabled")

    def _append_hist(self, text: str, tag: Optional[str] = None):
        self.txt_hist.config(state="normal")
        if tag:
            self.txt_hist.insert(tk.END, text, tag)
        else:
            self.txt_hist.insert(tk.END, text)
        self.txt_hist.config(state="disabled")
        self.txt_hist.see(tk.END)

    # ---------- Regras ----------
    @staticmethod
    def _gerar_secreto(n: int) -> str:
        digitos = list("0123456789")
        random.shuffle(digitos)
        return "".join(digitos[:n])

    @staticmethod
    def _gerar_dicas(guess: str, secret: str) -> List[str]:
        if guess == secret:
            # Devolve vários "Certo" para colorir a linha de dica
            return ["Certo"] * len(secret)
        dicas: List[str] = []
        for i, ch in enumerate(guess):
            if ch == secret[i]:
                dicas.append("Certo")
            elif ch in secret:
                dicas.append("Quase")
        if not dicas:
            return ["Nada"]
        return dicas

    # ---------- Teclado ----------
    def key_digit(self, d: str):
        if not self.jogo_ativo:
            return
        n = self.num_digitos.get()
        text = self.entry.get()
        if len(text) >= n:
            return
        # evita repetir dígitos
        if d in text:
            self.bell()
            return
        self.entry.insert(tk.END, d)

    def key_backspace(self):
        if not self.jogo_ativo:
            return
        text = self.entry.get()
        if text:
            self.entry.delete(len(text)-1, tk.END)

    def key_clear(self):
        if not self.jogo_ativo:
            return
        self.entry.delete(0, tk.END)

    # ---------- Confete (animação) ----------
    def _start_confetti(self):
        # Cria canvas por cima da janela
        if self.confetti_canvas is not None:
            self._stop_confetti()
        w = self.winfo_width()
        h = self.winfo_height()
        self.confetti_canvas = tk.Canvas(self, width=w, height=h, highlightthickness=0, bg="")
        self.confetti_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.confetti_canvas.lift()

        self.confetti_items = []
        cores = ["#ff4d4f", "#40a9ff", "#73d13d", "#faad14", "#9254de", "#13c2c2"]
        for _ in range(120):
            x = random.randint(0, w)
            y = random.randint(-h // 2, 0)
            size = random.randint(4, 10)
            cor = random.choice(cores)
            item = self.confetti_canvas.create_oval(x, y, x+size, y+size, fill=cor, outline="")
            self.confetti_items.append(item)

        self._animate_confetti(steps=60)

    def _animate_confetti(self, steps: int):
        if self.confetti_canvas is None:
            return
        w = self.winfo_width()
        h = self.winfo_height()

        for item in self.confetti_items:
            dx = random.randint(-3, 3)
            dy = random.randint(4, 9)
            self.confetti_canvas.move(item, dx, dy)
            # reaparece no topo quando chegar embaixo
            x1, y1, x2, y2 = self.confetti_canvas.coords(item)
            if y1 > h:
                nx = random.randint(0, w)
                self.confetti_canvas.coords(item, nx, -10, nx+8, -2)

        if steps > 0:
            self.after(30, lambda: self._animate_confetti(steps-1))
        else:
            # Fade out simples
            self.after(200, self._stop_confetti)

    def _stop_confetti(self):
        if self.confetti_canvas is not None:
            self.confetti_canvas.destroy()
            self.confetti_canvas = None
            self.confetti_items.clear()

    def _sobre(self):
        messagebox.showinfo(
            "Sobre",
            "Bagels (GUI+)\n\nAdivinhe o número secreto sem dígitos repetidos.\n"
            "Dicas: Certo (posição certa), Quase (posição errada), Nada (nenhum dígito).\n\n"
            "Extras: Teclado na tela, Modo fácil, Animação de confete.\n"
            "Baseado no projeto 'Bagels' de Al Sweigart."
        )


if __name__ == "__main__":
    BagelsApp().mainloop()
