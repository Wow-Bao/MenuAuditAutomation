from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

class Item:
    def __init__(self, name, description, modifier_groups):
        self.name = name
        self.description = description
        self.modifier_groups = modifier_groups
        self.template_item = None
    def addModifierGroup(self, group):
        self.modifier_groups.append(group)
    def getIssues(self):
        output = []
        if(self.description != self.template_item.description):
            output.append(Issue("Item", self.template_item.name, "Incorrect description"))
            
        if(len(self.modifier_groups) > len(self.template_item.modifier_groups)):
            output.append(Issue("Item", self.template_item.name, "Too many modifier groups"))
        elif(len(self.modifier_groups) < len(self.template_item.modifier_groups)):
            output.append(Issue("Item", self.template_item.name, "Too few modifier groups"))    
        else:
            for i in range(0, len(self.modifier_groups)):
                if(self.modifier_groups[i].getIssues(self.template_item.modifier_groups[i])):
                    output.append(self.modifier_groups[i].getIssues(self.template_item.modifier_groups[i]))
        return output

class ModifierGroup:
    def __init__(self, name, modifiers):
        self.name = name
        self.modifiers = modifiers
        self.template_group = None
    def addModifier(self, modifier):
        self.modifiers.append(modifier)
    def getIssues(self, template_group):
        self.template_group = template_group
        output = []
        if(self.name != self.template_group.name):
            output.append(Issue("Modifier Group", self.template_group.name, "Name does not match template"))
            
        if(len(self.modifiers) != len(self.template_group.modifiers)):
            output.append(Issue("Modifier Group", self.template_group.name, "Incorrect number of modifiers within modifier group - either missing or too many modifiers"))
        else:
            o=[]
            if(self.modifiers != self.template_group.modifiers):
                for i in range(0, len(self.modifiers)):
                    if(self.modifiers.sort()[i] != self.template_group.modifiers.sort()[i]):
                        o.append(Issue("Modifier", self.template_group.name, "Menu lists modifier as " + self.modifiers.sort()[i] + " instead of " + self.template_group.modifiers.sort()[i] + "\n"))
                if(not o):
                    o = Issue("Modifier Group", self.template_group.name, "Modifiers scrambled within modifier group - adjust order of modifiers to match template")
            output.append(o)
        return output

class Issue:
    def __init__(self, level, location, body):
        self.level = level
        self.location = location
        self.body = body
    def output(self):
        return self.level + " - " + self.location + " - " + self.body

class Menu:
    def __init__(self, address, template_menu):
        self.items = []
        self.categories = []
        self.address = address
        self.template_menu = template_menu
        self.issues = []
    def loadItems(self, deep_link):
        """Scrapes DoorDash menu page for all the necessary data and loads it into Item and ModifierGroup objects within the Menu object"""
        driver = webdriver.Chrome(executable_path="C:/Users/creek/Desktop/ChromeDriver/chromedriver.exe")
        driver.get("https://www.doordash.com/?newUser=false")
        time.sleep(3)
        elem = driver.find_element_by_css_selector("input")
        elem.clear()
        elem.send_keys(self.address)
        time.sleep(0.5)
        elem.send_keys(Keys.ENTER)
        time.sleep(1)
        driver.get(deep_link)
        time.sleep(1.5)

        #Load categories
        category_list = driver.find_elements_by_css_selector("h2[data-category-scroll-selector]")
        category_texts = [e.text for e in category_list]
        self.categories = category_texts
        print(self.categories)

        #Load items
        #items are located by searching rectangular buttons
        item_button_list = driver.find_elements_by_css_selector("button[shape='Rectangle']")
        actions = ActionChains(driver)
        actions2 = ActionChains(driver)
        for i in item_button_list:
            actions.move_to_element(i).perform()
            i.click()
            time.sleep(2)
            header_description = driver.find_elements_by_css_selector("span[overflow='normal']")
            item_title = header_description[0].find_element_by_css_selector("span").text
            item_description = header_description[1].text
            print("Item Title: " + item_title)
            print("Item Description: " + item_description)
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
                    print("Modifier group: " + group_title)
                    print("Number tag: " + group_number_tag)
                    for modifier in modifiers:
                        print(modifier)
                    mgroups.append(ModifierGroup(group_title, modifiers))
            except NameError:
                print("no modifiers for this item")
            self.items.append(Item(item_title, item_description, mgroups))
            close = driver.find_element_by_css_selector("button[aria-label*='Close']")
            close.click()
            time.sleep(1)
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
            if(t_category in real_categories):
                output.append(Issue("Category", t_category, t_category + " is missing!"))
        for extra_category in real_categories:
            output.append(Issue("Category", extra_category, "Category " + extra_category + " not on template menu"))

        #compare lists of items
        for t_item in template_items:
            if(t_item.name in [i.name for i in real_items]):
                real_items[[i.name for i in real_items].index(t_item.name)].template_item = t_item
                items_to_compare.append(real_items[[i.name for i in real_items].index(t_item.name)])
            else:
                output.append(Issue("Item", t_item.name, t_item.name + " is missing!"))
        for r_item in real_items:
            if(r_item not in items_to_compare):
                output.append(Issue("Item", r_item.name, "Extraneous item " + r_item.name + " found"))
        
        print("Comparing " + str(len(items_to_compare)) + " items")

        #compare each item
        #TODO: make this use inheritance and polymorphism and all that jazz to not fucking suck lol
        for item in items_to_compare:
            for i in range(len(item.modifier_groups)):
                item.modifier_groups[i].template_group = item.template_item.modifier_groups[i]
        for item in items_to_compare:
            output.append(item.getIssues())

        
        issues = output
        return output
    
    



        
            