"""
CLI Menu
"""
version = 0.1

from os import system, name, get_terminal_size
from termcolor import cprint, colored


class Menu_item:
    """Menu item class

    It instances each element of the menu

    Attribute:
        - title: the menu main title
        - name: name of the parent menu in case a sub-menu is displayed
        - index: position of the element in the menu
        - structure: all the parameters of the element
            - sub_menu: (list) its sub-menu items settled in a list of Sub_menu_item class objects
            - color: its unique color for the display

    Method:
        - has_sub_menu: to detect if it contains a sub-menu
    """
    def __init__(self, item_name, index, structure):
        """Menu item Menu_item class

        :param item_name: name of the menu element
        :param index: indicate its position in the menu
        :param structure: all its parameters
        """
        self.name = self.title = item_name
        self.index = index
        self.structure = structure

        # create a list of all the Sub_menu_item objects
        if self.structure.get("sub-menu"):
            self.sub_menu = [Sub_menu_item(self, k, i, v)
                for i, e in enumerate(self.structure["sub-menu"], 1) for k, v in e.items()]

        # use the color extracted from the structure otherwise it used the defaut color
        self.color = self.structure["color"] if self.structure.get("color") else Menu.color["menu"]

    def has_sub_menu(self):
        """Check if the items contains a sub-menu

        :return: True if the menu item has a sub-menu
        """
        return hasattr(self, "sub_menu")

    def __repr__(self):
        """Display the menu item object

        the item name is preceeded by its index followed by a full stop caracter "."

        :return: string of the
        """
        return f"{self.index}. {self.name}"


class Sub_menu_item(Menu_item):
    """Sub-menu item class

    Inherited from the Menu_item class

    Attribute:
        - parent: name of the parent menu

    No new method is added. See the Menu_item class description.
    """
    def __init__(self, parent, item_name, index, structure):
        """Initialize the Sub_menu_item class

        :param parent: parent object
        :param item_name: name of the sub-menu element
        :param index: indicate its position in the menu
        :param structure: all its parameters
        """
        super().__init__(item_name, index, structure)
        self.parent = parent


class Menu:
    """Main class of the project

    Display the CLI menu and prompt the user.
    All the potential errors of the user are handled.

    Attributes:
        - widht : the width of the menu display
        - breaked: True when the escape menu is activated
        - color: a list of all he used colors
        - title: the title of the main menu
        - main_color: the color of a menu element
        - structure: all the menu parameters
        - spaces: spaces added to center the menu display

        - border: ASCII character which fills the header and the footer line
        - header: the header name
        - footer: the footer name

        - walk: walker containing a list of the menu items encontered
        - current_menu: the actual list of all the menu or su-menu items

    Methods:
        - set_config: set the conguration of the menu display (header and footer names, etc...)
        - set_structure: parse the configuration parameters
        - walk_to_next_menu_list: set *current_menu* and *name* variables to display the menu correctly
        - keyboard_process: all the controls for the user prompt
        - _clear: clear the screen
        - _menu_display: decorator to display the menu
        - escape_menu: display the escape menu
    """
    width = 60  # default width of the menu display
    breaked = False
    # list of the color code list
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
        """Initialize the Menu class

        :param menu_name: name of the main menu
        :param structure: all the configuration parameters
            [{item_1: {"color": item1_color, "sub-menu": [{sub_item1: {"color":....}}, {sub_item2: {"color":....}}]}},
            [{item_2: {"color": item2_color, "sub-menu": [{sub_item1: {"color":....}}, {sub_item2: {"color":....}}]}}]
        """
        self.title = menu_name
        self.main_color = self.color["menu"]
        self.structure = structure
        self.walk_to_next_menu_list()

        try:
            self.spaces = int((get_terminal_size().columns - self.width) / 2)
        except OSError:  # to launch the program within the IDE
            self.spaces = 0

    def set_config(self, header="header", footer="footer", border="="):
        """Setting up the Menu display

        :param header: name of the header
        :param footer: name of the footer
        :param border: ASCII character which fills the header and the footer line
        """
        self.border = border
        self.header = colored(f" {header} ", self.color["border"])
        self.footer = colored(f" {footer} ", self.color["border"])

    def set_structure(self):
        """Parse the menu item configuration

        It may contain the color informations and all the sub-menu structures

        :return: a list of Menu_item objects
        """
        return [Menu_item(k, i, v) for i, el in enumerate(self.structure, 1) for k, v in el.items()]

    def walk_to_next_menu_list(self, entry=None):
        """Menu walker

        It sets *current_menu* and *name* in order to display the menu properly

        :param entry: (int) the index of the menu item entered by the user
        """
        if not hasattr(self, "walk"):
            self.walk = [self.set_structure()]  # first call
        elif entry:
            if self.current_menu[self.entry - 1].has_sub_menu():
                self.walk.append(self.current_menu[self.entry - 1].sub_menu)
        elif len(self.walk) > 1:  # reply = 0 (back to parent menu)
            del self.walk[-1]
        self.current_menu = self.walk[-1]
        # At the root menu the name is setted to title; within a sub-menu item, it is setted to parent item name
        self.name = self.current_menu[self.entry - 1].parent.name if len(self.walk) > 1 else self.title

    def keyboard_process(self, error):
        """Keyboard process

        Prompt the user to select the menu item.

        Catches the [ctrl]+c sequence interruption and displays the escape menu
            if the [ctrl]+c sequence is sent twice, the program exits

        Displays the error above the prompt.
        Error are handled if:
            - no numbers are entered within the menu display
            - the number entered exceeds the limit of the menu items range
            - the user enters a blank line
            - other characters than "y" or "n" are entered within the escape menu display

        :param error: (string) the raised error
        """
        cprint(f"{' '*self.spaces}{error}", self.color["error"]) if error else print()  # display the error line
        while True:
            try:
                reply = input(colored(f"{' '*self.spaces}Choice : ", self.color["input"]))
            except KeyboardInterrupt:
                    # the[ctrl]+c interruption is catched
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
        """"Clear the screen

        The command "clear" is used on Linux and Mac and "cls" under windows
        as the system is automatically detected.
        """
        _ = system('cls') if name == 'nt' else system('clear')  # os.name is used to detect the system

    def _menu_display(main_print):
        """Wrapper for the colored menu display

        Containing the header, the version number and the footer.
        Everything should be well centered on the screen.

        :return: _wrapper: all the functions are displayed together
        """
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

    @_menu_display
    def escape_menu(self):
        """ The colored escape menu

        Displayed by pressing the [ctrl] + c keyboard sequence.

        :return: the string of the menu
        """
        escape_menu = f"Quit?\nYes (y)"
        return f"{colored(escape_menu, self.color['escape_menu'])}"

    @_menu_display
    def __repr__(self):
        """ Print this Menu class

        Displaying a colored menu.
        If the sub-menu is active, the return option "0. back" is displayd at the top of it.

        :return: the string of the main menu
        """
        back = "\t0. Back\n" if len(self.walk) > 1 else "\n"
        menu = "\t\n".join(f"\t{colored(e, e.color)}" for e in self.current_menu)
        return f"{back}{colored(menu, self.main_color)}"

    def __call__(self, error=None, escape_menu=False):
        """This instance class is now callable as a function

        It prints the menu completely and prompt the user for the next menu element

        :param error: (string) an error occured and is displayed above the menu prompt
        :param escape_menu: (bool) True if the escape menu is activated
        """
        while True:
            print(self) if not self.breaked else print(self.escape_menu())
            self.walk_to_next_menu_list(self.keyboard_process(error))
            error = None


if __name__ == '__main__':
    structure = [
        {"Plop1": {"color": "red", "sub-menu": [
            {"Installer1": {"sub-menu": [
                {"sous-menu1": {"color": "magenta"}},
                {"Sous-menu2": {}}]}},
            {"Supprimer1": {}}]}},
        {"Plop2": {"color": "magenta", "sub-menu": [
            {"Installer2": {}},
            {"Supprimer2": {}}]}}]

    menu = Menu("Mon menu", structure)
    menu.set_config("header", "footer", "=")
    menu()  # call and display the menu