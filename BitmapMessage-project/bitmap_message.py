import tkinter as tk
import random

# ----------------------------
# Configurações
# ----------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 250
FONT_SIZE = 50
BASE_SPEED = 5
GRADIENT_COLORS = [
    "#FF0000", "#FF4500", "#FF8C00", "#FFD700", "#ADFF2F", "#00FA9A",
    "#00CED1", "#1E90FF", "#8A2BE2", "#FF1493"
]

# ----------------------------
# Função principal do letreiro
# ----------------------------
def start_ultra_cinematic_marquee():
    message = entry.get().upper()
    canvas.delete("all")  # limpa o canvas

    letters = []
    x_pos = WINDOW_WIDTH
    for char in message:
        # Criar sombra
        shadow_id = canvas.create_text(
            x_pos+3, WINDOW_HEIGHT//2+3, text=char,
            font=("Courier", FONT_SIZE, "bold"), fill="gray20"
        )
        # Criar letra
        color = random.choice(GRADIENT_COLORS)
        letter_id = canvas.create_text(
            x_pos, WINDOW_HEIGHT//2, text=char,
            font=("Courier", FONT_SIZE, "bold"), fill=color
        )
        letters.append({"id": letter_id, "shadow": shadow_id, "color_index": GRADIENT_COLORS.index(color), "alpha": 0})
        x_pos += FONT_SIZE  # espaçamento entre letras

    # Função para converter índice de cor para hex
    def get_color(index):
        return GRADIENT_COLORS[index % len(GRADIENT_COLORS)]

    # Função para converter alpha em cor cinza
    def alpha_to_gray(alpha):
        val = int(50 + 205 * (1 - alpha))  # 50 a 255
        val = max(0, min(255, val))
        return f"#{val:02x}{val:02x}{val:02x}"

    # Função de animação
    def animate():
        speed = speed_slider.get()
        for letter in letters:
            # Move letra e sombra
            canvas.move(letter["id"], -speed, 0)
            canvas.move(letter["shadow"], -speed, 0)
            
            # Gradiente contínuo
            letter["color_index"] += 1
            canvas.itemconfig(letter["id"], fill=get_color(letter["color_index"]))
            
            # Fade in e fade out
            letter["alpha"] += 0.05  # fade in
            if letter["alpha"] > 1:
                letter["alpha"] = 1
            
            # Piscar aleatório
            if random.random() < 0.02:
                letter["alpha"] = random.uniform(0.3, 1)
            
            # Ajusta sombra para acompanhar a letra
            canvas.itemconfig(letter["shadow"], fill=alpha_to_gray(letter['alpha']))

        # Remove letras que saíram da tela
        for letter in letters[:]:
            coords = canvas.coords(letter["id"])
            if coords[0] < -FONT_SIZE:
                canvas.delete(letter["id"])
                canvas.delete(letter["shadow"])
                letters.remove(letter)
        
        if letters:
            canvas.after(50, animate)

    animate()

# ----------------------------
# Janela Tkinter
# ----------------------------
root = tk.Tk()
root.title("Letreiro Ultra Cinematográfico")
root.resizable(False, False)

# Canvas
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
canvas.pack()

# Entrada de mensagem
entry = tk.Entry(root, font=("Arial", 16))
entry.pack(fill="x", padx=10, pady=5)
entry.insert(0, "Digite sua mensagem aqui")

# Botão iniciar
start_button = tk.Button(root, text="Iniciar Letreiro Ultra Cinematográfico", command=start_ultra_cinematic_marquee)
start_button.pack(pady=5)

# Slider de velocidade
speed_slider = tk.Scale(root, from_=1, to=20, orient="horizontal", label="Velocidade")
speed_slider.set(BASE_SPEED)
speed_slider.pack(fill="x", padx=20, pady=5)

root.mainloop()
