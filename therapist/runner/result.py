import time

from xml.etree import ElementTree

from therapist.collection import Collection
from therapist.process import Process

class Result(object):
    SUCCESS = 0
    FAILURE = 1
    ERROR = 2

    def __init__(self, process, status=None):
        self._process = None
        self.process = process
        self.status = status
        self.output = None
        self.error = None
        self.start_time = time.time()
        self.end_time = self.start_time

    def __str__(self):
        if self.is_success:
            return 'SUCCESS'
        elif self.is_failure:
            return 'FAILURE'
        elif self.is_error:
            return 'ERROR'
        else:
            return 'SKIP'

    def __repr__(self):  # pragma: no cover
        return '<Result {}>'.format(self.process)

    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, value):
        if not (isinstance(value, Process)):
            raise TypeError('Expected a `Process` object.')

        self._process = value

    @property
    def is_success(self):
        return self.status == self.SUCCESS

    @property
    def is_failure(self):
        return self.status == self.FAILURE

    @property
    def is_error(self):
        return self.status == self.ERROR

    @property
    def is_skip(self):
        return not (self.is_success or self.is_failure or self.is_error)

    @property
    def execution_time(self):
        return self.end_time - self.start_time

    def mark_complete(self, status=None, output=None, error=None):
        if status is not None:
            self.status = status
        self.output = output
        self.error = error
        self.end_time = time.time()


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

    def count_skipped(self):
        count = 0
        for result in self.objects:
            if result.status is None:
                count += 1
        return count

    def dump(self):
        """Returns the results in string format."""
        text = ''
        for result in self.objects:
            if result.is_failure or result.is_error:
                text += '\n#{red}#{bright}'
                text += '{}\n'.format(''.ljust(79, '='))

                status = 'FAILED' if result.is_failure else 'ERROR'
                text += '{}: {}\n'.format(status, result.process)
                text += '{}\n'.format(''.ljust(79, '='))

                if result.error:
                    text += '#{{reset_all}}{}'.format(result.error)
                else:
                    text += '#{{reset_all}}{}'.format(result.output)
        return text

    def dump_junit(self):
        """Returns a string containing XML mapped to the JUnit schema."""
        testsuites = ElementTree.Element('testsuites', name='therapist', time=str(round(self.execution_time, 2)),
                                         tests=str(self.count()), failures=str(self.count(Result.FAILURE)),
                                         errors=str(self.count(Result.ERROR)))

        for result in self.objects:
            failures = '1' if result.is_failure else '0'
            errors = '1' if result.is_error else '0'

            testsuite = ElementTree.SubElement(testsuites, 'testsuite', id=result.process.name,
                                               name=str(result.process), time=str(round(result.execution_time, 2)),
                                               tests='1', failures=failures, errors=errors)

            testcase = ElementTree.SubElement(testsuite, 'testcase', time=str(round(result.execution_time, 2)))
            testcase.attrib['name'] = result.process.name

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