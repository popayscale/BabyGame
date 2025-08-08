# Vérification et installation automatique de pygame
try:
    import pygame
except ImportError:
    print("Pygame n'est pas installé. Installation en cours...")
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        print("Pygame installé avec succès !")
        import pygame
    except Exception as e:
        print(f"Erreur lors de l'installation de pygame: {e}")
        print("Veuillez installer pygame manuellement avec : pip install pygame")
        sys.exit(1)

import random
import sys
import math

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 800
HAUTEUR = 600
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (50, 150, 255)
VERT = (50, 255, 50)
ROUGE = (255, 50, 50)
JAUNE = (255, 255, 50)
GRIS_CLAIR = (200, 200, 200)
GRIS_FONCE = (100, 100, 100)

class Pinceau:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.taille = 15
        self.vitesse = 3
        self.couleur_actuelle = BLEU
    
    def deplacer(self, dx, dy):
        """Déplace le pinceau sans peindre"""
        if dx == 0 and dy == 0:
            return
            
        nouveau_x = self.x + dx * self.vitesse
        nouveau_y = self.y + dy * self.vitesse
        
        # Garder le pinceau dans l'écran
        self.x = max(self.taille//2, min(LARGEUR - self.taille//2, nouveau_x))
        self.y = max(self.taille//2, min(HAUTEUR - self.taille//2, nouveau_y))
    
    def peindre_et_deplacer(self, dx, dy):
        """Déplace le pinceau ET peint en même temps"""
        if dx == 0 and dy == 0:
            return None
            
        # Position de départ
        ancien_x = self.x
        ancien_y = self.y
        
        # Déplacement
        self.deplacer(dx, dy)
        
        # Créer le tracé de peinture
        return TracePeinture(ancien_x, ancien_y, self.x, self.y, self.couleur_actuelle)
    
    def changer_couleur(self, nouvelle_couleur):
        self.couleur_actuelle = nouvelle_couleur
    
    def dessiner(self, ecran):
        # Dessiner le pinceau
        pygame.draw.circle(ecran, self.couleur_actuelle, (int(self.x), int(self.y)), self.taille//2)
        # Contour pour mieux voir le pinceau
        pygame.draw.circle(ecran, NOIR, (int(self.x), int(self.y)), self.taille//2, 2)

class TracePeinture:
    def __init__(self, x1, y1, x2, y2, couleur):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.couleur = couleur
        self.epaisseur = 8
    
    def dessiner(self, ecran):
        if self.x1 != self.x2 or self.y1 != self.y2:
            pygame.draw.line(ecran, self.couleur, (int(self.x1), int(self.y1)), 
                           (int(self.x2), int(self.y2)), self.epaisseur)

class Jeu:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Peinture au Pinceau")
        self.horloge = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.font_titre = pygame.font.Font(None, 32)
        
        # Support manette
        pygame.joystick.init()
        self.manette = None
        if pygame.joystick.get_count() > 0:
            self.manette = pygame.joystick.Joystick(0)
            self.manette.init()
        
        # État du jeu
        self.pinceau = Pinceau(LARGEUR // 2, HAUTEUR // 2)
        self.traces = []
        self.afficher_aide = False
        
        # Bouton aide
        self.bouton_aide = pygame.Rect(LARGEUR - 80, 10, 70, 30)
    
    def reinitialiser(self):
        """Efface tout et remet le pinceau au centre"""
        self.traces.clear()
        self.pinceau.x = LARGEUR // 2
        self.pinceau.y = HAUTEUR // 2
    
    def effacer_dernier_trace(self):
        """Efface le dernier tracé"""
        if self.traces:
            self.traces.pop()
    
    def gerer_entrees(self):
        touches = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        # CLAVIER
        # ZQSD : Déplacement seul
        if touches[pygame.K_q]:
            dx = -1
        if touches[pygame.K_d]:
            dx = 1
        if touches[pygame.K_z]:
            dy = -1
        if touches[pygame.K_s]:
            dy = 1
        
        # Si mouvement ZQSD, juste déplacer
        if dx != 0 or dy != 0:
            self.pinceau.deplacer(dx, dy)
            return
        
        # Flèches : Déplacement + peinture
        if touches[pygame.K_LEFT]:
            dx = -1
        if touches[pygame.K_RIGHT]:
            dx = 1
        if touches[pygame.K_UP]:
            dy = -1
        if touches[pygame.K_DOWN]:
            dy = 1
        
        # Si mouvement flèches, déplacer ET peindre
        if dx != 0 or dy != 0:
            trace = self.pinceau.peindre_et_deplacer(dx, dy)
            if trace:
                self.traces.append(trace)
            return
        
        # MANETTE
        if self.manette:
            # Stick gauche : déplacement seul
            stick_gauche_x = self.manette.get_axis(0)
            stick_gauche_y = self.manette.get_axis(1)
            
            # Stick droit : déplacement + peinture
            stick_droit_x = self.manette.get_axis(2)
            stick_droit_y = self.manette.get_axis(3)
            
            # Priorité au stick droit (peinture)
            if abs(stick_droit_x) > 0.2 or abs(stick_droit_y) > 0.2:
                dx = stick_droit_x if abs(stick_droit_x) > 0.2 else 0
                dy = stick_droit_y if abs(stick_droit_y) > 0.2 else 0
                trace = self.pinceau.peindre_et_deplacer(dx, dy)
                if trace:
                    self.traces.append(trace)
            
            # Sinon stick gauche (déplacement seul)
            elif abs(stick_gauche_x) > 0.2 or abs(stick_gauche_y) > 0.2:
                dx = stick_gauche_x if abs(stick_gauche_x) > 0.2 else 0
                dy = stick_gauche_y if abs(stick_gauche_y) > 0.2 else 0
                self.pinceau.deplacer(dx, dy)
    
    def gerer_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.reinitialiser()
                elif event.key == pygame.K_BACKSPACE:
                    self.effacer_dernier_trace()
                elif event.key == pygame.K_h:
                    self.afficher_aide = not self.afficher_aide
                # Couleurs
                elif event.key == pygame.K_1:
                    self.pinceau.changer_couleur(VERT)
                elif event.key == pygame.K_2:
                    self.pinceau.changer_couleur(JAUNE)
                elif event.key == pygame.K_3:
                    self.pinceau.changer_couleur(BLEU)
                elif event.key == pygame.K_4:
                    self.pinceau.changer_couleur(ROUGE)
                elif event.key == pygame.K_5:
                    self.pinceau.changer_couleur(NOIR)
            
            elif event.type == pygame.JOYBUTTONDOWN and self.manette:
                if event.button == 0:  # A - Vert
                    self.pinceau.changer_couleur(VERT)
                elif event.button == 3:  # Y - Jaune
                    self.pinceau.changer_couleur(JAUNE)
                elif event.button == 2:  # X - Bleu
                    self.pinceau.changer_couleur(BLEU)
                elif event.button == 1:  # B - Rouge
                    self.pinceau.changer_couleur(ROUGE)
                elif event.button == 7:  # Start - Reinitialiser
                    self.reinitialiser()
                elif event.button == 6:  # Select/Back - Effacer dernier
                    self.effacer_dernier_trace()
                elif event.button == 5:  # R1 - Ouvrir aide
                    self.afficher_aide = True
                elif event.button == 4:  # L1 - Fermer aide
                    self.afficher_aide = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.bouton_aide.collidepoint(event.pos):
                    self.afficher_aide = not self.afficher_aide
        
        return True
    
    def dessiner(self):
        self.ecran.fill(BLANC)
        
        # Dessiner toutes les traces
        for trace in self.traces:
            trace.dessiner(self.ecran)
        
        # Dessiner le pinceau
        self.pinceau.dessiner(self.ecran)
        
        # Dessiner le bouton aide
        pygame.draw.rect(self.ecran, GRIS_CLAIR, self.bouton_aide)
        pygame.draw.rect(self.ecran, NOIR, self.bouton_aide, 2)
        text_aide = self.font.render("AIDE", True, NOIR)
        text_rect = text_aide.get_rect(center=self.bouton_aide.center)
        self.ecran.blit(text_aide, text_rect)
        
        # Indicateur de couleur actuelle
        pygame.draw.circle(self.ecran, self.pinceau.couleur_actuelle, (30, 30), 15)
        pygame.draw.circle(self.ecran, NOIR, (30, 30), 15, 2)
        
        # Afficher l'aide si activée
        if self.afficher_aide:
            self.dessiner_aide()
        
        pygame.display.flip()
    
    def dessiner_aide(self):
        # Fond semi-transparent
        overlay = pygame.Surface((LARGEUR, HAUTEUR))
        overlay.set_alpha(200)
        overlay.fill(GRIS_FONCE)
        self.ecran.blit(overlay, (0, 0))
        
        # Titre
        titre = self.font_titre.render("COMMANDES", True, BLANC)
        titre_rect = titre.get_rect(center=(LARGEUR//2, 50))
        self.ecran.blit(titre, titre_rect)
        
        # Colonnes
        col_gauche_x = LARGEUR//4
        col_droite_x = 3*LARGEUR//4
        start_y = 100
        
        # Commandes manette (gauche)
        manette_titre = self.font_titre.render("MANETTE", True, BLANC)
        manette_rect = manette_titre.get_rect(center=(col_gauche_x, start_y))
        self.ecran.blit(manette_titre, manette_rect)
        
        commandes_manette = [
            "Stick gauche : Déplacer",
            "Stick droit : Peindre",
            "A : Vert",
            "Y : Jaune", 
            "X : Bleu",
            "B : Rouge",
            "Start : Effacer tout",
            "Select : Effacer dernier",
            "R1 : Ouvrir aide",
            "L1 : Fermer aide"
        ]
        
        for i, cmd in enumerate(commandes_manette):
            text = self.font.render(cmd, True, BLANC)
            self.ecran.blit(text, (col_gauche_x - 100, start_y + 40 + i * 25))
        
        # Commandes clavier (droite)
        clavier_titre = self.font_titre.render("CLAVIER", True, BLANC)
        clavier_rect = clavier_titre.get_rect(center=(col_droite_x, start_y))
        self.ecran.blit(clavier_titre, clavier_rect)
        
        commandes_clavier = [
            "ZQSD : Déplacer",
            "Flèches : Peindre",
            "1 : Vert",
            "2 : Jaune",
            "3 : Bleu",
            "4 : Rouge",
            "5 : Noir",
            "Espace : Effacer tout",
            "Backspace : Effacer dernier",
            "H : Aide"
        ]
        
        for i, cmd in enumerate(commandes_clavier):
            text = self.font.render(cmd, True, BLANC)
            self.ecran.blit(text, (col_droite_x - 80, start_y + 40 + i * 25))
        
        # Instructions pour fermer
        fermer_text = self.font.render("Cliquez sur AIDE ou appuyez sur H/L1 pour fermer", True, JAUNE)
        fermer_rect = fermer_text.get_rect(center=(LARGEUR//2, HAUTEUR - 30))
        self.ecran.blit(fermer_text, fermer_rect)
    
    def executer(self):
        en_cours = True
        
        while en_cours:
            en_cours = self.gerer_evenements()
            self.gerer_entrees()
            self.dessiner()
            self.horloge.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Lancement du jeu
if __name__ == "__main__":
    jeu = Jeu()
    jeu.executer()
