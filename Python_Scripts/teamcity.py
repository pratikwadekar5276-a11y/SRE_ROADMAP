from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Edge()
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    # १. लॉगिन
    driver.get("http://localhost:8111/login.html")
    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("admin")
    driver.find_element(By.NAME, "submitLogin").click()
    time.sleep(3)
    
    # २. थेट बिल्ड कॉन्फिगरेशनच्या URL वर जा
    driver.get("http://localhost:8111/buildConfiguration/Pythonautomation_JsonValidator")
    time.sleep(3)
    
    # ३. 'Run custom build' उघडणे
    custom_run = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Run custom build')]")))
    custom_run.click()
    time.sleep(3)
    
    # ४. पॅरामीटर्स सेट करणे
    tenant_field = wait.until(EC.visibility_of_element_located((By.NAME, "prop:tenant")))
    tenant_field.clear()
    tenant_field.send_keys("pfizer-a")
    time.sleep(3)
    
    env_field = driver.find_element(By.NAME, "prop:env")
    env_field.clear()
    env_field.send_keys("stg")
    time.sleep(3)
    
    # ५. बिल्ड रन करणे
    driver.find_element(By.NAME, "runBuild").click()
    
    print("Build triggered successfully via direct URL!")
    time.sleep(5)

finally:
    driver.quit()