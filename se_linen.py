import unittest, sys

def test_main(cls):
    unittest.TextTestRunner(verbosity=2).run(
        unittest.TestSuite([
            unittest.TestLoader().loadTestsFromTestCase(x) for x in [
                cls
            ]
        ])
    )

