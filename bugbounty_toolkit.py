# bugbounty.py → VERSIÓN FINAL CORREGIDA Y FUNCIONANDO EN WINDOWS

import os
import socket
import threading
import requests
import time
from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import urllib3

# Desactivar warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Inicializar colorama y definir colores
init(autoreset=True)
G = Fore.GREEN
R = Fore.RED
Y = Fore.YELLOW
C = Fore.CYAN
M = Fore.MAGENTA
W = Fore.WHITE
RESET = Style.RESET_ALL   # ← ESTA LÍNEA FALTABA

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""
{M}  ____              ____                  _       
  |  _ \            |  _ \                | |      
  | |_) | __ _  __ _| |_) | ___  _   _  ___| |_ _   _ 
  |  _ < / _` |/ _` |  _ < / _ \| | | |/ __| __| | | |
  | |_) | (_| | (_| | |_) | (_) | |_| | (__| |_| |_| |
  |____/ \__,_|\__, |____/ \___/ \__,_|\___|\__|\__, |
                __/ |                            __/ |
               |___/                            |___/ 
{C}       BUG BOUNTY TOOLKIT → Windows Edition 2025
{Y}               ¡Todo automático y corregido! 
{RESET}""")

def descargar_wordlist():
    if not os.path.exists("common.txt"):
        print(f"{Y}[*] Descargando wordlist de subdominios... (solo la primera vez)")
        url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-20000.txt"
        try:
            r = requests.get(url, timeout=60)
            with open("common.txt", "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"{G}[+] common.txt descargado correctamente")
        except Exception as e:
            print(f"{R}[-] Error al descargar wordlist: {e}")
            return False
    return True

def subdominios(domain):
    if not descargar_wordlist():
        return
    print(f"\n{Y}[*] Buscando subdominios (3000 palabras rápidas)...")
    encontrados = 0
    with open("common.txt", "r", encoding="utf-8") as f:
        palabras = [line.strip() for line in f if line.strip() and not line.startswith("#")][:3000]

    def probar(sub):
        target = f"{sub}.{domain}"
        try:
            socket.gethostbyname(target)
            print(f"{G}[+] Subdominio vivo → {target}")
            nonlocal encontrados
            encontrados += 1
        except:
            pass

    threads = []
    for palabra in palabras:
        t = threading.Thread(target=probar, args=(palabra,))
        t.daemon = True
        t.start()
        threads.append(t)
        if len(threads) >= 100:
            for thread in threads:
                thread.join()
            threads = []

    for thread in threads:
        thread.join()
    print(f"\n{G}[+] Total subdominios encontrados: {encontrados}")

def puertos(ip):
    print(f"\n{Y}[*] Escaneando puertos comunes en {ip}...")
    puertos = [21,22,80,81,443,3000,3306,3389,5000,5432,6379,8080,8443,9000,9200,27017]
    for p in puertos:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex((ip, p)) == 0:
            servicio = {80:"HTTP",443:"HTTPS",22:"SSH",21:"FTP",3306:"MySQL",8080:"HTTP-Alt",27017:"MongoDB"}.get(p, "")
            print(f"{G}[+] Puerto {p}/tcp ABIERTO → {servicio}")
        s.close()

def headers(domain):
    print(f"\n{Y}[*] Analizando cabeceras de https://{domain}...")
    try:
        r = requests.get(f"https://{domain}", verify=False, timeout=10,
                         headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        print(f"{C}[i] Status: {r.status_code}")
        for h in ["Server", "X-Powered-By", "X-Frame-Options", "Content-Security-Policy"]:
            if h in r.headers:
                print(f"{C}[i] {h}: {r.headers[h]}")
        if any(waf in str(r.headers).lower() for waf in ["cloudflare", "cloudfront", "akamai", "incapsula"]):
            print(f"{R}[!] WAF detectado")
    except Exception as e:
        print(f"{R}[-] Error conectando: {e}")

def screenshot(domain):
    print(f"\n{Y}[*] Tomando screenshot con Chrome (automático)...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(f"https://{domain}")
        time.sleep(5)
        archivo = f"screenshot_{domain.replace('.', '_')}.png"
        driver.save_screenshot(archivo)
        driver.quit()
        print(f"{G}[+] Screenshot guardado → {archivo}")
    except Exception as e:
        print(f"{R}[-] Error con Chrome/Selenium: {e}")
        print(f"{Y}[!] Asegúrate de tener Google Chrome instalado.")

def main():
    banner()
    print(f"{C}¡Todo listo y corregido!\n")
    
    domain = input(f"{C}[?] Dominio objetivo (ej: tesla.com): {W}").strip().lower()
    if not domain:
        return

    try:
        ip = socket.gethostbyname(domain)
        print(f"{G}[+] IP: {ip}\n")
    except:
        print(f"{R}[-] Dominio no resuelto.")
        return

    subdominios(domain)
    puertos(ip)
    headers(domain)
    screenshot(domain)

    print(f"\n{G}╔════════════════════════════════════╗")
    print(f"{G}║     ESCANEO COMPLETADO CON ÉXITO   ║")
    print(f"{G}╚════════════════════════════════════╝")
    input(f"\n{C}Presiona Enter para salir...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{R}[!] Cancelado por el usuario.")