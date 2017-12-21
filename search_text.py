import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class SearchText(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #create a new firefox session
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(30)
        cls.driver.maximize_window()

        #navigate to application home page
        cls.driver.get("http://www.google.com")
        

    def test_search_by_text(self):
        self.search_field = self.driver.find_element_by_name("q")

        self.search_field.send_keys("Selenium WebDriver Interview questions")
        self.search_field.submit()

        lists = self.driver.find_elements_by_class_name("r")
        #no = len(lists)
        self.assertEqual(11, len(lists))

    def test_search_by_name(self):
        self.search_field = self.driver.find_element_by_name("q")
        self.search_field.send_keys("Python class")
        self.search_field.submit()
        list_new = self.driver.find_elements_by_class_name("r")
        self.assertEqual(11, len(list_new))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        

if __name__ == '__main__':
    unittest.main(verbosity=2)