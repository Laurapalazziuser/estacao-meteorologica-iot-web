# Dashboard Meteorológico (versão 2 melhorada)
# Lê o CSV da estação, mostra os dados em uma tabela e apresenta a média
# de forma visual: número grande, classificação (Frio, Agradável...) e um
# medidor colorido com um marcador indicando onde a média está.
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

NOME_ARQUIVO = "c:/Users/eliel/OneDrive/Documentos/dados_estacao_meteorologica_set_out_2026.csv"

# --- PALETA DE CORES ---
# Tons tirados do site: fundo azul-marinho escuro, cards azul-acinzentados
# e azul vibrante (o mesmo da esfera da página inicial).
COR_FUNDO = "#0E111C"
COR_CARD = "#141C2C"
COR_BORDA = "#1F2A3F"
COR_TEXTO = "#E2E8F0"
COR_SUAVE = "#94A3B8"
COR_TOPO = "#0B0F1A"
COR_AZUL = "#3067CD"
COR_AZUL_ESCURO = "#2D45C8"
COR_TITULO = "#5B8DEF"

# Faixas de temperatura: (limite superior, nome, cor)
FAIXAS = [
    (10, "Frio", "#3B82F6"),
    (18, "Fresco", "#06B6D4"),
    (25, "Agradável", "#10B981"),
    (30, "Quente", "#F59E0B"),
    (60, "Muito quente", "#EF4444"),
]
ESCALA_MIN, ESCALA_MAX = 0, 40  # intervalo mostrado no medidor (°C)


def converter_numero(texto):
    """Converte textos como '14,72 °C' ou '63 %' em número (float)."""
    limpo = texto.replace("°C", "").replace("%", "").replace(",", ".").strip()
    return float(limpo)


def classificar(temp):
    """Devolve (nome, cor) da faixa em que a temperatura se encaixa."""
    for limite, nome, cor in FAIXAS:
        if temp < limite:
            return nome, cor
    return FAIXAS[-1][1], FAIXAS[-1][2]


# --- JANELA PRINCIPAL ---
janela = tk.Tk()
janela.title("Dashboard Meteorológico - Python")
janela.geometry("820x700")
janela.minsize(700, 600)
janela.configure(bg=COR_FUNDO)

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("Treeview", rowheight=24, font=("Segoe UI", 10),
                 background=COR_CARD, fieldbackground=COR_CARD,
                 foreground=COR_TEXTO, borderwidth=0)
estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                 background=COR_AZUL_ESCURO, foreground="white", relief="flat")
estilo.map("Treeview.Heading", background=[("active", COR_AZUL)])
estilo.map("Treeview", background=[("selected", "#1E3A6B")],
           foreground=[("selected", "white")])
estilo.configure("Vertical.TScrollbar", background=COR_BORDA, troughcolor=COR_CARD,
                 bordercolor=COR_CARD, arrowcolor=COR_SUAVE)

# --- CABEÇALHO ---
topo = tk.Frame(janela, bg=COR_TOPO, highlightbackground=COR_BORDA,
                highlightthickness=1)
topo.pack(fill="x")
tk.Label(topo, text="🌡️  Dashboard Meteorológico", bg=COR_TOPO, fg="white",
         font=("Segoe UI", 16, "bold")).pack(side="left", padx=16, pady=12)
botao = tk.Button(topo, text="Carregar dados", bg=COR_AZUL, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  padx=14, pady=4, activebackground=COR_AZUL_ESCURO,
                  activeforeground="white")
botao.pack(side="right", padx=16)

corpo = tk.Frame(janela, bg=COR_FUNDO)
corpo.pack(fill="both", expand=True, padx=16, pady=12)


def criar_card(pai):
    return tk.Frame(pai, bg=COR_CARD, highlightbackground=COR_BORDA,
                    highlightthickness=1)


# --- CARD PRINCIPAL: A MÉDIA ---
card_media = criar_card(corpo)
card_media.pack(fill="x")

tk.Label(card_media, text="TEMPERATURA MÉDIA", bg=COR_CARD, fg=COR_SUAVE,
         font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(12, 0))

linha_media = tk.Frame(card_media, bg=COR_CARD)
linha_media.pack(fill="x", padx=16)
lbl_media = tk.Label(linha_media, text="--", bg=COR_CARD, fg=COR_TEXTO,
                     font=("Segoe UI", 40, "bold"))
lbl_media.pack(side="left")
lbl_faixa = tk.Label(linha_media, text="", bg=COR_CARD, fg="white",
                     font=("Segoe UI", 11, "bold"), padx=12, pady=3)
lbl_faixa.pack(side="left", padx=14)

lbl_sub = tk.Label(card_media, text="Clique em “Carregar dados” para começar.",
                   bg=COR_CARD, fg=COR_SUAVE, font=("Segoe UI", 10))
lbl_sub.pack(anchor="w", padx=16)

medidor = tk.Canvas(card_media, height=58, bg=COR_CARD, highlightthickness=0)
medidor.pack(fill="x", padx=16, pady=(6, 12))

valor_medidor = {"temp": None}


def desenhar_medidor(event=None):
    """Desenha a barra colorida com um marcador na posição da média."""
    medidor.delete("all")
    largura = medidor.winfo_width()
    if largura < 50:
        return
    x0, x1, y0, y1 = 10, largura - 10, 22, 38
    total = ESCALA_MAX - ESCALA_MIN

    def pos(t):
        t = max(ESCALA_MIN, min(ESCALA_MAX, t))
        return x0 + (t - ESCALA_MIN) / total * (x1 - x0)

    # Segmentos coloridos de cada faixa
    inicio = ESCALA_MIN
    for limite, _, cor in FAIXAS:
        fim = min(limite, ESCALA_MAX)
        if fim > inicio:
            medidor.create_rectangle(pos(inicio), y0, pos(fim), y1, fill=cor, outline="")
        inicio = fim
    # Números da escala
    for t in range(ESCALA_MIN, ESCALA_MAX + 1, 10):
        medidor.create_text(pos(t), 50, text=f"{t}°", fill=COR_SUAVE,
                            font=("Segoe UI", 8))
    # Marcador da média
    if valor_medidor["temp"] is not None:
        x = pos(valor_medidor["temp"])
        medidor.create_polygon(x - 7, 4, x + 7, 4, x, 20, fill=COR_TEXTO, outline="")
        medidor.create_line(x, 20, x, y1 + 4, fill=COR_TEXTO, width=2)


medidor.bind("<Configure>", desenhar_medidor)

# --- CARDS SECUNDÁRIOS ---
linha_cards = tk.Frame(corpo, bg=COR_FUNDO)
linha_cards.pack(fill="x", pady=10)
valores = {}
for i, (chave, titulo, cor) in enumerate([
    ("min", "MÍNIMA", "#60A5FA"),
    ("max", "MÁXIMA", "#F87171"),
    ("umid", "UMIDADE MÉDIA", "#38BDF8"),
    ("n", "REGISTROS", COR_SUAVE),
]):
    c = criar_card(linha_cards)
    c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
    linha_cards.columnconfigure(i, weight=1)
    tk.Label(c, text=titulo, bg=COR_CARD, fg=COR_SUAVE,
             font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
    valores[chave] = tk.Label(c, text="--", bg=COR_CARD, fg=cor,
                              font=("Segoe UI", 18, "bold"))
    valores[chave].pack(anchor="w", padx=12, pady=(0, 8))

# --- TABELA DE DADOS ---
frame_tabela = criar_card(corpo)
frame_tabela.pack(fill="both", expand=True)
tabela = ttk.Treeview(frame_tabela, columns=("data", "temp", "umid"), show="headings")
tabela.heading("data", text="Data / Hora")
tabela.heading("temp", text="Temperatura")
tabela.heading("umid", text="Umidade")
tabela.column("data", width=280, anchor="w")
tabela.column("temp", width=140, anchor="center")
tabela.column("umid", width=140, anchor="center")
tabela.tag_configure("impar", background="#101826")
barra = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
tabela.configure(yscrollcommand=barra.set)
barra.pack(side="right", fill="y")
tabela.pack(side="left", fill="both", expand=True)


# --- FUNÇÃO EXECUTADA AO CLICAR NO BOTÃO ---
def carregar_dados():
    caminho = NOME_ARQUIVO
    if not os.path.exists(caminho):
        # Se o arquivo não estiver no caminho padrão, deixa o usuário escolher
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo CSV da estação",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")])
        if not caminho:
            return

    linhas, temps, umids = [], [], []
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            leitor = csv.reader(arquivo, delimiter=";")
            next(leitor, None)  # pula o cabeçalho
            for linha in leitor:
                if len(linha) < 6:
                    continue
                try:
                    temp = converter_numero(linha[1])
                except ValueError:
                    continue  # ignora linhas com temperatura inválida
                try:
                    umids.append(converter_numero(linha[2]))
                except ValueError:
                    pass
                temps.append(temp)
                linhas.append((linha[0], linha[1], linha[2]))
    except (OSError, UnicodeDecodeError) as erro:
        messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{erro}")
        return

    if not temps:
        messagebox.showwarning("Aviso", "Nenhum dado válido encontrado no arquivo.")
        return

    # Preenche a tabela
    tabela.delete(*tabela.get_children())
    for i, reg in enumerate(linhas):
        tabela.insert("", "end", values=reg, tags=("impar",) if i % 2 else ())

    # Estatísticas
    media = sum(temps) / len(temps)
    nome, cor = classificar(media)
    lbl_media.config(text=f"{media:.1f} °C")
    lbl_faixa.config(text=nome, bg=cor)
    lbl_sub.config(text=f"Média de {len(temps)} medições  •  "
                        f"variação de {min(temps):.1f} a {max(temps):.1f} °C")
    valores["min"].config(text=f"{min(temps):.1f} °C")
    valores["max"].config(text=f"{max(temps):.1f} °C")
    valores["umid"].config(text=f"{sum(umids) / len(umids):.0f} %" if umids else "--")
    valores["n"].config(text=str(len(temps)))

    valor_medidor["temp"] = media
    desenhar_medidor()


botao.config(command=carregar_dados)
janela.mainloop()