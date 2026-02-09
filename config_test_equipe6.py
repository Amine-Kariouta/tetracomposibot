# Configuration TEST - Équipe 6 seulement (sans adversaires)

import arenas

# Paramètres de base
display_mode = 1
arena = 0  # Commencer par l'arène la plus facile
position = False 
max_iterations = 2001

# Affichage
display_welcome_message = False
verbose_minimal_progress = True  # Afficher progression
display_robot_stats = False
display_team_stats = False
display_tournament_results = True
display_time_stats = False

# Import de notre équipe optimisée
import equipe6_challenger

def initialize_robots(arena_size=-1, particle_box=-1):
    global position
    x_init_pos = []
    if position == False:
        x_init_pos = [4, 93]
        orientation_challenger = 180
    else:
        x_init_pos = [93, 4]
        orientation_challenger = 0
    
    robots = []
    
    # 4 robots ÉQUIPE 6 - Stratégies complémentaires optimisées
    robots.append(equipe6_challenger.Robot_player(x_init_pos[0], arena_size//2-24, orientation_challenger, name="subsomption", team="A"))
    robots.append(equipe6_challenger.Robot_player(x_init_pos[0], arena_size//2-8, orientation_challenger, name="braitenberg_hateenemy", team="A"))
    robots.append(equipe6_challenger.Robot_player(x_init_pos[0], arena_size//2+8, orientation_challenger, name="braitenberg_lovewall", team="A"))
    robots.append(equipe6_challenger.Robot_player(x_init_pos[0], arena_size//2+24, orientation_challenger, name="algorithme_genetique", team="A"))
    
    # ADVERSAIRE SIMPLE - Équipe de robots dumb pour tester
    import robot_dumb
    for i in range(4):
        robots.append(robot_dumb.Robot_player(x_init_pos[1], arena_size//2-16+i*8, 0, name="dumb_"+str(i), team="B"))
    
    return robots
