import os
import sys
import time
import unicodedata
import urllib.request
from datetime import datetime
from pathlib import Path
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# classe de log duplo (terminal + txt)


class LoggerDuplo:
    def __init__(self, caminho_arquivo):
        self.terminal = sys.stdout
        self.log = open(caminho_arquivo, "w", encoding="utf-8")

    def write(self, mensagem):
        self.terminal.write(mensagem)
        self.log.write(mensagem)
        self.log.flush()  # grava log no arquivo no mesmo momento dos prints

    def flush(self):
        self.terminal.flush()
        self.log.flush()


# configuração pastas/path dos arquivos


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

# lista em memória para acumular os registros do log
historico_execucao = []


#função normalização de texto


def normalizar(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.split())



chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)


# acesso instancia do site e verificação do arq.


print("Abrindo Chrome...")
driver.get(URL)

if ARQUIVO_EXCEL.exists():
    print(f"[ARQUIVO] A planilha já existe localmente: {ARQUIVO_EXCEL.name}")
else:
    print("[ARQUIVO] Planilha não encontrada na pasta. Iniciando download...")
    btn_download = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(.,'Download Excel')]"))
    )
    url_download = btn_download.get_attribute("href")
    
    requisicao = urllib.request.Request(
        url_download,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )

    with urllib.request.urlopen(requisicao) as resposta, open(ARQUIVO_EXCEL, "wb") as arquivo:
        arquivo.write(resposta.read())
    print(f"[ARQUIVO] Download concluído com sucesso: {ARQUIVO_EXCEL.name}")


# executa a leitura do excel 

print("Lendo dados do Excel...")
df = pd.read_excel(ARQUIVO_EXCEL)
df.columns = df.columns.str.strip()

if df.empty:
    raise Exception("O Excel não possui registros.")

for coluna in MAPEAMENTO.values():
    if coluna not in df.columns:
        raise Exception(f"Coluna não encontrada no Excel: {coluna}")

print(f"Registros encontrados: {len(df)}")


#iniciando o challenge RPA 


print("Iniciando desafio...")
btn_start = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Start']")))
btn_start.click()


# df função executa os input no forms web 


def preencher_formulario(dados):
    campos = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//rpa1-field"))
    )

    map_normalizado = {normalizar(k): v for k, v in MAPEAMENTO.items()}
    preenchidos = 0

    for campo in campos:
        label = campo.find_element(By.XPATH, ".//label")
        nome_campo = label.get_attribute("innerText").strip()
        chave = normalizar(nome_campo)

        if chave not in map_normalizado:
            continue

        coluna_excel = map_normalizado[chave]
        valor = dados[coluna_excel]

        if pd.isna(valor):
            valor = ""
        elif isinstance(valor, float) and valor.is_integer():
            valor = str(int(valor))
        else:
            valor = str(valor)

        input_element = campo.find_element(By.XPATH, ".//input")
        input_element.clear()
        input_element.send_keys(valor)

        print(f"Preenchido: {nome_campo:<16} -> {valor}")
        preenchidos += 1

    btn_submit = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Submit']"))
    )
    btn_submit.click()

    return preenchidos


# execução a captura o printscreen 


try:
    total_geral_campo = 0
    total_linhas = len(df) 
   
    for indice, linha in df.iterrows():
        numero_round = indice + 1
      
        timestamp_atual = f'="{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"'
        print(f"\nExecutando Round {numero_round:02d}/{total_linhas}")
        
        # verifica se algum campo mapeado está nulo (NaN/None) ou vazio ("").
        tem_campo_em_branco = any(
            pd.isna(linha[coluna]) or str(linha[coluna]).strip() == ""
            for coluna in MAPEAMENTO.values()
        )
        
        try:
            campos_rodada = preencher_formulario(linha)
            total_geral_campo += campos_rodada
            
            #define Status e Observacao de acordo com a validação
            if tem_campo_em_branco:
                status_registro = "NOK"
                obs_registro = "Dado em branco"
            else:
                status_registro = "OK"
                obs_registro = f"Sucesso: {campos_rodada} campos preenchidos e enviados"
            
            historico_execucao.append({
                "Round": numero_round,
                "Status": status_registro,
                "Observacao": obs_registro,
                "Data_Hora": timestamp_atual
            })
            
        except Exception as erro_round:
            historico_execucao.append({
                "Round": numero_round,
                "Status": "NOK",
                "Observacao": f"Erro no round: {str(erro_round)}",
                "Data_Hora": timestamp_atual
            })
            raise erro_round

    resultado_final = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".message2"))
    ).text
    
    time.sleep(0.5)
    driver.save_screenshot(str(ARQUIVO_PRINT))
    print(f"\n[EVIDÊNCIA] Print da tela final salvo em: {ARQUIVO_PRINT.name}")
    
    # geração do CSV antes do pause
    if historico_execucao:
        df_log = pd.DataFrame(historico_execucao)
        try:
            df_log.to_csv(ARQUIVO_LOG, index=False, sep=";", encoding="utf-8-sig")
            print(f"[LOG] Arquivo de auditoria gerado em: {ARQUIVO_LOG.name}")
        except PermissionError:
            arquivo_alternativo = PASTA_PROJETO / f"log_execucao_{datetime.now().strftime('%H%M%S')}.csv"
            df_log.to_csv(arquivo_alternativo, index=False, sep=";", encoding="utf-8-sig")
            print(f"[AVISO] '{ARQUIVO_LOG.name}' estava em uso. Log salvo em: {arquivo_alternativo.name}")

    print("\n" + "=" * 44)
    print("RPA CHALLENGE CONCLUÍDO!")
    print(resultado_final)
    print("=" * 44)
    
    input("\nPara encerrar o processo aperte ENTER...")
    
except Exception as erro:
    print(f"\nErro na automação: {erro}")
    input("\nPressione ENTER para encerrar...")    
    
finally:
    driver.quit()
    print("Chrome encerrado.")