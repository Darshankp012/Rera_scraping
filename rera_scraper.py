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

project_links = driver.find_elements(By.XPATH, '//a[contains(text(), "View Details")]')
total_projects = min(len(project_links), 6)

if total_projects == 0:
    print("No projects found")
    driver.quit()
    exit()

data = []

for i in range(total_projects):
    print("Scraping", i + 1)

    project_links = driver.find_elements(By.XPATH, '//a[contains(text(), "View Details")]')

    driver.execute_script("arguments[0].scrollIntoView(true);", project_links[i])
    time.sleep(1)
    driver.execute_script("arguments[0].click();", project_links[i])

    def wait_for_detail_page(d):
        return "project-details" in d.current_url.lower()

    WebDriverWait(driver, 10).until(wait_for_detail_page)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    def get_value(name):
        tag = soup.find(string=name)
        if tag:
            return tag.find_next().text.strip()
        else:
            return "Not Available"

    reg_no = get_value("RERA Regd. No.")
    proj_name = get_value("Project Name")

    promoter = "Not Available"
    address = "Not Available"
    gst = "Not Available"

    try:
        prom = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Promoter Details"))
        )
        prom.click()
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        promoter = get_value("Company Name")
        address = get_value("Registered Office Address")
        gst = get_value("GST No.")
    except Exception as e:
        print("Error getting promoter details:", e)

    data.append({
        "RERA Regd. No": reg_no,
        "Project Name": proj_name,
        "Promoter Name": promoter,
        "Registered Office Address": address,
        "GST No.": gst
    })

    driver.back()
    time.sleep(2)

driver.quit()

with open("projects.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print("Saved to CSV")
