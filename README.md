# RPA Challenge
 Responsável: Adilson Cunha  
 Stack:** Python 3.10+ | Selenium WebDriver | Pandas | OpenPyXL


Automação desenvolvida para o [RPA Challenge](https://rpachallenge.com/), projetada com arquitetura autonoma  diante de  layouts dinâmicos, contedo geração de logs e evidência. 



Requisitos:

Leitura de Arquivo Excel:
Leitura automatizada da base challenge.xlsx, com download resiliente via urllib (User-Agent simulando navegador para contornar bloqueios HTTP 403) caso o arquivo não exista localmente.

Preenchimento Dinâmico:
Mapeamento semântico baseado nos nós <rpa1-field> ancorado nas tags <label>,devido a lternância aleatoria de posições e à mudança de IDs.
Log de Etapas:
Rastreamento do ciclo de vida da execução em tempo real (output/execucao.txt) via classe LoggerDuplo terminal + txt. 

Log de Resultados :
elatório estruturado (output/log_execucao.csv) com separador ponto e vírgula e encoding "utf-8-sig", contendo:
  Round: Ciclo/rodada em processamento.
  Status: OK para preenchimentos completos e NOK para dados faltantes.
  Observacao: Descrição de sucesso ou detalhamento (Dado em branco).
  Data_Hora: Timestamp formatado garantindo a precisão em segundos.

Evidência de Score:
Captura automática do print da tela final demonstrando a precisão e o tempo alcançado (output/evidencia_score.png).



Arquitetura e Decisões Técnicas

Mapeamento : 
O seletor não depende de posições fixas nem de atributos dinâmicos voláteis. A função normalizar() utiliza o módulo unicodedata (NFKD) para remover acentos, espaços duplos e padronizar caracteres antes do cruzamento entre planilha e DOM.

Tratamento de Dados Incompletos: Verificação  de valores nulos (NaN, None ou strings vazias). O robô mantém o fluxo de submissão do formulário para transicionar as fases do desafio, gravando no log tabular o Status: NOK e a Observacao: Dado em branco.
Tratamento de Concorrência de Arquivo: Mecanismo defensivo com captura de PermissionError ao gerar o log tabular. Caso o arquivo padrão esteja em uso (aberto no Excel pelo usuário), o sistema desvia a gravação para um arquivo de contingência com carimbo de hora sem abortar o script.
Isolamento de Artefatos:
Estrutura autocontida onde todas as saídas geradas em runtime são direcionadas exclusivamente para o diretório de pasta com o nome output/.


 Estrutura do Projeto

text
rpa-challenge-AC/
│
├── GoRPAChallenge_AC.py     # Script principal da automação
├── challenge.xlsx            # Planilha base (baixada automaticamente se ausente)
├── requirements.txt         # Pacotes e dependências externas
├── .gitignore               # Regras de exclusão de artefatos do Git
├── README.md                # Documentação técnica e operacional
│
└── output/                  # Diretório de artefatos gerados
    ├── evidencia_score.png  # Print da tela final com pontuação
    ├── execucao.txt         # Log de etapas em tempo real do terminal
    └── log_execucao.csv     # Log estruturado de auditoria das 10 rodadas



    ## Executando a rodagem
    # Repositorio do github

    git clone [https://github.com/adilson-architecture-solutions/rpa-challenge-AC.git](https://github.com/adilson-architecture-solutions/rpa-challenge-AC.git)
cd rpa-challenge-AC

2- Criar e ativar o ambiente (opcioanl)
# Windows
python -m venv .venv
.venv\Scripts\activate

3- Instalações das bibliotecas necessarias 
pip install -r requirements.txt

4- No Visual studio VSC como rodar:
Abra um terminal e execute

python GoRPAChallenge_AC.py