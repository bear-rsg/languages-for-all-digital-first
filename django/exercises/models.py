from django.db import models
from account.models import User, UserRole
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator
import random

OPTIONAL_HELP_TEXT = "(Optional)"
OPTIONAL_IF_AUDIO_HELP_TEXT = "Optional if supplying audio instead, otherwise required"
ORDER_HELP_TEXT = OPTIONAL_HELP_TEXT + " Specify the order you'd like this item to appear on the exercise page. Leave blank to order automatically."
AUDIO_HELP_TEXT = OPTIONAL_HELP_TEXT + " <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here"
AUDIO_UPLOAD_PATH = "exercises-exercise-audio"


def text_or_audiomsg(text_field, audio_field):
    """
    Handle automatic message based on if text and/or audio is provided for a given field
    E.g. if no text provided, but audio is, then give instruction for user to click the audio button
    """

    if text_field:
        return text_field
    elif audio_field:
        return "Please play the audio clip"
    else:
        return ""


class YearGroup(models.Model):
    """
    A year group that classes are organised into, e.g. 2022/23, 2023/24, etc.
    """

    name = models.CharField(max_length=255, unique=True)
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    is_published = models.BooleanField(default=False, verbose_name="Published")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'id']


class Language(models.Model):
    """
    A non-English language being taught, e.g. Portuguese, Italian, French
    """

    name = models.CharField(max_length=255, unique=True)
    is_published = models.BooleanField(default=True, verbose_name="Published")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'id']


class Difficulty(models.Model):
    """
    A level of difficulty (e.g. level 1, level 2, ..., level 7, level 8)
    """

    name = models.CharField(max_length=255, unique=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name', 'id']
        verbose_name_plural = 'difficulties'


class SchoolClass(models.Model):
    """
    A class of students and teacher(s) within the School
    """

    year_group = models.ForeignKey(YearGroup, on_delete=models.RESTRICT)
    language = models.ForeignKey(Language, on_delete=models.RESTRICT)
    difficulty = models.ForeignKey(Difficulty, on_delete=models.RESTRICT, blank=True, null=True)
    unique_feature = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="If other classes have the same name as this one because they have the same language, difficulty, and teachers, please specify something unique about this class (e.g. the day of the week its run) to make the class name unique")
    is_published = models.BooleanField(default=True, verbose_name="Published")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    @property
    def name(self):
        # Year Group and Language by default
        name = f"{self.year_group} - {self.language}"
        # Append difficulty (if exists)
        if self.difficulty:
            name += f" ({self.difficulty})"
        # Append unique feature (if exists)
        if self.unique_feature:
            name += f" [{self.unique_feature}]"
        # Append teachers' names (if exists)
        if self.teachers_names:
            name += f" - Taught by {', '.join(self.teachers_names)}"

        return name

    @property
    def students(self):
        """
        Return a queryset of students of this class
        """
        user_role_student = UserRole.objects.get(name='student')
        return User.objects.filter(classes__id=self.id, role=user_role_student)

    @property
    def students_count(self):
        return len(self.students)

    @property
    def teachers(self):
        """
        Return a queryset of teachers of this class
        """
        user_role_teacher = UserRole.objects.get(name='teacher')
        return User.objects.filter(classes__id=self.id, role=user_role_teacher)

    @property
    def teachers_names(self):
        """
        Return a list of names of teachers of this class
        (using the above 'teachers' queryset)
        """
        return [f'{teacher.first_name} {teacher.last_name}' for teacher in self.teachers]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['language', 'difficulty', 'id']
        verbose_name_plural = 'classes'


class Theme(models.Model):
    """
    A theme/section of exercises, e.g. Grammar, Vocabulary
    """

    name = models.CharField(max_length=255, unique=True)
    is_published = models.BooleanField(default=True, verbose_name="Published")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'id']


class ExerciseFormat(models.Model):
    """
    A format/type of exercise, e.g. multiple choice, fill in the blank, etc.
    """

    name = models.CharField(max_length=255, unique=True)
    icon = models.CharField(max_length=255)
    instructions = models.TextField(blank=True, null=True)
    is_marked_automatically_by_system = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True, verbose_name="Published")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'id']


class Exercise(models.Model):
    """
    An exercise/task/game that students complete
    """

    name = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.RESTRICT)
    exercise_format = models.ForeignKey(ExerciseFormat, on_delete=models.RESTRICT)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, blank=True, null=True, help_text=OPTIONAL_HELP_TEXT)
    difficulty = models.ForeignKey(Difficulty, on_delete=models.RESTRICT)
    instructions = models.TextField(blank=True, null=True, help_text=OPTIONAL_HELP_TEXT + " If left blank then the default instructions for this exercise format will be used (suitable for most cases)")
    instructions_image = models.ImageField(upload_to='exercises-exercise-instructions', blank=True, null=True, help_text=OPTIONAL_HELP_TEXT + " Include an image here to illustrate the instructions for the entire exercise. E.g. if all questions relate to this image.")
    is_published = models.BooleanField(default=True, verbose_name="Published")
    owned_by = models.ForeignKey(User, related_name="exercise_owned_by", on_delete=models.SET_NULL, blank=True, null=True, help_text="The only teacher who can manage this exercise")
    created_by = models.ForeignKey(User, related_name="exercise_created_by", on_delete=models.SET_NULL, blank=True, null=True, help_text="The teacher who originally created this exercise")

    @property
    def image_match_label_options(self):
        """
        If this is an ImageMatch exercise:
        Return an ordered list of all labels of image match objects that are used in this exercise
        """
        if self.exercise_format == ExerciseFormat.objects.get(name='Image Match'):
            labels = []
            for image_match_object in ExerciseFormatImageMatch.objects.filter(exercise=self):
                labels.append(image_match_object.label)
            random.shuffle(labels)  # important to mix up order
            return labels

    @property
    def items(self):
        if self.exercise_format.name == "Image Match":
            return ExerciseFormatImageMatch.objects.filter(exercise=self)
        elif self.exercise_format.name == "Multiple Choice":
            return ExerciseFormatMultipleChoice.objects.filter(exercise=self)
        elif self.exercise_format.name == "Sentence Builder":
            return ExerciseFormatSentenceBuilder.objects.filter(exercise=self)
        elif self.exercise_format.name == "Fill in the Blank":
            return ExerciseFormatFillInTheBlank.objects.filter(exercise=self)
        elif self.exercise_format.name == "Translation":
            return ExerciseFormatTranslation.objects.filter(exercise=self)
        elif self.exercise_format.name == "External":
            return ExerciseFormatExternal.objects.filter(exercise=self)
        else:
            return None

    @property
    def items_count(self):
        return self.items.count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'id']


class ExerciseFormatImageMatch(models.Model):
    """
    An individual image match question within an exercise
    """

    exercise = models.ForeignKey(Exercise,
                                 limit_choices_to={'exercise_format__name': "Image Match"},
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)
    image = models.ImageField(upload_to='exercises-exerciseformat-imagematch')
    label = models.CharField(max_length=255)
    label_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True)
    # no order field as these load in random order

    def has_audio(self):
        return bool(self.label_audio)
    has_audio.boolean = True  # sets tick/cross in admin dashboard

    def __str__(self):
        if self.exercise:
            return f"{self.exercise.name}: {self.label}"
        else:
            return self.label

    class Meta:
        ordering = ['exercise', '?', 'id']
        verbose_name_plural = 'exercise format image matches'


class ExerciseFormatMultipleChoice(models.Model):
    """
    A multiple choice question/answer set within an exercise
    """

    exercise = models.ForeignKey(Exercise,
                                 limit_choices_to={'exercise_format__name': "Multiple Choice"},
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)
    question = models.TextField(blank=True, null=True, help_text=OPTIONAL_IF_AUDIO_HELP_TEXT)
    question_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True)

    option_a = models.TextField(blank=True, null=True, help_text=OPTIONAL_IF_AUDIO_HELP_TEXT, verbose_name='Option A')
    option_a_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True, verbose_name='Option A (audio)')
    option_a_is_correct = models.BooleanField(default=False, verbose_name="Option A is correct")

    option_b = models.TextField(blank=True, null=True, help_text=OPTIONAL_IF_AUDIO_HELP_TEXT, verbose_name='Option B')
    option_b_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True, verbose_name='Option B (audio)')
    option_b_is_correct = models.BooleanField(default=False, verbose_name="Option B is correct")

    option_c = models.TextField(blank=True, null=True, help_text=OPTIONAL_IF_AUDIO_HELP_TEXT, verbose_name='Option C')
    option_c_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True, verbose_name='Option C (audio)')
    option_c_is_correct = models.BooleanField(default=False, verbose_name="Option C is correct")

    option_d = models.TextField(blank=True, null=True, help_text=OPTIONAL_IF_AUDIO_HELP_TEXT, verbose_name='Option D')
    option_d_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True, verbose_name='Option D (audio)')
    option_d_is_correct = models.BooleanField(default=False, verbose_name="Option D is correct")

    option_e = models.TextField(blank=True, null=True, help_text=OPTIONAL_IF_AUDIO_HELP_TEXT, verbose_name='Option E')
    option_e_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True, verbose_name='Option E (audio)')
    option_e_is_correct = models.BooleanField(default=False, verbose_name="Option E is correct")

    option_f = models.TextField(blank=True, null=True, help_text=OPTIONAL_IF_AUDIO_HELP_TEXT, verbose_name='Option F')
    option_f_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True, verbose_name='Option F (audio)')
    option_f_is_correct = models.BooleanField(default=False, verbose_name="Option F is correct")

    order = models.IntegerField(blank=True, null=True, help_text=ORDER_HELP_TEXT)

    @property
    def question_text_or_audiomsg(self):
        return text_or_audiomsg(self.question, self.question_audio)

    @property
    def option_a_text_or_audiomsg(self):
        return text_or_audiomsg(self.option_a, self.option_a_audio)

    @property
    def option_b_text_or_audiomsg(self):
        return text_or_audiomsg(self.option_b, self.option_b_audio)

    @property
    def option_c_text_or_audiomsg(self):
        return text_or_audiomsg(self.option_c, self.option_c_audio)

    @property
    def option_d_text_or_audiomsg(self):
        return text_or_audiomsg(self.option_d, self.option_d_audio)

    @property
    def option_e_text_or_audiomsg(self):
        return text_or_audiomsg(self.option_e, self.option_e_audio)

    @property
    def option_f_text_or_audiomsg(self):
        return text_or_audiomsg(self.option_f, self.option_f_audio)

    def has_audio(self):
        return bool(self.question_audio or self.option_a_audio or self.option_b_audio or self.option_c_audio or self.option_d_audio or self.option_e_audio or self.option_f_audio)
    has_audio.boolean = True  # sets tick/cross in admin dashboard

    @property
    def options(self):
        options_list = []

        # Option A
        if self.option_a_text_or_audiomsg:
            options_list.append([
                f"A. {self.option_a_text_or_audiomsg}",
                self.option_a_audio,
                f"{self.id}-1",
                int(self.option_a_is_correct)])
        # Option B
        if self.option_b_text_or_audiomsg:
            options_list.append([
                f"B. {self.option_b_text_or_audiomsg}",
                self.option_b_audio,
                f"{self.id}-2",
                int(self.option_b_is_correct)])
        # Option C
        if self.option_c_text_or_audiomsg:
            options_list.append([
                f"C. {self.option_c_text_or_audiomsg}",
                self.option_c_audio,
                f"{self.id}-3",
                int(self.option_c_is_correct)])
        # Option D
        if self.option_d_text_or_audiomsg:
            options_list.append([
                f"D. {self.option_d_text_or_audiomsg}",
                self.option_d_audio,
                f"{self.id}-4",
                int(self.option_d_is_correct)])
        # Option E
        if self.option_e_text_or_audiomsg:
            options_list.append([
                f"E. {self.option_e_text_or_audiomsg}",
                self.option_e_audio,
                f"{self.id}-5",
                int(self.option_e_is_correct)])
        # Option F
        if self.option_f_text_or_audiomsg:
            options_list.append([
                f"F. {self.option_f_text_or_audiomsg}",
                self.option_f_audio,
                f"{self.id}-6",
                int(self.option_f_is_correct)])

        return options_list

    @property
    def answer_text(self):
        text = ""
        for option in self.options:
            if option[3]:
                # Print option text (on new line if multiple)
                text += f"<br>{option[0]}" if len(text) else option[0]
        return text

    def has_audio(self):
        return bool(self.question_audio or self.option_a_audio or self.option_b_audio or self.option_c_audio or self.option_d_audio or self.option_e_audio or self.option_f_audio)
    has_audio.boolean = True  # sets tick/cross in admin dashboard

    def __str__(self):
        s = ""
        if self.exercise:
            s += f"{self.exercise.name}: "
        if self.question:
            s += self.question[0:60]
        else:
            s += "A 'Multiple Choice' item"
        return s

    class Meta:
        ordering = ['exercise', 'order', 'id']


class ExerciseFormatFillInTheBlank(models.Model):
    """
    A fill in the blank question/answer within an exercise
    """

    exercise = models.ForeignKey(Exercise,
                                 limit_choices_to={'exercise_format__name': "Fill in the Blank"},
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)
    source = models.TextField(help_text="E.g. an English sentence to translate, a YouTube video link, etc. " + OPTIONAL_IF_AUDIO_HELP_TEXT,  blank=True, null=True)
    source_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True)
    text_with_blanks_to_fill = models.TextField(help_text="Wrap words you want to be blank with 2 asterisks (e.g. **blank words**). If there are multiple possibile answers for a single blank then separate them with a single asterisk (e.g. **big*large*tall**). A full example: This is an **example*sample*illustration** of how to specify **blank words** in a **sentence**.")
    text_with_blanks_to_fill_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True, help_text=ORDER_HELP_TEXT)

    @property
    def source_text_or_audiomsg(self):
        return text_or_audiomsg(self.source, self.source_audio)

    @property
    def text_with_blanks_to_fill_list(self):
        """
        Generate a list of strings of the contents of the blanks
        E.g. if text_with_blanks_to_fill is "this is **an example** of the **words** to be **translated**"
        this will return the list: ['an example', 'words', 'translated']
        """
        return self.text_with_blanks_to_fill.split('**')

    @property
    def text_with_blanks_to_fill_html(self):
        """
        Return the translated statement with blanks replaced with HTML text inputs to be used in the website
        """
        html = self.text_with_blanks_to_fill
        for blank in self.text_with_blanks_to_fill_list:
            # This string has to be all one line or the template puts each element on a new line in the UI
            span = f"""<span class="exerciseformat-fillintheblank-fitb-item" dir="auto"><input type="text" dir="auto" size="{len(max(blank.split("."), key=len))}" title="fill in the blank" data-correct="{blank}"></input><span class="exerciseformat-showanswer"><i class="fas fa-info-circle" title="{blank.replace('*', ' OR ')}"></i></span><span class="exerciseformat-fillintheblank-fitb-item-result"></span></span>"""  # noqa: E501
            html = html.replace(f"**{blank}**", span)
        return html

    def has_audio(self):
        return bool(self.source_audio or self.text_with_blanks_to_fill_audio)
    has_audio.boolean = True  # sets tick/cross in admin dashboard

    def __str__(self):
        s = ""
        if self.exercise:
            s += f"{self.exercise.name}: "
        if self.source:
            s += self.source[0:60]
        else:
            s += "A 'Fill in the Blank' item"
        return s

    class Meta:
        ordering = ['exercise', 'order', 'id']


class ExerciseFormatSentenceBuilder(models.Model):
    """
    Build a correctly translated sentence with the words given in random order
    """

    exercise = models.ForeignKey(Exercise,
                                 limit_choices_to={'exercise_format__name': "Sentence Builder"},
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)
    sentence_source = models.TextField(help_text=OPTIONAL_IF_AUDIO_HELP_TEXT, blank=True, null=True)
    sentence_source_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True)
    sentence_translated = models.TextField()
    sentence_translated_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True)
    sentence_translated_extra_words = models.TextField(help_text='(Optional) Include extra words to show as options to make the exercise more challenging. Separate with a space, e.g. "car apple tree"', blank=True, null=True)
    order = models.IntegerField(blank=True, null=True, help_text=ORDER_HELP_TEXT)

    @property
    def sentence_source_text_or_audiomsg(self):
        return text_or_audiomsg(self.sentence_source, self.sentence_source_audio)

    @property
    def words(self):
        """
        Return the list of words that will be shown as options for building the translated sentence
        I.e. join sentence_translated and sentence_translated_extra_words into a randomly ordered list
        """
        words = self.sentence_translated.split() + self.sentence_translated_extra_words.split()
        random.shuffle(words)
        return words

    def has_audio(self):
        return bool(self.sentence_source_audio or self.sentence_translated_audio)
    has_audio.boolean = True  # sets tick/cross in admin dashboard

    def __str__(self):
        s = ""
        if self.exercise:
            s += f"{self.exercise.name}: "
        if self.sentence_source:
            s += self.sentence_source[0:60]
        else:
            s += "A 'Sentence Builder' item"
        return s

    class Meta:
        ordering = ['exercise', 'order', 'id']


class ExerciseFormatTranslation(models.Model):
    """
    A translation exercise
    """

    exercise = models.ForeignKey(Exercise,
                                 limit_choices_to={'exercise_format__name': "Translation"},
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)
    translation_image = models.ImageField(upload_to='exercises-exerciseformat-translation')
    correct_translation = models.TextField()
    correct_translation_audio = models.FileField(upload_to=AUDIO_UPLOAD_PATH, help_text=AUDIO_HELP_TEXT, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True, help_text=ORDER_HELP_TEXT)

    def has_audio(self):
        return bool(self.correct_translation_audio)
    has_audio.boolean = True  # sets tick/cross in admin dashboard

    def __str__(self):
        if self.exercise:
            return f"{self.exercise.name}: {self.correct_translation[0:40]}"
        else:
            return self.correct_translation[0:40]

    class Meta:
        ordering = ['exercise', 'order', 'id']


class ExerciseFormatExternal(models.Model):
    """
    An external exercise
    """

    exercise = models.ForeignKey(Exercise,
                                 limit_choices_to={'exercise_format__name': "External"},
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)
    url = models.URLField()
    instructions = models.TextField(blank=True, null=True, help_text=OPTIONAL_HELP_TEXT)
    order = models.IntegerField(blank=True, null=True, help_text=ORDER_HELP_TEXT)

    def __str__(self):
        if self.exercise:
            return f"{self.exercise.name}: {self.url[0:80]}"
        else:
            return self.url[0:80]

    class Meta:
        ordering = ['exercise', 'order', 'id']


class ExerciseFurtherStudyMaterial(models.Model):
    """
    A resource (e.g. PDF, URL, etc) for further study in relation to a particular exercise
    """

    exercise = models.ForeignKey(Exercise, on_delete=models.RESTRICT)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='exercises-exercisefurtherstudymaterial-file', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    is_published = models.BooleanField(default=True, verbose_name="Published")
    created_by = models.ForeignKey(User, related_name="exercisefurtherstudymaterial_created_by", on_delete=models.SET_NULL, blank=True, null=True, help_text="The teacher who originally created this material")

    @property
    def file_name(self):
        return str(self.file).split('/')[-1:][0]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'id']


class SchoolClassAlertExercise(models.Model):
    """
    Many to many relationship between Exercise and SchoolClass,
    which acts as an alert monitoring system
    """

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def is_active(self):
        if self.start_date <= date.today() <= self.end_date:
            return True
        else:
            return False

    def __str__(self):
        return f"Class exercise alert: {self.id}"

    class Meta:
        ordering = ['start_date', 'end_date', 'school_class', 'exercise', 'id']


class UserExerciseAttempt(models.Model):
    """
    Many to many relationship between User (students) and Exercise,
    to record attempts made by the student at the exercise
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    score = models.FloatField(blank=True, null=True)
    attempt_duration = models.IntegerField(blank=True, null=True)
    submit_timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def score_percentage(self):
        if self.score:
            return f"{round(self.score)}%"
        else:
            return None

    def __str__(self):
        return f"[{str(self.submit_timestamp)[0:19]}]: {self.user.username} - {self.exercise.name[0:20]}"

    class Meta:
        ordering = ['-submit_timestamp', 'user', 'exercise']
