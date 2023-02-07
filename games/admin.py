#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
# -*- coding: UTF-8 -*-

from django.contrib import admin
import xlrd

from .models import Series, Game, GameCard, CardConnection
from tools.langconv import *

class ConnectionInline(admin.StackedInline):
    model = CardConnection
    fk_name = 's_game'
    extra = 1

class SeriesAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['name','discription']
            }),
        (None, {
            'fields': ['author']
            }),
    ]
    list_display = ('name', 'discription', 'author')
    list_filter = ['name']
    search_fields = ['name']

class GameAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['series','name','xfile']
            }),
        (None, {
            'fields': ['discription','restriction','note']
            }),
        (None, {
            'fields': ['field_name_1','field_name_2','field_name_3','field_name_4','field_name_5','field_name_6']
            }),
    ]
    inlines = [ConnectionInline]

    list_display = ('name', 'series', 'discription',
        'field_name_1','field_name_2','field_name_3','field_name_4','field_name_5','field_name_6',
    )
    search_fields = ['name']

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
