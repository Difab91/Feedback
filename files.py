import os
import random
from dotenv import load_dotenv

load_dotenv()

bad_services = []
bad_dataservice= []
bad_restangular= []
bad_components= []
bad_constants = []

def parcourir_repertoire(repertoire: str, liste_fichiers: list, cle: str, exclus: list = None):
    exclus = exclus or []
    for racine, _, fichiers in os.walk(repertoire):
        for fichier in fichiers:
            if cle in fichier and not any(mot in fichier for mot in exclus):
                chemin_fichier = os.path.join(racine, fichier)
                liste_fichiers.append(chemin_fichier)

rep = os.getenv("rep")


# On crée les listes qui contiennent les paths de tous les services et constants du projet
parcourir_repertoire(rep, bad_services, "service", exclus=["restangular", "data."])
parcourir_repertoire(rep, bad_restangular, "restangular")
parcourir_repertoire(rep, bad_dataservice, "data.service")
parcourir_repertoire(rep, bad_components, "component.js")
parcourir_repertoire(rep, bad_constants, "constants")
'''
random.seed(42)

# On choisit 18 fichiers aléatoires pour chaque type de fichier
random.shuffle(bad_constants)
liste_constants = bad_constants[:18]

random.shuffle(liste_services)
liste_services = liste_services[:18]'''


print(len(bad_dataservice))
print(len(bad_services))
print(len(bad_restangular))
print(len(bad_components))
print(len(bad_constants))


# Affiche les résultats (optionnel)
#print("Fichiers constants sélectionnés :", bad_constants)
#print("Fichiers services sélectionnés :", liste_services)




