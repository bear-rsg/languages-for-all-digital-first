# Generated by Django 3.2.16 on 2022-10-05 19:27

import account.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_data_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersimportspreadsheet',
            name='spreadsheet',
            field=models.FileField(blank=True, help_text='Upload an Excel spreadsheet (.xlsx) with data of new users to add to the database.<br>Ensure the structure complies with the latest version of the template spreadsheet or the import may fail.<br>Contact the software developer for support if you require help.<br>Once you\'ve uploaded the file, you can begin <a href="/account/importdata/">the import process</a>', null=True, storage=account.storage.ReplaceFileStorage(), upload_to='account/userimportspreadsheets'),
        ),
    ]
