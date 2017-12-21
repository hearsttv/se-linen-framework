#! /usr/bin/env python
import unittest, sys
from home_page_test import HomePageTest
from search_text import SearchText



def test_main(cls):
    unittest.TextTestRunner(verbosity=2).run(
        unittest.TestSuite([
            unittest.TestLoader().loadTestsFromTestCase(x) for x in [
                cls
            ]
        ])
    )

if __name__ == "__main__":
    print(sys.argv)
    cls_name = sys.argv[1]
    cls = locals()[cls_name]
    print(cls)
    print(locals())

    class _LinenTest(cls):
        config = {"site":"wlwt"}

    test_main(_LinenTest)