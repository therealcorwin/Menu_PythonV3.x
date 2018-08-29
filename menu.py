# -*- coding: utf-8 -*-
"""
CLI Menu
"""
version = 0.1
"""TODO
see either on Linux or Mac the key history reaction on each onw terminal
"""

from keyboard import KEY_UP, KEY_DOWN, write, add_hotkey, send
from termcolor import cprint, colored
from time import sleep

from os import system, name, get_terminal_size
from subprocess import call
from sys import stdout, stdin, __stdin__


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

        if self.structure.get("command"):
            self.command =  self.structure["command"].split()

    def has_sub_menu(self):
        """Check if the items contains a sub-menu

        :return: True if the menu item has a sub-menu
        """
        return hasattr(self, "sub_menu")

    def is_callable(self):
        """Check if the item is callable

        :return: True is the item has a command line for executtion
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
        - keyboard_input: to select the menu item selection style
            (True -> prompt; False -> "up" / "down" arrow keys are used)

            Used only when *keyboard_input* is set to False
                - pressed_key: the key pressed
                - select: save the current menu item index
                - escape_select: the key pressed in the escape menu

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
        self.set_config()
        self.walk_next_menu_list()

        # get the size of the terminal
        try:
            self.spaces = int((get_terminal_size().columns - self.width) / 2 + 4)  # offset is set to 4
        except OSError:  # if the program is launch by the IDE
            self.spaces = 0

        add_hotkey(KEY_UP, self.keyboard_up)
        add_hotkey(KEY_DOWN, self.keyboard_down)
        add_hotkey('space', self.keyboard_space)

        self.select = 1
        self.escape_select = "y"
        self.touche = False

        call("doskey /listsize=0".split())

    def set_config(self, header="header", footer="footer", border="=", keyboard_input=True, arrow="→"):
        """Setting up the Menu display

        The display configuration and keyboard style may be set up.

        :param header: name of the header
        :param footer: name of the footer
        :param border: ASCII character which fills the header and the footer line
        :param keyboard_input (boolean): set the keyboard control method
            (True -> prompt; False -> "up" / "down" arrow keys are used)
        """
        self.border = border[0]
        self.header = colored(f" {header} ", self.color["border"])
        self.footer = colored(f" {footer} ", self.color["border"])
        self.arrow = arrow

        # set the keyboard control method
        if not keyboard_input:
            # "up" / "down" arrow keys are used
            self.select = 1  # the arrow initially set for the first menu element selection
        self.keyboard_input = keyboard_input

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
                entry = 0
                self.select = 1
                del self.walk[-1]
            elif entry:
                if self.current_menu[entry - 1].has_sub_menu():
                    self.walk.append(self.current_menu[entry - 1].sub_menu)
            if self.walk[-1] != self.current_menu:
                self.current_menu = self.walk[-1]
                # At the root menu the name is setted to title; within a sub-menu item, it is setted to parent item name
                self.name = self.current_menu[entry - 1].parent.name if len(self.walk) > 1 else self.title

                if not self.keyboard_input:
                    self.select = 1  # the arrow is initially set for the first menu element selection

    def keyboard_down(self):
        if self.select < len(self.current_menu) + 1:
            send("escape")
            self.touche = True
            if not self.escape:
                if self.select == len(self.current_menu):
                    self.select = 1 if len(self.walk) == 1 else 0
                else:
                    self.select += 1
            else:
                self.escape_select = "n" if self.escape_select == "y" else "y"
            send("escape")
            send("enter")

    def keyboard_up(self):
        send("escape")
        self.touche = True
        if not self.escape:
            if self.select == len(self.walk) == 1 or not self.select and len(self.walk) > 1:
                self.select = len(self.current_menu)
            else:
                self.select -= 1
        else:
            self.escape_select = "n" if self.escape_select == "y" else "y"
        send("escape")
        send("enter")

    def keyboard_space(self):
        send("escape")
        print(self.escape_select)
        if not self.escape:
            write(str(self.select))
        else:
            write(self.escape_select)
        send("enter")

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

        # select the menu keyboard style
        if self.keyboard_input:
            # input the menu item index
            while True:
                try:
                    reply = input(colored(f"{' '*self.spaces}Choice : ", self.color["input"]))
                except KeyboardInterrupt:
                    # the[ctrl]+c interruption is caught
                    self.escape_select = "y"
                    self.escape_event()
                else:
                    if not reply:
                        if self.touche:
                            self.touche = False
                            self()
                        else:
                            self("Please enter your choice!")  # blank line is returned
                    elif reply.lower()[0] == "y": self.escape_event()
                    elif reply.lower()[0] == "n":
                        self.escape = False
                        self()  # return to the last menu state
                    else:
                        try:
                            entry = int(reply)
                        except ValueError:  # other than a number is entered
                            if self.escape:
                                # escape menu state
                                if reply.lower()[0] == "y": self.escape_event()
                                elif reply.lower()[0] == "n":
                                    if hasattr(self, "select"):
                                        self.keyboard_input = False  # return to the keyboard initial style
                                        self.pressed_key = "enter"  # to not buffer the enter key
                                    self.escape = False
                                    self()  # return to the last menu state
                                else: self("Yes(y) or No(n)!")  # other than "y" or "n" and not a number is entered
                            else: self("Only numbers are allowed!")
                        else:  # a number is entered
                            # handle the potential user input errors
                            if self.escape: self("Yes(y) or No(n)!")  # on the escape menu...
                            elif entry > len(self.current_menu): self("Wrong choice!")
                            elif entry and not self.current_menu[entry - 1].has_sub_menu(): self("No sub-menu available!")
                            else:
                                self.escape = False
                                self.select = 1
                                return entry

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
        def _wraper(self) :
            self._clear()
            title = self.name if not self.escape else "Quit?"
            display = f"""
{self.header:{self.border}^{self.width}}
{colored(title, self.color["title"])}
{main_print(self)}
Version : {colored(version, self.color["version"])}
{self.footer:{self.border}^{self.width}}"""
            return display.replace("\n", f"\n{' '*self.spaces}")
        return _wraper

    @_menu_display
    def escape_menu(self):
        """ The colored escape menu

        Displayed by pressing the [ctrl] + c keyboard sequence.

        :return: the string of the menu
        """
        yes = f"\n\t{f'{self.arrow} (y)' if self.escape_select == 'y' else '  (y)'} Yes"
        no = f"\n\t{f'{self.arrow} (n)' if self.escape_select == 'n' else '  (n)'} No\n"
        return f"{colored(f'{yes}{no}', self.color['escape_menu'])}"

    def escape_event(self):
        """Handle the [ctrl]+c event

        Triggered when [ctrl]+c is caught by the keyboardInterruption exception
        in keyboard_process().
        """
        if self.escape:  # it exits if [ctrl]+c is pressed twice
            self._end()
        else:
            if not self.keyboard_input:
                self.escape_select = "y"
            self.escape = True  # [ctrl]+c has been received once
            self()

    @_menu_display
    def __repr__(self):
        """ Print this Menu class

        Displaying a colored menu.
        If the sub-menu is active, the return option "0. back" is displayed at the top of it.

        :return: the string of the main menu
        """
        back = f"\n\t{f'{self.arrow} 0.' if self.select == 0 else '  0.'} Back\n" if len(self.walk) > 1 else ""
        menu = "\t\n".join([colored(f"\t{f'{self.arrow} {e.index}.' if self.select == e.index else f'  {e.index}.'} "
                                                    f"{e.name}", e.color) for e in self.current_menu])
        return f"\n{colored(menu, self.main_color)}\n{back}"

    def __call__(self, error=None, escape_menu=False):
        """This instance class is now callable as a function

        It prints the menu completely and prompt the user for the next menu element

        :param error: (string) an error occurred and is displayed above the menu prompt
        :param escape_menu: (bool) True if the escape menu is activated
        """
        # main loop
        while True:
            print(self) if not self.escape else print(self.escape_menu())
            self.walk_next_menu_list(self.keyboard_process(error))
            error = None

    def _end(self, command=None):
        """Exit and run

        Clear the screen, run a command and exit.

        :param command: the command line to run
        """
        self._clear()
        if command:
            call(command)
        raise SystemExit


if __name__ == '__main__':
    structure = [
        {"Plop1": {"color": "red", "sub-menu": [
            {"Installer1": {"sub-menu": [
                {"sous-menu1": {"color": "magenta", "sub-menu": [
                    {"Sous-sous-menu1": {}},
                    {"Sous-sous-menu2": {}},
                    {"Sous-sous-menu3": {"command":"test.bat Jean", "color": "red"}}]}},
                {"Sous-menu2": {}}]}},
            {"Supprimer1": {}}]}},
        {"Plop2": {"color": "magenta", "sub-menu": [
            {"Installer2": {}},
            {"Supprimer2": {}}]}}]

    menu = Menu("Mon menu", structure)
    #menu.set_config("header", "footer", "=1", False)  # setting up the menu (False for keyboard style) - CLAVIER FLECHES
    menu.set_config("header", "footer", "=")  # DECOMMENTER POUR LE STYLE CLAVIER ORDINAIRE
    menu()  # call and display the menu
