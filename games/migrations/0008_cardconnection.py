# Generated by Django 3.2.12 on 2022-03-23 02:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_auto_20220308_0319'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('s_field_id', models.IntegerField(verbose_name='来源字段')),
                ('d_field_id', models.IntegerField(verbose_name='目标字段')),
                ('name', models.CharField(max_length=100, null=True, verbose_name='关联名称')),
                ('discription', models.CharField(blank=True, max_length=500, null=True, verbose_name='关联描述')),
                ('d_game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connection_to', to='games.game', verbose_name='目标游戏')),
                ('s_game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connection_from', to='games.game', verbose_name='来源游戏')),
            ],
        ),
    ]
