# Generated by Django 5.1.1 on 2024-10-12 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmapp', '0006_material'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='materials',
            field=models.ManyToManyField(blank=True, to='crmapp.material'),
        ),
    ]
