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

# Teclas brancas utilizadas no teclado virtual
TECLAS_BRANCAS = ["C", "D", "E", "F", "G", "A", "B"]

# Posição das teclas pretas
TECLAS_PRETAS = {
    "C#": 0,
    "D#": 1,
    "F#": 3,
    "G#": 4,
    "A#": 5
}


# ============================================================
# VARIÁVEIS GLOBAIS
# ============================================================

teclado_midi = None
notas_pressionadas = set()

# Uma oitava visual no teclado da interface
OITAVA_VISUAL = 4
NOTA_INICIAL = OITAVA_VISUAL * 12 + 0  # C4 = 48


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


# ============================================================
# IDENTIFICAÇÃO DE ACORDES
# ============================================================

def identificar_acorde(notas):
    """
    Identifica tríades maiores e menores.

    Exemplos:

    C E G  -> C MAIOR
    C D# G -> C MENOR
    E G C  -> C MAIOR
    """

    if len(notas) != 3:
        return "AGUARDANDO 3 NOTAS"

    for fundamental in notas:

        indice_fundamental = NOTAS.index(fundamental)

        intervalos = set()

        for nota in notas:

            indice_nota = NOTAS.index(nota)

            intervalo = (
                indice_nota - indice_fundamental
            ) % 12

            intervalos.add(intervalo)

        # Tríade maior
        if intervalos == {0, 4, 7}:
            return f"{fundamental} MAIOR"

        # Tríade menor
        if intervalos == {0, 3, 7}:
            return f"{fundamental} MENOR"

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

    for numero, botao in teclas_visuais.items():

        if numero in notas_pressionadas:

            botao.config(
                relief="sunken",
                bg="#4CAF50",
                fg="white"
            )

        else:

            botao.config(
                relief="raised",
                bg="white",
                fg="black"
            )


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

def verificar_midi():

    if teclado_midi is not None:

        try:

            while teclado_midi.poll():

                mensagem = teclado_midi.receive()

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

    notas_pressionadas.clear()


# ============================================================
# TECLADO VIRTUAL
# ============================================================

def criar_teclado_virtual():

    global teclas_visuais

    teclas_visuais = {}

    frame_teclado = tk.Frame(
        janela,
        bg="#202020",
        height=190
    )

    frame_teclado.pack(
        fill="x",
        padx=40,
        pady=20
    )

    # -----------------------------------------
    # Teclas brancas
    # -----------------------------------------

    largura = 95

    for i, nota in enumerate(TECLAS_BRANCAS):

        numero_midi = NOTAS.index(nota) + NOTA_INICIAL

        # Corrigir porque NOTAS.index retorna posição cromática
        numero_midi = NOTA_INICIAL + NOTAS.index(nota)

        botao = tk.Button(
            frame_teclado,
            text=nota,
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black",
            relief="raised"
        )

        botao.place(
            x=i * largura,
            y=0,
            width=largura,
            height=170
        )

        teclas_visuais[numero_midi] = botao

    # -----------------------------------------
    # Teclas pretas
    # -----------------------------------------

    posicoes = {
        "C#": 0.68,
        "D#": 1.68,
        "F#": 3.68,
        "G#": 4.68,
        "A#": 5.68
    }

    for nota, posicao in posicoes.items():

        numero_midi = NOTA_INICIAL + NOTAS.index(nota)

        botao = tk.Button(
            frame_teclado,
            text=nota,
            font=("Arial", 10, "bold"),
            bg="#202020",
            fg="white",
            relief="raised"
        )

        botao.place(
            x=int(posicao * largura),
            y=0,
            width=58,
            height=105
        )

        teclas_visuais[numero_midi] = botao


# ============================================================
# CONFIGURAÇÃO DA JANELA
# ============================================================

janela = tk.Tk()

janela.title(
    "Identificador de Acordes MIDI"
)

janela.geometry(
    "900x650"
)

janela.minsize(
    900,
    650
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