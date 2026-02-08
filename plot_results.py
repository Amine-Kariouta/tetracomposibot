import csv
import os
import matplotlib.pyplot as plt


def charger_csv(nom_fichier):
    # lit un fichier CSV et récupère evaluation + score_best
    evaluations = []
    scores_best = []

    if not os.path.exists(nom_fichier):
        print(f"Fichier introuvable: {nom_fichier}")
        return evaluations, scores_best

    with open(nom_fichier, "r") as f:
        lecteur = csv.DictReader(f)
        for row in lecteur:
            evaluations.append(int(row["evaluation"]))
            scores_best.append(float(row["score_best"]))

    return evaluations, scores_best


def tracer_simple(nom_fichier, titre):
    # trace un graphe simple pour un seul fichier
    evals, scores = charger_csv(nom_fichier)
    if not evals:
        return

    plt.figure(figsize=(12, 6))
    plt.plot(evals, scores, linewidth=2)
    plt.xlabel("Numéro d'évaluation")
    plt.ylabel("Meilleur score")
    plt.title(titre)
    plt.grid(True)

    nom_sortie = nom_fichier.replace(".csv", ".png")
    plt.savefig(nom_sortie)
    plt.show()

    print(f"Graphe sauvegardé: {nom_sortie}")


def tracer_comparaison():
    # compare la recherche aléatoire et l'algorithme génétique
    evals_rs, scores_rs = charger_csv("results_randomsearch2.csv")
    evals_ga, scores_ga = charger_csv("results_genetic.csv")

    if not evals_rs and not evals_ga:
        print("Aucun fichier de résultats trouvé")
        return

    plt.figure(figsize=(12, 6))

    if evals_rs:
        plt.plot(evals_rs, scores_rs, linewidth=2, label="Recherche aléatoire")
    if evals_ga:
        plt.plot(evals_ga, scores_ga, linewidth=2, label="Algorithme génétique")

    plt.xlabel("Numéro d'évaluation")
    plt.ylabel("Meilleur score")
    plt.title("Comparaison: Recherche aléatoire vs Algorithme génétique")
    plt.grid(True)
    plt.legend()

    plt.savefig("comparaison_algos.png")
    plt.show()

    print("Graphe sauvegardé: comparaison_algos.png")


def main():
    # graphe pour la recherche aléatoire (exercice 2)
    tracer_simple(
        "results_randomsearch2.csv",
        "Évolution du meilleur score - Recherche aléatoire",
    )

    # graphe pour l'algorithme génétique (exercice 3)
    if os.path.exists("results_genetic.csv"):
        tracer_simple(
            "results_genetic.csv",
            "Évolution du meilleur score - Algorithme génétique",
        )

    # comparaison sur un seul graphe
    tracer_comparaison()


if __name__ == "__main__":
    main()
