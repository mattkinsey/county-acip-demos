from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from io import StringIO
from urllib.parse import unquote
from pathlib import Path

output_dir = Path.cwd() / 'raw_scrapped_data'
output_dir.mkdir(exist_ok=True)

driver = webdriver.Firefox()
driver.get('https://www.covid19vaccineallocation.org/')

tabs = driver.find_elements_by_class_name('tab')

for tab in tabs:
    if tab.text in ('1 dose', 'ACIP'):
        tab.click()

#reset checkboxes

# go to first state

state_list=driver.find_element_by_id('state-dd')
state_list.click()
tmp=driver.find_element_by_class_name('Select-input')
tmp.send_keys(Keys.HOME)
tmp.send_keys(Keys.ENTER)

#unclick checkboxes
inputs = driver.find_elements_by_css_selector('input')
checks=[]
for inp in inputs:
    if inp.get_attribute('type') == 'checkbox':
        checks.append(inp)
        if inp.is_selected():
            inp.click()
            time.sleep(1)


#iterate states
while True:

    for i,check in enumerate(checks):
        check.click()
        time.sleep(5)
        down = driver.find_element_by_id('data-download-link')
        data = unquote(down.get_attribute('href')[28:])
        state = driver.find_element_by_class_name('Select-value-label').text
        fname = state + '_' + str(i) + '.csv'
        with open(output_dir/fname, 'w') as f:
            f.write(data)
        #embed()
        check.click()

    if state == 'Wyoming': break

    # go to next state
    state_list.click()
    tmp.send_keys(Keys.ARROW_DOWN)
    tmp.send_keys(Keys.ENTER)
    time.sleep(5)

driver.close()
