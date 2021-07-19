from MenuAuditmator import Menu, Issue
from TemplateMenuBuilder import BuildMenuTemplate
import os
import sys

# input_deep_link = sys.argv[1]

menu = Menu("1 Providence Place, Providence, RI", None)

menu.loadItems("https://www.doordash.com/store/1826111/?utm_source=partner-link&utm_medium=website&utm_campaign=%20\1826111")

print(menu.categories)
print(menu.items[8].name)
print(menu.items[8].description)
print(menu.items[8].modifier_groups)

menu.template_menu = menu

print(menu.compare())