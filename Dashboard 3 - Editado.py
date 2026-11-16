# Dashboard Meteorológico (versão 3 melhorada)
# Lê o CSV da estação e mostra um gráfico limpo da temperatura, com linha da
# média, destaque da máxima/mínima, resumo em cards e barra de zoom.
import csv
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)

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
COR_LINHA = "#5B8DEF"      # linha da temperatura
COR_MAX = "#F87171"
COR_MIN = "#38BDF8"
COR_MEDIA = "#34D399"

FORMATOS_DATA = (
    "%Y-%m-%d, %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y, %H:%M:%S", "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y, %H:%M", "%d/%m/%Y %H:%M",
)


def converter_numero(texto):
    """Converte textos como '14.72 °C' em número (float)."""
    return float(texto.replace("°C", "").replace(",", ".").strip())


def interpretar_data(texto):
    """Tenta transformar o texto em data/hora; devolve None se não der."""
    texto = texto.strip()
    for formato in FORMATOS_DATA:
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return None


# --- JANELA PRINCIPAL ---
janela = tk.Tk()
janela.title("Dashboard Meteorológico - Tkinter & Matplotlib")
janela.geometry("900x660")
janela.minsize(720, 520)
janela.configure(bg=COR_FUNDO)

# --- CABEÇALHO ---
topo = tk.Frame(janela, bg=COR_TOPO, highlightbackground=COR_BORDA,
                highlightthickness=1)
topo.pack(fill="x")
tk.Label(topo, text="📈  Evolução da Temperatura", bg=COR_TOPO, fg="white",
         font=("Segoe UI", 16, "bold")).pack(side="left", padx=16, pady=12)
botao = tk.Button(topo, text="Carregar dados e gerar gráfico", bg=COR_AZUL,
                  fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", padx=14, pady=4,
                  activebackground=COR_AZUL_ESCURO, activeforeground="white")
botao.pack(side="right", padx=16)

# --- CARDS DE RESUMO ---
linha_cards = tk.Frame(janela, bg=COR_FUNDO)
linha_cards.pack(fill="x", padx=16, pady=(12, 0))
valores = {}
for i, (chave, titulo, cor) in enumerate([
    ("media", "MÉDIA", COR_MEDIA),
    ("min", "MÍNIMA", COR_MIN),
    ("max", "MÁXIMA", COR_MAX),
    ("n", "REGISTROS", COR_SUAVE),
]):
    c = tk.Frame(linha_cards, bg=COR_CARD, highlightbackground=COR_BORDA,
                 highlightthickness=1)
    c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
    linha_cards.columnconfigure(i, weight=1)
    tk.Label(c, text=titulo, bg=COR_CARD, fg=COR_SUAVE,
             font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
    valores[chave] = tk.Label(c, text="--", bg=COR_CARD, fg=cor,
                              font=("Segoe UI", 18, "bold"))
    valores[chave].pack(anchor="w", padx=12, pady=(0, 8))

# --- ÁREA DO GRÁFICO ---
area = tk.Frame(janela, bg=COR_CARD, highlightbackground=COR_BORDA,
                highlightthickness=1)
area.pack(fill="both", expand=True, padx=16, pady=12)

fig = plt.Figure(figsize=(9, 5), dpi=100, facecolor=COR_CARD)
canvas = FigureCanvasTkAgg(fig, master=area)
barra_ferramentas = NavigationToolbar2Tk(canvas, area)  # zoom, mover e salvar
barra_ferramentas.update()
barra_ferramentas.config(background="#CBD5E1")
for _filho in barra_ferramentas.winfo_children():
    try:
        _filho.config(background="#CBD5E1")
    except tk.TclError:
        pass
canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)


def desenhar_vazio():
    fig.clear()
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.5, 0.5, "Clique em “Carregar dados e gerar gráfico”",
            ha="center", va="center", color=COR_SUAVE, fontsize=12)
    canvas.draw()


# --- FUNÇÃO PRINCIPAL: lê o arquivo e desenha o gráfico ---
def gerar_dashboard():
    caminho = NOME_ARQUIVO
    if not os.path.exists(caminho):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo CSV da estação",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")])
        if not caminho:
            return

    textos_data, horas, temperaturas = [], [], []
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
                    continue
                textos_data.append(linha[0])
                horas.append(linha[0].split(",")[-1].strip())
                temperaturas.append(temp)
    except (OSError, UnicodeDecodeError) as erro:
        messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{erro}")
        return

    if not temperaturas:
        messagebox.showwarning("Aviso", "Nenhum dado encontrado para exibir no gráfico.")
        return

    # Estatísticas
    n = len(temperaturas)
    media = sum(temperaturas) / n
    t_max, t_min = max(temperaturas), min(temperaturas)
    i_max, i_min = temperaturas.index(t_max), temperaturas.index(t_min)

    valores["media"].config(text=f"{media:.1f} °C")
    valores["min"].config(text=f"{t_min:.1f} °C")
    valores["max"].config(text=f"{t_max:.1f} °C")
    valores["n"].config(text=str(n))

    # Tenta usar datas reais no eixo X; se não der, usa a posição (0, 1, 2...)
    datas = [interpretar_data(t) for t in textos_data]
    usa_datas = all(d is not None for d in datas)
    x = datas if usa_datas else list(range(n))

    # --- DESENHO DO GRÁFICO ---
    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_facecolor(COR_CARD)

    ax.plot(x, temperaturas, color=COR_LINHA, linewidth=1.8,
            marker="o" if n <= 60 else None, markersize=4, label="Temperatura")
    ax.fill_between(x, temperaturas, t_min, color=COR_LINHA, alpha=0.18)
    ax.axhline(media, color=COR_MEDIA, linestyle="--", linewidth=1.5,
               label=f"Média ({media:.1f} °C)")

    # Destaque da máxima e da mínima
    ax.scatter([x[i_max]], [t_max], color=COR_MAX, s=60, zorder=5)
    ax.annotate(f"Máx {t_max:.1f} °C", (x[i_max], t_max), xytext=(0, 10),
                textcoords="offset points", ha="center", fontsize=9,
                fontweight="bold", color=COR_MAX)
    ax.scatter([x[i_min]], [t_min], color=COR_MIN, s=60, zorder=5)
    ax.annotate(f"Mín {t_min:.1f} °C", (x[i_min], t_min), xytext=(0, -16),
                textcoords="offset points", ha="center", fontsize=9,
                fontweight="bold", color=COR_MIN)

    # Eixo X
    if usa_datas:
        localizador = mdates.AutoDateLocator()
        ax.xaxis.set_major_locator(localizador)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(localizador))
    else:
        passo = max(1, n // 10)  # mostra no máximo ~10 horários
        posicoes = list(range(0, n, passo))
        ax.set_xticks(posicoes)
        ax.set_xticklabels([horas[i] for i in posicoes], rotation=45, ha="right")

    # Estilo
    ax.set_title("Evolução da Temperatura ao Longo do Tempo", fontsize=13,
                 fontweight="bold", color=COR_TEXTO, pad=12)
    ax.set_xlabel("Horário" if not usa_datas else "Data / Hora", color=COR_SUAVE)
    ax.set_ylabel("Temperatura (°C)", color=COR_SUAVE)
    ax.set_ylim(t_min - 1.5, t_max + 2)
    ax.grid(True, color=COR_BORDA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#334155")
    ax.tick_params(colors=COR_SUAVE)
    ax.legend(loc="upper right", frameon=False, labelcolor=COR_TEXTO)

    fig.tight_layout()
    barra_ferramentas.update()
    canvas.draw()


botao.config(command=gerar_dashboard)
desenhar_vazio()
janela.mainloop()