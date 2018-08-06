#!/usr/bin/env python
# coding: utf-8

"""Configuration class for the CLI Menu

This module allows to preprare the menu configuration in order be well dressed,
taking all the custom specifications into account.
"""

import os

import yaml


class Config:
    """Menu configuration class

    Attributs :
        filename : the complete filename of the configuration file
        folder : the directory name which contains the configuration file
        setup : a dictionary object containing all the setup items
    """
    def __init__(self, filename, folder):
        """Initialize the class

            :param filename: the filename of the file with its extension
            :param folder: the name of the directory which contains the configuration file
        """
        # First, we need to validate the file type by testing its extension
        file, extension = os.path.splitext(filename)
        if extension != ".yaml":
            raise Exception("Unrecognised file extension! This module only supports .yaml files!")

        # Attributs
        self.filename = filename
        self.folder = folder

    def parse_config_file(self):
        """Parse the configuration file

        Converting the configuration file into a Python dictionnary object which
        contains all the necesary parameters to set up the menu properly.

        The text file has to respect the YAML writing rules.
        For more information: 'https://pyyaml.org/wiki/PyYAML'

        :return: The YAML dictionary object
        """
        # Full path of the configuration file
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), \
                                        self.folder, self.filename)

        # Parsing the Yaml file
        with open(config_file, mode="r", encoding="utf-8") as f:
            self.setup = yaml.load(f.read())
        return self.setup


if __name__ == '__main__':
    config = Config("menu1.yaml", "resource")
    config.parse_config_file()
    print(config.setup)