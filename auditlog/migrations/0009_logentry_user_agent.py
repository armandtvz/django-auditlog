# Generated by Django 3.2.6 on 2021-08-07 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditlog', '0008_auto_20210701_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='user_agent',
            field=models.TextField(blank=True),
        ),
    ]
