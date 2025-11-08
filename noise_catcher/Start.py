import sounddevice as sd
import numpy as np
import wave , os
import datetime , time
from pydub import AudioSegment
import sqlite3


class AudioRecorder:

    def __init__(self, threshold=70, duration=10):
        self.threshold = threshold
        self.duration = duration
        self.fs = 44100  # Taux d'échantillonnage par sec
        self.audio_data = []

    def convert_wav_to_mp3(self, wav_file):
        mp3_file = wav_file.replace('.wav', '.mp3')
        audio = AudioSegment.from_wav(wav_file)
        self.duree = (len(audio))/1000 # non utilisé si pour un enregistrement continue
        audio.export(mp3_file, format='wav')
        print(f"Converti en MP3 : {mp3_file}")
    
    def duree_enregistrement(self, filename):
        echantillon = AudioSegment.from_mp3(filename)
        duree= (len(echantillon))/1000 # durée en sec
        return duree
        

    def log_recording(self, filename):
        # recuperation du nom du fichier pour donner la date d'enregistrement et sa durée 
        duree=self.duree_enregistrement(filename)
        conn = sqlite3.connect('recordings.db')
        filename=filename.replace(".wav",".mp3")
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS recordings
                    (date TEXT, filename TEXT, duree TEXT)''')

        c.execute("INSERT INTO recordings (date, filename, duree) VALUES (?, ?, ?)", 
                (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), filename, duree))
        
        conn.commit()
        conn.close()

    def record(self):
        # configuration de l'enregistrement
        
        last_record=datetime.datetime.now()
        time.sleep(1) 

        while True:
 
            data = sd.rec(int(self.fs * 5), samplerate=self.fs, channels=1, dtype='int16') # echantillon de 5 sec min 
            sd.wait()  # Attendre que l'enregistrement soit terminé
            volume_norm = np.linalg.norm(data)
            db = 20 *  np.log10(volume_norm/8)
            
            
            print(f"Volume db: {round(db,1)}")
            
            
            if db > self.threshold:
                start_time = datetime.datetime.now()
                print("Niveau de décibels dépassé ! Enregistrement...")
                if (start_time-last_record).total_seconds() > 5.5:
                    if self.audio_data:
                        self.save_audio()
                        self.audio_data=[]
                        self.audio_data.append(data)
                        last_record=datetime.datetime.now()
                    else:
                        self.audio_data.append(data)
                        last_record=datetime.datetime.now()
                    
                else:
                    self.audio_data.append(data)
                    last_record=datetime.datetime.now()
                   
                
            else:
                print("Aucun enregistrement effectué.")


    def save_audio(self):
        
        filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bits
            wf.setframerate(self.fs)
            wf.writeframes(np.concatenate(self.audio_data).tobytes())
        print(f"Enregistrement sauvegardé sous : {filename}")
        self.convert_wav_to_mp3(filename)
        self.log_recording(filename)
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    recorder = AudioRecorder(threshold=70, duration=30)
    recorder.record()
