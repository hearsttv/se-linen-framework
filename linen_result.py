import unittest, json, sys, yaml, traceback
from unittest.result import failfast

debug = False

class LinenResult(unittest.TestResult):

    truncation_threshold = 255


    class Better(yaml.Dumper):
        def increase_indent(self, flow=False, indentless= False):
            return super(LinenResult.Better, self).increase_indent(flow, False)

    def printErrors(self):
        def unique_messages(msgs):
            return list(
                set(
                    [x[1].strip() for x in msgs]
                )
            )

        def as_yaml(title, fields):
            return {
                "title": title,
                "fields": yaml.dump(fields, Dumper=self.Better, allow_unicode=True,
                    default_flow_style=False)
            }

        tmp = self.failures + self.errors
        if tmp:
            
            testcase = tmp[0][0]
            failures = unique_messages(self.failures)
            errors = unique_messages(self.errors)

            title = "%s: %s" %(
                getattr(testcase, "printable_url", str(testcase)),
                getattr(testcase, "session_id", "No session created")
            )
            report = {
                "failures": as_yaml(title, failures),
                "errors": as_yaml(title, errors)
            }

            if debug and errors:
                for error in errors:
                    print(error)
                # Failures not needed because they will be reported as they occur
                # and there's no need for a stacktrace since they're just
                # AssertionErrors
            else:
                print(json.dumps(report), file=sys.stdout)


    def appendToFailures(self, test, err):
        self.failures.append((test, "%s" %(
            str(err[1])
        )))

    @failfast
    def addFailure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        #self.failures.append((test, self._exc_info_to_string(str(err), test)))
        self.appendToFailures(test, err)
        self._mirrorOutput = True
        print(self.err_msg("FAILED", test, err), file=sys.stderr)

    def appendToErrors(self, test, err):
        tb_str = "".join(traceback.format_tb(err[2])) if debug else ""
        self.errors.append((test, "%s\n%s" % (
            self.truncated_str(str(err[1])), tb_str
        )))

    @failfast
    def addError(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        """
        self.appendToErrors(test, err)
        self._mirrorOutput = True
        print(self.err_msg("ERROR", test, err), file=sys.stderr)

    def addSuccess(self, test):
        msg = "%s... %s" % (str(test), "ok")
        print(msg, file=sys.stderr)

    def addSubTest(self, test, subtest, err):
        """Called at the end of a subtest.
        'err' is None if the subtest ended successfully, otherwise it's a
        tuple of values as returned by sys.exc_info().
        """
        if err:
            if isinstance(err[1], AssertionError):
                fail_type = "FAILURE"
                self.appendToFailures(test, err)
            else:
                fail_type = "ERROR"
                self.appendToErrors(test, err)

            result_msg = self.err_msg(fail_type, subtest, err)
        else:
            result_msg = "%s... %s" % (str(subtest), "ok")

        print("%s" % result_msg, file=sys.stderr)
        #super(LinenResult, self).addSubTest(test, subtest, err)

    def err_msg(self, type, test, err):
        return "%s... %s: %s\n    %s" % (
            str(test), type, err[0].__qualname__, str(err[1])
        )

    def truncated_str(self, str):
        if len(str) > self.truncation_threshold:
            return "%s..." % str[:self.truncation_threshold]
        return str
