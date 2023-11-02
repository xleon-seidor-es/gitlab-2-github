import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from config import Secrets as MySecrets
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging


def github_initialize_wiki(organization, repo_name):
    url = f"https://github.com/{organization}/{repo_name}/wiki/_new"

    headers = {'Authorization': 'token %s' % MySecrets.github_token, 'Cookie': 'tz = Europe % 2FMadrid; tz = Europe % 2FMadrid; logged_in = yes; user_session = Kg0LWH9no_X6uK4IO8gwrDDVdy7sELxlwOCANPLGnK1GuUkR; __Host-user_session_same_site = Kg0LWH9no_X6uK4IO8gwrDDVdy7sELxlwOCANPLGnK1GuUkR; _octo = GH1.1.396151676.1695707171; _device_id = 38c1940b497542e7079cb0a470be8f93; color_mode = %7B % 22color_mode % 22 % 3A % 22auto % 22 % 2C % 22light_theme % 22 % 3A % 7B % 22name % 22 % 3A % 22light_colorblind % 22 % 2C % 22color_mode % 22 % 3A % 22light % 22 % 7D % 2C % 22dark_theme % 22 % 3A % 7B % 22name % 22 % 3A % 22dark % 22 % 2C % 22color_mode % 22 % 3A % 22dark % 22 % 7D % 7D; dotcom_user = xleon-seidor-es; has_recent_activity = 1; preferred_color_mode = light; _gh_sess = DQdKnZ % 2Fs4xVq9GmWZ5suZJ0j2Dq472MqOJTfS55cewoIgbZXha73yak8qNKdYSNMkJa % 2B2iJ3l9LaYSm5mO4nnv % 2B7K2PCTXoYG % 2BCjWRFtJ4stHtuV5sYUn6vhF31zFZnjpc % 2BQmNyMX1EilHUdfNYPg2hMBduUWHJ1l2as4vCQ % 2ByjNi % 2Bhm4AuKOgS93msbJkjq80Qp6fVP89f2TQVdGZJOyw1gG8 % 2FsOvvK % 2Bmp % 2Bsf4nXnMDGs2NY % 2F841 % 2Fi6wlfCqmuU5MtqtuWdSXK44Up0VAHug % 2FCb3LHWkRYuEmNT8Q4Ep % 2FC0e0y9wXsT5dfACBlSlVK79 % 2BVVL % 2FG % 2FBtNh18OwbYP73e % 2FiNeR8h % 2BLm7 % 2F4N4Sr8wceRZLmG7hZy76OPzkHSnakrQfdXrUdJ9rc6Ug7XreAxwN4REO3jWRVjJxot6qPIB49skGgESPYvA08JtcTTya6QFxHhbxZQTRQWEX1Sv8mApnVpaveu9VZgAhkOdh4l0jtOfebCzE9qkwrgvTCqn4gCgk5kem9iCCLDPBkq7sJPHVq8pcWTpLgedX5DhsLIfKWtWiRe % 2B2XFL % 2BXznUkInvzjSCcryiCMkKatG8HDfEEdwBwdvdzKS3TXImaarZpSXmr5t8Re1huW9ZhrhI79w1cu--NLFpRjzC3WShdwU9--m2yg % 2FgA9gkDyYpDj9tGdKg % 3D % 3D',
               }
    options = webdriver.ChromeOptions()
    headers_options = webdriver.ChromeOptions()
    #headers_options.add_argument('--headless')
    headers_options.add_argument(f'{headers}"')

    webdriver_path = 'selenium/webdrive/chromedriver'
    driver = webdriver.Chrome(options=headers_options)

    driver.get('https://github.com/login')
    username = MySecrets.github_user
    password = MySecrets.github_user_password

    username_field = WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.ID, "login_field")) )
    password_field = WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.ID, "password")) )

    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    logging.debug("User loged into github, exploring to wiki page")
    
    time.sleep(20)

    driver.get(url)

    driver.implicitly_wait(10)
    title_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gollum-editor-page-title")))
    text_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gollum-editor-body")))
    title_field.send_keys("Migration Page")
    text_field.send_keys("This page was created automatically by the migration script.")
    logging.debug("Creating new wiki page")
    submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gollum-editor-submit")))
    submit_button.click()

    logging.debug("Clossing browser")
    driver.quit()
