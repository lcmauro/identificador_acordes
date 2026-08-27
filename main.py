import mido

# ============================================================
# NOTAS
# ============================================================

NOTAS_CROMATICAS = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B"
]

# ============================================================
# CONVERTER NÚMERO MIDI PARA NOME DA NOTA
# ============================================================

def numero_para_nota(numero_midi):
    """
    Converte um número MIDI para o nome da nota.

    Exemplos:
    60 -> C
    61 -> C#
    64 -> E
    67 -> G
    """

    return NOTAS_CROMATICAS[numero_midi % 12]


# ============================================================
# IDENTIFICADOR DE ACORDES
# ============================================================

def identificar_acorde(notas):
    """
    Recebe uma lista de notas e tenta identificar o acorde.

    Exemplos:
    C E G   -> C maior
    C D# G  -> C menor
    D F# A  -> D maior
    """

#ToDo: Validar se começaremos apenas com triades
    if len(notas) != 3:
        return "Aguardando 3 notas"

    # Testamos cada nota como possível fundamental.
    for fundamental in notas:

        indice_fundamental = NOTAS_CROMATICAS.index(fundamental)

        intervalos = set()

        for nota in notas:

            indice_nota = NOTAS_CROMATICAS.index(nota)

            intervalo = (
                indice_nota - indice_fundamental
            ) % 12

            intervalos.add(intervalo)

        # Acorde maior:
        # fundamental + 4 semitons + 7 semitons
        if intervalos == {0, 4, 7}:
            return fundamental + " maior"

        # Acorde menor:
        # fundamental + 3 semitons + 7 semitons
        if intervalos == {0, 3, 7}:
            return fundamental + " menor"

    return "Acorde desconhecido"


# ============================================================
# MOSTRAR ESTADO ATUAL
# ============================================================

def mostrar_estado(notas_midi):
    """
    Mostra as notas pressionadas e o acorde identificado.
    """

    # Converte os números MIDI para nomes.
    notas = [
        numero_para_nota(numero)
        for numero in sorted(notas_midi)
    ]

    acorde = identificar_acorde(notas)

    print("-" * 50)

    print("Notas pressionadas:", end=" ")

    if notas:
        print(" - ".join(notas))
    else:
        print("Nenhuma")

    print("Acorde:", acorde)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 50)
    print("       IDENTIFICADOR DE ACORDES MIDI")
    print("=" * 50)

    # --------------------------------------------------------
    # Encontrar dispositivos MIDI
    # --------------------------------------------------------

    portas = mido.get_input_names()

    if not portas:

        print()
        print("Nenhum dispositivo MIDI encontrado.")
        print()
        print("Conecte o teclado MIDI e tente novamente.")

        return

    print()
    print("Dispositivos MIDI encontrados:")
    print()

    for i, porta in enumerate(portas):

        print(f"[{i}] {porta}")

    print()

    # --------------------------------------------------------
    # Escolher teclado
    # --------------------------------------------------------

    while True:

        try:

            escolha = int(
                input("Digite o número do teclado que deseja usar: ")
            )

            if 0 <= escolha < len(portas):
                break

            print("Número inválido.")

        except ValueError:

            print("Digite apenas um número.")

    nome_teclado = portas[escolha]

    print()
    print("Conectando ao dispositivo:")
    print(nome_teclado)

    # --------------------------------------------------------
    # Abrir conexão MIDI
    # --------------------------------------------------------

    try:

        with mido.open_input(nome_teclado) as teclado:

            print()
            print("TECLADO CONECTADO COM SUCESSO!")
            print()
            print("Agora toque algumas notas.")
            print("Pressione 3 notas para tentar identificar um acorde.")
            print()
            print("Pressione Ctrl+C para sair.")
            print()

            # Conjunto que guarda as notas atualmente pressionadas.
            notas_pressionadas = set()

            # ------------------------------------------------
            # Escutar teclado continuamente
            # ------------------------------------------------

            for mensagem in teclado:

                # ==================================================
                # TECLA PRESSIONADA
                # ==================================================

                if (
                    mensagem.type == "note_on"
                    and mensagem.velocity > 0
                ):

                    notas_pressionadas.add(mensagem.note)

                    mostrar_estado(notas_pressionadas)

                # ==================================================
                # TECLA SOLTA
                # ==================================================

                elif (
                    mensagem.type == "note_off"
                    or (
                        mensagem.type == "note_on"
                        and mensagem.velocity == 0
                    )
                ):

                    if mensagem.note in notas_pressionadas:

                        notas_pressionadas.remove(mensagem.note)

                    mostrar_estado(notas_pressionadas)

    except KeyboardInterrupt:

        print()
        print()
        print("Programa encerrado.")

    except Exception as erro:

        print()
        print("Ocorreu um erro:")
        print(erro)


# ============================================================
# INICIAR PROGRAMA
# ============================================================

if __name__ == "__main__":
    main()