import unittest, sys, json, time
import linen_result
from selenium import webdriver
from functools import wraps

class FooRunner():
    def run(self, test):
        print(test)

def test_main(cls):
    unittest.TextTestRunner(
        resultclass=linen_result.LinenResult,
        verbosity=2
    ).run(
    #FooRunner().run(
        unittest.TestSuite([
            unittest.TestLoader().loadTestsFromTestCase(x) for x in [
                cls
            ]
        ])
    )

def retryIfException(exception_types, attempts = 10, sleep = 0):
    class M: pass
    M.attempts = attempts
    def deco(f):
        def wrapper(self, *args, **kwargs):
            try:
                M.attempts -= 1
                return f(self, *args,**kwargs)
            except tuple(exception_types) as e:
                if M.attempts > 0:
                    time.sleep(sleep)
                    return wrapper(self, *args, **kwargs)
                raise e
        return wrapper
    return deco


def skipIfEval(source, reason):
    def deco(f):
        def wrapper(self, *args, **kwargs):
            if eval(source):
                self.skipTest(reason)
            else:
                f(self, *args, **kwargs)
        return wrapper
    return deco

class ConfigurationError(AssertionError):
    pass

class SeDriverTest(unittest.TestCase):

    config = {}
    session_id = None

    @classmethod
    def setUpClass(cls):
        
        if not cls.config:
            raise Exception("Config is empty!")

        cls.printable_url, cls.url = cls.get_urls()
        cls.__qualname__ = "%s: \"%s\"" % (cls.__qualname__, cls.printable_url)
        
        cls.driver = cls.create_driver()
        cls.session_id = cls.driver.session_id
        
        cls.driver.get(cls.url)
        
    @classmethod
    def create_driver(cls):
        if cls.config.get("binary"):
            options = webdriver.ChromeOptions()
            options.binary_location = cls.config.get("binary")
            driver = webdriver.Chrome(
                chrome_options=options,
                desired_capabilities={"loggingPrefs":{"browser":"ALL"}})
        else:
            se_config = json.loads(cls.config.get("se"))

            #se_config["capabilities"]["build"] += " " + str(time.time())

            driver = webdriver.Remote(
                command_executor='http://%s/wd/hub' % (se_config.get("host")),
                desired_capabilities=se_config.get("capabilities"))

        return driver

    @classmethod
    def get_url_maybe_credentials(cls, candidate):
        if cls.config.get("user") and cls.config.get("pass"):
            username = quote(cls.config.get("user"))
            password = quote(cls.config.get("pass"))
            url_parts = candidate.split("//")
            url = url_parts[0] + "//" + ("%s:%s@" % (username, password)) + url_parts[1]
        else:
            url = candidate

        return url

    @classmethod
    def get_urls(cls):
        if cls.config.get("dynamic-url"):
            printable_url = cls.config.get("dynamic-url")
        else:
            printable_url = "http://%s%s" % (cls.config.get("host"), cls.config.get("path"))

        url = cls.get_url_maybe_credentials(printable_url)
        
        return printable_url, url
    
    def find_el(self, selector):
        if type(selector) != str:
            return selector

        return self.driver.find_element_by_css_selector(selector)


    #selenium utility methods
    def assert_el_attr_equals(self, selector, attr, expected, assert_label):
        el = self.find_el(selector)
        el_val = el.get_attribute(attr)
        assert_text = "%s Found \"%s\" instead." % (assert_label, el_val) 
        #self.assertEqual(el_val, expected, assert_text)
        assert el_val == expected, assert_text

    def assert_el_relative_to_el(self, sel1, position, sel2, assert_text):
        el1 = self.find_el(sel1)
        el2 = self.find_el(sel2)


        #el1 is below el2
        if position == "below":
            number1 = el1_top_y = el1.location.get("y")
            number2 = el2_bottom_y = el2.location.get("y") + el2.size.get("height")
            result = el1_top_y > el2_bottom_y

        #el1 is above el2
        if position == "above":
            number1 = el1_bottom_y = el1.location.get("y") + el1.size.get("height")
            number2 = el2_top_y = el2.location.get("y")
            result =  el2_top_y > el1_bottom_y

        #el1 is to the left of el2
        if position == "left":
            number1 = el1_right_x = el1.location.get("x") + el1.size.get("width")
            number2 = el2_left_x = el2.location.get("x")
            result = el1_right_x < el2_left_x

        #el1 is to the right of el2
        if position == "right":
            number1 = el1_left_x = el1.location.get("x") 
            number2 = el2_right_x = el2.location.get("x") + el2.size.get("width")
            result = el1_left_x > el2_right_x
            
        assert result, assert_text % (number1, number2)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
