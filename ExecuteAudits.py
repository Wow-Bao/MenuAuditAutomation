from MenuAuditmator import Menu, Issue
from TemplateMenuBuilder import BuildMenuTemplate
import pandas as pd

# input_deep_link = sys.argv[1]

infile = "C:/Users/creek/Desktop/WowBaoScripts/MenuAuditAutomation/SomeLocations.csv"
outfile = "C:/Users/creek/Desktop/WowBaoScripts/MenuAuditAutomation/AuditOutput.csv"
def audit(address, deep_link, isCheeseburgerBao, isCoconutBao, isEggSausageBao, isIMPOSSIBLEBao, isBundles, isPotDumpCombined):
    menu = Menu(address, None)
    temp = BuildMenuTemplate('C:/Users/creek/Desktop/WowBaoScripts/MenuAuditAutomation/MenuReference.json', isCheeseburgerBao, isCoconutBao, isEggSausageBao, isIMPOSSIBLEBao, isBundles, isPotDumpCombined)

    menu.loadItems(deep_link)

    menu.template_menu = temp

    return menu.compare()

def writeIssues(issues):
    output = ""
    for issue in issues:
        output = output + issue.output() + "\n"
    return output

locations = pd.read_csv(infile)
rows = []

for location in locations.iterrows():
    try:
        address = location[1]["Store Address"] + " " + location[1]["Store City"] + " " + location[1]["Store State"] + " " + str(location[1]["Store Zip"])
        issues = audit(address, location[1]["DD Deep Link"])
        dict = {
            'Opportunity ID':location[1]["Opportunity ID"],
            'Opportunity Name':location[1]["Opportunity Name"],
            'DD Category Issues':writeIssues([i for i in issues if i.level=="Category"]),
            'DD Item Issues':writeIssues([i for i in issues if i.level=="Item"]),
            'DD Modifier Group Issues':writeIssues([i for i in issues if i.level=="Modifier Group"]),
            'DD Modifier Issues':writeIssues([i for i in issues if i.level=="Modifier"])
        }
        rows.append(dict)
        print("successfully audited " + location[1]["Opportunity Name"] + ": found " + str(len(issues)) + " issues")
    except:
        print("exception while auditing " + location[1]["Opportunity Name"])

df_output = pd.DataFrame(rows)

df_output.to_csv("auditOutput.csv")
