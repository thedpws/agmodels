from django.db import models
from .canvas import DjangoCanvasStorage


class Status(models.Model):
    update_date = models.DateTimeField(auto_now=True)


class Course(models.Model):
    lms_id = models.CharField(max_length=20)

    name = models.CharField(max_length=100, blank=True, null=True)

    enabled = models.BooleanField(default=True)

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

    message = models.CharField(max_length=100, blank=True)

    has_updated_plagiarism_check = models.BooleanField(default=False)

    language = models.CharField(max_length=20, choices=[
        ('python3', 'Python3'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('matlab', 'MATLAB')
    ])

    # default is invalid for quiz assignments
    grading_strategy = models.CharField(max_length=100, blank=False, default='grade_tasks_passing')

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


def task_resource_function(task, filename):
    return f'{task.assignment.course.lms_id}/solutions/{task.assignment.id}/{task.id}_{filename}'


class Task(models.Model):

    def __str__(self):
        return f'{self.assignment} (Course {self.assignment.course}): {self.name}'

    language = models.CharField(max_length=20, choices=[
        ('python3', 'Python3'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('matlab', 'MATLAB')
    ])

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    correct_program = models.FileField(storage=DjangoCanvasStorage, upload_to=task_resource_function, blank=True)

    name = models.CharField(max_length=20)

    lms_question_id = models.CharField(max_length=20, blank=True, default='')

    points_possible = models.FloatField(blank=True, default=0.0)

    is_manual_grade = models.BooleanField(blank=True, default=False)

    is_extra_credit = models.BooleanField(blank=True, default=False)

    # TODO: WILL DEPRECATE FILENAME-MATCHING VIA THESE FIELDS BELOW. Prefer the SubmissionFile.
    filename_match_function = models.CharField(max_length=20, choices=[
        ('startswith', 'Starts with'),
        ('endswith', 'Ends with'),
        ('contains', 'Contains'),
        ('matches', 'Matches regex'),
    ])
    filename_match_pattern = models.CharField(max_length=65)

    # driver_filename is independent of submission files.
    # It may be a submission file or a provided resource file.
    # The file referred to by this field will be executed at runtime.
    driver_filename = models.ForeignKey('FilenameMatch', on_delete=models.DO_NOTHING, blank=True,
                                        related_name='driver_submission_file', null=True)

    compile_script_filename = models.CharField(max_length=65, blank=True, default=None, null=True)
    execute_script_filename = models.CharField(max_length=65, blank=True, default=None, null=True)

    # Capabilities
    lenient_whitespace = models.BooleanField(default=False)
    ignore_whitespace = models.BooleanField(default=False)
    ignore_case = models.BooleanField(default=False)
    ignore_numerical = models.BooleanField(default=False)
    ignore_alphabetical = models.BooleanField(default=False)
    ignore_punctuation = models.BooleanField(default=False)
    similarity_required = models.FloatField(default=1.00)

    restricted_functions = models.CharField(max_length=200, blank=True, default='')
    mandatory_functions = models.CharField(max_length=200, blank=True, default='')

    preprocess_function = models.CharField(max_length=200, blank=True, default='')
    postprocess_function = models.CharField(max_length=200, blank=True, default='')

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


class FilenameMatch(models.Model):
    """A Utility for matching filenames"""

    # This is blank when used as a driver filename
    task_as_submission_filename = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submission_filenames',
                                                    blank=True, null=True)

    # startswith, endswith, contains, matches regex
    filename_match_function = models.CharField(max_length=20, choices=[
        ('startswith', 'Starts with'),
        ('endswith', 'Ends with'),
        ('contains', 'Contains'),
        ('matches', 'Matches regex'),
    ])

    # Lab3.m
    filename_match_pattern = models.CharField(max_length=65)


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

    insert_code_before = models.CharField(max_length=2000, blank=True, default='')

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


# Deprecated! Prefer { Program, CodeBlock, CodeBlockSimilarity }
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


class Program(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING, null=True, related_name='programs')
    submission = models.ForeignKey(Submission, on_delete=models.DO_NOTHING, null=True, related_name='programs')
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    filename = models.CharField(max_length=100)
    code = models.CharField(max_length=10_000)
    programming_language = models.CharField(max_length=100)


class CodeBlock(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    start_index = models.PositiveIntegerField()
    end_index = models.PositiveIntegerField()

    def get_text(self) -> str:
        return self.program.code[self.start_index:self.end_index]


# Link to Assignment. Don't link to Task. Linking from program to task is not guaranteed (incorrect filename).
# We don't want to limit plagiarism checks to only the valid programs.
class PlagiarismCheck(models.Model):
    performed_at = models.DateTimeField(auto_now_add=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING)


class CodeBlockSimilarity(models.Model):
    code_block_1 = models.ForeignKey(CodeBlock, related_name="code_block_1", on_delete=models.CASCADE)
    code_block_2 = models.ForeignKey(CodeBlock, related_name="code_block_2", on_delete=models.CASCADE)
    plagiarism_check = models.ForeignKey(PlagiarismCheck, related_name="code_block_similarities", on_delete=models.CASCADE)


class SimilarPrograms(models.Model):
    program_1 = models.ForeignKey(Program, related_name="similar_programs", on_delete=models.CASCADE)
    program_2 = models.ForeignKey(Program, on_delete=models.CASCADE)
    program_1_percent_similar = models.FloatField()
    program_2_percent_similar = models.FloatField()
    plagiarism_check = models.ForeignKey(PlagiarismCheck, related_name="program_similarities", on_delete=models.CASCADE)


def resource_filepath_function(resource, filename):

    if resource.task:
        course_id = resource.task.assignment.course.lms_id
        assignment_name = resource.task.assignment.name
        assignment_id = resource.task.assignment.lms_id
        task_name = resource.task.name
        return f'{course_id}/resources/{assignment_name} ({assignment_id})/{task_name}/{filename}'

    elif resource.testcase_as_input:
        c_id = resource.testcase_as_input.task.assignment.course.lms_id
        a_id = resource.testcase_as_input.task.assignment.lms_id
        a_name = resource.testcase_as_input.task.assignment.name
        t_name = resource.testcase_as_input.task.name
        tc_name = resource.testcase_as_input.description
        tc_id = resource.testcase_as_input.id
        return f'{c_id}/resources/{a_name} ({a_id})/{task_name}/{tc_name} ({tc_id})/inputs/{filename}'
    elif resource.testcase_as_output:
        c_id = resource.testcase_as_output.task.assignment.course.lms_id
        a_id = resource.testcase_as_output.task.assignment.lms_id
        a_name = resource.testcase_as_output.task.assignment.name
        t_name = resource.testcase_as_output.task.name
        tc_name = resource.testcase_as_output.description
        tc_id = resource.testcase_as_output.id
        return f'{c_id}/resources/{a_name} ({a_id})/{t_name}/{tc_name} ({tc_id})/outputs/{filename}'
    else:
        raise Exception(f'Orphaned filename {filename}')


class Resource(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True, related_name='task_resources')
    testcase_as_input = models.ForeignKey(
        TestCase,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='input_resources'
    )

    testcase_as_output = models.ForeignKey(
        TestCase,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='output_resources'
    )

    file = models.FileField(storage=DjangoCanvasStorage, upload_to=resource_filepath_function, max_length=500)
