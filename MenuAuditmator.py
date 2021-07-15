class Item:
    def __init__(self, name, description, modifier_groups):
        self.name = name
        self.description = description
        self.modifier_groups = modifier_groups
    def addModifierGroup(group):
        modifier_groups.append(group)
    def getIssues(template_item):
        output = []
        if(description != template_item.description):
            output.append(Issue("Item", template_item.name, "Incorrect description"))
            
        if(len(modifier_groups) > len(template_item.modifier_groups)):
            output.append(Issue("Item", template_item.name, "Too many modifier groups"))
        elif(len(self.modifier_groups) < len(template_item.modifier_groups)):
            output.append(Issue("Item", template_item.name, "Too few modifier groups"))
        
        else:
            for i in range(0, len(modifier_groups)):
                if(modifier_groups[i].getIssues(template_item.modifier_groups[i])):
                    output.append(modifier_groups[i].getIssues(template_item.modifier_groups[i]))
        return output

class ModifierGroup:
    def __init__(self, name, modifiers):
        self.name = name
        self.modifiers = modifiers
    def addModifier(modifier):
        modifiers.append(modifier)
    def getIssues(template_group):
        output = []
        if(self.name != template_group.name):
            output.append(Issue("Modifier Group", template_group.name, "Name does not match template"))
            
        if(len(self.modifiers) != len(template_group.modifiers)):
            output.append(Issue("Modifier Group", template_group.name, "Incorrect number of modifiers within modifier group - either missing or too many modifiers"))
        else:
            o=[]
            if(self.modifiers != template_group.modifiers):
                for i in range(0, len(self.modifiers)):
                    if(self.modifiers.sort()[i] != template_group.modifiers.sort()[i]):
                        o.append(Issue("Modifier", template_group.name, "Menu lists modifier as " + self.modifiers.sort()[i] + " instead of " + template_group.modifiers.sort()[i] + "\n"))
                if(not o):
                    o = Issue("Modifier Group", template_group.name, "Modifiers scrambled within modifier group - adjust order of modifiers to match template")
            output.append(o)
        return output

class Issue:
    def __init__(self, level, location, body):
        self.level = level
        self.location = location
        self.body = body
    def output():
        return level + " - " + location + " - " + body
class Menu:
    def __init__(self, deep_link, address):
        self.items = []
        self.categories = []
        self.address = address
    def loadItems(deep_link):
        driver = webdriver.Chrome(executable_path="C:/Users/creek/Desktop/ChromeDriver/chromedriver.exe")
        driver.get("https://www.doordash.com/?newUser=false")
        time.sleep(3)
        elem = driver.find_element_by_css_selector("input")
        elem.clear()
        elem.send_keys(address)
        time.sleep(0.5)
        elem.send_keys(Keys.ENTER)
        time.sleep(0.5)
        driver.get(deep_link)
        time.sleep(1.5)
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
            items.append(Item(item_title, item_description, mgroups))
            close = driver.find_element_by_css_selector("button[aria-label*='Close']")
            close.click()
            time.sleep(1)
    def compare(template_menu):
        real_items = items
        template_items = template_menu.items
        output = []
        for t_item in template_items:
            try:
                real_items.remove(t_item)
            except ValueError:
                output.append(Issue("Item", t_item.name, t_item.name + " is missing!"))
        for extra_item in real_items:
            output.append(Issue("Item", extra_item.name, "Item " + extra_item.name + " not on template menu"))


        
            