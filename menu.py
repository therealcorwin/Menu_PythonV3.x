# -*- coding: utf-8 -*-
"""
CLI Menu
"""
version = 0.2
"""TODO
see either on Linux or Mac the key history reaction on each onw terminal
"""

from termcolor import cprint, colored

from os import system, name, get_terminal_size
from subprocess import call


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
        self.name = item_name
        self.index = index
        self.structure = structure

        # create a list of all the Sub_menu_item objects
        if self.structure.get("sub-menu"):
            self.sub_menu = [Sub_menu_item(self, k, i, v)
                for i, e in enumerate(self.structure["sub-menu"], 1) for k, v in e.items()]

        # use the color extracted from the structure otherwise it used the default color
        self.color = self.structure["color"] if self.structure.get("color") else Menu.color["menu"]
        # set the command to the menu item
        if self.structure.get("command"): self.command =  self.structure["command"].split()

    def has_sub_menu(self):
        """Check if the items contains a sub-menu

        :return: True if the menu item has a sub-menu
        """
        return hasattr(self, "sub_menu")

    def is_callable(self):
        """Check if the item is callable

        :return: True is the item has a command line for execution
        """
        return hasattr(self, "command")


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
        - width : the width of the menu display
        - escape: True when the escape menu is activated
        - color: a list of all he used colors
        - title: the title of the main menu
        - main_color: the color of a menu element
        - structure: all the menu parameters
        - spaces: spaces added to center the menu display

        - border: ASCII character which fills the header and the footer line
        - header: the header name
        - footer: the footer name
        - walk: walker containing a list of the menu items encountered
        - current_menu: the actual list of all the menu or su-menu items

    Methods:
        - set_config: set the configuration of the menu display (header and footer names, etc...)
        - set_structure: parse the configuration parameters
        - walk_next_menu_list: set *current_menu* and *name* variables to display the menu correctly
        - keyboard_process: the keyboard control stuffs
        - _clear: clear the screen
        - _menu_display: decorator to display the menu
        - escape_event: triggered when [ctrl]+c is caught by the keyboardInterruption exception
        - escape_menu: display the escape menu
    """
    width = 60  # default width of the menu display
    escape = False
    # list of the color code list
    color = {
        "error":"red",
        "border":"green",
        "version":"blue",
        "menu":"cyan",
        "escape_menu":"magenta",
        "title": "yellow",
        "input": "yellow"}

    def __init__(self, menu_name, structure):
        """Initialize the Menu class

        :param menu_name: name of the main menu
        :param structure: all the configuration parameters
            [{item_1: {"color": item1_color, "sub-menu": [{sub_item1: {"color":....}}, {sub_item2: {"color":....}}]}},
            [{item_2: {"color": item2_color, "sub-menu": [{sub_item1: {"color":....}}, {sub_item2: {"color":....}}]}}]
        """
        self.title = menu_name
        self.structure = structure
        self.set_config()
        self.walk_next_menu_list()

        # get the size of the terminal
        try:
            self.spaces = int((get_terminal_size().columns - self.width) / 2 + 4)  # offset is set to 4
        except OSError:  # if the program is launch by the IDE
            self.spaces = 0

    def set_config(self, header="header", footer="footer", border="="):
        """Setting up the Menu display

        The display configuration and keyboard style may be set up.

        :param header: name of the header
        :param footer: name of the footer
        :param border: ASCII character which fills the header and the footer line
        """
        self.border = border[0]
        self.header = colored(f" {header} ", self.color["border"])
        self.footer = colored(f" {footer} ", self.color["border"])

    def set_structure(self):
        """Parsing the menu item configuration structure

        It may contain the color information and all the sub-menu structures

        :return: a list of Menu_item class objects
        """
        return [Menu_item(k, i, v) for i, el in enumerate(self.structure, 1) for k, v in el.items()]

    def walk_next_menu_list(self, entry=None):
        """Menu walker

        It sets *current_menu* and *name* in order to display the menu properly.
        While *escape* is True, the escape is shown and handled.

        :param entry: (int) the index of the menu item entered by the user
        """
        if self.escape:
            # within the escape menu
            if entry == "y": self.escape_event()
            else: self.escape = False
        else:
            # first call
            if not hasattr(self, "walk"):
                self.walk = self.current_menu = [self.set_structure()]
            elif not entry and len(self.walk) > 1:  # reply = 0 (back to parent menu)
                del self.walk[-1]
            elif entry:
                if self.current_menu[entry - 1].has_sub_menu():
                    self.walk.append(self.current_menu[entry - 1].sub_menu)
            if self.walk[-1] != self.current_menu:
                self.current_menu = self.walk[-1]
                # At the root menu the name is setted to title; within a sub-menu item, it is setted to parent item name
                self.name = self.current_menu[entry - 1].parent.name if len(self.walk) > 1 else self.title

    def keyboard_process(self, error=""):
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
        # input the menu item index
        while True:
            try:
                reply = input(colored(f"{' '*self.spaces}Choice : ", self.color["input"]))
            except KeyboardInterrupt:
                self.escape_event()  # the[ctrl]+c interruption is caught
            else:
                if not reply: self("Please enter your choice!")  # blank line is returned
                else:
                    try:
                        entry = int(reply)
                    except ValueError:  # other than a number is entered
                        if self.escape:
                            # escape menu state
                            if reply.lower()[0] == "y": self.escape_event()
                            elif reply.lower()[0] == "n":
                                self.escape = False
                                self()  # return to the last menu state
                            else: self("Yes(y) or No(n)!")  # other than "y" or "n" and not a number is entered
                        else: self("Only numbers are allowed!")
                    else:  # a number is entered
                        # handle the potential user input errors
                        if self.escape: self("Yes(y) or No(n)!")  # on the escape menu...
                        elif entry > len(self.current_menu): self("Wrong choice!")
                        elif entry and self.current_menu[entry - 1].is_callable(): self._end(self.current_menu[entry - 1].command)
                        elif entry and not self.current_menu[entry - 1].has_sub_menu(): self("No sub-menu available!")
                        else: return entry

    @staticmethod
    def _clear():
        """"Clear the screen

        The command "clear" is used on Linux and Mac and "cls" under Windows
        as the system is automatically detected.
        """
        system("cls") if name == "nt" else system("clear")  # os.name is used to detect the system

    def _menu_display(main_print):
        """Wrapper for the colored menu display

        Containing the header, the version number and the footer.
        Everything should be well centered on the screen.

        :return: _wrapper: all the functions are displayed together
        """
        def _wraper(self):
            self._clear()
            title = "Quit?" if self.escape else self.name
            display = f"""
{self.header:{self.border}^{self.width}}\n\n
{colored(title, self.color["title"])}\n
{main_print(self)}\n\n
Version : {colored(version, self.color["version"])}\n
{self.footer:{self.border}^{self.width}}"""
            return display.replace("\n", f"\n{' '*self.spaces}")

        return _wraper

    @_menu_display
    def escape_menu(self):
        """ The colored escape menu

        Displayed by pressing the [ctrl] + c keyboard sequence.

        :return: the string of the menu
        """
        return colored(f"\t(y) Yes\n\t(n) No", self.color['escape_menu'])

    @_menu_display
    def __repr__(self):
        """ Print this Menu class

        Displaying a colored menu.
        If the sub-menu is active, the return option "0. back" is displayed at the top of it.

        :return: the string of the main menu
        """
        back = f"\n\n\t0. Back" if len(self.walk) > 1 else ""
        menu = "\t\n".join([colored(f"\t{e.index}. {e.name}", e.color) for e in self.current_menu])
        return f"{colored(menu, self.color['menu'])}{back}"

    def __call__(self, error=None, escape_menu=False):
        """This instance class is now callable as a function

        It prints the menu completely and prompt the user for the next menu element

        :param error: (string) an error occurred and is displayed above the menu prompt
        :param escape_menu: (bool) True if the escape menu is activated
        """
        # main loop
        while True:
            print(self.escape_menu()) if self.escape else print(self)
            self.walk_next_menu_list(self.keyboard_process(error))
            error = None

    def escape_event(self):
        """Handle the [ctrl]+c event

        Triggered when [ctrl]+c is caught by the keyboardInterruption exception
        in keyboard_process().
        """
        if self.escape:  # it exits if [ctrl]+c is pressed twice
            self._end()
        else:
            self.escape = True  # [ctrl]+c has been received once
            self()

    def _end(self, command=None):
        """Exit and run

        Clear the screen, run a command and exit.

        :param command: the command line to run
        """
        self._clear()
        if command: call(command)
        raise SystemExit


if __name__ == '__main__':
    structure = [
        {"Plop1": {"color": "red", "sub-menu": [
            {"Installer1": {"sub-menu": [
                {"sous-menu1": {"color": "magenta", "sub-menu": [
                    {"Sous-sous-menu1": {}},
                    {"Sous-sous-menu2": {}},
                    {"Sous-sous-menu3": {"command":"fichier.bat /arguments", "color": "red"}}]}},
                {"Sous-menu2": {}}]}},
            {"Supprimer1": {}}]}},
        {"Plop2": {"color": "magenta", "sub-menu": [
            {"Installer2": {}},
            {"Supprimer2": {}}]}}]

    menu = Menu("Mon menu", structure)
    menu.set_config("header", "footer", "=")
    menu()  # call and display the menu