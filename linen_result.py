import unittest, json, sys, yaml
from unittest.result import failfast

class LinenResult(unittest.TestResult):

    truncation_threshold = 255

    def printErrors(self):
        tmp = self.failures + self.errors
        if tmp:
            
            testcase = tmp[0][0]
            failures = [x[1] for x in self.failures]
            errors = [x[1] for x in self.errors]

            value = {}
            if failures:
                value["failures"] = failures
            if errors:
                value["errors"] = errors
            
            report = {
                "title": "%s: %s" %(
                    getattr(testcase, "printable_url", "Unknown error"),
                    getattr(testcase, "session_id", None)
                ),
                "value": json.dumps(value, indent=4)
            }
            
            print(json.dumps(report), file=sys.stdout)


    @failfast
    def addFailure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        #self.failures.append((test, self._exc_info_to_string(str(err), test)))
        self.failures.append((test, str(err[1])))
        self._mirrorOutput = True

    @failfast
    def addError(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        """
        self.errors.append((test, self.truncated_str(str(err[1]))))
        self._mirrorOutput = True

    def truncated_str(self, str):
        if len(str) > self.truncation_threshold:
            return "%s..." % str[:self.truncation_threshold]
        return str
