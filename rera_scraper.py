from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import time


options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)


driver.get("https://rera.odisha.gov.in/projects/project-list")


WebDriverWait(driver, 15).until(
    EC.presence_of_all_elements_located((By.XPATH, '//a[contains(text(), "View Details")]'))
)


projects = driver.find_elements(By.XPATH, '//a[contains(text(), "View Details")]')
num_projects = min(len(projects), 6)  

if num_projects == 0:
    print("X No projects found. Exiting.")
    driver.quit()
    exit()

project_data = []


for i in range(num_projects):
    print(f"=>  Visiting project {i + 1}")

    
    projects = driver.find_elements(By.XPATH, '//a[contains(text(), "View Details")]')

    
    driver.execute_script("arguments[0].scrollIntoView(true);", projects[i])
    time.sleep(1)
    driver.execute_script("arguments[0].click();", projects[i])

    
    WebDriverWait(driver, 10).until(lambda d: "project-details" in d.current_url.lower())
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    def extract_field(label):
        tag = soup.find(string=label)
        return tag.find_next().text.strip() if tag else "Not Found"

    regd_no = extract_field("RERA Regd. No.")
    project_name = extract_field("Project Name")

    try:
        promoter_tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Promoter Details"))
        )
        promoter_tab.click()
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        promoter = extract_field("Company Name")
        address = extract_field("Registered Office Address")
        gst = extract_field("GST No.")
    except:
        promoter = address = gst = "Not Found"

    project_data.append({
        "RERA Regd. No": regd_no,
        "Project Name": project_name,
        "Promoter Name": promoter,
        "Registered Office Address": address,
        "GST No.": gst
    })

    driver.back()
    time.sleep(2)

driver.quit()


with open("projects.csv", "w", newline='', encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=project_data[0].keys())
    writer.writeheader()
    writer.writerows(project_data)

print("=> Done! Data saved to 'projects.csv'")
