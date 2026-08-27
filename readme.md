🎹 Identificador de Acordes MIDI

Projeto desenvolvido para a feira de profissões da faculdade.

A ideia do projeto é conectar um teclado MIDI ao computador e identificar automaticamente o acorde formado pelas notas pressionadas.

📌 Como funciona

O teclado MIDI envia mensagens para o computador sempre que uma tecla é pressionada ou solta.

O Python recebe essas mensagens através da biblioteca Mido, identifica as notas pressionadas e tenta descobrir qual acorde foi formado.

🎹 Teclado MIDI
       ↓
      USB
       ↓
💻 Computador
       ↓
🐍 Python + Mido
       ↓
🎵 Notas pressionadas
       ↓
🧠 Identificador de acordes
       ↓
🎼 Nome do acorde

🛠️ Tecnologias utilizadas

* Python
* Mido
* python-rtmidi
* Git/GitHub

📋 Requisitos

Para executar o projeto, é necessário ter:

* Python 3 instalado
* Um teclado MIDI conectado ao computador via USB
* Conexão com a internet na primeira instalação das bibliotecas

O teclado MIDI não é necessário para desenvolver a lógica do projeto, mas é necessário para testar a comunicação MIDI.

📥 Instalação

1. Clonar o repositório

git clone URL_DO_REPOSITORIO

Entre na pasta:

cd identificador_acordes

2. Instalar as dependências

Execute:

pip install mido python-rtmidi

▶️ Executando o programa

Conecte o teclado MIDI ao computador através do USB.

Depois execute:

python main.py

O programa irá mostrar os dispositivos MIDI encontrados.

Exemplo:

Dispositivos MIDI encontrados:
[0] Meu Teclado MIDI
[1] Outro dispositivo MIDI
Digite o número do teclado que deseja usar:

Digite o número correspondente ao teclado.

Por exemplo:

0

O programa deverá mostrar:

TECLADO CONECTADO COM SUCESSO!
Agora toque algumas notas.
Pressione 3 notas para tentar identificar um acorde.

🎵 Testando

Ao pressionar uma tecla, o programa adicionará a nota às notas atualmente pressionadas.

Por exemplo:

Notas pressionadas: C
Acorde: Aguardando 3 notas

Ao pressionar E:

Notas pressionadas: C - E
Acorde: Aguardando 3 notas

Ao pressionar G:

Notas pressionadas: C - E - G
Acorde: C maior

🎼 Acordes reconhecidos

A versão atual reconhece:

* 12 acordes maiores
* 12 acordes menores

Total:

24 acordes

Exemplos:

Notas	Resultado
C - E - G	C maior
C - D# - G	C menor
D - F# - A	D maior
D - F - A	D menor
G - B - D	G maior
A - C - E	A menor

O programa também consegue reconhecer inversões.

Por exemplo:

C - E - G
E - G - C
G - C - E

Todas correspondem a:

C maior

🎹 Notas MIDI

O MIDI representa as notas através de números.

Uma oitava pode ser representada como:

C   = 60
C#  = 61
D   = 62
D#  = 63
E   = 64
F   = 65
F#  = 66
G   = 67
G#  = 68
A   = 69
A#  = 70
B   = 71

O programa utiliza o valor MIDI para descobrir o nome da nota.

As diferentes oitavas são tratadas utilizando o módulo 12, permitindo que, por exemplo, C3, C4 e C5 sejam identificados simplesmente como C.

🧪 Teste sem teclado MIDI

A lógica de identificação de acordes pode ser testada sem um teclado MIDI.

Exemplo:

print(identificar_acorde(["C", "E", "G"]))

Resultado:

C maior

Outro exemplo:

print(identificar_acorde(["A", "C", "E"]))

Resultado:

A menor

🚧 Estado atual do projeto

Concluído

* Estrutura inicial do projeto
* Conversão de número MIDI para nota
* Recebimento de mensagens MIDI
* Detecção de note_on
* Detecção de note_off
* Controle das notas pressionadas
* Identificação de acordes maiores
* Identificação de acordes menores
* Reconhecimento de inversões

Próximos passos

* Testar com o teclado MIDI real
* Definir as teclas que serão utilizadas na apresentação
* Testar todas as notas
* Melhorar a identificação de acordes
* Criar interface gráfica
* Criar teclado virtual na interface
* Destacar as notas pressionadas
* Preparar versão final para a feira

👥 Desenvolvimento

Projeto desenvolvido para apresentação acadêmica na feira de profissões.

📄 Licença

Projeto acadêmico para fins educacionais.