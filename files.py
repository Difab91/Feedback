import os
import random
from dotenv import load_dotenv

load_dotenv()


liste_services = []
liste_constants = []



def parcourir_repertoire(repertoire: str, liste_fichiers: list):
    for racine, _, fichiers in os.walk(repertoire):
        for fichier in fichiers:
            chemin_fichier = os.path.join(racine, fichier)
            liste_fichiers.append(chemin_fichier)
   


services = os.getenv("path_services")
constants = os.getenv("path_constants")

# on creer les listes qui contiennent les paths de tous les services et constants du projet

parcourir_repertoire(services, liste_services)
parcourir_repertoire(constants, liste_constants)


# on initialise une graine pour controler l'aléatoire

random.seed(42)

# on choisis 18 fichiers aléatoires pour chaque type de fichier
random.shuffle(liste_constants)
liste_constants= liste_constants[:18]

random.shuffle(liste_services)
liste_services= liste_services[:18]




