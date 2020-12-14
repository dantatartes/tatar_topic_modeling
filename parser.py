import csv
import os
import argparse
import logging
import datetime

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC


class NewsParser:
    __slots__ = "main_driver", "main_wait", "page_driver", "page_wait", "writer", "start_link", "start_link_visited"

    def __init__(self,
                 chrome_bin_location: str,
                 chrome_driver_location: str,
                 filename: str,
                 main_link: str,
                 start_link: str,
                 ) -> None:
        ChromeOptions.binary_location = chrome_bin_location

        self.main_driver = Chrome(chrome_driver_location)
        self.main_driver.get(main_link)
        self.main_wait = WebDriverWait(self.main_driver, 120)
        self.main_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.items a")))
        if start_link:
            self.main_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ct-cc-trigger")))
            self.main_driver.find_element_by_css_selector("div.ct-cc-trigger").click()

            now = datetime.datetime.now()
            current_month, current_year = now.month, now.year
            day, month, year = map(int, start_link.split("/")[5].split("-")[:3])
            for i in range((current_year - year)*12 + current_month - month):
                self.main_driver.find_element_by_css_selector("div.ct-cc-control.__left").click()
            self.main_driver.find_element_by_xpath(f'//div[text()="{day}"]').click()
            for i in range(24):
                self.main_driver.find_element_by_css_selector("div.ct-cc-control.__left").click()
            self.main_driver.find_element_by_xpath(f'//div[text()="{day}"]').click()
            self.main_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.items a")))

        self.page_driver = Chrome(chrome_driver_location)
        self.page_wait = WebDriverWait(self.main_driver, 120)

        self.start_link = start_link
        self.start_link_visited = True if start_link == "" else False

        if not os.path.isfile(filename):
            self.writer = csv.writer(open(filename, 'w', encoding="utf-8"))
            self.writer.writerow(['title', 'topic', 'date', 'text'])
        else:
            self.writer = csv.writer(open(filename, 'a', encoding="utf-8"))

    def scroll(self) -> None:
        check_height = self.main_driver.execute_script("return document.body.scrollHeight;")
        self.main_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.main_wait.until(lambda d:
                             self.main_driver.execute_script("return document.body.scrollHeight;") > check_height)

    def parse_and_write(self, last_parsed_index: int) -> int:
        links = list(map(lambda e: e.get_attribute("href"),
                         self.main_driver.find_elements_by_css_selector("div.items a")[last_parsed_index:]))
        original_links_len = len(links)
        if self.start_link in set(links):
            self.start_link_visited = True
            logging.info("Start link found!")
            links = links[links.index(self.start_link):]
        elif self.start_link_visited:
            pass
        else:
            links = []
        for link in links:
            self.page_driver.get(link)
            try:
                self.page_wait.until(lambda d:
                                     self.page_driver.execute_script("return document.readyState;") == 'complete')

                title = self.page_driver.find_element_by_tag_name('h1').text
                text = self.page_driver.find_element_by_css_selector('div.content-block').text
                topic, date = link.split("/")[4:6]
            except (NoSuchElementException, TimeoutException):
                logging.exception("Exception occurred")
                self.page_driver.execute_script("window.stop();")
                self.page_driver.get(link)
                self.page_wait.until(lambda d:
                                     self.page_driver.execute_script("return document.readyState;") == 'complete')
                self.page_driver.implicitly_wait(1)
                title = self.page_driver.find_element_by_tag_name('h1').text
                text = self.page_driver.find_element_by_css_selector('div.content-block').text
                topic, date = link.split("/")[4:6]
            self.writer.writerow([title, topic, date, text])
            logging.info(link)
        return last_parsed_index + original_links_len


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--bin_location', type=str, required=True,
                            help='Chrome binary location')
    arg_parser.add_argument('--driver_location', type=str, required=True,
                            help='Chrome driver location')
    arg_parser.add_argument('--save_to', type=str, default='data.csv',
                            help='where the data will be saved')
    arg_parser.add_argument('--main_link', type=str, default='https://tatar-inform.tatar/news/',
                            help='link to news page')
    arg_parser.add_argument('--start_link', type=str, default='',
                            help='if parameter passed, news will be skipped until visiting this link')
    args = arg_parser.parse_args()

    logging.basicConfig(filename="parser.log", format='%(asctime)s - %(message)s', level=logging.INFO)

    news_parser: NewsParser = NewsParser(
        chrome_bin_location=args.bin_location,
        chrome_driver_location=args.driver_location,
        filename=args.save_to,
        main_link=args.main_link,
        start_link=args.start_link,
    )

    last_index = 0
    while True:
        last_index = news_parser.parse_and_write(last_index)
        news_parser.scroll()
