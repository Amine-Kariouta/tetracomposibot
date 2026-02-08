
from robot import * 
import math

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "RandomSearch2"
    robot_id = -1
    iteration = 0

    param = []
    bestParam = []
    it_per_evaluation = 400
    trial = 0
    max_trials = 500
    nb_evaluations = 3  # nombre d'évaluations par comportement
    current_evaluation = 0  # évaluation courante (0, 1, 2)

    best_score = -float("inf")
    best_trial = -1
    evaluation_score = 0.0  # score de l'évaluation courante
    total_score = 0.0  # score total sur les 3 évaluations
    prev_log_translation = 0.0
    prev_log_rotation = 0.0

    mode = "search"  # "search" (recherche) ou "replay" (rejeu)
    replay_duration = 1000
    
    results_file = None  # fichier pour sauvegarder les résultats
    evaluation_number = 0  # compteur d'évaluations globales

    x_0 = 0
    y_0 = 0
    theta_0 = 0 # in [0,360]

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a",evaluations=0,it_per_evaluation=0):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0
        # Parent initial aléatoire
        self.param = [random.randint(-1, 1) for i in range(8)]
        if it_per_evaluation > 0:
            self.it_per_evaluation = it_per_evaluation
        if evaluations > 0:
            self.max_trials = evaluations
        # Ouvrir fichier de résultats
        if self.robot_id == 0:
            self.results_file = open("results_randomsearch2.csv", "w")
            self.results_file.write("evaluation,score_current,score_best\n")
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def reset(self):
        # orientation aléatoire pour chaque évaluation
        self.theta0 = self.theta = random.randint(0, 359)
        super().reset()
        # remise à zéro du score pour une nouvelle évaluation
        self.evaluation_score = 0.0
        self.prev_log_translation = 0.0
        self.prev_log_rotation = 0.0

    def _update_score(self):
        # on calcule un score simple pour évaluer un comportement
        # idée: avancer vite et tourner peu donne un meilleur score
        # formule: score += translation_effective * (1 - |rotation_effective|)
        # exemples:
        # - translation=1, rotation=0 -> +1
        # - translation=1, rotation=1 -> +0
        # - translation=0, rotation=0 -> +0
        # on utilise les mesures effectives pour éviter les faux gains
        # log_sum_of_translation / log_sum_of_rotation sont des compteurs cumulés
        # on prend la différence depuis la dernière itération
        # delta_translation = distance réellement parcourue depuis la dernière fois
        delta_translation = self.log_sum_of_translation - self.prev_log_translation
        # delta_rotation = rotation réellement effectuée depuis la dernière fois
        delta_rotation = self.log_sum_of_rotation - self.prev_log_rotation
        if self.iteration > 0:
            # on ajoute la contribution de cette itération au score total
            self.evaluation_score += delta_translation * (1 - abs(delta_rotation))
        # on mémorise les valeurs actuelles pour l'itération suivante
        self.prev_log_translation = self.log_sum_of_translation
        self.prev_log_rotation = self.log_sum_of_rotation

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # fonction principale appelée à chaque itération
        # même principe que randomsearch, mais chaque comportement est évalué 3 fois
        # le score final d'un comportement = somme des 3 évaluations
        # on garde les mêmes règles mais on réduit le hasard lié au point de départ

        # chaque appel correspond à un pas de temps du simulateur
        # on met à jour le score avant de décider s'il faut changer de comportement

        # mise à jour du score à chaque itération
        self._update_score()

        # toutes les X itérations: fin d'une évaluation
        if self.iteration % self.it_per_evaluation == 0:
            if self.iteration > 0:
            # on affiche l'évaluation en cours
                print ("\teval",self.current_evaluation+1,"/",self.nb_evaluations)
                print ("\tscore eval          =",self.evaluation_score)
                self.total_score += self.evaluation_score
                self.current_evaluation += 1

                # après les 3 évaluations: décision
                if self.current_evaluation >= self.nb_evaluations:
                    print ("\tparameters           =",self.param)
                    print ("\tscore total          =",self.total_score)
                    
                    # enregistrer les résultats pour les graphes
                    if self.results_file:
                        self.results_file.write(f"{self.evaluation_number},{self.total_score},{max(self.best_score, self.total_score)}\n")
                        self.results_file.flush()
                    self.evaluation_number += 1
                    
                    # si ce comportement est le meilleur, on le sauvegarde
                    if self.total_score > self.best_score:
                        self.best_score = self.total_score
                        self.bestParam = self.param.copy()
                        self.best_trial = self.trial
                        print ("[NOUVEAU MEILLEUR] essai",self.best_trial,"score",self.best_score)

                    # phase recherche
                    if self.mode == "search":
                        if self.trial >= self.max_trials:
                            # budget épuisé: on passe en rejeu
                            self.mode = "replay"
                            if len(self.bestParam) == 0:
                                self.bestParam = self.param.copy()
                            print ("[RECHERCHE FINIE] meilleur score",self.best_score,"essai",self.best_trial)
                        else:
                            # nouveau comportement aléatoire
                            # (8 poids tirés dans {-1, 0, 1})
                            self.param = [random.randint(-1, 1) for i in range(8)]
                            self.trial = self.trial + 1
                            print ("Test de la stratégie n°",self.trial)

                    # phase rejeu
                    if self.mode == "replay":
                        # on réutilise le meilleur comportement trouvé
                        self.param = self.bestParam.copy()

                    # reset pour nouveau comportement
                    self.current_evaluation = 0
                    self.total_score = 0.0

            self.iteration = self.iteration + 1
            # demander au simulateur de remettre le robot à sa position initiale
            return 0, 0, True # ask for reset

        # pendant le rejeu, on reset toutes les 1000 itérations
        if self.mode == "replay" and self.iteration % self.replay_duration == 0:
            # on rejoue le meilleur comportement depuis le début
            self.param = self.bestParam.copy()
            self.iteration = self.iteration + 1
            return 0, 0, True

        # perceptron simple pour calculer translation et rotation
        # 3 capteurs avant + 8 poids, puis tanh
        # on garde la même structure que dans l'algorithme génétique
        translation = math.tanh ( self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right] )
        rotation = math.tanh ( self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right] )

        if debug == True:
            if self.iteration % 100 == 0:
                print ("Robot",self.robot_id," (équipe "+str(self.team_name)+")","à l'itération",self.iteration,":")
                print ("\tsensors (distance, max is 1.0)  =",sensors)
                print ("\ttype (0:vide, 1:mur, 2:robot) =",sensor_view)
                print ("\trobot's name (if relevant)      =",sensor_robot)
                print ("\trobot's team (if relevant)      =",sensor_team)

        self.iteration = self.iteration + 1        

        return translation, rotation, False