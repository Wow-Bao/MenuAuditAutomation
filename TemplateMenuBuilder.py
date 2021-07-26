from MenuAuditmator import ModifierGroup, Item, Menu
import pandas as pd

def BuildMenuTemplate(itemFile, mGroupFile, isCheeseburgerBao, isCoconutBao, isEggSausageBao, isIMPOSSIBLEBao, isBundles, isPotDumpCombined):
    """This method returns a template Menu object based on SF parameters for the menu. Method output is the optimal menu for a location - what it should be."""
    template = Menu(None, None)
    items = []
    df_item = pd.read_csv(itemFile, index_col=False)
    df_mg = pd.read_csv(mGroupFile, index_col=0)
    #categories are hardcoded get over it
    template.categories = ["Bao", "Bowls", "Pan-Seared Potstickers", "Steamed Dumplings", "Combo"]
    if(isBundles):
        template.categories.append("Bundles")
    if(isPotDumpCombined):
        template.categories.remove("Pan-Seared Potstickers")
        template.categories.remove("Steamed Dumplings")
        template.categories.append("Potstickers and Dumplings")    
    #fuck it just email me at archand@andrew.cmu.edu if you need help updating the template menu sometime in the future
    bao_modifiers = ["BBQ Berkshire Pork", "Teriyaki Chicken", "Spicy Mongolian Beef", "Whole Wheat Vegetable"]
    if(isCheeseburgerBao):
        bao_modifiers.append("Cheeseburger")
    if(isCoconutBao):
        bao_modifiers.append("Coconut Custard")
    if(isEggSausageBao):
        bao_modifiers.append("Egg and Spicy Sausage")
    if(isIMPOSSIBLEBao):
        bao_modifiers.append("IMPOSSIBLE") #this is probably wrong but i can't find any examples

    pot_dump_modifiers = ["Ginger Chicken", "Green Vegetable"]
    bowl_modifiers = ["Teriyaki Chicken Bowl", "Spicy Kung Pao Chicken Bowl", "Orange Chicken Bowl"]
    for row in df_item.iterrows():
        if(not ((int(row['Bundle?']) == 1) and (isBundles==False))):
            mgs = row['ModifierGroup1':'ModifierGroup18']
            mset = []
            groups = []
            for mg in mgs:
                if(mg):
                    if("Bao" in mg):
                        mset = bao_modifiers
                    elif("Potsticker" in row['Name'] or "Dumpling" in mg):
                        mset = pot_dump_modifiers
                    elif("Bowl" in mg):
                        mset = [""]
                    groups.append(ModifierGroup(mg, mset))
            item = Item(row['Name'], row['Description'], groups)
            items.append(item)
    template.items = items
    