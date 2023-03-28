#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
# -*- coding: UTF-8 -*-

from django.contrib import admin
import xlrd

from .models import Series, Game, GameCard, CardConnection
from tools.langconv import *

class ConnectionInline(admin.TabularInline):
    model = CardConnection
    fields = (('d_game','connection_type','name','discription'),('s_para_1','s_para_2'),('d_para_1','d_para_2'))
    fk_name = 's_game'
    extra = 0

class GamesInline(admin.StackedInline):
    model = Game
    fields = ('discription',)
    fk_name = 'series'
    readonly_fields=('discription',)
    extra = 0
    can_delete = False
    def has_add_permission(request, obj, t):
        return False

class GameCardAdmin(admin.ModelAdmin):
    list_display = ('game', 'field_1', 'field_2', 'field_3', 'field_4', 'field_5', 'field_6')
    actions_on_top = False
    list_filter = ['game']

    def has_add_permission(request, obj):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class SeriesAdmin(admin.ModelAdmin):
    fields = (('name','author'),('discription'))
    inlines = [GamesInline]

    list_display = ('name', 'discription', 'author')
    actions_on_top = False

class GameAdmin(admin.ModelAdmin):
    fields = (('name','series','xfile'),
        ('discription','restriction','note'),
        ('field_name_1','field_name_2','field_name_3'),
        ('field_name_4','field_name_5','field_name_6'))
    inlines = [ConnectionInline]

    list_display = ('name', 'series',
        'field_name_1','field_name_2','field_name_3','field_name_4','field_name_5','field_name_6',
    )

    list_filter = ['series']
    actions_on_top = False

    def save_model(self, request, obj, form, change):
        # create new gamecard model and import dataset
        super().save_model(request, obj, form, change)

        if bool(obj.xfile) != False:
            # if xfile is uploaded, retrieve card records from excel file
            print(obj.xfile.url)
            wb = xlrd.open_workbook("./" + obj.xfile.url)
            # remove all cards belongs to curent game
            # self.gamecards.all.delete()
            # insert each record into database
            table = wb.sheets()[0]
            row_count = table.nrows
            obj.game_card.all().delete()

            index_names = table.row_values(0)
            for index, value in enumerate(index_names):
                obj.__dict__['field_name_' + str(index + 1) ] = value
            obj.save()

            for i in range(1, row_count):
                row = table.row_values(i)
                c = GameCard()
                c.game = obj
                for index, value in enumerate(row):
                    #setattr(c, 'field_' + str(index + 1), Converter('zh-hans').convert(value))
                    setattr(c, 'field_' + str(index + 1), value)
                c.save()

            obj.xfile.delete()

admin.site.register(Series,SeriesAdmin)
admin.site.register(Game,GameAdmin)
admin.site.register(GameCard,GameCardAdmin)
