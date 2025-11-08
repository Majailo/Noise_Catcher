import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading
from audio_recorder import AudioRecorder


class Interface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enregistreur Audio")
        self.recorder = AudioRecorder()
        self.setup_interface()

    def setup_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Contrôles
        ttk.Button(main_frame, text="Démarrer", command=self.demarrer).grid(row=0, column=0, padx=5)
        ttk.Button(main_frame, text="Arrêter", command=self.arreter).grid(row=0, column=1, padx=5)

        # Liste des enregistrements
        self.tree = ttk.Treeview(main_frame, columns=('Date', 'Niveau DB'), show='headings')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Niveau DB', text='Niveau DB')
        self.tree.grid(row=1, column=0, columnspan=2, pady=10)

        # Graphique
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=main_frame)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2)

    def mettre_a_jour_graphique(self):
        self.ax.clear()
        if self.recorder.fichiers_enregistres:
            niveaux = [f['niveau_db'] for f in self.recorder.fichiers_enregistres]
            heures = [f['date'].hour for f in self.recorder.fichiers_enregistres]

            self.ax.pie(niveaux, labels=[f"{h}h" for h in heures], autopct='%1.1f%%')
            self.ax.set_title("Répartition des enregistrements par niveau sonore")
            self.canvas.draw()

    def mettre_a_jour_liste(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for enreg in self.recorder.fichiers_enregistres:
            self.tree.insert('', 'end', values=(
                enreg['date'].strftime('%Y-%m-%d %H:%M:%S'),
                f"{enreg['niveau_db']:.1f} dB"
            ))

    def demarrer(self):
        self.recorder.demarrer()
        threading.Thread(target=self.actualisation_interface, daemon=True).start()

    def arreter(self):
        self.recorder.arreter()

    def actualisation_interface(self):
        while True:
            self.mettre_a_jour_liste()
            self.mettre_a_jour_graphique()
            self.root.after(1000)  # Actualisation toutes les secondes

    def lancer(self):
        self.root.mainloop()