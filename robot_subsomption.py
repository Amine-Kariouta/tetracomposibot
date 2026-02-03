from robot import * 

nb_robots = 0
debug = True

class Robot_player(Robot):

    team_name = "Subsomption"
    robot_id = -1
    iteration = 0

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        # Séparer les capteurs pour déterminer ce qu'on détecte
        sensor_to_wall = []
        sensor_to_robot = []
        for i in range(0, 8):
            if sensor_view[i] == 1:  # mur
                sensor_to_wall.append(sensors[i])
                sensor_to_robot.append(1.0)
            elif sensor_view[i] == 2:  # robot
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(sensors[i])
            else:  # rien
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)

        # ARCHITECTURE DE SUBSOMPTION: 3 niveaux de priorité
        
        # NIVEAU 1 (PRIORITÉ BASSE): Aller tout droit
        translation = 0.5 # Vitesse moyenne à la base.
        rotation = 0.0 # Tout droit.
        
        # NIVEAU 2 ( PRIORITÉ MOYENEN): Si mur proche → éviter les murs (priorité sur niveau 1)
        if sensor_to_wall[sensor_front] < 0.8 or sensor_to_wall[sensor_front_left] < 0.7 or sensor_to_wall[sensor_front_right] < 0.7:
            translation = sensor_to_wall[sensor_front] * 0.8
            rotation = (sensor_to_wall[sensor_front_left] - sensor_to_wall[sensor_front_right])
        
        # NIVEAU 3 (PRIORITÉ HAUTe): Si robot détecté → aller vers les robots (priorité sur tous)
        if sensor_to_robot[sensor_front] < 1.0 or sensor_to_robot[sensor_front_left] < 1.0 or sensor_to_robot[sensor_front_right] < 1.0:
            translation = sensor_to_robot[sensor_front] * 0.8
            rotation = -(sensor_to_robot[sensor_front_left] - sensor_to_robot[sensor_front_right])

        if debug == True:
            if self.iteration % 100 == 0:
                print("Robot", self.robot_id, " (team " + str(self.team_name) + ") at step", self.iteration, ":")
                print("\tsensors =", sensors)
                print("\ttype =", sensor_view)

        self.iteration = self.iteration + 1        
        return translation, rotation, False
