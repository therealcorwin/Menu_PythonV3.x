"""
CLI Menu
"""
version = 0.1

from os import system, name


class Menu_item:
    def __init__(self, name, index, structure):
        self.name = self.title = name
        self.index = index
        self.structure = structure

        if self.structure.get("sub-menu"):
            self.sub_menu = [Sub_menu_item(self, k, i, v) for i, e in enumerate(self.structure["sub-menu"], 1) for k, v in e.items()]

    def has_sub_menu(self):
        return hasattr(self, "sub_menu")

    def __repr__(self):
        return f"{self.index}. {self.name}"


class Sub_menu_item(Menu_item):
    def __init__(self, parent, name, index, structure):
        super().__init__(name, index, structure)
        self.parent = parent


class Menu:
    def __init__(self, name, structure):
        self.title = name
        self.structure = structure
        self.walk_to_next_menu_list()

    def set_config(self, header, footer, border):
        self.bordure = border
        self.header = f" {header} "
        self.footer = f" {footer} "

    def is_sub_menu(self):
        return len(self.walk) > 1

    def set_structure(self):
        return [Menu_item(k, i, v) for i, el in enumerate(self.structure, 1) for k, v in el.items()]

    def walker(self, entry):
        if not hasattr(self, "walk"):
            self.walk = [self.set_structure()]
        elif entry:
            if self.current_menu_elements[self.entry - 1].has_sub_menu():
                self.walk.append(self.current_menu_elements[self.entry - 1].sub_menu)
        elif len(self.walk) > 1:  # Retour au précédant
            del self.walk[-1]
        self.current_menu_elements = self.walk[-1]
        self.name = self.current_menu_elements[self.entry - 1].parent.name if len(self.walk) > 1 else self.title
        return self.current_menu_elements

    def walk_to_next_menu_list(self, entry=None):
        self.current_menu = "\t\n".join(f"\t{e}" for e in self.walker(entry))

    def __repr__(self):
        self.clear()
        menu = self.current_menu
        if self.is_sub_menu():
            menu += f"\n 0. Back"
        affichage = f"{self.header:{self.bordure}^60}\n{self.name}\n{menu}\nVersion : {version}\n{self.footer:{self.bordure}^60}"
        if self.is_sub_menu():
            affichage += f"\n 0. retour"
        return affichage

    def keyboard_process(self):
        breaked = 0
        while True:
            try:
                reply = input("Choice : ")
            except (KeyboardInterrupt, ValueError) as e:
                if "KeyboardInterrupt" in e.__repr__():
                    print("keyboard")
                    breaked = self.escape_menu()
                elif "ValueError" in e.__repr__():
                    print("Only numbers are allowed!")
            else:
                if not reply: self()
                try:
                    self.entry = int(reply)
                except ValueError:
                    if reply.lower()[0] == "y" and breaked: exit(0)
                    elif reply.lower()[0] == "n": self()
                    else:
                        print("Only numbers are allowed!")
                else:
                    if self.entry > len(self.current_menu_elements):
                        print("exceed the value!")
                    else:
                        return self.entry

    def __call__(self):
        while True:
            print(self)
            self.walk_to_next_menu_list(self.keyboard_process())


    @staticmethod
    def clear():
        _ = system('cls') if name == 'nt' else system('clear')

    def escape_menu(self):
        self.clear()
        print(f"{self.header:{self.bordure}^60}\nQuit?\nYes (y)\nVersion : {version}\n{self.footer:{self.bordure}^60}")
        return 1


if __name__ == '__main__':
    config = [
        {"Plop1": {"sub-menu": [{"Installer1": {"sub-menu": [{"sous-menu1": {}}, {"Sous-menu2": {}}]}}, {"Supprimer1": {}}]}},
        {"Plop2": {"sub-menu": [{"Installer2": {}}, {"Supprimer2": {}}]}}
    ]

    menu = Menu("Mon menu", config)
    menu.set_config("header", "footer", "=")
    menu()