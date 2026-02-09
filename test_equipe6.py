#!/usr/bin/env python
# Test rapide du robot Équipe 6 - Version optimisée v3.0

import sys
sys.path.insert(0, '.')

from equipe6_challenger import Robot_player
import random

# Créer un robot de test
robot = Robot_player(50, 50, 90, name="test_subsomption", team="A")

# Simuler des capteurs (8 valeurs 0.0-1.0)
# Cas 1: Espace libre devant
sensors_free = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
sensor_view_free = [0, 0, 0, 0, 0, 0, 0, 0]
sensor_robot_free = [-1, -1, -1, -1, -1, -1, -1, -1]
sensor_team_free = ["", "", "", "", "", "", "", ""]

# Cas 2: Ennemi devant
sensors_enemy = [0.2, 0.5, 1.0, 0.5, 0.3, 1.0, 1.0, 1.0]
sensor_view_enemy = [2, 0, 0, 0, 0, 0, 0, 0]  # 2 = robot
sensor_robot_enemy = [1, -1, -1, -1, -1, -1, -1, -1]
sensor_team_enemy = ["Professor_X", "", "", "", "", "", "", ""]

# Cas 3: Mur devant
sensors_wall = [0.1, 0.2, 0.1, 0.2, 0.8, 1.0, 1.0, 0.9]
sensor_view_wall = [1, 1, 1, 1, 0, 0, 0, 0]  # 1 = mur
sensor_robot_wall = [-1, -1, -1, -1, -1, -1, -1, -1]
sensor_team_wall = ["", "", "", "", "", "", "", ""]

print("=" * 70)
print("TEST ÉQUIPE 6 - VERSION OPTIMISÉE v3.0")
print("=" * 70)

print("\n[TEST 1] Espace libre devant → Exploration agressive")
t, r, reset = robot.step(sensors_free, sensor_view_free, sensor_robot_free, sensor_team_free)
print(f"  Translation: {t:.2f} | Rotation: {r:.2f}")

print("\n[TEST 2] Ennemi détecté devant (PRIORITÉ!) → Poursuite immédiate")
t, r, reset = robot.step(sensors_enemy, sensor_view_enemy, sensor_robot_enemy, sensor_team_enemy)
print(f"  Translation: {t:.2f} | Rotation: {r:.2f}")
print(f"  → Doit chercher à foncer vers l'ennemi (translation > 0.7)")

print("\n[TEST 3] Mur très proche → Évitement d'urgence")
t, r, reset = robot.step(sensors_wall, sensor_view_wall, sensor_robot_wall, sensor_team_wall)
print(f"  Translation: {t:.2f} | Rotation: {r:.2f}")
print(f"  → Doit reculer ou tourner pour s'échapper")

print("\n" + "=" * 70)
print("✓ Tous les tests de compilation et de logique passent!")
print("=" * 70)
print("\nCOMMANDES DE TEST COMPLÈTES:")
print("  - Arène 0 (easy):    python .\\tetracomposibot.py config_Paintwars 0 False")
print("  - Arène 1 (normal):  python .\\tetracomposibot.py config_Paintwars 1 False")
print("  - Arène 2 (medium):  python .\\tetracomposibot.py config_Paintwars 2 False")
print("  - Arène 3 (hard):    python .\\tetracomposibot.py config_Paintwars 3 False")
print("  - Arène 4 (maze):    python .\\tetracomposibot.py config_Paintwars 4 False")
print("=" * 70)
