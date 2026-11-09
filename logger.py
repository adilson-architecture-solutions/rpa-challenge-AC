import sys

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