#!/usr/bin/env python
# coding: utf-8

"""Fichier de configuration du Menu CLI

Module permettant de préparer le menu en prenant en compte toutes ses spécificitées
"""

import os

import yaml


class Config:
    """Classe de configuration du menu

    Attributs :
        nom_fichier : Nom complet du fichier de configuration
        repertoire : Nom du répertoire contenant le fichier de configuration
        menu_conf : Configuration du menu sous forme de Dictionnaire
    """
    def __init__(self, nom_fichier, repertoire):
        """Initialise la classe de configuration

            :param nom_fichier: Nom du fichier complet lié à son extension
            :param repertoire: Nom du répertoire contenant le(s) fichier(s) de configuration
        """
        # Testons d'abord la validité du fichier
        fichier, extension = os.path.splitext(nom_fichier)
        if extension != ".yaml":
            raise Exception("Fichier inconnu, l'extension .yaml doit est utilisé !")

        # Attributs
        self.nom_fichier = nom_fichier
        self.repertoire = repertoire

    def parse_config_file(self):
        """Analyse du fichier de configuration

        Conversion du contenu du fichier en un objet Python du type dictionnaire
        contenant tous les paramètres nécessaires à la construction du menu.

        Le fichier texte devra respecter la norme d'écriture de fichier YAML.
        Pour plus d'information : 'https://pyyaml.org/wiki/PyYAML'

        :return: L'objet dictionnaire de YAML
        """
        # Chemin du fichier complet de configuration
        fichier_config = os.path.join(os.path.dirname(os.path.realpath(__file__)), \
                                        self.repertoire, self.nom_fichier)

        # Traitement du fichier de configuration
        with open(fichier_config, mode="r", encoding="utf-8") as f:
            self.menu_conf = yaml.load(f.read())
        return self.menu_conf


if __name__ == '__main__':
    config = Config("menu1.yaml", "ressource")
    config.parse_config_file()
    print(config.menu_conf)