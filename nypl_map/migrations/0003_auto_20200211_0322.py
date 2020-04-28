# Generated by Django 3.0.2 on 2020-02-11 03:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nypl_map', '0002_auto_20200202_0337'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Hours',
            new_name='Hour',
        ),
        migrations.RemoveField(
            model_name='library',
            name='is_open',
        ),
        migrations.AddField(
            model_name='library',
            name='about_text',
            field=models.TextField(default=''),
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(default='')),
                ('closure_reason', models.CharField(default='', max_length=1000)),
                ('is_closed', models.BooleanField(default=False)),
                ('period_start', models.TimeField(null=True)),
                ('period_end', models.TimeField(null=True)),
                ('hyperlink', models.URLField(blank=True)),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nypl_map.Library')),
            ],
        ),
    ]
