from django.db import models
from django.utils.translation import gettext_lazy as _

class Series(models.Model):
    # this is what deboga is all about
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='丛书名称')
    discription = models.CharField(max_length=500, null=False, blank=False, verbose_name='详细介绍')
    cfile = models.ImageField(upload_to="covers", verbose_name='丛书封面')
    author = models.CharField(max_length=100, null=True, blank=True, verbose_name='作者')
    status = models.CharField(max_length=20, null=True, blank=True, verbose_name='状态')
    def __str__(self):
        return self.name

class Game(models.Model):
    # each game belongs to a category
    series = models.ForeignKey(Series, null=True,blank=True, related_name='game_include',verbose_name='所属丛书名称', on_delete = models.CASCADE)

    # the basic info for a game
    name = models.CharField(max_length=100, null=True, verbose_name='游戏名称')
    xfile = models.FileField(null=True, blank=True, verbose_name='游戏卡数据文件')
    # to make an expression for a game
    # users will know a game by watching these information
    discription = models.CharField(max_length=500, null=True, blank=True, verbose_name='游戏描述')
    restriction = models.CharField(max_length=500, null=True, blank=True, verbose_name='游戏限制')
    note = models.CharField(max_length=500, null=True, blank=True, verbose_name='对游戏的其他说明')

    # to indcate the meaning of fields in each game card
    # the gamecard model will be created based on following information
    field_name_1 = models.CharField(max_length=100, null=True, blank=True)
    field_name_2 = models.CharField(max_length=100, null=True, blank=True)
    field_name_3 = models.CharField(max_length=100, null=True, blank=True)
    field_name_4 = models.CharField(max_length=100, null=True, blank=True)
    field_name_5 = models.CharField(max_length=100, null=True, blank=True)
    field_name_6 = models.CharField(max_length=100, null=True, blank=True)

    card_count = models.IntegerField(null=True, blank=True, verbose_name='游戏卡数量')

    def __str__(self):
        return self.name

class GameCard(models.Model):
    # each gamecard belongs to a game
    game = models.ForeignKey(Game, null=True, blank=True, related_name='game_card', verbose_name='游戏', on_delete = models.CASCADE)

    # the basic info for a game
    field_1 = models.CharField(max_length=500, null=True, blank=True)
    field_2 = models.CharField(max_length=500, null=True, blank=True)
    field_3 = models.CharField(max_length=500, null=True, blank=True)
    field_4 = models.CharField(max_length=500, null=True, blank=True)
    field_5 = models.CharField(max_length=500, null=True, blank=True)
    field_6 = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.field_1

class CardConnection(models.Model):
    # 当前计划支持多种关联模式，分别是：
    # 实体相似关联，“fieldis”，“fieldhas”，”fieldin“
    # 时间相似关联，“timein”，“timehas”，“timecross”
    # 空间相似关联，
    class ConnectionMode(models.TextChoices):
        # 实体相似
        FIELDIS = 'FIS', _('Field is： 和目标是同样的字符串')
        FIELDIN = 'FIN', _('Field in： 自己被包含在目标字符串中')
        # 时间段重叠
        TIMEHAS = 'THS', _('Time has： 自己的时间段涵盖了目标时间')
        TIMEIN = 'TIN', _('Time in： 自己的时间被包括在目标时间段中')
        TIMECROSS = 'TCR', _('Time cross： 两个时间段有交集')
        # 空间重叠 TBD

    name = models.CharField(max_length=100, null=True, verbose_name='关联名称')
    discription = models.CharField(max_length=500, null=True, blank=True, verbose_name='关联描述')

    s_game = models.ForeignKey(Game, null=False, blank=False, related_name='connection_from', verbose_name='来源游戏', on_delete = models.CASCADE)
    s_para_1 = models.IntegerField(null=True, blank=True, verbose_name='源参1')
    s_para_2 = models.IntegerField(null=True, blank=True, verbose_name='源参2')
    s_para_3 = models.IntegerField(null=True, blank=True, verbose_name='源参3')

    connection_type = models.CharField(
        max_length=100,
        null=False,
        choices=ConnectionMode.choices,
        verbose_name='关联类型'
    )

    d_game = models.ForeignKey(Game, null=False, blank=False, related_name='connection_to', verbose_name='目标游戏', on_delete = models.CASCADE)
    d_para_1 = models.IntegerField(null=True, blank=True, verbose_name='标参1')
    d_para_2 = models.IntegerField(null=True, blank=True, verbose_name='标参2')
    d_para_3 = models.IntegerField(null=True, blank=True, verbose_name='标参3')

    def __str__(self):
        return self.name
