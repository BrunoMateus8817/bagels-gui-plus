# Birthday Paradox Interactive 🎂

Uma aplicação em Python com interface gráfica (Tkinter) que simula o famoso **Paradoxo do Aniversário**.  
O programa calcula a probabilidade de, em um grupo de `n` pessoas, pelo menos duas compartilharem a mesma data de aniversário.

---

## 📖 Sobre o Paradoxo do Aniversário
O Paradoxo do Aniversário é um problema de probabilidade que demonstra que, em um grupo relativamente pequeno de pessoas, é surpreendentemente provável que duas compartilhem a mesma data de aniversário.  

Por exemplo:
- Em um grupo de **23 pessoas**, a chance é de aproximadamente **50%**.
- Em um grupo de **50 pessoas**, a probabilidade passa de **96%**.

---

## ✨ Funcionalidades
- Interface gráfica amigável usando **Tkinter**.
- Entrada de:
  - Número de pessoas.
  - Número de simulações.
  - Consideração de ano bissexto (366 dias).
  - Semente opcional para reprodutibilidade.
- Visualização gráfica da distribuição dos aniversários.
  - **Vermelho**: datas repetidas.
  - **Azul**: datas únicas.
- Exportação dos resultados para CSV.
- Copiar resultados diretamente da interface.

---

## 🚀 Como Executar

### **Pré-requisitos**
- **Python 3.8+**
- Bibliotecas:
  ```bash
  pip install matplotlib pandas

🛠 Tecnologias

Python 3.8+

Tkinter — Interface gráfica

Matplotlib — Visualização de gráficos

Pandas — Manipulação de dados

📚 Referência

Livro: The Big Book of Small Python Projects

Autor: Al Sweigart