# Generated by Django 3.2.12 on 2022-08-29 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0009_auto_20220420_0153'),
    ]

    operations = [
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='丛书名称')),
                ('discription', models.CharField(max_length=500, verbose_name='详细介绍')),
                ('cfile', models.CharField(max_length=100, verbose_name='丛书封面')),
                ('author', models.CharField(blank=True, max_length=100, null=True, verbose_name='作者')),
                ('status', models.CharField(blank=True, max_length=20, null=True, verbose_name='状态')),
            ],
        ),
        migrations.AlterField(
            model_name='cardconnection',
            name='connection_type',
            field=models.CharField(choices=[('FIS', 'Field is： 和目标是同样的字符串'), ('FIN', 'Field in： 自己被包含在目标字符串中'), ('THS', 'Time has： 自己的时间段涵盖了目标时间'), ('TIN', 'Time in： 自己的时间被包括在目标时间段中'), ('TCR', 'Time cross： 两个时间段有交集')], max_length=100, verbose_name='关联类型'),
        ),
        migrations.AddField(
            model_name='gamecategory',
            name='series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='games.series', verbose_name='丛书名称'),
        ),
    ]