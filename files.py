import os
import random
import Levenshtein
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


# repertoire de base angular JS à convertir
rep = os.getenv("rep")


# On build les listes des path de chaque fichier à convertir par types
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

"""print(len(bad_dataservice))
print(len(bad_services))
print(len(bad_restangular))
print(len(bad_components))"""


# repertoire contenant les fichiers correctes réecrit par Yael
rep2 = os.getenv("rep2")

good_services = []
good_dataservice= []
good_restangular= []
good_components= []
good_constants = []

# on build les les listes contenant les path des fichers correctes pour chaque types
parcourir_repertoire(rep2, good_services, "service", exclus=["restangular", "data.","spec"])
parcourir_repertoire(rep2, good_restangular, "restangular",exclus=["spec"])
parcourir_repertoire(rep2, good_dataservice, "data.service",exclus=["spec"])
parcourir_repertoire(rep2, good_components, "component.ts",exclus=["spec"])
parcourir_repertoire(rep2, good_constants, "constants",exclus=["spec"])

# 31 ok
print(len(good_restangular))
print(len(good_components))
print(len(good_constants))
print(len(good_dataservice))
print(len(good_services))



def count_caracteres(code_source: str) -> int:
    return len(code_source)

def count_lines_of_code(code):
    return len(code.splitlines())

def levenshtein_distance(code1, code2):
    return Levenshtein.distance(code1, code2)



# Affiche les résultats (optionnel)
#print("Fichiers constants sélectionnés :", bad_constants)
#print("Fichiers services sélectionnés :", liste_services)




