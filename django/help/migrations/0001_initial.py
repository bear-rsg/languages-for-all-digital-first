# Generated by Django 3.2.15 on 2022-08-22 14:27

from django.db import migrations, models
import embed_video.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                ('link', models.URLField(blank=True, help_text='Must be a valid URL, e.g. https://www.birmingham.ac.uk', null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='help-image')),
                ('video', embed_video.fields.EmbedVideoField(blank=True, help_text='Provide a URL of a video hosted on YouTube or Vimeo, e.g. https://www.youtube.com/watch?v=BHACKCNDMW8', null=True)),
                ('pdf', models.FileField(blank=True, null=True, upload_to='help-pdf')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('lastupdated_datetime', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('admin_published', models.BooleanField(default=False, verbose_name='published')),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('visible_only_to_user_groups', models.ManyToManyField(blank=True, related_name='helpitems', to='account.UserRole')),
            ],
        ),
    ]
