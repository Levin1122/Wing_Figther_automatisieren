import subprocess
import os

# Pfad zum auszuführenden Skript
script_path = "D:\VSC\Wing_Figther_automatomatisieren.py"

# Überprüfen, ob das Skript existiert
if os.path.exists(script_path):
    try:
        # Skript ausführen
        subprocess.run(["python3", script_path], check=True)
        print("Skript erfolgreich gestartet.")
    except subprocess.CalledProcessError as e:
        print("Fehler beim Starten des Skripts:", e)
else:
    print("Das Skript wurde nicht gefunden:", script_path)
