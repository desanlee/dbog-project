# Generated by Django 3.2.12 on 2022-03-03 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_alter_game_xfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='xfile',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='游戏卡数据文件'),
        ),
    ]
