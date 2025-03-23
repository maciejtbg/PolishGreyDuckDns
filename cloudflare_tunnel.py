import os
import subprocess
import time
import json

# 🔹 ŁADOWANIE KONFIGURACJI Z PLIKU JSON 🔹 #
def load_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

# Załaduj dane konfiguracyjne
config = load_config()

# Pobranie ustawień
PORT = config["port"]
WEBSITE_FOLDER = config["website_folder"]

# Sprawdzenie folderu strony
if not os.path.isdir(WEBSITE_FOLDER):
    print("❌ BŁĄD: Folder ze stroną nie istnieje!")
    exit(1)

# Globalne zmienne dla procesów
http_server_process = None
cloudflare_process = None
public_url = None

# 🔹 URUCHOMIENIE SERWERA HTTP 🔹 #
def start_http_server():
    global http_server_process
    print(f"🔵 Uruchamianie serwera HTTP na porcie {PORT} dla folderu: {WEBSITE_FOLDER}")
    os.chdir(WEBSITE_FOLDER)
    http_server_process = subprocess.Popen(
        ["python", "-m", "http.server", str(PORT)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return http_server_process

# 🔹 URUCHOMIENIE CLOUDFLARED (Quick Tunnel) 🔹 #
def start_cloudflare_tunnel():
    global cloudflare_process
    print(f"🔵 Uruchamianie tunelu Cloudflare dla http://localhost:{PORT}")
    # Używamy PIPE, aby móc odczytać wyjście procesu
    cloudflare_process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{PORT}"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    return cloudflare_process

# 🔹 POBRANIE ADRESU PUBLICZNEGO Z CLOUDFLARED 🔹 #
def get_cloudflare_url(process, timeout=30):
    """
    Czyta wyjście procesu cloudflared i szuka linii zawierającej wygenerowany adres.
    Przykładowy komunikat: "Your quick tunnel is available at https://abc123.trycloudflare.com"
    """
    global public_url
    start_time = time.time()
    while time.time() - start_time < timeout:
        line = process.stdout.readline()
        if line:
            print(line.strip())  # Wypisujemy log dla debugowania
            if "Your quick tunnel is available at" in line:
                # Przyjmujemy, że adres jest ostatnim słowem w tej linii
                parts = line.strip().split()
                public_url = parts[-1]
                return public_url
        else:
            time.sleep(0.5)
    print("❌ Błąd pobierania adresu Cloudflare Tunnel. Sprawdź logi procesu.")
    return None

# 🔹 FUNKCJE ZAMYKANIA USŁUG 🔹 #
def stop_http_server():
    global http_server_process
    if http_server_process:
        print("🔴 Zamykanie serwera HTTP...")
        http_server_process.terminate()
        http_server_process = None

def stop_cloudflare():
    global cloudflare_process
    if cloudflare_process:
        print("🔴 Zamykanie tunelu Cloudflare...")
        cloudflare_process.terminate()
        cloudflare_process = None

def shutdown_all():
    stop_http_server()
    stop_cloudflare()
    print("🔴 Wszystkie usługi zostały zamknięte.")

# 🔹 MONITOR WYŁĄCZENIA USŁUG 🔹 #
def monitor_shutdown():
    while True:
        input_str = input("Wpisz 'q' i naciśnij Enter, aby zamknąć tunel i serwer: ")
        if input_str.strip().lower() == 'q':
            shutdown_all()
            break

# 🔹 START WSZYSTKIEGO 🔹 #
start_http_server()
cf_proc = start_cloudflare_tunnel()

url = get_cloudflare_url(cf_proc)
if url:
    print(f"🌍 Twoja strona jest dostępna pod: {url}")
else:
    print("❌ Nie udało się pobrać adresu tunelu Cloudflare.")

monitor_shutdown()
