# Generated by Django 3.2.12 on 2022-04-20 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0008_cardconnection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardconnection',
            name='d_field_id',
        ),
        migrations.RemoveField(
            model_name='cardconnection',
            name='s_field_id',
        ),
        migrations.AddField(
            model_name='cardconnection',
            name='connection_type',
            field=models.CharField(default='is', max_length=100, verbose_name='关联类型'),
        ),
        migrations.AddField(
            model_name='cardconnection',
            name='d_para_1',
            field=models.IntegerField(blank=True, null=True, verbose_name='标参1'),
        ),
        migrations.AddField(
            model_name='cardconnection',
            name='d_para_2',
            field=models.IntegerField(blank=True, null=True, verbose_name='标参2'),
        ),
        migrations.AddField(
            model_name='cardconnection',
            name='d_para_3',
            field=models.IntegerField(blank=True, null=True, verbose_name='标参3'),
        ),
        migrations.AddField(
            model_name='cardconnection',
            name='s_para_1',
            field=models.IntegerField(blank=True, null=True, verbose_name='源参1'),
        ),
        migrations.AddField(
            model_name='cardconnection',
            name='s_para_2',
            field=models.IntegerField(blank=True, null=True, verbose_name='源参2'),
        ),
        migrations.AddField(
            model_name='cardconnection',
            name='s_para_3',
            field=models.IntegerField(blank=True, null=True, verbose_name='源参3'),
        ),
        migrations.AddField(
            model_name='game',
            name='field_visible_1',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='field_visible_2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='field_visible_3',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='field_visible_4',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='field_visible_5',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='game',
            name='field_visible_6',
            field=models.BooleanField(default=False),
        ),
    ]
