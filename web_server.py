import os
import subprocess
import time
import json
import threading
import socket

# 🔹 ŁADOWANIE DANYCH KONFIGURACYJNYCH Z PLIKU JSON 🔹 #
def load_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

config = load_config()

# Pobranie konfiguracji
WEBSITE_FOLDER = config["website_folder"]
PORT = int(config["port"])  # Konwersja na liczbę całkowitą

if not os.path.isdir(WEBSITE_FOLDER):
    print("BŁĄD: Folder ze stroną nie istnieje!")
    exit(1)

# 🔹 SPRAWDZENIE, CZY PORT JEST ZAJĘTY 🔹 #
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

if is_port_in_use(PORT):
    print(f"⚠️ Port {PORT} jest już zajęty! Sprawdź, czy inny proces nie używa tego portu.")
    exit(1)

# 🔹 URUCHOMIENIE SERWERA WWW 🔹 #
def start_http_server():
    print(f"🔵 Uruchamianie serwera HTTP na porcie {PORT} dla folderu: {WEBSITE_FOLDER}")
    os.chdir(WEBSITE_FOLDER)
    process = subprocess.Popen(
        ["python", "-m", "http.server", str(PORT)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"🌍 Serwer działa! Odwiedź: http://127.0.0.1:{PORT}")
    return process

# 🔹 MONITOROWANIE ZAMKNIĘCIA 🔹 #
def monitor_shutdown(process):
    print("🔹 Wpisz 'q' i naciśnij Enter, aby zamknąć serwer.")
    while True:
        user_input = input()
        if user_input.strip().lower() == 'q':
            print("\n🔴 Zamykanie serwera HTTP...")
            process.terminate()
            break

# Start serwera
http_server_process = start_http_server()
shutdown_thread = threading.Thread(target=monitor_shutdown, args=(http_server_process,))
shutdown_thread.start()
shutdown_thread.join()
