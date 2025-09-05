# Sistema de Processamento de Vídeos Cliente-Servidor

## Descrição do Projeto

Video Processing System (VPS) é uma aplicação cliente/servidor desenvolvida para processamento e organização de vídeos de maneira eficiente e estruturada. O sistema permite que o usuário envie vídeos através de uma interface gráfica (GUI) desenvolvida com Tkinter, escolha filtros de processamento (como escala de cinza, pixelização e detecção de bordas), e visualize tanto o vídeo original quanto o processado.

No lado do servidor, construído com Flask e OpenCV, os vídeos são recebidos, processados conforme os filtros escolhidos e armazenados de forma organizada em diretórios. Metadados dos vídeos, como nome, formato, tamanho, e parâmetros de filtro, são registrados em um banco de dados SQLite. O sistema também gera thumbnails para facilitar a visualização rápida dos vídeos processados.

Com uma arquitetura de três camadas (cliente, servidor e banco de dados), o VPS oferece uma solução prática para a gestão de vídeos, mantendo um histórico de vídeos processados e permitindo a consulta de metadados com facilidade. O sistema é ideal para organizações ou indivíduos que desejam processar vídeos em massa, mantendo o controle e a organização em um único sistema integrado.

O sistema foi desenhado para ser robusto, desacoplado e escalável, separando as responsabilidades entre a interface do usuário (cliente) e a lógica de processamento pesada (servidor).

# Funcionalidades Principais
##  Cliente (Desktop - Tkinter)
Seleção de Arquivos: Interface gráfica para selecionar arquivos de vídeo locais (.mp4, .avi, etc.).

 - Escolha de Filtros: Permite ao usuário escolher um filtro de processamento antes do envio (ex: Escala de Cinza, Pixelização).

- Envio via HTTP: Envia o vídeo e o filtro selecionado para o servidor de forma segura e eficiente.

- Histórico de Envios: Exibe uma lista de todos os vídeos processados, consultando o servidor em tempo real.

- Visualização Remota: Permite visualizar o vídeo original e o processado diretamente, abrindo os arquivos hospedados no servidor.

#  Servidor (Backend - Flask & OpenCV)
 - API RESTful: Endpoints para receber uploads (/upload) e fornecer dados (/history, /media).

- Processamento de Vídeo: Utiliza a biblioteca OpenCV para aplicar filtros frame a frame em vídeos enviados. Filtros implementados:

- grayscale (Escala de Cinza)

- pixelate (Pixelização)

- canny_edges (Detecção de Bordas Canny)

- Armazenamento Organizado: Salva os vídeos em uma estrutura de pastas organizada por data e UUID para evitar colisões e facilitar o gerenciamento (/media/videos/AAAA/MM/DD/{UUID}/).

- Persistência de Dados: Registra metadados completos de cada vídeo (duração, FPS, resolução, etc.) em um banco de dados SQLite.

- Dashboard Web: Uma interface web simples para visualizar os vídeos salvos no servidor, com thumbnails e links diretos para os arquivos.

# Arquitetura e Tecnologias Utilizadas
O projeto é dividido em dois componentes principais que se comunicam via HTTP:


~~~~ 
[Cliente Desktop (Tkinter)] <---(HTTP Requests)---> [Servidor Web (Flask)]ˋˋˋ
~~~~

### Cliente:

 - Linguagem: Python 3

- Interface Gráfica: Tkinter

- Comunicação HTTP: Biblioteca requests

### Servidor:

 - Linguagem: Python 3

 - Framework Web/API: Flask

 - Processamento de Vídeo: OpenCV

 - Banco de Dados: SQLite3

## 📁 Estrutura de Arquivos

~~~~
video_processing_app/
├── server/
│   ├── server_app.py         # Lógica principal do Flask (rotas, etc.)
│   ├── database.py           # Funções para interagir com o SQLite
│   ├── video_processor.py    # Funções de processamento com OpenCV
│   ├── requirements.txt      # Dependências do servidor
│   └── templates/
│       └── index.html        # GUI web do servidor para visualização
│
├── client/
│   ├── client_app.py         # Aplicação GUI com Tkinter
│   └── requirements.txt      # Dependências do cliente
│
└── media/                    # Criada automaticamente pelo servidor
    ├── videos.db
    └── videos/
        └─ {AAAA}/{MM}/{DD}/
           └─ {UUID}/
              ├─ original.mp4
              ├─ processed_filter.avi
              └─ thumbnail.jpg
              
~~~~
# Guia de Instalação e Execução
- Pré-requisitos
- Python 3.8 ou superior

- pip (gerenciador de pacotes do Python)

1. Clonar o Repositório 
~~~~Bash git clone [URL_DO_SEU_REPOSITORIO]
cd video_processing_app
2. Configurar e Iniciar o Servidor
Bash

# Navegue até a pasta do servidor
cd server

# Crie e ative um ambiente virtual (recomendado)
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor
python server_app.py
O servidor estará rodando, geralmente em http://127.0.0.1:5000. Anote o endereço IP se for diferente.

3. Configurar e Iniciar o Cliente
Abra um novo terminal.

Bash

# Navegue até a pasta do cliente (a partir da raiz do projeto)
cd client

# Crie e ative um ambiente virtual
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Inicie a aplicação cliente
python client_app.py
A interface gráfica do cliente será aberta.
~~~~

##  Como Usar
Com o servidor e o cliente rodando, a janela do cliente aparecerá.

Clique em "Selecionar Arquivo..." para escolher um vídeo do seu computador.

Escolha um dos filtros disponíveis no menu dropdown.

Clique em "Enviar Vídeo". A barra de progresso indicará o upload.

Após o envio, a lista de Histórico de Vídeos será atualizada automaticamente.

Para visualizar, selecione um item na lista e clique em "Ver Original" ou "Ver Processado".

Para visualizar o dashboard do servidor, acesse http://127.0.0.1:5000 em seu navegador.
