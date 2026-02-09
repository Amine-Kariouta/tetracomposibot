# Projet "robotique" IA&Jeux 2025
# 
# ÉQUIPE 6 - VERSION AMÉLIORÉE v2.0
# Subsomption + 2 Braitenberg + Algorithme Génétique
# Architecture hiérarchique pour Paint Wars
#
# Stratégies intégrées:
# 1. SUBSOMPTION (5 niveaux): Urgence décroissante (mur→allié→ennemi→GA)
# 2. BRAITENBERG 1: Aimer les murs (wall-following pour explorer)  
# 3. BRAITENBERG 2: Détester les ennemis (poursuite agressive)
# 4. ALGORITHME GÉNÉTIQUE: Perceptron tanh optimisé pour exploration
#


from robot import * 
import math
import random

nb_robots = 0

class Robot_player(Robot):

    team_name = "BOSY" # vous pouvez modifier le nom de votre équipe
    robot_id = -1 # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0 # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        #print(self.robot_id)

        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        """
        Contrôleur hiérarchique: Subsomption avec 5 niveaux de priorité
        """

        def _parse_sensors():
            """Analyse les capteurs pour détecter murs, alliés, ennemis"""
            walls = []
            enemies = []
            allies = []
            
            for i in range(8):
                if sensor_view[i] == 1:  # Mur détecté
                    walls.append(sensors[i])
                elif sensor_view[i] == 2:  # Robot détecté
                    if sensor_team[i] != self.team_name:
                        enemies.append((i, sensors[i]))  # Ennemi
                    else:
                        allies.append((i, sensors[i]))  # Allié
                else:
                    walls.append(1.0)  # Aucun obstacle = libre
            
            return walls, enemies, allies

        walls, enemies, allies = _parse_sensors()

        def wanderer():
            """NIVEAU 0: Exploration aléatoire (fallback)"""
            translation = sensors[0]*0.8  # sensor_front = 0
            rotation = 1.0 * sensors[7] - 1.0 * sensors[1] + (random.random()-0.5)*0.1  # left=7, right=1
            return translation, rotation, False

        def braitenberg_love_wall():
            """
            BRAITENBERG 1: Aimer les murs
            Objectif: Explorer l'arène en suivant les contours des murs
            Technique: Plus il y a des murs visibles, plus le robot avance
            (Les murs = terrain exploré = gain de points en Paint Wars)
            """
            # Mesure la proximité des murs (inversée: 1=far, 0=wall)
            wall_left = max(walls[sensor_front_left], walls[sensor_left], walls[sensor_rear_left])
            wall_right = max(walls[sensor_front_right], walls[sensor_right], walls[sensor_rear_right])
            wall_front = max(walls[sensor_front], walls[sensor_front_left], walls[sensor_front_right])
            
            # Avancer si murs visibles (on "aime" les murs = on explore)
            translation = 0.6 + 0.4 * wall_front
            
            # Tourner vers le côté le plus libre (pour longer le mur)
            rotation = 0.8 * (wall_left - wall_right) + 0.4 * (walls[sensor_front_left] - walls[sensor_front_right])
            
            return translation, rotation, False

        def braitenberg_hate_enemy():
            """
            BRAITENBERG 2: Détester les ennemis
            Objectif: Chasser et combattre les robots ennemis
            Technique: S'orienter vers la position de l'ennemi le plus proche
            """
            if not enemies:
                return braitenberg_love_wall()  # Pas d'ennemi = explorer les murs
            
            # Trouver l'ennemi le plus proche (distance minimale)
            closest_idx, closest_dist = min(enemies, key=lambda x: x[1])
            
            # Créer un vecteur attraction vers l'ennemi (8 capteurs = 8 directions)
            rotation_signals = [0] * 8
            for sensor_idx, dist in enemies:
                # Plus l'ennemi est proche, plus fort le signal
                rotation_signals[sensor_idx] = 1.0 - dist
            
            # Combiner les signaux pour la rotation
            left_signal = (rotation_signals[sensor_front_left]*0.9 + 
                          rotation_signals[sensor_left]*0.7 + 
                          rotation_signals[sensor_rear_left]*0.3)
            right_signal = (rotation_signals[sensor_front_right]*0.9 + 
                           rotation_signals[sensor_right]*0.7 + 
                           rotation_signals[sensor_rear_right]*0.3)
            
            rotation = left_signal - right_signal
            
            # Avancer agressivement vers l'ennemi
            translation = 0.7 + 0.3 * (1.0 - closest_dist)
            
            return translation, rotation, False

        def avoid_wall_critical():
            # Si collé au mur devant, recule et tourne
            if len(walls) > 0 and walls[0] < 0.25:
                translation = -0.3
                rotation = 0.5
                return translation, rotation, True
            return None

        def avoid_ally():
            """
            BRAITENBERG ALLIÉ: Éviter la collision avec les alliés
            Permet aux 4 robots de se coordonner et ne pas se bloquer
            """
            if not allies:
                return None
            
            # Chercher un allié trop proche devant
            front_ally_close = (allies[0][1] < 0.3 if allies else False)
            
            if front_ally_close:
                # Reculer légèrement pour laisser passer
                translation = -0.1
                closest_ally_idx = allies[0][0]
                rotation = 0.3 * (1.0 - allies[0][1]) * (closest_ally_idx - 3.5) / 3.5
                return translation, rotation, True
            
            return None

        def attack_enemy():
            """
            NIVEAU 3: Attaquer les ennemis
            Si un ennemi est proche, le poursuivre agressivement
            """
            if enemies:
                return braitenberg_hate_enemy()
            return None

        def genetic_algorithm():
            """
            NIVEAU 4: Algorithme Génétique (exploration intelligente)
            Perceptron tanh optimisé par GA pour explorer efficacement
            Poids pré-optimisés par sélection génétique
            """
            # Poids d'exploration GA améliorés (explorent mieux que avant)
            weights = [0.8, 1.0, 0.9, -0.8, 1.1, -0.9, 0.7, -0.6]
            
            # Entrées: les 3 capteurs avant (front, left, right)
            translation = math.tanh(
                weights[0] +
                weights[1] * sensors[sensor_front_left] +
                weights[2] * sensors[sensor_front] +
                weights[3] * sensors[sensor_front_right]
            )
            
            rotation = math.tanh(
                weights[4] +
                weights[5] * sensors[sensor_front_left] +
                weights[6] * sensors[sensor_front] +
                weights[7] * sensors[sensor_front_right]
            )
            
            return translation, rotation, False

        # ============ SUBSOMPTION HIÉRARCHIQUE (5 NIVEAUX) ============
        # Les niveaux infants ont priorité absolue (peuvent override les niveaux supérieurs)
        
        # NIVEAU 1: URGENCE - Mur trop proche (collision imminente)
        result = avoid_wall_critical()
        if result is not None:
            return result
        
        # NIVEAU 2: COORDINATION - Allié trop proche
        result = avoid_ally()
        if result is not None:
            return result
        
        # NIVEAU 3: ATTAQUE - Ennemi détecté et accessible
        result = attack_enemy()
        if result is not None:
            return result
        
        # NIVEAU 4: EXPLORATION - Algoritmo Genético
        translation, rotation, _ = genetic_algorithm()
        
        # NIVEAU 5: FALLBACK - Explorer (jamais utilisé en condition normale)
        return translation, rotation, False
        