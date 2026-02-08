import csv
import os
import sys
import subprocess
import shutil
import matplotlib.pyplot as plt

# Exercice 4 - Visualisation et comparaison des résultats
# 
# OBJECTIF: Comparer 2 algorithmes (Recherche aléatoire vs Algorithme génétique)
# de manière statistiquement valide avec 10 essais indépendants chacun
#
# UTILISATION:
# 1) Lancer ce script avec AUTO_LANCER_10_ESSAIS = True pour générer les 10 essais:
#      python tracer_resultats.py
# 2) Les données seront sauvegardées dans:
#    - results_randomsearch2_01.csv ... _10.csv
#    - results_genetic_01.csv ... _10.csv
# 3) Les graphes seront créés automatiquement:
#    - randomsearch2_moyenne.png (moyenne recherche aléatoire)
#    - genetic_moyenne.png (moyenne algorithme génétique)
#    - comparaison_moyennes.png (comparaison des deux moyennes)
#
# N.B. : Le lancement de 10 essais complets est long; mais assure la comparaison équitable.

# mettre True pour lancer automatiquement les 10 essais des deux algorithmes
AUTO_LANCER_10_ESSAIS = True


def charger_csv(nom_fichier):
    # lit un fichier CSV produit par randomsearch2 ou genetic_algorithms
    # chaque ligne contient:
    # evaluation, score_current, score_best
    # ici on récupère seulement evaluation et score_best
    evaluations = []
    scores_best = []

    if not os.path.exists(nom_fichier):
        # si le fichier n'existe pas, on affiche un message et on renvoie des listes vides
        print(f"Fichier introuvable: {nom_fichier}")
        return evaluations, scores_best

    # ouvrir le fichier en lecture
    with open(nom_fichier, "r") as f:
        # DictReader lit chaque ligne sous forme de dictionnaire
        # ex: row["evaluation"], row["score_best"]
        lecteur = csv.DictReader(f)
        for row in lecteur:
            # convertir en int/float pour pouvoir tracer
            evaluations.append(int(row["evaluation"]))
            scores_best.append(float(row["score_best"]))

    # on renvoie les deux listes prêtes pour le graphe
    return evaluations, scores_best


def tracer_simple(nom_fichier, titre):
    # trace un graphe simple pour un seul fichier CSV
    # X = numéro d'évaluation
    # Y = meilleur score trouvé jusqu'ici
    # charger les données du fichier
    evals, scores = charger_csv(nom_fichier)
    if not evals:
        # pas de données -> pas de graphe
        return

    # création de la figure
    # on crée une nouvelle figure
    plt.figure(figsize=(12, 6))
    # tracer la courbe du meilleur score
    plt.plot(evals, scores, linewidth=2)
    # axes et titre
    # texte des axes et titre
    plt.xlabel("Numéro d'évaluation")
    plt.ylabel("Meilleur score")
    plt.title(titre)
    # grille pour mieux lire le graphe
    plt.grid(True)

    # nom de sortie (même nom que le CSV mais en .png)
    nom_sortie = nom_fichier.replace(".csv", ".png")
    # sauvegarder l'image sur disque
    plt.savefig(nom_sortie)
    # afficher la fenêtre du graphe
    # afficher la fenêtre du graphe
    plt.show()

    print(f"Graphe sauvegardé: {nom_sortie}")


def tracer_comparaison():
    # compare la recherche aléatoire et l'algorithme génétique
    # sur un même graphe pour voir qui progresse le mieux
    # charger les deux fichiers
    evals_rs, scores_rs = charger_csv("results_randomsearch2.csv")
    evals_ga, scores_ga = charger_csv("results_genetic.csv")

    if not evals_rs and not evals_ga:
        # aucun fichier trouvé -> on arrête ici
        print("Aucun fichier de résultats trouvé")
        return

    # création de la figure
    # nouvelle figure pour la comparaison
    plt.figure(figsize=(12, 6))

    if evals_rs:
        # courbe de la recherche aléatoire
        plt.plot(evals_rs, scores_rs, linewidth=2, label="Recherche aléatoire")
    if evals_ga:
        # courbe de l'algorithme génétique
        plt.plot(evals_ga, scores_ga, linewidth=2, label="Algorithme génétique")

    # axes, titre et légende
    # texte des axes et titre
    plt.xlabel("Numéro d'évaluation")
    plt.ylabel("Meilleur score")
    plt.title("Comparaison: Recherche aléatoire vs Algorithme génétique")
    # grille et légende
    plt.grid(True)
    plt.legend()

    # sauvegarde du graphe
    plt.savefig("comparaison_algos.png")
    # affichage du graphe
    plt.show()

    print("Graphe sauvegardé: comparaison_algos.png")


def lancer_essais_randomsearch2(nb_essais=10):
    # Lance 10 essais indépendants de recherche aléatoire
    # (consigne TP: moyenne sur 10 essais pour être statistiquement valide)
    # Génère: results_randomsearch2_01.csv ... _10.csv
    for i in range(1, nb_essais + 1):
        nom_sortie = f"results_randomsearch2_{i:02d}.csv"

        # si un fichier existe déjà, on le supprime pour éviter la confusion
        if os.path.exists(nom_sortie):
            os.remove(nom_sortie)

        # on supprime l'ancien CSV courant s'il existe
        if os.path.exists("results_randomsearch2.csv"):
            os.remove("results_randomsearch2.csv")

        # lancer un essai
        # lancer le simulateur pour un essai complet
        subprocess.run(
            [sys.executable, "tetracomposibot.py", "config_TP2_ex2.py"],
            check=False,
        )

        # renommer le fichier généré
        if os.path.exists("results_randomsearch2.csv"):
            os.rename("results_randomsearch2.csv", nom_sortie)
            # garder aussi une copie simple pour le graphe individuel
            if i == nb_essais:
                shutil.copyfile(nom_sortie, "results_randomsearch2.csv")
        else:
            print(f"CSV manquant pour l'essai {i}")


def lancer_essais_genetic(nb_essais=10):
    # Lance 10 essais indépendants d'algorithme génétique
    # (consigne TP: moyenne sur 10 essais pour comparaison valide)
    # Génère: results_genetic_01.csv ... _10.csv
    for i in range(1, nb_essais + 1):
        nom_sortie = f"results_genetic_{i:02d}.csv"

        # si un fichier existe déjà, on le supprime pour éviter la confusion
        if os.path.exists(nom_sortie):
            os.remove(nom_sortie)

        # on supprime l'ancien CSV courant s'il existe
        if os.path.exists("results_genetic.csv"):
            os.remove("results_genetic.csv")

        # lancer un essai
        # lancer le simulateur pour un essai complet avec genetic algorithm
        subprocess.run(
            [sys.executable, "tetracomposibot.py", "config_TP2_ex3.py"],
            check=False,
        )

        # renommer le fichier généré
        if os.path.exists("results_genetic.csv"):
            os.rename("results_genetic.csv", nom_sortie)
            # garder aussi une copie simple pour le graphe individuel
            if i == nb_essais:
                shutil.copyfile(nom_sortie, "results_genetic.csv")
        else:
            print(f"CSV manquant pour l'essai {i}")


def tracer_moyenne_randomsearch(nb_essais=10):
    # calcule la moyenne des meilleurs scores sur plusieurs essais
    # on suppose des fichiers: results_randomsearch2_01.csv ... _10.csv
    toutes_les_courbes = []
    evaluations_ref = None

    for i in range(1, nb_essais + 1):
        nom = f"results_randomsearch2_{i:02d}.csv"
        evals, scores = charger_csv(nom)
        if not evals:
            continue
        if evaluations_ref is None:
            evaluations_ref = evals
        # on stocke la courbe (liste de scores)
        toutes_les_courbes.append(scores)

    if not toutes_les_courbes:
        print("Aucun fichier pour la moyenne des 10 essais")
        return

    # moyenne point par point (même longueur supposée)
    # on prend la longueur minimale pour éviter les erreurs
    longueur = min(len(c) for c in toutes_les_courbes)
    moyenne = []
    for idx in range(longueur):
        # moyenne point par point
        moyenne.append(sum(c[idx] for c in toutes_les_courbes) / len(toutes_les_courbes))

    # graphe de la moyenne
    # nouvelle figure pour la moyenne
    plt.figure(figsize=(12, 6))
    plt.plot(evaluations_ref[:longueur], moyenne, linewidth=2, label="Moyenne (10 essais)")
    # texte des axes et titre
    plt.xlabel("Numéro d'évaluation")
    plt.ylabel("Meilleur score moyen")
    plt.title("Recherche aléatoire - moyenne sur 10 essais")
    # grille et légende
    plt.grid(True)
    plt.legend()

    # sauvegarde et affichage
    plt.savefig("randomsearch2_moyenne.png")
    plt.show()

    print("Graphe sauvegardé: randomsearch2_moyenne.png")


def tracer_moyenne_genetic(nb_essais=10):
    # calcule la moyenne des meilleurs scores sur plusieurs essais du GA
    # on suppose des fichiers: results_genetic_01.csv ... _10.csv
    toutes_les_courbes = []
    evaluations_ref = None

    for i in range(1, nb_essais + 1):
        nom = f"results_genetic_{i:02d}.csv"
        evals, scores = charger_csv(nom)
        if not evals:
            continue
        if evaluations_ref is None:
            evaluations_ref = evals
        # on stocke la courbe (liste de scores)
        toutes_les_courbes.append(scores)

    if not toutes_les_courbes:
        print("Aucun fichier pour la moyenne des 10 essais du GA")
        return

    # moyenne point par point
    # on prend la longueur minimale pour éviter les erreurs
    longueur = min(len(c) for c in toutes_les_courbes)
    moyenne = []
    for idx in range(longueur):
        # moyenne point par point
        moyenne.append(sum(c[idx] for c in toutes_les_courbes) / len(toutes_les_courbes))

    # graphe de la moyenne
    # nouvelle figure pour la moyenne du GA
    plt.figure(figsize=(12, 6))
    plt.plot(evaluations_ref[:longueur], moyenne, linewidth=2, label="Moyenne (10 essais)")
    # texte des axes et titre
    plt.xlabel("Numéro d'évaluation")
    plt.ylabel("Meilleur score moyen")
    plt.title("Algorithme génétique - moyenne sur 10 essais")
    # grille et légende
    plt.grid(True)
    plt.legend()

    # sauvegarde et affichage
    plt.savefig("genetic_moyenne.png")
    plt.show()

    print("Graphe sauvegardé: genetic_moyenne.png")


def tracer_comparaison_moyennes():
    # compare les moyennes sur 10 essais des deux algorithmes
    # charger les moyennes calculées
    evals_rs = []
    scores_rs = []
    evals_ga = []
    scores_ga = []
    
    # collecte randomsearch2
    for i in range(1, 11):
        nom = f"results_randomsearch2_{i:02d}.csv"
        evals, scores = charger_csv(nom)
        if evals:
            evals_rs = evals
            if len(scores_rs) == 0:
                scores_rs = [0] * len(scores)
            for j in range(len(scores)):
                if j < len(scores_rs):
                    scores_rs[j] += scores[j]
    
    if scores_rs:
        scores_rs = [s / 10 for s in scores_rs]
    
    # collecte genetic
    for i in range(1, 11):
        nom = f"results_genetic_{i:02d}.csv"
        evals, scores = charger_csv(nom)
        if evals:
            evals_ga = evals
            if len(scores_ga) == 0:
                scores_ga = [0] * len(scores)
            for j in range(len(scores)):
                if j < len(scores_ga):
                    scores_ga[j] += scores[j]
    
    if scores_ga:
        scores_ga = [s / 10 for s in scores_ga]
    
    if not (scores_rs or scores_ga):
        print("Aucun fichier pour la comparaison des moyennes")
        return
    
    # créer le graphe comparatif
    plt.figure(figsize=(12, 6))
    
    if scores_rs and evals_rs:
        plt.plot(evals_rs, scores_rs, linewidth=2, label="Recherche aléatoire (moyenne 10 essais)")
    
    if scores_ga and evals_ga:
        plt.plot(evals_ga, scores_ga, linewidth=2, label="Algorithme génétique (moyenne 10 essais)")
    
    # axes, titre et légende
    plt.xlabel("Numéro d'évaluation")
    plt.ylabel("Meilleur score moyen")
    plt.title("Comparaison: Moyennes sur 10 essais")
    plt.grid(True)
    plt.legend()
    
    # sauvegarde et affichage
    plt.savefig("comparaison_moyennes.png")
    plt.show()
    
    print("Graphe sauvegardé: comparaison_moyennes.png")


def main():
    # génération automatique des 10 essais si activé
    if AUTO_LANCER_10_ESSAIS:
        # lancer 10 essais de recherche aléatoire
        print("\n=== Lancement de 10 essais: Recherche aléatoire ===")
        lancer_essais_randomsearch2(nb_essais=10)
        
        # lancer 10 essais d'algorithme génétique
        print("\n=== Lancement de 10 essais: Algorithme génétique ===")
        lancer_essais_genetic(nb_essais=10)

    # graphe pour la recherche aléatoire (exercice 2) - un seul essai
    tracer_simple(
        "results_randomsearch2.csv",
        "Évolution du meilleur score - Recherche aléatoire (dernier essai)",
    )

    # graphe pour l'algorithme génétique (exercice 3) - un seul essai
    if os.path.exists("results_genetic.csv"):
        tracer_simple(
            "results_genetic.csv",
            "Évolution du meilleur score - Algorithme génétique (dernier essai)",
        )

    # comparaison simple sur un seul graphe (derniers essais)
    tracer_comparaison()

    # MOYENNES SUR 10 ESSAIS (consigne TP)
    # moyenne recherche aléatoire
    print("\n=== Calcul de la moyenne: Recherche aléatoire (10 essais) ===")
    tracer_moyenne_randomsearch(nb_essais=10)
    
    # moyenne algorithme génétique
    print("\n=== Calcul de la moyenne: Algorithme génétique (10 essais) ===")
    tracer_moyenne_genetic(nb_essais=10)
    
    # comparaison des moyennes
    print("\n=== Comparaison des moyennes ===")
    tracer_comparaison_moyennes()


if __name__ == "__main__":
    # point d'entrée du script
    main()
