from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Edge ब्राउझर सुरू करा
driver = webdriver.Edge()

try:
    # १. गुगलवर जा
    driver.get("https://www.google.com")
    time.sleep(2)

    # २. सर्च बार शोधणे (गुगलच्या सर्च बारसाठी 'q' हे नाव असते)
    search_box = driver.find_element(By.NAME, "q")
    
    # ३. 'Gemini' सर्च करणे
    search_box.send_keys("Gemini")
    search_box.send_keys(Keys.ENTER)
    time.sleep(3) # रिझल्ट लोड होण्यासाठी थोडा वेळ

    # ४. आता Gemini ची लिंक शोधून त्यावर क्लिक करा (किंवा थेट Gemini च्या URL वर जा)
    # थेट URL वर जाणे अधिक सोपे आहे:
    driver.get("https://gemini.google.com/")
    time.sleep(5) # लोड होण्यासाठी वेळ द्या

    # ५. आता तिथे 'shutil module' बद्दल सर्च करा
    # (टीप: इथले XPATH वेबपेजच्या स्ट्रक्चरवर अवलंबून असते)
    prompt_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
    prompt_box.send_keys("Tell me about Python shutil module")
    prompt_box.send_keys(Keys.ENTER)

    input("Press Enter to close the browser...")

finally:
    driver.quit()