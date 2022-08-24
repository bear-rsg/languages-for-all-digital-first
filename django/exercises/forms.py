from django import forms
from captcha.fields import ReCaptchaField, ReCaptchaV3
from . import models


"""
These forms all do the same thing but for the different ExerciseFormats
e.g. Multiple Choice, Fill in the Blank, etc.

They're forms to create and update each model object
"""


class ExerciseFormatMultipleChoiceForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.ExerciseFormatMultipleChoice
        exclude = ('exercise',)


class ExerciseFormatFillInTheBlankForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.ExerciseFormatFillInTheBlank
        exclude = ('exercise',)


class ExerciseFormatImageMatchForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.ExerciseFormatImageMatch
        exclude = ('exercise',)


class ExerciseFormatSentenceBuilderForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.ExerciseFormatSentenceBuilder
        exclude = ('exercise',)


class ExerciseFormatTranslationForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.ExerciseFormatTranslation
        exclude = ('exercise',)


class ExerciseFormatExternalForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.ExerciseFormatExternal
        exclude = ('exercise',)
