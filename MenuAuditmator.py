from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

class Item:
    """Object representing one DoorDash item"""
    def __init__(self, name, description, modifier_groups):
        self.name = name
        self.description = description
        self.modifier_groups = modifier_groups
        self.template_item = None
    def addModifierGroup(self, group):
        self.modifier_groups.append(group)
    def getIssues(self):
        """Returns list of Issue objects corresponding to all of the issues with the Item and its child ModifierGroup objects"""
        real_groups = self.modifier_groups.copy()
        template_groups = self.template_item.modifier_groups.copy()

        output = []
        if(self.description != self.template_item.description):
            output.append(Issue("Item", self.template_item.name, "Incorrect description: menu lists '" + self.description + "' instead of '" + self.template_item.description))
        groups_to_compare = []
        for t_group in template_groups:
            if(t_group.name in [i.name for i in real_groups]):
                real_groups[[i.name for i in real_groups].index(t_group.name)].template_group = t_group
                groups_to_compare.append(real_groups[[i.name for i in real_groups].index(t_group.name)])
            else:
                output.append(Issue("Modifier Group", self.name, t_group.name + " is missing!"))
        for r_group in real_groups:
            if(r_group.name not in [i.name for i in groups_to_compare]):
                output.append(Issue("Modifier Group", self.name, "Extraneous modifier group " + r_group.name + " found"))
        for g in groups_to_compare:
            output.extend(g.getIssues(g.template_group))
        return output

class ModifierGroup:
    """Object representing a modifier group on DoorDash"""
    def __init__(self, name, modifiers):
        self.name = name
        self.modifiers = modifiers
        self.parent = None
        self.template_group = None
    def addModifier(self, modifier):
        self.modifiers.append(modifier)
    def getIssues(self, template_group):
        """Returns a list of Issue objects corresponding to the discrepancies between self and template_group"""
        self.template_group = template_group
        output = []
        if(self.name != self.template_group.name):
            output.append(Issue("Modifier Group", self.parent.name + "/" + self.template_group.name, "Name does not match template"))
        if(len(self.modifiers) < len(self.template_group.modifiers)):
            missing = set(self.template_group.modifiers) - set(self.modifiers)
            output.append(Issue("Modifier Group", self.parent.name + "/" + self.template_group.name, "Missing modifiers"))
        elif(len(self.modifiers) > len(self.template_group.modifiers)):
            output.append(Issue("Modifier Group", self.parent.name + "/" + self.template_group.name, "Too many modifiers"))
        else:
            o=[]
            if(self.modifiers != self.template_group.modifiers):
                for i in range(0, len(self.modifiers)):
                    if(sorted(self.modifiers)[i] != sorted(self.template_group.modifiers)[i]):
                        o.append(Issue("Modifier", self.parent.name + "/" + self.template_group.name, "Menu lists modifier as " + sorted(self.modifiers)[i] + " instead of " + sorted(self.template_group.modifiers)[i]))
                if(not o):
                    pass
                    #o.append(Issue("Modifier Group", self.parent.name + "/" + self.template_group.name, "Modifiers scrambled within modifier group - adjust order of modifiers to match template"))
            output.extend(o)
        return output

class Issue:
    """Object representing one issue with a menu"""
    def __init__(self, level, location, body):
        self.level = level
        self.location = location
        self.body = body
    def output(self):
        return self.level + " - " + self.location + " - " + self.body

class Menu:
    """Object representing a DoorDash Menu"""
    def __init__(self, address, template_menu):
        self.items = []
        self.categories = []
        self.address = address
        self.template_menu = template_menu
        self.issues = []
    def loadItems(self, deep_link):
        """Scrapes DoorDash menu page for all the necessary data and loads it into Item and ModifierGroup objects within the Menu object"""
        #Load webpage
        driver = webdriver.Chrome(executable_path="C:/Users/creek/Desktop/ChromeDriver/chromedriver.exe")
        driver.get(deep_link)

        #Enter address
        dummy = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Address']")))
        time.sleep(1)
        address_field = driver.find_element_by_css_selector("input[placeholder='Address']")
        address_field.send_keys(self.address)
        time.sleep(0.5)
        address_field.send_keys(Keys.ENTER)
        time.sleep(1)
        driver.find_element_by_css_selector("button[data-anchor-id='AddressEditSave']").click()
        time.sleep(1)

        #Load categories
        category_list = driver.find_elements_by_css_selector("h2[data-category-scroll-selector]")
        category_texts = [e.text for e in category_list]
        try:
            category_texts.remove("Popular Items")
        except:
            pass
        self.categories = category_texts
        print(self.categories)

        #Load items
        #items are located by searching rectangular buttons
        item_button_list = driver.find_elements_by_xpath("//button[@shape='Rectangle']")
        actions = ActionChains(driver)
        for i in item_button_list:
            #moves item listing to center of page
            driver.execute_script("var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);"
                                            + "var elementTop = arguments[0].getBoundingClientRect().top;"
                                            + "window.scrollBy(0, elementTop-(viewPortHeight/2));", i)
            
            #click on item
            i.click()

            #wait until close item listing button is on page to move on
            dummy = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label*='Close']")))
            
            #header_description holds the text for the title and description
            header_description = i.text.split("\n")
            item_title = header_description[0]

            #if there is a description pull it, otherwise no description
            try:
                item_description = header_description[1]
            except:
                item_description = ""
            # header_description = driver.find_elements_by_css_selector("span[overflow='normal'][display='block']")
            # item_title = header_description[0].text
            # item_description = header_description[1].text
            close = driver.find_element_by_css_selector("button[aria-label*='Close']")

            #if the item has already been loaded, don't load it again (Popular Items section)
            if item_title in [i.name for i in self.items]:
                close.click()
                continue

            print("Item Title: " + item_title)
            print("Item Description: " + item_description)
            time.sleep(0.5)
            menu_modal_body = driver.find_element_by_css_selector("div[data-anchor-id='MenuItemModalBody']")
            mgroups = []
            try:
                modifier_groups = menu_modal_body.find_elements_by_css_selector("div[role='group']")
                for group in modifier_groups:
                    modifier_containers = group.find_elements_by_xpath("*")
                    #print([mod.get_attribute("innerHTML") for mod in modifier_containers])
                    group_title_container = modifier_containers.pop(0).find_element_by_css_selector("div").find_elements_by_css_selector("span")
                    group_title = group_title_container[0].text
                    group_number_tag = group_title_container[1].text
                    modifiers = []
                    for div in modifier_containers:
                        #print(div.get_attribute('innerHTML'))
                        modifiers.append(div.find_element_by_css_selector("div").find_element_by_css_selector("span").text)
                    #print("Modifier group: " + group_title)
                    #print("Number tag: " + group_number_tag)
                    # for modifier in modifiers:
                    #     #print(modifier)
                    #     pass
                    mgroups.append(ModifierGroup(group_title, modifiers))
            except NameError:
                print("no modifiers for this item")
            item = Item(item_title, item_description, mgroups)

            #MG object needs to know its parent to generate correct location in getIssues()
            for mgroup in item.modifier_groups:
                mgroup.parent = item
            
            self.items.append(item)
            close = driver.find_element_by_css_selector("button[aria-label*='Close']")
            close.click()
            time.sleep(0.5)
        driver.close()
    def compare(self):
        """Compares the loaded menu with a template (set by the template_menu property) and outputs a list of Issue objects"""
        real_items = self.items.copy()
        template_items = self.template_menu.items.copy()
        real_categories = self.categories.copy()
        template_categories = self.template_menu.categories.copy()
        output = []

        items_to_compare = []

        #compare categories
        to_remove = ["Drinks", "Desserts", "Beverages"]
        for r in to_remove:
            try:
                real_categories.remove(r)
            except:
                pass

        for t_category in template_categories:
            if(t_category not in real_categories):
                output.append(Issue("Category", t_category, t_category + " is missing!"))
        for e_category in real_categories:
            if(e_category not in template_categories):
                output.append(Issue("Category", e_category, "Category " + e_category + " not on template menu"))
        
        if(self.categories[0] != "Bao"):
            output.append(Issue("Category", "Layout", "First category on menu not Bao"))

        #compare lists of items
        for t_item in template_items:
            if(t_item.name in [i.name for i in real_items]):
                real_items[[i.name for i in real_items].index(t_item.name)].template_item = t_item
                items_to_compare.append(real_items[[i.name for i in real_items].index(t_item.name)])
            else:
                output.append(Issue("Item", t_item.name, t_item.name + " is missing!"))
        for r_item in real_items:
            if(r_item.name not in [i.name for i in items_to_compare]):
                output.append(Issue("Item", r_item.name, "Extraneous item " + r_item.name + " found"))
        
        print("Comparing " + str(len(items_to_compare)) + " items")

        #compare each item
        #TODO: make this use inheritance and polymorphism and all that jazz to not fucking suck lol
        # for item in items_to_compare:
        #     if(item.modifier_groups and item.template_item.modifier_groups):
        #         for i in range(min(len(item.modifier_groups), len(item.template_item.modifier_groups))):
        #             item.modifier_groups[i].template_group = item.template_item.modifier_groups[i]
        for item in items_to_compare:
            output.extend(item.getIssues())

        
        issues = output
        
        return output
    
    



        
            