import unittest, sys, json, time, math
import linen_result
from selenium import webdriver
from selenium.webdriver.support.color import Color
from functools import wraps

class FooRunner():
    def run(self, test):
        print(test)

def test_main(cls):
    
    suite = unittest.TestLoader().loadTestsFromTestCase(cls)
    cls.suite = suite

    runner = unittest.TextTestRunner(
        resultclass=linen_result.LinenResult,
        verbosity=2
    )

    runner.run(suite)


# def test_main(cls):

#     cls.setUpDriver()
#     for member_name in dir(cls):
#         if member_name.startswith("generate_"):
#             getattr(cls, member_name)()
    
#     unittest.TextTestRunner(
#         resultclass=linen_result.LinenResult,
#         verbosity=2
#     ).run(
#     #FooRunner().run(
#         unittest.TestSuite([
#             unittest.TestLoader().loadTestsFromTestCase(x) for x in [
#                 cls
#             ]
#         ])
#     )

def retryIfException(exception_types, attempts = 10, sleep = 0):
    def deco(f):
        def wrapper(self, *args, attempts=attempts, **kwargs):
            try:
                return f(self, *args,**kwargs)
            except tuple(exception_types) as e:
                attempts -= 1
                print("Caught exception of type %s: %s attempts remaining" % (
                    type(e).__qualname__, attempts
                ), file=sys.stderr)
                if attempts > 0:
                    time.sleep(sleep)
                    return wrapper(self, *args, attempts=attempts, **kwargs)
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
        # cls._generate_driver_dependent_tests()


    # @classmethod
    # def _generate_driver_dependent_tests(cls):
    #     for member_name in dir(cls):
    #         if member_name.startswith("generate_"):
    #             # dynamically generate additional tests
    #             getattr(cls, member_name)()
    #     # clear the old tests out
    #     del cls.suite._tests[:]
    #     # add tests from the current state of the testcase class
    #     cls.suite.addTests(
    #         unittest.TestLoader().loadTestsFromTestCase(cls)
    #     )
        
        
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
    
    #selenium utility methods
    #takes a selector, returns a web element
    def find_el(self, selector, context = None):
        if type(selector) != str:
            return selector

        return (context or self.driver).find_element_by_css_selector(selector)

    def assert_el_relative_to_container(self, container_sel, position, el_sel, assert_text):
        container = self.find_el(container_sel)
        container_halfway = container.location.get("x") + math.ceil(container.size.get("width") / 2)

        element = self.find_el(el_sel)
        element_left_x = element.location.get("x")

        if position == "left":
            comparison_element = el_right_x = element_left_x + element.size.get("width")
            result = comparison_element <= container_halfway

        if position == "right":
            comparison_element = element_left_x
            result = comparison_element >= container_halfway

        assert result, assert_text % (container_halfway, comparison_element)


    def el_attr_equals(self, selector, attr, expected, pipe = lambda x: x):
        el = self.find_el(selector)
        el_val = el.get_attribute(attr)
        val = pipe(el_val)
        return val == expected, val

    #returns a css property
    def get_el_css_property(self, selector, property, pipe = lambda x: x):
        el = self.find_el(selector)
        el_prop = el.value_of_css_property(property)
        return pipe(el_prop)

    #checks css property against a value
    def el_property_equals(self, selector, property, expected, pipe = lambda x: x):
        prop = self.get_el_css_property(selector, property, pipe)
        return prop == expected, prop

    #checks css property against a list
    def el_property_in(self, selector, property, expected, pipe = lambda x: x):
        prop = self.get_el_css_property(selector, property, pipe)
        return prop in expected, prop

    @staticmethod
    def to_hex(color):
        return Color.from_string(color).hex
    
    #because values returned are context specific, for clarity, we have broken into 
    #4 distinct methods
    def el_below_el(self, top_sel, bottom_sel):
        top_el = self.find_el(top_sel)
        bottom_el = self.find_el(bottom_sel)

        top_el_lower_y = top_el.location.get("y") + top_el.size.get("height")
        bottom_el_upper_y = bottom_el.location.get("y")

        result = bottom_el_upper_y >= top_el_lower_y
        return result, top_el_lower_y, bottom_el_upper_y


    def el_above_el(self, top_sel, bottom_sel):
        top_el = self.find_el(top_sel)
        bottom_el = self.find_el(bottom_sel)

        top_el_lower_y = top_el.location.get("y") + top_el.size.get("height")
        bottom_el_upper_y = bottom_el.location.get("y")

        result =  top_el_lower_y <= bottom_el_upper_y
        return result, top_el_lower_y, bottom_el_upper_y


    def el_left_of_el(self, left_sel, right_sel):
        left_el = self.find_el(left_sel)
        right_el = self.find_el(right_sel)

        left_el_right_x = left_el.location.get("x") + left_el.size.get("width")
        right_el_left_x = right_el.location.get("x")

        result = left_el_right_x <= right_el_left_x
        return result, left_el_right_x, right_el_left_x


    def el_right_of_el(self, left_sel, right_sel):
        left_el = self.find_el(left_sel)
        right_el = self.find_el(right_sel)

        left_el_right_x = left_el.location.get("x") + left_el.size.get("width")
        right_el_left_x = right_el.location.get("x")

        result =  right_el_left_x >= left_el_right_x
        return result, left_el_right_x, right_el_left_x

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
