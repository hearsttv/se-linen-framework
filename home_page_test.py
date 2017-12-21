import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class HomePageTest(unittest.TestCase):

    # def __init__(self, *args, **kwargs):
    #     super(HomePageTest, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        #create a new firefox session
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(30)
        cls.driver.maximize_window()

        #navigate to application home page
        cls.driver.get("http://www.google.com")
        

    def test_search_box(self):
        #check search box exists on home page
        self.assertTrue(self.is_element_present(By.NAME, "q"))

    def test_language_settings(self):
        #check language options on home page
        self.assertTrue(self.is_element_present(By.ID, "_eEe"))

    def test_images_link(self):
        #check images link on home page
        images_link = self.driver.find_element_by_link_text("Images")
        images_link.click()
        
        #check search field exists on images page
        self.assertTrue(self.is_element_present(By.NAME, "q"))
        self.search_field = self.driver.find_element_by_name("q")

        self.search_field.send_keys("Selenium WebDriver frame architecture diagram")
        self.search_field.submit()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True
        

if __name__ == '__main__':
    unittest.main(verbosity=2)