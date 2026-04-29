import os
import sys
import subprocess
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

# Um único dados.json para bot + site
os.environ.setdefault("ARQUIVO_DADOS", os.path.join(ROOT, "dados.json"))
os.environ.setdefault("PAINEL_LOGO_PATH", os.path.join(ROOT, "logo_croacia.png"))

def run_bot():
    print("🤖 Iniciando bot...")
    subprocess.run([sys.executable, os.path.join(ROOT, "bot", "main.py")], cwd=ROOT)

def run_site():
    print("🌐 Iniciando site...")
    subprocess.run([sys.executable, os.path.join(ROOT, "site", "app.py")], cwd=ROOT)

if __name__ == "__main__":
    print("🇭🇷 CENTRAL CROÁCIA FASE 6 REAL COMPLETA")
    print("📁 Dados:", os.environ["ARQUIVO_DADOS"])

    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=run_site, daemon=True).start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("Encerrado.")
