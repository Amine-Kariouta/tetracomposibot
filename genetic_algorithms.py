
from robot import * 
import math

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "GeneticAlgorithm"
    robot_id = -1
    iteration = 0

    param = []  # enfant courant
    parent_param = []  # parent
    bestParam = []
    it_per_evaluation = 400
    trial = 0
    max_trials = 500
    # Paramètres GA (projet): (μ + λ)
    # - μ = nombre de parents conservés
    # - λ = nombre d'enfants évalués avant sélection
    mu = 5  # nombre de parents
    lambda_ = 20  # nombre d'enfants par génération
    nb_evaluations = 3  # nombre d'évaluations par comportement
    current_evaluation = 0  # évaluation courante (0, 1, 2)

    best_score = -float("inf")
    best_trial = -1
    parent_score = -float("inf")  # score du parent
    evaluation_score = 0.0  # score de l'évaluation courante
    total_score = 0.0  # score total sur les 3 évaluations
    prev_log_translation = 0.0
    prev_log_rotation = 0.0

    mode = "search"  # "search" (recherche) ou "replay" (rejeu)
    replay_duration = 1000

    # Populations et états du GA
    parents = []
    parent_scores = []
    children = []
    children_scores = []
    # phase = "init_parents": on évalue les μ parents initiaux
    # phase = "children": on génère/évalue les λ enfants
    phase = "init_parents"  # "init_parents" puis "children"
    current_parent_init = 0
    generation = 0
    
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
        # Initialiser une population de μ parents (paramètres aléatoires)
        self.parents = [[random.randint(-1, 1) for i in range(8)] for _ in range(self.mu)]
        self.parent_scores = [-float("inf")] * self.mu
        self.children = []
        self.children_scores = []
        self.current_parent_init = 0
        self.phase = "init_parents"
        self.generation = 0
        # Premier individu à évaluer
        self.param = self.parents[0].copy()
        self.parent_param = self.param.copy()
        if it_per_evaluation > 0:
            self.it_per_evaluation = it_per_evaluation
        if evaluations > 0:
            self.max_trials = evaluations
        # Ouvrir fichier de résultats
        if self.robot_id == 0:
            self.results_file = open("results_genetic.csv", "w")
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

    def _mutate(self, parent):
        # Mutation : change 1 seul paramètre aléatoirement (sans retirage)
        child = parent.copy()
        idx = random.randint(0, len(child) - 1)
        old_value = child[idx]
        # Nouvelles valeurs possibles (sans l'ancienne)
        possible_values = [-1, 0, 1]
        possible_values.remove(old_value)
        child[idx] = random.choice(possible_values)
        return child

    def _update_score(self):
        """
        Accumule le score du comportement à chaque itération.
        
        On préfère que le robot avance tout droit (translation max, rotation min) car :
        - plus le robot se déplace, plus il couvre de terrain (utile pour Paint Wars)
        - si le robot tourne trop, il perd du temps à changer de direction au lieu d'avancer
        - idéalement : avancer sans tourner = meilleure couverture de l'arène
        
        Formule: score += translation_effective * (1 - |rotation_effective|)
        - translation=1, rotation=0 → score += 1 * (1 - 0) = 1
        - translation=1, rotation=1 → score += 1 * (1 - 1) = 0
        - translation=0, rotation=0 → score += 0 (immobile, moins utile)
        
        Note: log_sum_of_translation et log_sum_of_rotation sont fournies par le simulateur
        (voir robot.py, classe Robot). Ce sont des accumulateurs qui enregistrent la vraie
        distance/rotation du robot, même s'il se cogne contre un mur (ce qui invalide la commande).
        C'est pour ça qu'on les utilise plutôt que les commandes brutes.
        """
        
        # Calcule la translation effective depuis la dernière itération
        # (la vraie distance parcourue, pas juste la commande moteur)
        delta_translation = self.log_sum_of_translation - self.prev_log_translation
        
        # Calcule la rotation effective depuis la dernière itération
        delta_rotation = self.log_sum_of_rotation - self.prev_log_rotation
        
        # À partir de la 2e itération, on accumule le score
        # (on ignore iteration 0 pour éviter les erreurs de calcul au reset)
        if self.iteration > 0:
            # Récompense la translation, pénalise la rotation
            self.evaluation_score += delta_translation * (1 - abs(delta_rotation))
        
        # Mémoriser les sommes actuelles pour la prochaine itération
        self.prev_log_translation = self.log_sum_of_translation
        self.prev_log_rotation = self.log_sum_of_rotation

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        """
        Fonction principale appelée à chaque itération par le simulateur.
        
        Entrées:
        - sensors: liste de 8 distances (0.0 à 1.0) pour 8 capteurs autour du robot
        - sensor_view: type d'obstacle (0:vide, 1:mur, 2:robot)
        - sensor_robot: numéro du robot détecté (si type 2, c'est-à-dire robot)
        - sensor_team: équipe du robot détecté (si type 2)
        
        Retour: (translation, rotation, ask_for_reset)
        - translation: vitesse linéaire (-1 à +1)
        - rotation: vitesse angulaire (-1 à +1)
        - ask_for_reset: True si on veut réinitialiser la position (après 400 itérations)
        """

        # --------- RÉSUMÉ DU DÉROULÉ GA (μ + λ) ---------
        # 1) Phase init_parents:
        #    - On évalue les μ parents initiaux (chaque parent = 3 évaluations).
        #    - On mémorise leur score dans parent_scores.
        # 2) Phase children:
        #    - On génère des enfants par mutation d'un parent tiré au hasard.
        #    - Chaque enfant est évalué (3 évaluations) puis stocké.
        # 3) Sélection (μ + λ):
        #    - Dès qu'on a λ enfants, on mélange parents + enfants,
        #      puis on garde les μ meilleurs individus.
        # 4) Répéter jusqu'à max_trials, puis passer en mode "replay".
        # -----------------------------------------------
        
        # À chaque itération, on accumule le score du comportement actuel
        self._update_score()

        # Tous les 400 itérations: fin d'une évaluation (on test 3 fois)
        if self.iteration % self.it_per_evaluation == 0:
                if self.iteration > 0:
                    # afficher le score de cette évaluation
                    print ("\teval",self.current_evaluation+1,"/",self.nb_evaluations)
                    print ("\tscore eval          =",self.evaluation_score)
                    # ajouter au score total
                    self.total_score += self.evaluation_score
                    # passer à l'évaluation suivante
                    self.current_evaluation += 1

                    # Après les 3 évaluations: fin d'un comportement
                    if self.current_evaluation >= self.nb_evaluations:
                        # Ici, total_score = performance moyenne du comportement
                        # (somme des 3 évaluations)
                        print ("\tparamètres enfant    =",self.param)
                        print ("\tscore total enfant   =",self.total_score)
                        
                        if self.phase == "init_parents":
                            # Phase 1: on évalue les μ parents initiaux
                            # enregistrement du score du parent courant
                            self.parent_scores[self.current_parent_init] = self.total_score

                            # meilleur global
                            if self.total_score >= self.best_score:
                                self.best_score = self.total_score
                                self.bestParam = self.param.copy()
                                self.best_trial = self.trial
                                print ("[NOUVEAU MEILLEUR] stratégie",self.best_trial,"score",self.best_score)

                            # sauvegarder les résultats
                            if self.results_file:
                                best_parent_score = max(self.parent_scores[: self.current_parent_init + 1])
                                self.results_file.write(f"{self.evaluation_number},{best_parent_score},{self.best_score}\n")
                                self.results_file.flush()
                            self.evaluation_number += 1

                            # passer au parent suivant
                            # passer au parent suivant
                            self.current_parent_init += 1
                            if self.current_parent_init < self.mu:
                                # encore des parents à évaluer
                                self.param = self.parents[self.current_parent_init].copy()
                                self.parent_param = self.param.copy()
                            else:
                                # fin d'initialisation -> début de la génération d'enfants
                                self.phase = "children"
                                # sélectionner un parent au hasard puis muter
                                parent_idx = random.randint(0, self.mu - 1)
                                self.parent_param = self.parents[parent_idx].copy()
                                self.parent_score = self.parent_scores[parent_idx]
                                # créer un enfant par mutation
                                self.param = self._mutate(self.parent_param)
                                print ("Test de la stratégie n°",self.trial + 1)

                        elif self.phase == "children":
                            # Phase 2: on évalue les enfants (λ enfants par génération)
                            # stocker l'enfant évalué
                            self.children.append(self.param.copy())
                            self.children_scores.append(self.total_score)

                            # meilleur global
                            if self.total_score >= self.best_score:
                                self.best_score = self.total_score
                                self.bestParam = self.param.copy()
                                self.best_trial = self.trial
                                print ("[NOUVEAU MEILLEUR] stratégie",self.best_trial,"score",self.best_score)

                            # sauvegarder les résultats
                            if self.results_file:
                                best_parent_score = max(self.parent_scores)
                                self.results_file.write(f"{self.evaluation_number},{best_parent_score},{self.best_score}\n")
                                self.results_file.flush()
                            self.evaluation_number += 1

                            # compteur de comportements testés
                            # incrémente le nombre total de comportements testés
                            self.trial = self.trial + 1

                            # arrêt après max_trials
                            if self.trial >= self.max_trials:
                                self.mode = "replay"
                                if len(self.bestParam) == 0:
                                    self.bestParam = self.parents[0].copy()
                                print ("[RECHERCHE FINIE] meilleur score",self.best_score,"stratégie",self.best_trial)
                            else:
                                # Sélection (μ + λ) quand on a assez d'enfants
                                # On garde les μ meilleurs individus parmi parents + enfants
                                if len(self.children_scores) >= self.lambda_:
                                    # fusionner parents et enfants
                                    combined_params = self.parents + self.children
                                    combined_scores = self.parent_scores + self.children_scores
                                    # trier par score décroissant
                                    selection = sorted(
                                        zip(combined_scores, combined_params),
                                        key=lambda x: x[0],
                                        reverse=True,
                                    )[: self.mu]
                                    # garder les μ meilleurs
                                    self.parents = [p for s, p in selection]
                                    self.parent_scores = [s for s, p in selection]
                                    # vider la liste d'enfants pour la prochaine génération
                                    self.children = []
                                    self.children_scores = []
                                    # incrémenter le compteur de générations
                                    self.generation += 1

                                # préparer un nouvel enfant
                                if self.mode == "search":
                                    # choisir un parent au hasard (parmi les μ)
                                    parent_idx = random.randint(0, self.mu - 1)
                                    self.parent_param = self.parents[parent_idx].copy()
                                    self.parent_score = self.parent_scores[parent_idx]
                                    # muter ce parent pour créer un enfant
                                    self.param = self._mutate(self.parent_param)
                                    print ("Test de la stratégie n°",self.trial + 1)

                        # mode rejeu: rejouer le meilleur comportement indéfiniment
                        if self.mode == "replay":
                            self.param = self.bestParam.copy()

                        # réinitialiser pour la prochaine évaluation
                        self.current_evaluation = 0
                        self.total_score = 0.0

                self.iteration = self.iteration + 1
                # demander un reset au simulateur (remettre le robot à sa position initiale)
                return 0, 0, True

        # pendant le rejeu: toutes les 1000 itérations, remettre le robot à zéro
        # (pour tester le meilleur comportement indéfiniment)
        if self.mode == "replay" and self.iteration % self.replay_duration == 0:
            self.param = self.bestParam.copy()
            self.iteration = self.iteration + 1
            return 0, 0, True

        # Perceptron: combine les 3 capteurs avant avec les poids pour calculer translation/rotation
        # param = [poids_biais, poids_gauche, poids_centre, poids_droite, ...]
        # exemple: capteurs=[0.3, 0.8, 0.5], param[0-3]=[0, -1, 1, 0]
        # translation = tanh(0 + (-1)*0.3 + 1*0.8 + 0*0.5) = tanh(0.5) = 0.46
        
        # translation: combine les 3 capteurs avec les poids param[0-3]
        translation = math.tanh ( self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right] )
        
        # rotation: combine les 3 capteurs avec les poids param[4-7] en utilisant la même logique
        rotation = math.tanh ( self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right] )

        if debug == True:
            if self.iteration % 100 == 0:
                print ("Robot",self.robot_id," (team "+str(self.team_name)+")","at step",self.iteration,":")
                print ("\tsensors (distance, max is 1.0)  =",sensors)
                # sensor_view contient le type: 0=vide, 1=mur, 2=robot
                print ("\ttype (0:empty, 1:wall, 2:robot) =",sensor_view)
                print ("\trobot's name (if relevant)      =",sensor_robot)
                print ("\trobot's team (if relevant)      =",sensor_team)

        self.iteration = self.iteration + 1        

        return translation, rotation, False