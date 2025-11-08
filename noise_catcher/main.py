import sounddevice as sd
import numpy as np
import wave
import datetime
from pydub import AudioSegment
import sqlite3

class AudioRecorder:
    def __init__(self, threshold=100, duration=10):
        self.threshold = threshold
        self.duration = duration
        self.fs = 44100  # Taux d'échantillonnage
        self.audio_data = []

    def record(self):
        print("Écoute en cours...")
        start_time = datetime.datetime.now()
        
        while (datetime.datetime.now() - start_time).seconds < self.duration:
            data = sd.rec(int(self.fs * 1), samplerate=self.fs, channels=1, dtype='int16')
            sd.wait()  # Attendre que l'enregistrement soit terminé
            volume_norm = np.linalg.norm(data) * 10
            print(volume_norm)
            
            if volume_norm > self.threshold:
                print("Niveau de décibels dépassé ! Enregistrement...")
                self.audio_data.append(data)

        if self.audio_data:
            self.save_audio()
        else:
            print("Aucun enregistrement effectué.")

    def save_audio(self):
        filename = f"enregistrement_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bits
            wf.setframerate(self.fs)
            wf.writeframes(np.concatenate(self.audio_data).tobytes())
        print(f"Enregistrement sauvegardé sous : {filename}")
        self.convert_wav_to_mp3(filename)
        self.log_recording(filename)

    def convert_wav_to_mp3(self, wav_file):
        mp3_file = wav_file.replace('.wav', '.mp3')
        audio = AudioSegment.from_wav(wav_file)
        audio.export(mp3_file, format='mp3')
        print(f"Converti en MP3 : {mp3_file}")

    def log_recording(self, filename):
        conn = sqlite3.connect('recordings.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS recordings
                     (date TEXT, filename TEXT)''')

        c.execute("INSERT INTO recordings (date, filename) VALUES (?, ?)", 
                  (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), filename))
        
        conn.commit()
        conn.close()


if __name__ == "__main__":
    recorder = AudioRecorder(threshold=70, duration=10)
    recorder.record()