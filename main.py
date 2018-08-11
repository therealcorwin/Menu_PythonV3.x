from src.menu import Menu
from config import Config

config = Config('menu1.yaml', 'config').parse_config_file()
menu = Menu(config, '-')
menu.create_menus()
