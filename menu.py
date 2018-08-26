"""
CLI Menu
"""
version = 0.1

from os import system, name, get_terminal_size
from termcolor import cprint, colored


class Menu_item:
    def __init__(self, name, index, structure):
        self.name = self.title = name
        self.index = index
        self.structure = structure

        if self.structure.get("sub-menu"):
            self.sub_menu = [Sub_menu_item(self, k, i, v)
                for i, e in enumerate(self.structure["sub-menu"], 1) for k, v in e.items()]

        self.color = self.structure["color"] if self.structure.get("color") else Menu.color["menu"]

    def has_sub_menu(self):
        return hasattr(self, "sub_menu")

    def __repr__(self):
        return f"{self.index}. {self.name}"


class Sub_menu_item(Menu_item):
    def __init__(self, parent, name, index, structure):
        super().__init__(name, index, structure)
        self.parent = parent


class Menu:
    width = 60
    color = {
        "warning":"red",
        "border":"green",
        "version":"blue",
        "menu":"cyan",
        "escape_menu":"magenta",
        "title": "yellow",
        "input": "yellow"
    }

    def __init__(self, name, structure):
        self.title = name
        self.main_color = self.color["menu"]
        self.structure = structure
        self.walk_to_next_menu_list()

        try:
            self.spaces = int((get_terminal_size().columns - self.width) / 2)
        except OSError:
            self.spaces = 0

    def set_config(self, header="header", footer="footer", border="="):
        self.border = border
        self.header = colored(f" {header} ", self.color["border"])
        self.footer = colored(f" {footer} ", self.color["border"])

    def set_structure(self):
        return [Menu_item(k, i, v) for i, el in enumerate(self.structure, 1) for k, v in el.items()]

    def walk_to_next_menu_list(self, entry=None):
        if not hasattr(self, "walk"):
            self.walk = [self.set_structure()]
        elif entry:
            if self.current_menu[self.entry - 1].has_sub_menu():
                self.walk.append(self.current_menu[self.entry - 1].sub_menu)
        elif len(self.walk) > 1:  # Back to parent menu
            del self.walk[-1]
        self.current_menu = self.walk[-1]
        self.name = self.current_menu[self.entry - 1].parent.name if len(self.walk) > 1 else self.title


    def keyboard_process(self):
        breaked = 0
        while True:
            try:
                reply = input(colored(f"\n{' '*self.spaces}Choice : ", self.color["input"]))
            except KeyboardInterrupt:
                    print(self.escape_menu())
                    if breaked: exit()
                    else: breaked = True
            else:
                if not reply:
                    cprint(f"\n{' '*self.spaces}Please enter your choice!", self.color["warning"])
                    continue
                try:
                    self.entry = int(reply)
                except ValueError:
                    if breaked:
                        if reply.lower()[0] == "y": exit(0)
                        elif reply.lower()[0] == "n": self()
                        else: cprint(f"\n{' '*self.spaces}Yes(y) or No(n)!", self.color["warning"])
                    else:
                        cprint(f"\n{' '*self.spaces}Only numbers are allowed!", self.color["warning"])
                else:
                    if breaked:
                        cprint(f"\n{' '*self.spaces}Yes(y) or No(n)!", self.color["warning"])
                    elif self.entry > len(self.current_menu):
                        cprint(f"\n{' '*self.spaces}exceed the value!", self.color["warning"])
                    else: return self.entry

    @staticmethod
    def clear():
        _ = system('cls') if name == 'nt' else system('clear')

    def _header_footer(main_print):
        def _wraper(self) :
            self.clear()
            display = f"""
{self.header:{self.border}^{self.width}}
{colored(self.name, self.color["title"])}
{main_print(self)}
Version : {colored(version, self.color["version"])}
{self.footer:{self.border}^{self.width}}"""
            return display.replace("\n", f'\n{" "*self.spaces}')
        return _wraper

    @_header_footer
    def escape_menu(self):
        escape_menu = f"Quit?\nYes (y)"
        return f"{colored(escape_menu, self.color['escape_menu'])}"

    @_header_footer
    def __repr__(self):
        back = "\t0. Back\n" if len(self.walk) > 1 else "\n"
        menu = "\t\n".join(f"\t{colored(e, e.color)}" for e in self.current_menu)
        return f"{back}{colored(menu, self.main_color)}"

    def __call__(self):
        while True:
            print(self)
            self.walk_to_next_menu_list(self.keyboard_process())


if __name__ == '__main__':
    config = [
        {"Plop1": {"color": "red", "sub-menu": [
            {"Installer1": {"sub-menu": [
                {"sous-menu1": {"color": "magenta"}}, {"Sous-menu2": {}}]}},
            {"Supprimer1": {}}]}},
        {"Plop2": {"color": "magenta", "sub-menu": [
            {"Installer2": {}}, {"Supprimer2": {}}]}}]

    menu = Menu("Mon menu", config)
    menu.set_config("header", "footer", "=")
    menu()