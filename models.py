from django.db import models
from .hipergator_storage import HiPerGatorStorage


class Status(models.Model):
    update_date = models.DateTimeField(auto_now=True)

class Course(models.Model):
    lms_id = models.CharField(max_length=20)

    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Course {self.lms_id}'


class Person(models.Model):
    lms_id = models.CharField(max_length=20)

    def __str__(self):
        return f'Person {self.lms_id}'


class Assignment(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lms_id = models.CharField(max_length=20, blank=True)

    enabled = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    restricted_functions = models.CharField(max_length=200, blank=True, default='')
    assignment_group_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.name} (Course {self.course})'

    def task_list(self):
        return self.task_set.all()

    def export_dict(self):
        return {
            'name': self.name,
            'restricted_functions': self.restricted_functions,
            'tasks': [task.export_dict() for task in self.task_set.all()],
        }


def task_filename_function(task, filename):
    return f'uploads/solutions/{task.assignment.id}/{task.id}_{filename}'


def task_resource_function(task, filename):
    return f'uploads/solutions/{task.assignment.id}/{task.id}_{filename}'


class Task(models.Model):

    def __str__(self):
        return f'{self.assignment} (Course {self.assignment.course}): {self.name}'

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    correct_program = models.FileField(upload_to=task_resource_function, blank=True)


    name = models.CharField(max_length=20)

    language = models.CharField(max_length=20, choices=[
        ('python3', 'Python3'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('matlab', 'MATLAB')
    ])

    # startswith, endswith, contains, matches regex
    filename_match_function = models.CharField(max_length=20, choices=[
        ('startswith', 'Starts with'),
        ('endswith', 'Ends with'),
        ('contains', 'Contains'),
        ('matches', 'Matches regex'),
    ])

    # Lab3.m
    filename_match_pattern = models.CharField(max_length=65)

    # Capabilities
    lenient_whitespace = models.BooleanField(default=False)
    ignore_whitespace = models.BooleanField(default=False)
    ignore_case = models.BooleanField(default=False)
    ignore_numerical = models.BooleanField(default=False)
    ignore_alphabetical = models.BooleanField(default=False)
    ignore_punctuation = models.BooleanField(default=False)

    restricted_functions = models.CharField(max_length=200, blank=True, default='')

    preprocess_function = models.CharField(max_length=200, blank=True, default='')

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def testcase_list(self):
        return self.testcase_set.all()

    def export_dict(self):
        return {
            # 'correct_program': self.correct_program,
            # 'task_resources': self.task_resources,
            'name': self.name,
            'language': self.language,
            'filename_match_function': self.filename_match_function,
            'filename_match_pattern': self.filename_match_pattern,
            # 'driver_file': self.driver_file,
            'ignore_case': self.ignore_case,
            'testcases': [testcase.export_dict() for testcase in self.testcase_set.all()],
        }


def testcase_input_resource_function(testcase, filename):
    course_id = testcase.task.assignment.course.id
    assignment_id = testcase.task.assignment.id
    return f'uploads/{course_id}/{assignment_id}/{testcase.id}/inputs/{filename}'


def testcase_output_resource_function(testcase, filename):
    course_id = testcase.task.assignment.course.id
    assignment_id = testcase.task.assignment.id
    return f'uploads/{course_id}/{assignment_id}/{testcase.id}/outputs/{filename}'


class TestCase(models.Model):

    def __str__(self):
        return f'{self.task}: {self.description} {"HIDDEN" if self.hidden else ""}'

    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    restricted_functions = models.CharField(max_length=200, blank=True, default='')

    # Tokenization
    stdin = models.CharField(max_length=1_000_000, blank=True)

    stdout = models.CharField(max_length=1_000_000, blank=True)

    hidden = models.BooleanField(default=False)

    hint = models.CharField(max_length=200, blank=True, default='')

    description = models.CharField(max_length=1000)

    rng_seed = models.PositiveIntegerField(blank=True, null=True)

    def export_dict(self):
        return {
            # 'input_resource_files': self.input_resource_files,
            # 'output_resource_files': self.output_resource_files,
            'stdin': self.stdin,
            'stdout': self.stdout,
            'hidden': self.hidden,
            'hint': self.hint,
        }


class Submission(models.Model):

    def __str__(self):
        return f'{self.assignment}: {self.student} submission #{self.attempt} (Course {self.course})'

    lms_id = models.CharField(max_length=20, db_index=True)

    submitted_at = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    assignment = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING)
    student = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    attempt = models.IntegerField()

    class Meta:
        unique_together = ('lms_id', 'attempt')


class TestcaseResult(models.Model):
    testcase = models.ForeignKey(TestCase, blank=True, on_delete=models.SET_NULL, null=True)

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    status = models.CharField(max_length=50, choices=[
        ('Passed', 'Passed'),
        ('Wrong Answer', 'Wrong Answer'),
        ('Rejected', 'Rejected'),
        ('Error', 'Error')
    ])

    program_input = models.CharField(max_length=10_000)
    program_output = models.CharField(max_length=1_000_000)
    program_error = models.CharField(max_length=1_000_000)


class CodeSimilarity(models.Model):
    submission_1 = models.ForeignKey(Submission, on_delete=models.DO_NOTHING, related_name="submission_1")
    similar_code_1 = models.CharField(max_length=50_000)
    percent_similar_1 = models.DecimalField(decimal_places=2, max_digits=4)
    text1 = models.CharField(max_length=50_000)
    filename1 = models.CharField(max_length=60)

    submission_2 = models.ForeignKey(Submission, on_delete=models.DO_NOTHING, related_name="submission_2")
    similar_code_2 = models.CharField(max_length=50_000)
    percent_similar_2 = models.DecimalField(decimal_places=2, max_digits=4)
    text2 = models.CharField(max_length=50_000)
    filename2 = models.CharField(max_length=60)


def resource_filepath_function(resource, filename):
    if resource.task:
        return f'resources/{resource.task.assignment.course.lms_id}/{resource.task.assignment.lms_id}/{"".join([c for c in resource.task.description if c.isalnum()])}/resources/{filename}'
    elif resource.testcase_as_input:
        return f'resources/{resource.testcase_as_input.task.assignment.course.lms_id}/{resource.testcase_as_input.task.assignment.lms_id}/{"".join([c for c in resource.testcase_as_input.task.description if c.isalnum()])}/{"".join([c for c in resource.testcase_as_input.description if c.isalnum()])}/inputs/{filename}'
    elif resource.testcase_as_output:
        return f'resources/{resource.testcase_as_output.task.assignment.course.lms_id}/{resource.testcase_as_output.task.assignment.lms_id}/{"".join([c for c in resource.testcase_as_output.task.description if c.isalnum()])}/{"".join([c for c in resource.testcase_as_output.description if c.isalnum()])}/outputs/{filename}'
    else:
        return f'orphan_resources/{filename}'


class Resource(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True, related_name='task_resources')
    testcase_as_input = models.ForeignKey(TestCase, on_delete=models.CASCADE, blank=True, null=True, related_name='input_resources')
    testcase_as_output = models.ForeignKey(TestCase, on_delete=models.CASCADE, blank=True, null=True, related_name='output_resources')

    file = models.FileField(upload_to=resource_filepath_function)

