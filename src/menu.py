from pprint import pprint


class Menu(object):
    def __init__(self, config, symbol):
        self.config = config
        self.symbol = symbol

    def beautify_menu(self, func):
        def _wrapper(*args):
            print(self.symbol * 40)
            for i in args:
                func(i)
            print(self.symbol * 40)

        return _wrapper

    def display_content(self):
        """
            Will display menus and sub-menus content
        """
        pass

    def create_menus(self):
        """
            Will create menus and sub-menus and store
            them in a dictionnary
        """
        for key in self.config.keys():
            if 'menu' in self.config.get(key).keys():
                self.config.get(key)

    def manage_choice(self):
        """
            Will manage key acquisition and dynamically show the choice
            with '->' character or by changing clolor
            #TODO finding a module for key acquisition
        """
        pass
