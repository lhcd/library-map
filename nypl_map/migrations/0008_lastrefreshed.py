# Generated by Django 3.0.2 on 2020-03-05 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nypl_map', '0007_auto_20200222_2243'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastRefreshed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refresh_time', models.DateTimeField()),
            ],
        ),
    ]
