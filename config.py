from pathlib import Path
import sys
from logger import LoggerDuplo

class Config():
    
    PASTA_PROJETO = Path(__file__).parent.resolve()

    PASTA_OUTPUT = PASTA_PROJETO / "output"
    PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)

    # ativa o log de etapas em arquivo de texto, o objetivo é simular que esses dados podem capturados e gravados.
    # matenho a integridade da base principal
    sys.stdout = LoggerDuplo(PASTA_OUTPUT / "execucao.txt")

    ARQUIVO_EXCEL = PASTA_PROJETO / "challenge.xlsx"
    ARQUIVO_PRINT = PASTA_OUTPUT / "evidencia_score.png"
    ARQUIVO_LOG = PASTA_OUTPUT / "log_execucao.csv"
    URL = "https://rpachallenge.com/"

    MAPEAMENTO = {
        "First Name": "First Name",
        "Last Name": "Last Name",
        "Company Name": "Company Name",
        "Role in Company": "Role in Company",
        "Address": "Address",
        "Email": "Email",
        "Phone Number": "Phone Number"
    }