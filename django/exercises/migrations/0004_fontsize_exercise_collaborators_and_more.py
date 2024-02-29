# Generated by Django 4.2.9 on 2024-02-29 15:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exercises', '0003_exercise_instructions_image_width_percent_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FontSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('size_em', models.FloatField(help_text='Size of font (measured in em) as a decimal number. 1.0 is considered default/medium.')),
            ],
            options={
                'ordering': ['size_em', 'name', 'id'],
            },
        ),
        migrations.AddField(
            model_name='exercise',
            name='collaborators',
            field=models.ManyToManyField(blank=True, help_text='Persons who can also manage this exercise, in addition to the owner', related_name='exercises', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exercise',
            name='exercise_format_reverse_image_match',
            field=models.BooleanField(default=False, help_text='Reverse the layout of this image match exercise, so that the student must select the image that matches the word instead of the word that matches the image.', verbose_name='reverse image match'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='instructions_image_url',
            field=models.URLField(blank=True, help_text='(Optional) Include a URL/link to an existing image on the internet, instead of needing to download and upload it using the above file upload facility.', null=True),
        ),
        migrations.AddField(
            model_name='exerciseformatimagematch',
            name='correct_answer_feedback_audio',
            field=models.FileField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning, using an audio file alongside or instead of feedback text. <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio'),
        ),
        migrations.AddField(
            model_name='exerciseformatimagematch',
            name='image_url',
            field=models.URLField(blank=True, help_text='(Optional) Include a URL/link to an existing image on the internet, instead of needing to download and upload it using the above file upload facility.', null=True),
        ),
        migrations.AddField(
            model_name='exerciseformatmultiplechoice',
            name='correct_answer_feedback_audio',
            field=models.FileField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning, using an audio file alongside or instead of feedback text. <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio'),
        ),
        migrations.AddField(
            model_name='exerciseformatsentencebuilder',
            name='correct_answer_feedback_audio',
            field=models.FileField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning, using an audio file alongside or instead of feedback text. <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio'),
        ),
        migrations.AddField(
            model_name='exerciseformattranslation',
            name='correct_answer_feedback_audio',
            field=models.FileField(blank=True, help_text='(Optional) Provide feedback about the correct answer (if relevant) to help aid student learning, using an audio file alongside or instead of feedback text. <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio'),
        ),
        migrations.AddField(
            model_name='exerciseformattranslation',
            name='translation_source_image_url',
            field=models.URLField(blank=True, help_text='(Optional) Include a URL/link to an existing image on the internet, instead of needing to download and upload it using the above file upload facility.', null=True, verbose_name='URL to image of source text'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='The person who originally created this exercise', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercise_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='owned_by',
            field=models.ForeignKey(blank=True, help_text='The person who is mainly responsible for managing this exercise', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercise_owned_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='exerciseformatfillintheblank',
            name='source_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio'),
        ),
        migrations.AlterField(
            model_name='exerciseformatimagematch',
            name='image',
            field=models.ImageField(blank=True, help_text='Optional if providing a URL to an image below, otherwise required.', null=True, upload_to='exercises-exerciseformat-imagematch'),
        ),
        migrations.AlterField(
            model_name='exerciseformatmultiplechoice',
            name='option_a_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio', verbose_name='Option A (audio)'),
        ),
        migrations.AlterField(
            model_name='exerciseformatmultiplechoice',
            name='option_b_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio', verbose_name='Option B (audio)'),
        ),
        migrations.AlterField(
            model_name='exerciseformatmultiplechoice',
            name='option_c_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio', verbose_name='Option C (audio)'),
        ),
        migrations.AlterField(
            model_name='exerciseformatmultiplechoice',
            name='option_d_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio', verbose_name='Option D (audio)'),
        ),
        migrations.AlterField(
            model_name='exerciseformatmultiplechoice',
            name='option_e_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio', verbose_name='Option E (audio)'),
        ),
        migrations.AlterField(
            model_name='exerciseformatmultiplechoice',
            name='option_f_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio', verbose_name='Option F (audio)'),
        ),
        migrations.AlterField(
            model_name='exerciseformatmultiplechoice',
            name='question_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio'),
        ),
        migrations.AlterField(
            model_name='exerciseformatsentencebuilder',
            name='sentence_source',
            field=models.TextField(blank=True, help_text='(Optional) Provide an original source text in one language, which will be translated below', null=True, verbose_name='source text'),
        ),
        migrations.AlterField(
            model_name='exerciseformatsentencebuilder',
            name='sentence_source_audio',
            field=models.FileField(blank=True, help_text='(Optional) <a href="https://online-voice-recorder.com/" target="_blank">Record your audio clip</a> and then upload the file here', null=True, upload_to='exercises-exercise-audio', verbose_name='source audio'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='font_size',
            field=models.ForeignKey(blank=True, help_text='(Optional) Set size of all font in exercise. Leave blank for a default font size.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='exercises.fontsize'),
        ),
    ]