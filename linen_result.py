import unittest, json, sys, yaml
from unittest.result import failfast

class LinenResult(unittest.TestResult):

    truncation_threshold = 255


    class Better(yaml.Dumper):
        def increase_indent(self, flow=False, indentless= False):
            return super(LinenResult.Better, self).increase_indent(flow, False)

    def printErrors(self):
        tmp = self.failures + self.errors
        if tmp:
            
            def unique_messages(msgs):
                return list(
                    set(
                        [x[1].strip() for x in msgs]
                    )
                )

            testcase = tmp[0][0]
            failures = unique_messages(self.failures)
            errors = unique_messages(self.errors)

            value = {}
            if failures:
                value["failures"] = failures
            if errors:
                value["errors"] = errors
            
            report = {
                "title": "%s: %s" %(
                    getattr(testcase, "printable_url", str(testcase)),
                    getattr(testcase, "session_id", None)
                ),
                "value": yaml.dump(value, Dumper=self.Better,
                    allow_unicode=True, default_flow_style=False)
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
        msg = "%s: %s" % (str(err[0]), str(err[1]))
        self.errors.append((test, self.truncated_str(str(err[1]))))
        self._mirrorOutput = True

    def truncated_str(self, str):
        if len(str) > self.truncation_threshold:
            return "%s..." % str[:self.truncation_threshold]
        return str
