import pyaudio
import numpy as np
import wave
from datetime import datetime
from collections import deque
import threading
from config import *


class AudioRecorder:
    def __init__(self):
        self.buffer = deque(maxlen=int(TAUX_ECHANTILLONNAGE * BUFFER_TEMPS))
        self.enregistrement = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.fichiers_enregistres = []

    def calculer_db(self, donnees):
        donnees_array = np.frombuffer(donnees, dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(donnees_array)))
        db = 20 * np.log10(rms) if rms > 0 else -float('inf')
        return db

    def callback(self, in_data, frame_count, time_info, status):
        self.buffer.extend(in_data)
        db_niveau = self.calculer_db(in_data)

        if db_niveau > SEUIL_DB and not self.enregistrement:
            self.demarrer_enregistrement()

        return (in_data, pyaudio.paContinue)

    def demarrer_enregistrement(self):
        self.enregistrement = True
        nom_fichier = f"enregistrement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        wf = wave.open(nom_fichier, 'wb')
        wf.setnchannels(CANAUX)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(TAUX_ECHANTILLONNAGE)

        # Écriture du buffer
        for data in self.buffer:
            wf.writeframes(data)

        self.fichiers_enregistres.append({
            'nom': nom_fichier,
            'date': datetime.now(),
            'niveau_db': self.calculer_db(data)
        })

    def demarrer(self):
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=CANAUX,
            rate=TAUX_ECHANTILLONNAGE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback
        )
        self.stream.start_stream()

    def arreter(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()