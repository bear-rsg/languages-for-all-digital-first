# Generated by Django 3.2.14 on 2022-07-20 18:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Difficulty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'difficulties',
                'ordering': ['order', 'name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('instructions', models.TextField(blank=True, help_text='(Optional) If left blank then the default instructions for this exercise format will be used (suitable for most cases)', null=True)),
                ('instructions_image', models.ImageField(blank=True, help_text='(Optional) Include an image here to illustrate the instructions for the entire exercise. E.g. if all questions relate to this image.', null=True, upload_to='exercises-exercise-instructions')),
                ('is_a_formal_assessment', models.BooleanField(default=False, help_text="Marking this as a formal assessment (i.e. a test that counts to the student's grade) will put restrictions on this exercise, like preventing students from being able to check answers and only allowing a single attempt")),
                ('is_published', models.BooleanField(default=True, verbose_name='Published')),
                ('created_by', models.ForeignKey(blank=True, help_text='The teacher who originally created this exercise', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercise_created_by', to=settings.AUTH_USER_MODEL)),
                ('difficulty', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='exercises.difficulty')),
            ],
            options={
                'ordering': ['name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseFormat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('icon', models.CharField(max_length=255)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('is_marked_automatically_by_system', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=True, verbose_name='Published')),
            ],
            options={
                'ordering': ['name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('is_published', models.BooleanField(default=True, verbose_name='Published')),
            ],
            options={
                'ordering': ['name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_feature', models.CharField(blank=True, help_text='If other classes have the same name as this one because they have the same language, difficulty, and teachers, please specify something unique about this class (e.g. the day of the week its run) to make the class name unique', max_length=255, null=True)),
                ('is_published', models.BooleanField(default=True, verbose_name='Published')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('difficulty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='exercises.difficulty')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='exercises.language')),
            ],
            options={
                'verbose_name_plural': 'classes',
                'ordering': ['language', 'difficulty', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('is_published', models.BooleanField(default=True, verbose_name='Published')),
            ],
            options={
                'ordering': ['name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='YearGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('date_start', models.DateField(blank=True, null=True)),
                ('date_end', models.DateField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=False, verbose_name='Published')),
            ],
            options={
                'ordering': ['name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='UserExerciseAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(blank=True, null=True)),
                ('attempt_duration', models.IntegerField(blank=True, null=True)),
                ('submit_timestamp', models.DateTimeField(auto_now_add=True)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submit_timestamp', 'user', 'exercise'],
            },
        ),
        migrations.CreateModel(
            name='SchoolClassAlertExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.schoolclass')),
            ],
            options={
                'ordering': ['start_date', 'end_date', 'school_class', 'exercise', 'id'],
            },
        ),
        migrations.AddField(
            model_name='schoolclass',
            name='year_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='exercises.yeargroup'),
        ),
        migrations.CreateModel(
            name='ExerciseFurtherStudyMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(blank=True, null=True, upload_to='exercises-exercisefurtherstudymaterial-file')),
                ('url', models.URLField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=True, verbose_name='Published')),
                ('created_by', models.ForeignKey(blank=True, help_text='The teacher who originally created this material', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercisefurtherstudymaterial_created_by', to=settings.AUTH_USER_MODEL)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='exercises.exercise')),
            ],
            options={
                'ordering': ['name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseFormatTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translation_image', models.ImageField(upload_to='exercises-exerciseformat-translation')),
                ('correct_translation', models.TextField()),
                ('correct_translation_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio')),
                ('correct_answer_feedback', models.TextField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning', null=True)),
                ('order', models.IntegerField(blank=True, help_text="(Optional) Specify the order you'd like this item to appear on the exercise page. Leave blank to order automatically.", null=True)),
                ('exercise', models.ForeignKey(blank=True, limit_choices_to={'exercise_format__name': 'Translation'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
            ],
            options={
                'ordering': ['exercise', 'order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseFormatSentenceBuilder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentence_source', models.TextField(blank=True, help_text='Optional if supplying audio instead, otherwise required', null=True)),
                ('sentence_source_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio')),
                ('sentence_translated', models.TextField()),
                ('sentence_translated_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio')),
                ('sentence_translated_extra_words', models.TextField(blank=True, help_text='(Optional) Include extra words to show as options to make the exercise more challenging. Separate with a space, e.g. "car apple tree"', null=True)),
                ('correct_answer_feedback', models.TextField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning', null=True)),
                ('order', models.IntegerField(blank=True, help_text="(Optional) Specify the order you'd like this item to appear on the exercise page. Leave blank to order automatically.", null=True)),
                ('exercise', models.ForeignKey(blank=True, limit_choices_to={'exercise_format__name': 'Sentence Builder'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
            ],
            options={
                'ordering': ['exercise', 'order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseFormatMultipleChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(blank=True, help_text='Optional if supplying audio instead, otherwise required', null=True)),
                ('question_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio')),
                ('option_a', models.TextField(blank=True, help_text='Optional if supplying audio instead, otherwise required', null=True, verbose_name='Option A')),
                ('option_a_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio', verbose_name='Option A (audio)')),
                ('option_a_is_correct', models.BooleanField(default=False, verbose_name='Option A is correct')),
                ('option_b', models.TextField(blank=True, help_text='Optional if supplying audio instead, otherwise required', null=True, verbose_name='Option B')),
                ('option_b_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio', verbose_name='Option B (audio)')),
                ('option_b_is_correct', models.BooleanField(default=False, verbose_name='Option B is correct')),
                ('option_c', models.TextField(blank=True, help_text='Optional if supplying audio instead, otherwise required', null=True, verbose_name='Option C')),
                ('option_c_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio', verbose_name='Option C (audio)')),
                ('option_c_is_correct', models.BooleanField(default=False, verbose_name='Option C is correct')),
                ('option_d', models.TextField(blank=True, help_text='Optional if supplying audio instead, otherwise required', null=True, verbose_name='Option D')),
                ('option_d_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio', verbose_name='Option D (audio)')),
                ('option_d_is_correct', models.BooleanField(default=False, verbose_name='Option D is correct')),
                ('option_e', models.TextField(blank=True, help_text='Optional if supplying audio instead, otherwise required', null=True, verbose_name='Option E')),
                ('option_e_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio', verbose_name='Option E (audio)')),
                ('option_e_is_correct', models.BooleanField(default=False, verbose_name='Option E is correct')),
                ('option_f', models.TextField(blank=True, help_text='Optional if supplying audio instead, otherwise required', null=True, verbose_name='Option F')),
                ('option_f_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio', verbose_name='Option F (audio)')),
                ('option_f_is_correct', models.BooleanField(default=False, verbose_name='Option F is correct')),
                ('correct_answer_feedback', models.TextField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning', null=True)),
                ('order', models.IntegerField(blank=True, help_text="(Optional) Specify the order you'd like this item to appear on the exercise page. Leave blank to order automatically.", null=True)),
                ('exercise', models.ForeignKey(blank=True, limit_choices_to={'exercise_format__name': 'Multiple Choice'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
            ],
            options={
                'ordering': ['exercise', 'order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseFormatImageMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='exercises-exerciseformat-imagematch')),
                ('label', models.CharField(max_length=255)),
                ('label_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio')),
                ('correct_answer_feedback', models.TextField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning', null=True)),
                ('exercise', models.ForeignKey(blank=True, limit_choices_to={'exercise_format__name': 'Image Match'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
            ],
            options={
                'verbose_name_plural': 'exercise format image matches',
                'ordering': ['exercise', '?', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseFormatFillInTheBlank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.TextField(blank=True, help_text='E.g. an English sentence to translate, a YouTube video link, etc. Optional if supplying audio instead, otherwise required', null=True)),
                ('source_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio')),
                ('text_with_blanks_to_fill', models.TextField(help_text='Wrap words you want to be blank with 2 asterisks (e.g. **blank words**). If there are multiple possibile answers for a single blank then separate them with a single asterisk (e.g. **big*large*tall**). A full example: This is an **example*sample*illustration** of how to specify **blank words** in a **sentence**.')),
                ('text_with_blanks_to_fill_audio', models.FileField(blank=True, help_text="(Optional) <a href='https://online-voice-recorder.com/' target='_blank'>Record your audio clip</a> and then upload the file here", null=True, upload_to='exercises-exercise-audio')),
                ('correct_answer_feedback', models.TextField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning', null=True)),
                ('order', models.IntegerField(blank=True, help_text="(Optional) Specify the order you'd like this item to appear on the exercise page. Leave blank to order automatically.", null=True)),
                ('exercise', models.ForeignKey(blank=True, limit_choices_to={'exercise_format__name': 'Fill in the Blank'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
            ],
            options={
                'ordering': ['exercise', 'order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseFormatExternal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('instructions', models.TextField(blank=True, help_text='(Optional)', null=True)),
                ('order', models.IntegerField(blank=True, help_text="(Optional) Specify the order you'd like this item to appear on the exercise page. Leave blank to order automatically.", null=True)),
                ('exercise', models.ForeignKey(blank=True, limit_choices_to={'exercise_format__name': 'External'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
            ],
            options={
                'ordering': ['exercise', 'order', 'id'],
            },
        ),
        migrations.AddField(
            model_name='exercise',
            name='exercise_format',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='exercises.exerciseformat'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='exercises.language'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='owned_by',
            field=models.ForeignKey(blank=True, help_text='The only teacher who can manage this exercise', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercise_owned_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exercise',
            name='theme',
            field=models.ForeignKey(blank=True, help_text='(Optional)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='exercises.theme'),
        ),
    ]
