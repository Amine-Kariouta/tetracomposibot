# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Amine KARIOUTA 21316380
#  Prénom Nom No_étudiant/e : Aymen BRAHIMI 21102062
#
# Robot Challenger: 4 stratégies hybrides pour Paint Wars
# - Subsomption: architecture hiérarchisée
# - Braitenberg Love Wall: attire vers les murs  
# - Braitenberg Hate Wall: fuit les murs
# - Algorithme Génétique: poids optimisés par GA sur 500 générations
#
# Exécution: python tetracomposibot.py config_Paintwars 1 False 1 ( ex: python tetracomposibot.py config_Paintwars 1 2 1)
# Paramètres: affiche=1, position=False (gauche), mode=1 (jeu complet = 2001 itérations)
# Les poids GA viennent de genetic_algorithms.py (TP2): sélection roulette, 500 générations, μ=5 λ=20

from robot import *
import math
import random

nb_robots = 0

class Robot_player(Robot):
    """
    Classe principale pour le projet Paint Wars.
    Contient 4 stratégies différentes, sélectionnées par le nom du robot.
    
    Stratégies disponibles:
    1. "subsomption": Architecture de subsomption (3 niveaux de priorité)
    2. "braitenberg_lovewall": Braitenberg love wall (attire vers les murs)
    3. "braitenberg_hatewall": Braitenberg hate wall (fuit les murs)
    4. "ga_optimized": Perceptron avec poids optimisés par GA
    """

    team_name = "Equipe6"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # Compteur de blocage en subsomption: compte les itérations où robot est coincé
                              # Si memory > 15: robot recule et tourne pour sortir de l'impasse
    
    # Paramètres Braitenberg
    braitenberg_weights = [1.0, -1.0, -1.0, 1.0]  # love wall
    
    # Paramètres GA (poids pré-optimisés)
    # Ces poids proviennent de l'optimisation par algorithme génétique
    # Trouvés en lançant genetic_algorithms.py pendant 500 générations (μ=5, λ=20)
    # À chaque génération: sélection roulette, mutation des meilleurs parents
    # Les poids finaux représentent un perceptron qui équilibre exploration et combat
    # Les poids exacts s'affichent dans la console terminal avec "[NOUVEAU MEILLEUR]"
    # Les scores sont sauvegardés dans results_genetic_*.csv (voir ligne avec bestParam)
    ga_params = [-1, -1, -1, -1, -1, 1, 0, -1]  # Poids optimisés pour Paint Wars (meilleur en équipe: 47 pts)

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        self.robot_name = name
        super().__init__(x_0, y_0, theta_0, name=name, team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        """
        Fonction principale appelée à chaque itération par le simulateur.
        Route vers la stratégie appropriée selon le nom du robot.
        
        Entrées:
        - sensors: liste de 8 distances (0.0 à 1.0) pour 8 capteurs autour du robot
        - sensor_view: type d'obstacle (0:vide, 1:mur, 2:robot)
        - sensor_robot: numéro du robot détecté
        - sensor_team: équipe du robot détecté
        
        Retour: (translation, rotation, ask_for_reset)
        """
        
        # Routage vers la stratégie appropriée
        if "subsomption" in self.robot_name.lower():
            translation, rotation = self._strategy_subsomption(sensors, sensor_view)
        elif "braitenberg_lovewall" in self.robot_name.lower():
            translation, rotation = self._strategy_braitenberg_lovewall(sensors)
        elif "braitenberg_hatewall" in self.robot_name.lower():
            translation, rotation = self._strategy_braitenberg_hatewall(sensors)
        elif "algorithme_genetique" in self.robot_name.lower():
            translation, rotation = self._strategy_algorithme_genetique(sensors)
        else:
            # Par défaut: subsomption
            translation, rotation = self._strategy_subsomption(sensors, sensor_view)
        
        return translation, rotation, False
    
    # ========== STRATÉGIE 1: SUBSOMPTION ==========
    def _strategy_subsomption(self, sensors, sensor_view):
        """
        Architecture de subsomption: 3 niveaux de priorité hiérarchisés.
        
        Les niveaux supérieurs supprimentes (subsument) les niveaux inférieurs.
        - Niveau 1 (priorité basse): Avancer tout droit (comportement par défaut)
        - Niveau 2 (priorité moyenne): Éviter les murs
        - Niveau 3 (priorité haute): Attaquer les robots (ignorer les murs)
        """
        
        # Séparer capteurs: murs vs robots
        sensor_to_wall = []
        sensor_to_robot = []
        for i in range(8):
            if sensor_view[i] == 1:  # mur
                sensor_to_wall.append(sensors[i])
                sensor_to_robot.append(1.0)
            elif sensor_view[i] == 2:  # robot
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(sensors[i])
            else:  # rien
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)
        
        # NIVEAU 1 (PRIORITÉ BASSE): Aller tout droit
        translation = 0.7  # vitesse plus rapide pour explorer plus vite
        rotation = 0.0  # tout droit
        
        # NIVEAU 2 (PRIORITÉ MOYENNE): Éviter les murs
        # Si mur détecté -> tourner pour éviter
        if (sensor_to_wall[sensor_front] < 0.8 or 
            sensor_to_wall[sensor_front_left] < 0.7 or 
            sensor_to_wall[sensor_front_right] < 0.7):
            translation = sensor_to_wall[sensor_front] * 0.8
            rotation = (sensor_to_wall[sensor_front_left] - sensor_to_wall[sensor_front_right])
        
        # NIVEAU 3 (PRIORITÉ HAUTE): Attaquer les robots
        # Si robot détecté -> foncer dessus (supprime niveaux 1 et 2)
        if (sensor_to_robot[sensor_front] < 1.0 or 
            sensor_to_robot[sensor_front_left] < 1.0 or 
            sensor_to_robot[sensor_front_right] < 1.0):
            translation = sensor_to_robot[sensor_front] * 0.8
            rotation = -(sensor_to_robot[sensor_front_left] - sensor_to_robot[sensor_front_right])
        
        # COMPTEUR DE BLOCAGE: Si on n'avance pas malgré les ordres, on est coincé
        # Incrémenter si translation commandée mais capteur avant < 0.3 (bloquer par quelque chose)
        if translation > 0.3 and sensor_to_wall[sensor_front] < 0.3:
            self.memory += 1  # Robot commande avancer mais mur détecté -> coinçé
        else:
            self.memory = 0   # Libre: réinitialiser compteur
        
        # Après 8 itérations coincé, inverser pour sortir du blocage
        # Au lieu d'avancer dans le mur, on recule et tourne pour explorer ailleurs
        if self.memory > 8:
            translation = -0.8  # Recule: négatif = arrière
            rotation = 0.2      # Tourne légèrement pour se dégager
            # memory restera > 15 tant qu'on avance pas, donc on va continuer à reculer
        
        return translation, rotation
    
    # ========== STRATÉGIE 2: BRAITENBERG LOVE WALL ==========
    def _strategy_braitenberg_lovewall(self, sensors):
        """
        Réseau de Braitenberg: 'Love Wall' (attire vers les murs).
        
        Poids: [1.0, -1.0, -1.0, 1.0]
        - Capteur avant-gauche → moteur droit (croisé)
        - Capteur avant-droit → moteur gauche (croisé)
        
        Comportement: Le robot est attiré par les murs et les longe.
        """
        
        # Capteurs avant (indices 0, 1, 2)
        sensor_left = sensors[sensor_front_left]
        sensor_center = sensors[sensor_front]
        sensor_right = sensors[sensor_front_right]
        
        # Braitenberg avec croisement des connexions
        left_motor = self.braitenberg_weights[0] * sensor_left + self.braitenberg_weights[1] * sensor_right
        right_motor = self.braitenberg_weights[2] * sensor_left + self.braitenberg_weights[3] * sensor_right
        
        # Normaliser les valeurs
        translation = (left_motor + right_motor) / 2.0
        rotation = (right_motor - left_motor) / 2.0
        
        # Clamp aux limites [-1, 1]
        translation = max(-1.0, min(1.0, translation))
        rotation = max(-1.0, min(1.0, rotation))
        
        return translation, rotation
    
    # ========== STRATÉGIE 3: BRAITENBERG HATE WALL ==========
    def _strategy_braitenberg_hatewall(self, sensors):
        """
        Réseau de Braitenberg: 'Hate Wall' (fuit les murs).
        
        Poids inversés par rapport à love wall.
        
        Comportement: Le robot fuit les murs et cherche l'espace ouvert.
        """
        
        # Capteurs avant
        sensor_left = sensors[sensor_front_left]
        sensor_center = sensors[sensor_front]
        sensor_right = sensors[sensor_front_right]
        
        # Inverse de love wall (fuite des murs)
        hate_weights = [-w for w in self.braitenberg_weights]
        left_motor = hate_weights[0] * sensor_left + hate_weights[1] * sensor_right
        right_motor = hate_weights[2] * sensor_left + hate_weights[3] * sensor_right
        
        # Normaliser
        translation = (left_motor + right_motor) / 2.0
        rotation = (right_motor - left_motor) / 2.0
        
        translation = max(-1.0, min(1.0, translation))
        rotation = max(-1.0, min(1.0, rotation))
        
        return translation, rotation
    
    # ========== STRATÉGIE 4: ALGORITHME GÉNÉTIQUE ==========
    def _strategy_algorithme_genetique(self, sensors):
        """
        Perceptron dont les 8 poids ont été optimisés au TP2 par algorithme génétique.
        
        Ces poids viennent de genetic_algorithms.py:
        - Lancé sur 500 générations
        - Population: μ=5 parents, λ=20 enfants par génération
        - Sélection: roulette (probabilité = score / somme des scores)
        - Mutation: ajout de bruit aléatoire aux meilleurs parents
        - Résultats sauvegardés dans results_genetic_*.csv avec les scores
        - Les 8 poids finaux ga_params = [-1, -1, -1, -1, -1, 1, 0, -1]
        """
        
        # Capteurs avant (gauche, centre, droite)
        sensor_left = sensors[sensor_front_left]
        sensor_center = sensors[sensor_front]
        sensor_right = sensors[sensor_front_right]
        
        # Perceptron simple: chaque poids multiplie un capteur et s'ajoute au biais
        # Puis on passe le résultat par tanh pour normaliser en [-1, 1]
        # Les 8 poids proviennent de 500 générations d'algorithme génétique
        translation = math.tanh(self.ga_params[0] + self.ga_params[1] * sensor_left + self.ga_params[2] * sensor_center + self.ga_params[3] * sensor_right)
        rotation = math.tanh(self.ga_params[4] + self.ga_params[5] * sensor_left + self.ga_params[6] * sensor_center + self.ga_params[7] * sensor_right)
        
        return translation, rotation

