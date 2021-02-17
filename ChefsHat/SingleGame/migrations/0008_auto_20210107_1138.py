# Generated by Django 3.0.5 on 2021-01-07 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SingleGame', '0007_auto_20210107_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.AlterField(
            model_name='dataset',
            name='expName',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SingleGame.Experiment'),
        ),
    ]