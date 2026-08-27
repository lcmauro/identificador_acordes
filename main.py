notas = []

notas_midi = {
    60: "C",
    61: "C#",
    62: "D",
    63: "D#",
    64: "E",
    65: "F",
    66: "F#",
    67: "G",
    68: "G#",
    69: "A",
    70: "A#",
    71: "B"
}

notas_pressionadas = {60,64,67}  # Conjunto de notas pressionadas (exemplo)

for nota_midi in notas_pressionadas:
    notas.append(notas_midi[nota_midi])  # Adiciona a nota correspondente ao conjunto de notas pressionadas

print(notas)  # Exibe a lista de notas, incluindo as pressionadas