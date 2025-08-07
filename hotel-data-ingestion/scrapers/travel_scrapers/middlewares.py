# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
################################################################################################

# Selenium imports - commented out for GraphQL approach
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from scrapy.http import HtmlResponse
# from selenium.webdriver.common.keys import Keys
# # from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# from datetime import date
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
#################################################################################################

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class BookingSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BookingDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

#########################################################################################################3

# SeleniumMiddleware - Disabled for GraphQL approach
# class SeleniumMiddleware:
#     
#     def __init__(self):
#         chrome_options = Options()
#         chrome_options.add_experimental_option('detach',True)
#         # chrome_service = ChromeService(executable_path='./../chromedriver.exe', chrome_options=chrome_options)
#         self.driver = webdriver.Chrome(options=chrome_options)
#         self.wait = WebDriverWait(self.driver, 5)
#         self.PAUSE_TIME = 5
#         self.DEST = "Jaipur"
# 
#     def process_request(self, request, spider):
#         self.driver.get(request.url)
# 
#         try:
#             self.close_popup()
# 
#             time.sleep(self.PAUSE_TIME)
# 
#             self.fill_details()
#         except:
#             self.close_popup()
# 
#             time.sleep(self.PAUSE_TIME)
# 
#             self.fill_details()
#         
#         self.scroll_to_bottom()
# 
#          # Get the HTML after scrolling
#         body = self.driver.page_source
#         response = HtmlResponse(url=self.driver.current_url, body=body, encoding='utf-8', request=request)
#         return response
#     
# 
#     def close_popup(self):
# 
#         try: 
#             self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Dismiss sign in information."]')))
#             popup_close = self.driver.find_element(By.CSS_SELECTOR,value='button[aria-label="Dismiss sign in information."]')
#             popup_close.click()
#         except TimeoutException as ex:
#             print("Exception has been thrown. " + str(ex))
# 
# 
#     def fill_details(self):
#         '''----------------------Uncomment the lines in this function if you want to enter a custom check-out date------------------------'''
# 
#          # Entering Destination:
#         dest = self.driver.find_element(By.CSS_SELECTOR, value='input[name="ss"]')
#         dest.send_keys(self.DEST, Keys.ENTER)
# 
#         #Calculating today's date:
#         today = date.today().strftime("%d %B %Y")
#         time.sleep(self.PAUSE_TIME)
# 
# 
#         #Picking the check in date:
#         try:
#             self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="searchbox-datepicker-calendar"]')))
#             check_in = self.driver.find_element(By.CSS_SELECTOR, value=f'span[aria-label="{today}"]')
#             check_in.click()
#         except TimeoutException as ex:
#             print("Exception has been thrown:" + str(ex))
# 
#             date_picker = self.driver.find_element(By.CSS_SELECTOR, value='div[data-testid="searchbox-dates-container"]')
#             date_picker.click()
# 
#             self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="searchbox-datepicker-calendar"]')))
#             check_in = self.driver.find_element(By.CSS_SELECTOR, value=f'span[aria-label="{today}"]')
#             check_in.click()
# 
#         # Clicking the search button:
#         time.sleep(self.PAUSE_TIME)
#         search = self.driver.find_element(By.CSS_SELECTOR, value='button[type="submit"]')
#         search.click()
# 
#         
# 
#     def scroll_to_bottom(self):
#         # Scroll to the bottom of the page
#         self.wait.until(EC.presence_of_element_located, 'h1[aria-live="assertive"]')
# 
# 
#         last_height = self.driver.execute_script("return document.body.scrollHeight")
#         scroll = True
#         while scroll:
#             # Scroll down to bottom
#             self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# 
#             # Wait to load page
#             time.sleep(self.PAUSE_TIME)
# 
#             # Calculate new scroll height and compare with last scroll height
#             new_height = self.driver.execute_script("return document.body.scrollHeight")
# 
#             try:
#                 self.wait.until(EC.presence_of_element_located, 'span.ad82e69f7d')
#                 load = self.driver.find_element(By.CSS_SELECTOR, value='button.bf33709ee1.a190bb5f27.b9d0a689f2.bb5314095f.b81c794d25.da4da790cd')
#                 load.click()
#             except NoSuchElementException as ex:
#                 print("Error message: " + str(ex))
#                 
# 
#             if new_height == last_height:
#                 break
#             last_height = new_height
# 
#     def __del__(self): #This function closes the browser automatically after every run
#         self.driver.quit()


class ResponseSaverMiddleware:
    """Middleware to save responses for debugging"""
    
    def process_response(self, request, response, spider):
        # Save the response content for debugging
        if hasattr(spider, 'name') and spider.name == 'booking_spider':
            with open('debug_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            spider.logger.info(f"Saved response to debug_response.html (status: {response.status})")
        return response