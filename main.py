import tkinter as tk
from tkinter import ttk, messagebox
import mido


# ============================================================
# CONFIGURAÇÕES
# ============================================================

NOTAS = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]

# Classes de altura (pitch class, 0-11) que correspondem
# às teclas brancas e pretas de um piano
BRANCAS_PC = {0, 2, 4, 5, 7, 9, 11}   # C D E F G A B
PRETAS_PC = {1, 3, 6, 8, 10}          # C# D# F# G# A#

# Faixa de um piano de 88 teclas: A0 (21) até C8 (108)
NOTA_MIN = 21
NOTA_MAX = 108

# ------------------------------------------------------------
# FÓRMULAS DE ACORDES
# ------------------------------------------------------------
# Cada fórmula é o conjunto de intervalos (em semitons) entre
# cada nota do acorde e a fundamental (que é sempre o intervalo 0).
# O reconhecimento testa cada nota tocada como possível fundamental
# e vê se o conjunto de intervalos resultante bate com alguma
# fórmula abaixo.
# ------------------------------------------------------------

TRIADES = {
    frozenset({0, 4, 7}): "MAIOR",
    frozenset({0, 3, 7}): "MENOR",
    frozenset({0, 3, 6}): "DIMINUTA",
    frozenset({0, 4, 8}): "AUMENTADA",
    frozenset({0, 2, 7}): "SUS2",
    frozenset({0, 5, 7}): "SUS4",
}

TETRADES = {
    frozenset({0, 4, 7, 11}): "MAIOR 7 (maj7)",
    frozenset({0, 4, 7, 10}): "7 (dominante)",
    frozenset({0, 3, 7, 10}): "MENOR 7 (m7)",
    frozenset({0, 3, 7, 11}): "MENOR COM 7 MAIOR (mMaj7)",
    frozenset({0, 3, 6, 9}): "DIMINUTO 7 (dim7)",
    frozenset({0, 3, 6, 10}): "MEIO-DIMINUTO (m7b5)",
    frozenset({0, 4, 8, 10}): "AUMENTADO 7 (aug7)",
    frozenset({0, 4, 7, 9}): "6 (sexta)",
    frozenset({0, 3, 7, 9}): "MENOR 6 (m6)",
}


# ============================================================
# VARIÁVEIS GLOBAIS
# ============================================================

teclado_midi = None
notas_pressionadas = set()

# Nota atualmente sendo tocada pelo mouse (para permitir soltar
# corretamente mesmo se o cursor sair de cima da tecla)
nota_mouse_ativa = None


# ============================================================
# CONVERSÃO MIDI -> NOTA
# ============================================================

def numero_para_nota(numero_midi):
    """
    Converte um número MIDI para o nome da nota.

    Exemplo:
    60 -> C
    64 -> E
    67 -> G
    """

    return NOTAS[numero_midi % 12]


def numero_para_oitava(numero_midi):
    """
    Converte um número MIDI para o número da oitava
    (padrão onde a nota 60 = C4).
    """

    return numero_midi // 12 - 1


# ============================================================
# IDENTIFICAÇÃO DE ACORDES
# ============================================================

def identificar_acorde(notas):
    """
    Identifica tríades (maior, menor, diminuta, aumentada, sus2, sus4)
    e tétrades com sétima/sexta (7, maj7, m7, dim7, m7b5, aug7, 6, m6).

    Notas repetidas em oitavas diferentes contam como uma única nota
    para fins de identificação do acorde.

    Exemplos:

    C E G       -> C MAIOR
    C D# G      -> C MENOR
    C D# F#     -> C DIMINUTA
    C E G#      -> C AUMENTADA
    C F G       -> C SUS4
    C E G A#    -> C 7
    C E G B     -> C MAIOR 7 (maj7)
    """

    # Remove notas repetidas (mesma classe, oitavas diferentes),
    # preservando a ordem em que apareceram
    notas_unicas = list(dict.fromkeys(notas))

    quantidade = len(notas_unicas)

    if quantidade < 3:
        return "AGUARDANDO 3 NOTAS"

    if quantidade == 3:
        formulas = TRIADES

    elif quantidade == 4:
        formulas = TETRADES

    else:
        return "MUITAS NOTAS DIFERENTES (máx. 4)"

    for fundamental in notas_unicas:

        indice_fundamental = NOTAS.index(fundamental)

        intervalos = set()

        for nota in notas_unicas:

            indice_nota = NOTAS.index(nota)

            intervalo = (
                indice_nota - indice_fundamental
            ) % 12

            intervalos.add(intervalo)

        nome_formula = formulas.get(frozenset(intervalos))

        if nome_formula is not None:
            return f"{fundamental} {nome_formula}"

    return "ACORDE DESCONHECIDO"


# ============================================================
# OBTER NOTAS ATUAIS
# ============================================================

def obter_nomes_das_notas():

    return [
        numero_para_nota(numero)
        for numero in sorted(notas_pressionadas)
    ]


# ============================================================
# ATUALIZAR INTERFACE
# ============================================================

def atualizar_interface():

    notas = obter_nomes_das_notas()

    # -----------------------------------------
    # Notas
    # -----------------------------------------

    if notas:

        texto_notas = "  •  ".join(notas)

    else:

        texto_notas = "Nenhuma nota pressionada"

    label_notas.config(
        text=texto_notas
    )

    # -----------------------------------------
    # Acorde
    # -----------------------------------------

    acorde = identificar_acorde(notas)

    label_acorde.config(
        text=acorde
    )

    # -----------------------------------------
    # Teclado visual
    # -----------------------------------------

    atualizar_teclado_visual()

    janela.after(50, atualizar_interface)


# ============================================================
# ATUALIZAR TECLADO VISUAL
# ============================================================

def atualizar_teclado_visual():

    for numero, item in teclas_visuais.items():

        branca = numero_e_branca[numero]

        if numero in notas_pressionadas:

            cor = "#4CAF50"

        else:

            cor = "white" if branca else "#202020"

        canvas_teclado.itemconfig(item, fill=cor)


# ============================================================
# PROCESSAR MENSAGEM MIDI
# ============================================================

def processar_mensagem(mensagem):

    # -----------------------------------------
    # Tecla pressionada
    # -----------------------------------------

    if (
        mensagem.type == "note_on"
        and mensagem.velocity > 0
    ):

        notas_pressionadas.add(mensagem.note)

    # -----------------------------------------
    # Tecla solta
    # -----------------------------------------

    elif (
        mensagem.type == "note_off"
        or (
            mensagem.type == "note_on"
            and mensagem.velocity == 0
        )
    ):

        notas_pressionadas.discard(
            mensagem.note
        )


# ============================================================
# VERIFICAR MIDI
# ============================================================
#
# CORREÇÃO DO BUG "só reconhece quando aperta 2 vezes":
#
# O código original fazia:
#
#     while teclado_midi.poll():
#         mensagem = teclado_midi.receive()
#
# O método poll() do mido já CONSOME a mensagem pendente da fila
# (ele funciona como um receive não-bloqueante) apenas para
# verificar "existe algo?". A mensagem que ele acabou de puxar
# é descartada, e o receive() logo em seguida pega a PRÓXIMA
# mensagem da fila. Ou seja, a cada 2 eventos MIDI enviados pelo
# teclado, só 1 era realmente processado — por isso era preciso
# apertar a tecla duas vezes para o app perceber.
#
# A forma correta e segura de esvaziar a fila sem perder mensagens
# é usar iter_pending(), que devolve todas as mensagens pendentes
# sem descartar nenhuma.
# ============================================================

def verificar_midi():

    if teclado_midi is not None:

        try:

            for mensagem in teclado_midi.iter_pending():

                processar_mensagem(mensagem)

        except Exception as erro:

            print("Erro MIDI:", erro)

            status_var.set(
                "🔴 Erro na comunicação MIDI"
            )

    janela.after(10, verificar_midi)


# ============================================================
# CONECTAR AO MIDI
# ============================================================

def conectar_midi():

    global teclado_midi

    portas = mido.get_input_names()

    if not portas:

        messagebox.showwarning(
            "MIDI",
            "Nenhum dispositivo MIDI encontrado.\n\n"
            "Conecte o teclado e tente novamente."
        )

        status_var.set(
            "Nenhum dispositivo MIDI encontrado"
        )

        return

    # -----------------------------------------
    # Janela de seleção
    # -----------------------------------------

    janela_selecao = tk.Toplevel(janela)

    janela_selecao.title(
        "Selecionar dispositivo MIDI"
    )

    janela_selecao.geometry(
        "500x300"
    )

    janela_selecao.resizable(
        False,
        False
    )

    tk.Label(
        janela_selecao,
        text="Selecione seu teclado MIDI",
        font=("Arial", 18, "bold")
    ).pack(pady=30)

    dispositivo_var = tk.StringVar()

    combo = ttk.Combobox(
        janela_selecao,
        textvariable=dispositivo_var,
        values=portas,
        state="readonly",
        font=("Arial", 12),
        width=45
    )

    combo.pack()

    combo.current(0)

    def confirmar():

        global teclado_midi

        nome = dispositivo_var.get()

        try:

            if teclado_midi is not None:

                teclado_midi.close()

            teclado_midi = mido.open_input(nome)

            status_var.set(
                "🟢 MIDI conectado: " + nome
            )

            janela_selecao.destroy()

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível conectar ao MIDI.\n\n{erro}"
            )

    tk.Button(
        janela_selecao,
        text="CONECTAR",
        command=confirmar,
        font=("Arial", 13, "bold"),
        padx=20,
        pady=8
    ).pack(pady=30)


# ============================================================
# LIMPAR NOTAS
# ============================================================

def limpar_notas():

    global nota_mouse_ativa

    notas_pressionadas.clear()

    nota_mouse_ativa = None


# ============================================================
# TECLADO VIRTUAL (88 TECLAS, A0 -> C8)
# ============================================================
#
# É desenhado num Canvas (em vez de 88 widgets Button) para
# ficar leve e permitir posicionamento preciso das teclas pretas
# sobre as brancas, com rolagem horizontal já que 88 teclas não
# cabem lado a lado numa janela comum.
# ============================================================

LARGURA_BRANCA = 32
ALTURA_BRANCA = 150

LARGURA_PRETA = int(LARGURA_BRANCA * 58 / 95)
ALTURA_PRETA = int(ALTURA_BRANCA * 105 / 170)

OFFSET_PRETA = 0.68  # fração da largura da tecla branca anterior


def criar_teclado_virtual():

    global canvas_teclado, teclas_visuais, numero_e_branca

    teclas_visuais = {}     # numero_midi -> id do item no canvas
    numero_e_branca = {}    # numero_midi -> True/False (branca/preta)

    frame_teclado = tk.Frame(
        janela,
        bg="#202020"
    )

    frame_teclado.pack(
        fill="x",
        padx=20,
        pady=20
    )

    canvas_teclado = tk.Canvas(
        frame_teclado,
        height=ALTURA_BRANCA,
        bg="#202020",
        highlightthickness=0
    )

    barra_rolagem = tk.Scrollbar(
        frame_teclado,
        orient="horizontal",
        command=canvas_teclado.xview
    )

    canvas_teclado.configure(
        xscrollcommand=barra_rolagem.set
    )

    canvas_teclado.pack(
        side="top",
        fill="x"
    )

    barra_rolagem.pack(
        side="top",
        fill="x"
    )

    # -----------------------------------------
    # Teclas brancas
    # -----------------------------------------

    indice_branco = 0
    posicao_branca = {}  # numero_midi -> índice da tecla branca

    for numero in range(NOTA_MIN, NOTA_MAX + 1):

        pc = numero % 12

        if pc in BRANCAS_PC:

            x = indice_branco * LARGURA_BRANCA

            item = canvas_teclado.create_rectangle(
                x, 0,
                x + LARGURA_BRANCA, ALTURA_BRANCA,
                fill="white",
                outline="#555555",
                width=1
            )

            # Rótulo só na tecla "C" de cada oitava, para orientação
            if numero_para_nota(numero) == "C":

                canvas_teclado.create_text(
                    x + LARGURA_BRANCA / 2,
                    ALTURA_BRANCA - 12,
                    text=f"C{numero_para_oitava(numero)}",
                    font=("Arial", 7),
                    fill="#999999"
                )

            teclas_visuais[numero] = item
            numero_e_branca[numero] = True
            posicao_branca[numero] = indice_branco

            indice_branco += 1

    largura_total = indice_branco * LARGURA_BRANCA

    canvas_teclado.configure(
        scrollregion=(0, 0, largura_total, ALTURA_BRANCA)
    )

    # -----------------------------------------
    # Teclas pretas (desenhadas por cima das brancas)
    # -----------------------------------------

    for numero in range(NOTA_MIN, NOTA_MAX + 1):

        pc = numero % 12

        if pc in PRETAS_PC:

            # A tecla anterior (numero - 1) é sempre uma tecla
            # branca, então usamos a posição dela como referência
            indice_branca_anterior = posicao_branca[numero - 1]

            x = (
                indice_branca_anterior * LARGURA_BRANCA
                + OFFSET_PRETA * LARGURA_BRANCA
            )

            item = canvas_teclado.create_rectangle(
                x, 0,
                x + LARGURA_PRETA, ALTURA_PRETA,
                fill="#202020",
                outline="black",
                width=1
            )

            teclas_visuais[numero] = item
            numero_e_branca[numero] = False

    # -----------------------------------------
    # Interação com o mouse
    # -----------------------------------------

    canvas_teclado.bind("<ButtonPress-1>", ao_pressionar_mouse)
    canvas_teclado.bind("<B1-Motion>", ao_arrastar_mouse)
    canvas_teclado.bind("<ButtonRelease-1>", ao_soltar_mouse)

    # Começa a visão já em torno do dó central (C4)
    janela.after(
        50,
        lambda: canvas_teclado.xview_moveto(
            max(0, (posicao_branca.get(60, 0) - 6) / max(indice_branco, 1))
        )
    )


def nota_sob_cursor(x, y):
    """
    Retorna o número MIDI da tecla que está sob o cursor,
    dando prioridade às teclas pretas (que ficam por cima).
    """

    x_canvas = canvas_teclado.canvasx(x)

    itens = canvas_teclado.find_overlapping(
        x_canvas, y, x_canvas, y
    )

    if not itens:

        return None

    # O último item da lista é o que está mais no topo (desenhado
    # por último) — nesse caso, uma tecla preta, se houver alguma ali
    item_no_topo = itens[-1]

    for numero, item in teclas_visuais.items():

        if item == item_no_topo:

            return numero

    return None


def ao_pressionar_mouse(evento):

    global nota_mouse_ativa

    numero = nota_sob_cursor(evento.x, evento.y)

    if numero is not None:

        notas_pressionadas.add(numero)

        nota_mouse_ativa = numero


def ao_arrastar_mouse(evento):

    global nota_mouse_ativa

    numero = nota_sob_cursor(evento.x, evento.y)

    if numero != nota_mouse_ativa:

        if nota_mouse_ativa is not None:

            notas_pressionadas.discard(nota_mouse_ativa)

        if numero is not None:

            notas_pressionadas.add(numero)

        nota_mouse_ativa = numero


def ao_soltar_mouse(evento):

    global nota_mouse_ativa

    if nota_mouse_ativa is not None:

        notas_pressionadas.discard(nota_mouse_ativa)

    nota_mouse_ativa = None


# ============================================================
# CONFIGURAÇÃO DA JANELA
# ============================================================

janela = tk.Tk()

janela.title(
    "Identificador de Acordes MIDI"
)

janela.geometry(
    "900x700"
)

janela.minsize(
    900,
    700
)

janela.configure(
    bg="#f2f2f2"
)


# ============================================================
# CABEÇALHO
# ============================================================

frame_titulo = tk.Frame(
    janela,
    bg="#f2f2f2"
)

frame_titulo.pack(
    pady=(25, 10)
)

tk.Label(
    frame_titulo,
    text="🎹",
    font=("Arial", 35),
    bg="#f2f2f2"
).pack(
    side="left",
    padx=10
)

tk.Label(
    frame_titulo,
    text="IDENTIFICADOR DE ACORDES",
    font=("Arial", 28, "bold"),
    bg="#f2f2f2"
).pack(
    side="left"
)


# ============================================================
# ÁREA DO ACORDE
# ============================================================

frame_acorde = tk.Frame(
    janela,
    bg="white",
    bd=2,
    relief="groove"
)

frame_acorde.pack(
    padx=80,
    pady=15,
    fill="x"
)

tk.Label(
    frame_acorde,
    text="ACORDE IDENTIFICADO",
    font=("Arial", 14, "bold"),
    bg="white"
).pack(
    pady=(20, 5)
)

label_acorde = tk.Label(
    frame_acorde,
    text="AGUARDANDO 3 NOTAS",
    font=("Arial", 36, "bold"),
    bg="white"
)

label_acorde.pack(
    pady=(5, 25)
)


# ============================================================
# NOTAS
# ============================================================

tk.Label(
    janela,
    text="NOTAS PRESSIONADAS",
    font=("Arial", 13, "bold"),
    bg="#f2f2f2"
).pack(
    pady=(10, 5)
)

label_notas = tk.Label(
    janela,
    text="Nenhuma nota pressionada",
    font=("Arial", 20),
    bg="#f2f2f2"
)

label_notas.pack()


# ============================================================
# TECLADO VIRTUAL
# ============================================================

criar_teclado_virtual()


# ============================================================
# STATUS
# ============================================================

status_var = tk.StringVar()

status_var.set(
    "MIDI não conectado"
)

label_status = tk.Label(
    janela,
    textvariable=status_var,
    font=("Arial", 12),
    bg="#f2f2f2"
)

label_status.pack(
    pady=5
)


# ============================================================
# BOTÕES
# ============================================================

frame_botoes = tk.Frame(
    janela,
    bg="#f2f2f2"
)

frame_botoes.pack(
    pady=15
)

tk.Button(
    frame_botoes,
    text="🎹 CONECTAR MIDI",
    command=conectar_midi,
    font=("Arial", 13, "bold"),
    padx=20,
    pady=8
).pack(
    side="left",
    padx=10
)

tk.Button(
    frame_botoes,
    text="🧹 LIMPAR",
    command=limpar_notas,
    font=("Arial", 13, "bold"),
    padx=20,
    pady=8
).pack(
    side="left",
    padx=10
)


# ============================================================
# INICIAR SISTEMA
# ============================================================

atualizar_interface()

verificar_midi()

janela.mainloop()
