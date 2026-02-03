
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
        # score = translation_effective * (1 - |rotation_effective|)
        delta_translation = self.log_sum_of_translation - self.prev_log_translation
        delta_rotation = self.log_sum_of_rotation - self.prev_log_rotation
        if self.iteration > 0:
            self.evaluation_score += delta_translation * (1 - abs(delta_rotation))
        self.prev_log_translation = self.log_sum_of_translation
        self.prev_log_rotation = self.log_sum_of_rotation

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        # cet exemple montre comment générer au hasard, et évaluer, des stratégies comportementales
        # Remarques:
        # - la liste "param", définie ci-dessus, permet de stocker les paramètres de la fonction de contrôle
        # - la fonction de controle est une combinaison linéaire des senseurs, pondérés par les paramètres (c'est un "Perceptron")

        # mise à jour du score à chaque itération
        self._update_score()

        # toutes les X itérations: fin d'une évaluation
        if self.iteration % self.it_per_evaluation == 0:
                if self.iteration > 0:
                    print ("\teval",self.current_evaluation+1,"/",self.nb_evaluations)
                    print ("\tscore eval          =",self.evaluation_score)
                    self.total_score += self.evaluation_score
                    self.current_evaluation += 1

                    # après les 3 évaluations: décision
                    if self.current_evaluation >= self.nb_evaluations:
                        print ("\tparameters           =",self.param)
                        print ("\tscore total          =",self.total_score)
                        
                        # Sauvegarder dans le fichier
                        if self.results_file:
                            self.results_file.write(f"{self.evaluation_number},{self.total_score},{max(self.best_score, self.total_score)}\n")
                            self.results_file.flush()
                        self.evaluation_number += 1
                        
                        if self.total_score > self.best_score:
                            self.best_score = self.total_score
                            self.bestParam = self.param.copy()
                            self.best_trial = self.trial
                            print ("[NEW BEST] trial",self.best_trial,"score",self.best_score)

                        # mode recherche
                        if self.mode == "search":
                            if self.trial >= self.max_trials:
                                self.mode = "replay"
                                if len(self.bestParam) == 0:
                                    self.bestParam = self.param.copy()
                                print ("[SEARCH DONE] best score",self.best_score,"trial",self.best_trial)
                            else:
                                self.param = [random.randint(-1, 1) for i in range(8)]
                                self.trial = self.trial + 1
                                print ("Trying strategy no.",self.trial)

                        # mode rejeu (après la recherche)
                        if self.mode == "replay":
                            self.param = self.bestParam.copy()

                        # reset pour nouveau comportement
                        self.current_evaluation = 0
                        self.total_score = 0.0

                self.iteration = self.iteration + 1
                return 0, 0, True # ask for reset

        # pendant le rejeu, on reset toutes les 1000 itérations
        if self.mode == "replay" and self.iteration % self.replay_duration == 0:
            self.param = self.bestParam.copy()
            self.iteration = self.iteration + 1
            return 0, 0, True

        # fonction de contrôle (qui dépend des entrées sensorielles, et des paramètres)
        translation = math.tanh ( self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right] )
        rotation = math.tanh ( self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right] )

        if debug == True:
            if self.iteration % 100 == 0:
                print ("Robot",self.robot_id," (team "+str(self.team_name)+")","at step",self.iteration,":")
                print ("\tsensors (distance, max is 1.0)  =",sensors)
                print ("\ttype (0:empty, 1:wall, 2:robot) =",sensor_view)
                print ("\trobot's name (if relevant)      =",sensor_robot)
                print ("\trobot's team (if relevant)      =",sensor_team)

        self.iteration = self.iteration + 1        

        return translation, rotation, False