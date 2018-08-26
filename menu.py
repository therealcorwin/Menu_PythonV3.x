"""
CLI Menu
"""
version = 0.1

from os import system, name, get_terminal_size
from termcolor import cprint, colored


class Menu_item:
    def __init__(self, item_name, index, structure):
        self.name = self.title = item_name
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
    def __init__(self, parent, item_name, index, structure):
        super().__init__(item_name, index, structure)
        self.parent = parent


class Menu:
    width = 60
    error = 0
    breaked = 0
    color = {
        "error":"red",
        "border":"green",
        "version":"blue",
        "menu":"cyan",
        "escape_menu":"magenta",
        "title": "yellow",
        "input": "yellow"
    }

    def __init__(self, menu_name, structure):
        self.title = menu_name
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

    def keyboard_process(self, error):
        cprint(f"{' '*self.spaces}{error}", self.color["error"]) if error else print()  # display the error line
        while True:
            try:
                reply = input(colored(f"{' '*self.spaces}Choice : ", self.color["input"]))
            except KeyboardInterrupt:
                    # the[ctrl]+c exception is catched
                    if self.breaked: exit()  # exit if [ctrl]+c is pressed 2x
                    else:
                        self.breaked = True  # flag two detect the escape_menu state
                        self()  # display the escape menu
            else:
                if not reply: self("Please enter your choice!")  # blank line is returned
                try:
                    self.entry = int(reply)
                except ValueError:  # other than a number is entered
                    if self.breaked:
                        # escape menu state
                        if reply.lower()[0] == "y": exit(0)
                        elif reply.lower()[0] == "n":
                            self.breaked = False
                            self("")  # return two the last menu state
                        else: self("Yes(y) or No(n)!")  # other than "y" or "n" and not a number is entered
                    else: self("Only numbers are allowed!")
                else:
                    # a number is entered
                    if self.breaked:  # on the escape menu...
                        self("Yes(y) or No(n)!")
                    elif self.entry > len(self.current_menu):
                        self("Exceed the value!")
                    else:
                        self.breaked = False
                        return self.entry

    @staticmethod
    def _clear():
        if name == 'nt':
            system('cls')
        else:
            system('clear')

    def _header_footer(main_print):
        def _wraper(self) :
            self._clear()
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

    def __call__(self, error=0, escape_menu=False):
        while True:
            print(self) if not self.breaked else print(self.escape_menu())
            self.walk_to_next_menu_list(self.keyboard_process(error))


if __name__ == '__main__':
    structure = [
        {"Plop1": {"color": "red", "sub-menu": [
            {"Installer1": {"sub-menu": [
                {"sous-menu1": {"color": "magenta"}}, {"Sous-menu2": {}}]}},
            {"Supprimer1": {}}]}},
        {"Plop2": {"color": "magenta", "sub-menu": [
            {"Installer2": {}}, {"Supprimer2": {}}]}}]

    menu = Menu("Mon menu", structure)
    menu.set_config("header", "footer", "=")
    menu()