# pip install -U selenium
# pip install requests beautifulsoup4
#

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time

#ipaddress="10.59.93.5:944"
#ipaddress="10.59.93.3:935"
ipaddress="10.105.101.4:936"

def show_top10_table_name():

    #browser = webdriver.Firefox()
    browser = webdriver.Chrome()
    browser.get('http://fazbd:fortinet@123@'+ipaddress+'/mem-trackers')

    wait = WebDriverWait(browser, 10)
    element = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/table/thead/tr/th[4]")))

    element.click()
    element.click()

    # locate pagination button
    dropdown_xpath = "/html/body/div[1]/div[3]/div[1]/span[2]/span/button"
    dropdown_element = browser.find_element(By.XPATH, dropdown_xpath)


    # click to open page_num options list of pagination
    dropdown_element.click()

    # wait for a moment to make sure it was expended
    time.sleep(1)

    # select "100"
    option_xpath = "//li[@role='menuitem']/a[text()='100']"
    option_element = browser.find_element(By.XPATH, option_xpath)
    option_element.click()

    # wait for a moment to make sure it was expended
    time.sleep(1)

    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    table_xpath = "table.table:nth-child(2)"
    table = soup.select_one(table_xpath)

    if table:
        # init a dict to save the values behind "tablet-"
        matches = {}

        if table:
            rows = table.find_all('tr')
            for row in rows:
                # the 1st column
                cells = row.find_all('td')
                if cells:
                    first_column = cells[0].text.strip()
                    mem_val = cells[3].text.strip()
                    # check if it is eligible
                    if first_column.startswith("tablet-"):
                        # extract the value behind "tablet-"
                        value = first_column[len("tablet-"):]
                        matches[value]=mem_val
                        # limit 10
                        # if len(matches) >= 10:
                        #    break
        html_trs = ''
        idx = 0
        for tablet_id,mem_value in matches.items():
            idx+=1
            html_trs = html_trs + generate_tablet_info_list(idx, tablet_id, mem_value)

        html_table = """
        <table border="1">
            <tr>
                <th>#</th>
                <th>Tablet ID</th>
                <th>Mem</th>
                <th>Table Name</th>
                <th>Partition</th>
            </tr>
            {}
        </table>
        """.format(html_trs)

        insert_script = f"""
        var newTable = document.createElement('div');
        newTable.innerHTML = `{html_table}`;
        document.body.insertBefore(newTable, document.body.firstChild);
        """

        # excute JavaScript to insert the top
        browser.execute_script(insert_script)

        input("Press Enter to close the browser...")

def generate_tablet_info_list(idx, tablet_id, mem_value):
    url = "http://fazbd:fortinet@123@"+ipaddress+"/tablet?id="+tablet_id  # Such as , 5c6b0055e0e942bd876d11b90f217d0c
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    prefix = "Table "

    tbl_name_ele = soup.find('h3') # remove the prefix: "/html/body/"
    if tbl_name_ele:
        content_tbl_name = tbl_name_ele.text

        if content_tbl_name.startswith(prefix):
            content_tbl_name = content_tbl_name[len(prefix):]
    else:
        content_tbl_name = ""

    part_ele = soup.select_one('table tr:nth-of-type(1) td:nth-of-type(2)')

    if part_ele:
        content_partition = part_ele.text
    else:
        content_partition = ""

    html_tr = """
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
        </tr>
    """.format(idx, tablet_id, mem_value, content_tbl_name, content_partition)

    return html_tr
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    show_top10_table_name()
