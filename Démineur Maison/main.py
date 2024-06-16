import tkinter as tk
import random
import os
import time

class Demineur:
    def __init__(self, root):
        self.root = root
        self.menu_difficulte()

    def menu_difficulte(self):
        self.clear_window()

        tk.Label(self.root, text="Choisir la difficulté :", font=("Arial", 14)).grid(row=0, columnspan=3, pady=10)

        tk.Button(self.root, text="Facile", command=lambda: self.commencer_jeu(8, 8, 10)).grid(row=1, column=0, padx=10, pady=5)
        tk.Button(self.root, text="Moyen", command=lambda: self.commencer_jeu(12, 12, 20)).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Difficile", command=lambda: self.commencer_jeu(16, 16, 40)).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(self.root, text="Extrème", command=lambda: self.commencer_jeu(24, 24, 100)).grid(row=1, column=3, padx=10, pady=5)

        credits_btn = tk.Button(self.root, text="Crédits", command=self.afficher_credits)
        credits_btn.grid(row=2, column=1, pady=10)
        credits_btn.bind("<Button-2>", lambda event: self.creer_grille_egg())

    def commencer_jeu(self, lignes, colonnes, mines):
        self.clear_window()

        self.lignes = lignes
        self.colonnes = colonnes
        self.mines = mines
        self.boutons = {}
        self.positions_mines = set()
        self.cases_revelees = 0
        self.cases_drapeaux = set()
        self.mines_restantes = self.mines

        self.charger_images()
        self.creer_widgets()
        self.placer_mines()
        self.calculer_nombre_mines()
        self.creer_interface()

        self.temps_debut = time.time()
        self.update_temps()

    def creer_grille_egg(self):
        self.clear_window()
        self.lignes = 7
        self.colonnes = 29  # Largeur ajustée pour inclure "HAIKO"
        self.boutons = {}
        self.positions_mines = set()
        self.cases_revelees = 0
        self.cases_drapeaux = set()
        self.mines_restantes = 5  # Pas de mines dans cette grille spéciale

        self.charger_images()
        self.creer_widgets_egg()
        self.creer_interface()

        self.temps_debut = time.time()
        self.update_temps()

    def creer_widgets_egg(self):
        # Grille formant "HAIKO"
        grille_haiko = [
            "H   H  AAAAA IIIII K   K  OOO ",
            "H   H  A   A   I   K  K  O   O",
            "H   H  A   A   I   K K   O   O",
            "HHHHH  AAAAA   I   KK    O   O",
            "H   H  A   A   I   K K   O   O",
            "H   H  A   A   I   K  K  O   O",
            "H   H  A   A IIIII K   K  OOO ",
        ]

        for r, ligne in enumerate(grille_haiko):
            for c, char in enumerate(ligne):
                if char != " ":
                    btn = tk.Button(self.root, image=self.images['case'])
                    btn.grid(row=r + 2, column=c)
                    btn.bind("<Button-1>", lambda e, r=r, c=c: self.reveler(r, c))
                    btn.bind("<Button-3>", lambda e, r=r, c=c: self.basculer_drapeau(r, c))
                    self.boutons[(r, c)] = btn
                else:
                    self.boutons[(r, c)] = None

        tk.Button(self.root, text="Recommencer", command=self.menu_difficulte).grid(row=self.lignes + 3, columnspan=self.colonnes, pady=10)

    def afficher_credits(self):
        credits_text = """
        Développé par : Haiko | OmégaCraft
        Version : 1.0
        """

        fenetre_credits = tk.Toplevel(self.root)
        fenetre_credits.title("Crédits")
        tk.Label(fenetre_credits, text=credits_text, padx=20, pady=20).pack()

    def charger_images(self):
        chemin_assets = os.path.join(os.path.dirname(__file__), "assets")
        self.images = {
            'case': self.charger_image(os.path.join(chemin_assets, "tuille.png")),
            'mine': self.charger_image(os.path.join(chemin_assets, "mine.png")),
            'drapeau': self.charger_image(os.path.join(chemin_assets, "drapeau.png")),
        }
        for i in range(9):
            self.images[str(i)] = self.charger_image(os.path.join(chemin_assets, f"{i}.png"))

    def charger_image(self, chemin):
        try:
            return tk.PhotoImage(file=chemin)
        except tk.TclError:
            print(f"Erreur : Impossible de charger l'image {chemin}")
            return tk.PhotoImage()

    def creer_widgets(self):
        for r in range(self.lignes):
            for c in range(self.colonnes):
                btn = tk.Button(self.root, image=self.images['case'])
                btn.grid(row=r + 2, column=c)
                btn.bind("<Button-1>", lambda e, r=r, c=c: self.reveler(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.basculer_drapeau(r, c))
                btn.bind("<Button-2>", lambda e, r=r, c=c: self.reveler_voisins(r, c)) 
                self.boutons[(r, c)] = btn

        tk.Button(self.root, text="Recommencer", command=self.menu_difficulte).grid(row=self.lignes + 4, columnspan=self.colonnes, pady=10)

    def creer_interface(self):
        self.label_mines = tk.Label(self.root, text=f"Mines restantes : {self.mines_restantes}")
        self.label_mines.grid(row=self.lignes + 3, columnspan=self.colonnes, pady=10)

        self.label_temps = tk.Label(self.root, text="Temps : 0 s")
        self.label_temps.grid(row=self.lignes + 2, columnspan=self.colonnes, pady=10)

    def placer_mines(self):
        while len(self.positions_mines) < self.mines:
            r = random.randint(0, self.lignes - 1)
            c = random.randint(0, self.colonnes - 1)
            self.positions_mines.add((r, c))

    def calculer_nombre_mines(self):
        self.nombre_mines = {}
        for r in range(self.lignes):
            for c in range(self.colonnes):
                if (r, c) in self.positions_mines:
                    self.nombre_mines[(r, c)] = -1
                else:
                    count = sum((nr, nc) in self.positions_mines for nr in range(r-1, r+2) for nc in range(c-1, c+2))
                    self.nombre_mines[(r, c)] = count

    def reveler(self, r, c):
        if self.boutons[(r, c)]['state'] == 'disabled' or (r, c) in self.cases_drapeaux:
            return
        
        if (r, c) in self.positions_mines:
            self.boutons[(r, c)].config(image=self.images['mine'])
            self.fin_de_jeu()
        else:
            count = self.nombre_mines[(r, c)]
            self.boutons[(r, c)].config(image=self.images[str(count)], state='disabled')
            self.cases_revelees += 1
            
            if count == 0:
                self.reveler_voisins(r, c)
            
            self.verifier_victoire()

    def reveler_voisins(self, r, c):
        for nr in range(max(0, r-1), min(self.lignes, r+2)):
            for nc in range(max(0, c-1), min(self.colonnes, c+2)):
                if (nr, nc) in self.boutons and self.boutons[(nr, nc)]['state'] == 'normal':
                    self.reveler(nr, nc)

    def basculer_drapeau(self, r, c):
        if self.boutons[(r, c)]['state'] == 'disabled':
            return

        if (r, c) in self.cases_drapeaux:
            self.boutons[(r, c)].config(image=self.images['case'])
            self.cases_drapeaux.remove((r, c))
            self.mines_restantes += 1  # Retirer un drapeau augmente le nombre de mines restantes
        else:
            self.boutons[(r, c)].config(image=self.images['drapeau'])
            self.cases_drapeaux.add((r, c))
            self.mines_restantes -= 1  # Placer un drapeau diminue le nombre de mines restantes
        
        self.label_mines.config(text=f"Mines restantes : {self.mines_restantes}")

    def update_temps(self):
        temps_actuel = time.time() - self.temps_debut
        self.label_temps.config(text=f"Temps : {int(temps_actuel)} s")
        self.root.after(1000, self.update_temps)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def verifier_victoire(self):
        if self.cases_revelees == self.lignes * self.colonnes - self.mines:
            for (r, c) in self.boutons:
                if self.boutons[(r, c)]['state'] == 'normal':
                    self.boutons[(r, c)].config(state='disabled')
            self.afficher_message_victoire()

    def afficher_message_victoire(self):
        fenetre_victoire = tk.Toplevel(self.root)
        fenetre_victoire.title("Victoire !")
        tk.Label(fenetre_victoire, text="Félicitations, vous avez gagné !").pack()
        tk.Button(fenetre_victoire, text="OK", command=fenetre_victoire.destroy).pack()

    def fin_de_jeu(self):
        for (r, c) in self.positions_mines:
            self.boutons[(r, c)].config(image=self.images['mine'])
        for bouton in self.boutons.values():
            bouton.config(state='disabled')
        self.afficher_message_fin_jeu()

    def afficher_message_fin_jeu(self):
        fenetre_fin_jeu = tk.Toplevel(self.root)
        fenetre_fin_jeu.title("Game Over")
        tk.Label(fenetre_fin_jeu, text="Game Over! Vous avez perdu.").pack()
        tk.Button(fenetre_fin_jeu, text="OK", command=fenetre_fin_jeu.destroy).pack()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Démineur")
    jeu = Demineur(root)
    root.mainloop()
