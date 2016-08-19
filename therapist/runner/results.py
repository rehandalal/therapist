from xml.etree import ElementTree

from therapist.printer import BOLD, RED, stylize
from therapist.runner.actions import Action
from therapist.runner.collections import Collection


class Result(object):
    SUCCESS = 0
    FAILURE = 1
    SKIP = 2
    ERROR = 3

    def __init__(self, action, status=SKIP, output=None, error=None, execution_time=0.0):
        self._action = None
        self.action = action
        self.status = status
        self.output = output
        self.error = error
        self.execution_time = execution_time

    def __str__(self):
        if self.is_success:
            return 'SUCCESS'
        elif self.is_failure:
            return 'FAILURE'
        elif self.is_skip:
            return 'SKIP'
        else:
            return 'ERROR'

    def __repr__(self):
        return '<Result {}>'.format(self.action)

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        if not isinstance(value, Action):
            raise TypeError('Expected an `Action` object.')
        self._action = value

    @property
    def is_success(self):
        return self.status == self.SUCCESS

    @property
    def is_failure(self):
        return self.status == self.FAILURE

    @property
    def is_skip(self):
        return self.status == self.SKIP

    @property
    def is_error(self):
        return self.status == self.ERROR


class ResultCollection(Collection):
    class Meta:
        object_class = Result

    @property
    def has_success(self):
        for result in self.objects:
            if result.is_success:
                return True
        return False

    @property
    def has_failure(self):
        for result in self.objects:
            if result.is_failure:
                return True
        return False

    @property
    def has_skip(self):
        for result in self.objects:
            if result.is_skip:
                return True
        return False

    @property
    def has_error(self):
        for result in self.objects:
            if result.is_error:
                return True
        return False

    @property
    def execution_time(self):
        execution_time = 0
        for result in self.objects:
            execution_time += result.execution_time
        return execution_time

    def count(self, status=None):
        if status:
            count = 0
            for result in self.objects:
                if result.status == status:
                    count += 1
            return count
        return len(self.objects)

    def dump(self, colors=False):
        """Returns the results in string format."""
        def _(msg, styles=()):
            if colors:
                msg = stylize(msg, styles)
            return msg

        text = ''
        for result in self.objects:
            if result.is_failure or result.is_error:
                text += _('{}\n'.format(''.ljust(79, '=')), (RED, BOLD,))

                status = 'FAILED' if result.is_failure else 'ERROR'
                text += _('{}: {}\n'.format(status, result.action), (RED, BOLD,))

                text += _('{}\n'.format(''.ljust(79, '=')), (RED, BOLD,))

                if result.error:
                    text += _(result.error)
                else:
                    text += _(result.output)
        return text

    def dump_junit(self):
        """Returns a string containing XML mapped to the JUnit schema."""
        testsuites = ElementTree.Element('testsuites', name='therapist', time=str(round(self.execution_time, 2)),
                                         tests=str(self.count()), failures=str(self.count(Result.FAILURE)),
                                         errors=str(self.count(Result.ERROR)))

        for result in self.objects:
            failures = '1' if result.is_failure else '0'
            errors = '1' if result.is_error else '0'

            testsuite = ElementTree.SubElement(testsuites, 'testsuite', id=result.action.name,
                                               name=str(result.action), time=str(round(result.execution_time, 2)),
                                               tests='1', failures=failures, errors=errors)

            testcase = ElementTree.SubElement(testsuite, 'testcase', time=str(round(result.execution_time, 2)))
            testcase.attrib['name'] = result.action.run if result.action.run else result.action.name

            if result.is_failure or result.is_error:
                if result.is_failure:
                    element = ElementTree.SubElement(testcase, 'failure', type='failure')
                else:
                    element = ElementTree.SubElement(testcase, 'error', type='error')

                if result.error:
                    element.text = result.error
                else:
                    element.text = result.output if result.output else ''

        xmlstr = ElementTree.tostring(testsuites, encoding='utf-8').decode('utf-8')
        return '<?xml version="1.0" encoding="UTF-8"?>\n{}'.format(xmlstr)
