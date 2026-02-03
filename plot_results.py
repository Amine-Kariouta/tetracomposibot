import matplotlib.pyplot as plt
import csv

# Lire le fichier CSV
evaluations = []
scores_best = []

with open('results_randomsearch2.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        evaluations.append(int(row['evaluation']))
        scores_best.append(float(row['score_best']))

# Tracer le graphe
plt.figure(figsize=(10, 6))
plt.plot(evaluations, scores_best, linewidth=2)
plt.xlabel('Numéro d\'évaluation')
plt.ylabel('Meilleur score')
plt.title('Évolution du meilleur score - Recherche aléatoire')
plt.grid(True)
plt.savefig('results_randomsearch2.png')
plt.show()

print("Graphe sauvegardé dans results_randomsearch2.png")
