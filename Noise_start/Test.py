import pyaudio
import numpy as np

# Paramètres de l'enregistrement
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Initialisation de PyAudio
audio = pyaudio.PyAudio()

# Ouverture du flux audio
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Mesure des décibels en cours...")

def calculer_db(data):
    # Conversion des données en tableau numpy
    donnees_array = np.frombuffer(data, dtype=np.int16)
    # Calcul de la valeur RMS (Root Mean Square)
    rms = np.sqrt(np.mean(np.square(donnees_array)))
    # Conversion en décibels
    db = 20 * np.log10(rms) if rms > 0 else -float('inf')
    return db

try:
    while True:
        # Lecture des données audio
        data = stream.read(CHUNK)
        # Calcul des décibels
        db = calculer_db(data)
        print(f"Niveau de décibels : {db:.2f} dB")
except KeyboardInterrupt:
    print("Mesure arrêtée.")

# Arrêt et fermeture du flux
stream.stop_stream()
stream.close()
audio.terminate()