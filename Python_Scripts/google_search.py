from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Safari()

driver.get("https://www.google.com")

search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("LinkedIn")
search_box.send_keys(Keys.RETURN)

input("Press Enter to exit...")
driver.quit()