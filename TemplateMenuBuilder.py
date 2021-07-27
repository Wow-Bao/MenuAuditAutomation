from MenuAuditmator import ModifierGroup, Item, Menu
import json
import pandas as pd

def BuildMenuTemplate(itemFile, mGroupFile, isCheeseburgerBao, isCoconutBao, isEggSausageBao, isIMPOSSIBLEBao, isBundles, isPotDumpCombined):
    """This method returns a template Menu object based on SF parameters for the menu and a menu reference JSON file. Method output is the optimal menu for a location - what it should be."""
    infile = "C:/Users/creek/Desktop/WowBaoScripts/MenuAuditAutomation/MenuReference.json"
    with open(infile) as file:
        data = json.load(file)
    
    template_menu = Menu(None, None)
    for category in data['Categories']:
        #have fun figuring out this part n00b
        if(category.get("bundleDependency", isBundles)==isBundles):
            if(category.get("potDumpDependency", isPotDumpCombined)==isPotDumpCombined):
                template_menu.categories.append(category["Name"])
    
    #setting standard modifier sets
    #no use encoding the same 4 bao flavors over and over again in the json with hella dependencies
    #modifier sets are the only parts of the menu you have to edit in the code
    #IF YOU NEED TO CHANGE MODIFIERS DO IT HERE

    #base modifiers
    bao_modifiers = ["BBQ Berkshire Pork", "Teriyaki Chicken", "Spicy Mongolian Beef", "Whole Wheat Vegetable"]
    pot_dump_modifiers = ["Ginger Chicken", "Green Vegetable"]
    bowl_modifiers = ["Teriyaki Chicken Bowl", "Spicy Kung Pao Chicken Bowl", "Orange Chicken Bowl"]

    #continegent modifiers (atm only bao)
    if(isCheeseburgerBao):
        bao_modifiers.append("Cheeseburger")
    if(isCoconutBao):
        bao_modifiers.append("Coconut Custard")
    if(isEggSausageBao):
        bao_modifiers.append("Egg & Sausage")
    if(isIMPOSSIBLEBao):
        bao_modifiers.append("IMPOSSIBLE")

    modifier_sets = {"Bao":bao_modifiers, "Potsticker/Dumpling":pot_dump_modifiers, "Bowl":bowl_modifiers}
    


    for i in data['Items']:
        if(category.get("bundleDependency", isBundles)==isBundles):
            mgs = []
            for m in i.get("ModifierGroups", []):
                mgs.append(ModifierGroup(m["Name"], modifier_sets[m["ModifierSet"]]))
            item = Item(i["Name"], i["Description"], mgs)
            template_menu.items.append(item)
    
    return template_menu