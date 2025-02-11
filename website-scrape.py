import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# List of province URLs with formatted province names
def format_province_name(url):
    return re.sub(r'[-]', ' ', url.split('/')[-1]).title()

province_urls = [
    "https://municipalities.co.za/provinces/view/1/eastern-cape",
    "https://municipalities.co.za/provinces/view/2/free-state",
    "https://municipalities.co.za/provinces/view/3/gauteng",
    "https://municipalities.co.za/provinces/view/4/kwazulu-natal",
    "https://municipalities.co.za/provinces/view/5/limpopo",
    "https://municipalities.co.za/provinces/view/6/mpumalanga",
    "https://municipalities.co.za/provinces/view/7/north-west",
    "https://municipalities.co.za/provinces/view/8/northern-cape",
    "https://municipalities.co.za/provinces/view/9/western-cape"
]

# Set up Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--enable-logging")
options.add_argument("--v=1")

# Set the ChromeDriver path
service = Service("/usr/bin/chromedriver")

# Start the WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Open CSV file for writing
with open("municipalities.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Province", "Municipality", "City"])

    # Iterate through each province URL
    for url in province_urls:
        province_name = format_province_name(url)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        def get_table_rows():
            table = driver.find_element(By.TAG_NAME, "table")
            return table.find_elements(By.TAG_NAME, "tr")

        try:
            rows = get_table_rows()
            for i in range(1, len(rows)):  # Skip header row
                try:
                    rows = get_table_rows()
                    cols = rows[i].find_elements(By.TAG_NAME, "td")
                    if cols:
                        municipality_link = cols[0].find_element(By.TAG_NAME, "a")
                        municipality_name = municipality_link.text

                        if "Metropolitan" in municipality_name or "District" in municipality_name:
                            municipality_link.click()

                            try:
                                cities_paragraph = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//p[contains(., 'Cities/Towns:')]"))
                                )
                                cities_text = cities_paragraph.text.replace("Cities/Towns:", "").strip()
                                cities = [city.strip() for city in cities_text.split(",")]

                                for city in cities:
                                    writer.writerow([province_name, municipality_name, city])
                            except Exception as e:
                                print(f"Error extracting cities for {municipality_name}: {e}")
                            
                            driver.back()
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                except Exception as e:
                    print(f"Error processing row {i}: {e}")
                    continue
        except Exception as e:
            print("Error extracting municipality data:", e)

# Close the browser
driver.quit()

print("Data extraction complete. Saved to municipalities.csv.")
