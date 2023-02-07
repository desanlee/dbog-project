from django.shortcuts import get_object_or_404, render

from .models import Series, Game, GameCard
from tools.langconv import *
from django.db.models.fields import Field
from django.db.models import Transform
import re

@Field.register_lookup
class IntegerValue(Transform):
    # Register this before you filter things, for example in models.py
    lookup_name = 'int'  # Used as object.filter(LeftField__int__gte, "777")
    bilateral = True  # To cast both left and right

    def as_sql(self, compiler, connection):
        sql, params = compiler.compile(self.lhs)
        sql = 'CAST(%s AS UNSIGNED)' % sql
        return sql, params

def ValidInt(intstr):
    if isinstance(intstr, str):
        pat = "(-)*[0-9]+"
        if re.search(pat, intstr):
        	return True
        else:
            print(intstr)
    return False

def index(request):
    series_list = Series.objects.all()
    for s in series_list:
        if s.game_include.first() :
            setattr(s,'first_game_id', s.game_include.first().id)
        else :
            setattr(s,'first_game_id', 0)
    context = {
        'series_list': series_list,
    }
    return render(request, 'games/index.html', context)

def detail(request, game_id):
    # cate_list = GameCategory.objects.all()
    game = get_object_or_404(Game, pk = game_id)
    series = game.series
    games = series.game_include.all()

    # prepare a cards list
    try:
        ss = request.POST['searchstr']
    except:
        cards = game.game_card.all().order_by('?')[:4]
    else :
        stripstr = ss.strip()
        if stripstr != "" :
            cards = game.game_card.filter(field_1__icontains=stripstr)
            if len(cards) > 4 :
                cards = cards[:4]
        else :
            cards = []
            cards = game.game_card.all().order_by('?')[:4]

    # for all A card in card list find their connected B cards
    card_diags = {}
    for ca in cards:
        setattr(ca,'diag_count',0)
        card_diags[ca.id] = {"count":0, "calist":[]}
        out_connections = ca.game.connection_from.all()
        for conn in out_connections:
            diag = {}
            diag['game'] = conn.d_game
            diag['conn'] = conn.name
            diag['cards'] = []
            condition,condition1,condition2 = {},{},{}
            if conn.connection_type == 'FIS': # field is
            # d_para_1 is s_para_1 两个字段数据相同
                condition["field_"+str(conn.d_para_1)] = ca.__dict__["field_"+str(conn.s_para_1)]
                diag['cards'] += list(conn.d_game.game_card.filter(**condition).all())[0:8]
                diag['cards'] = list(set(diag['cards']))
            elif conn.connection_type == 'FIN': # field in
            # d_para_1 has s_para_1 目标字段数据包含原字段数据
                condition["field_"+str(conn.d_para_1)+"__icontains"] = ca.__dict__["field_"+str(conn.s_para_1)]
                diag['cards'] += list(conn.d_game.game_card.filter(**condition).all())[0:8]
                diag['cards'] = list(set(diag['cards']))
            elif conn.connection_type == 'THS': # time has
            # d_para_1 > s_para_1 & < s_para_2 源事件的区间包括目的事件
            # 定义两个源字段一个目标字段
                if ValidInt(ca.__dict__["field_"+str(conn.s_para_1)]) and ValidInt(ca.__dict__["field_"+str(conn.s_para_2)]) :
                    condition["field_"+str(conn.d_para_1)+"__int__gte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                    condition["field_"+str(conn.d_para_1)+"__int__lte"] = int(float(ca.__dict__["field_"+str(conn.s_para_2)]))
                    diag['cards'] = list(conn.d_game.game_card.filter(**condition).all())[0:8]
                    diag['cards'] = list(set(diag['cards']))
            elif conn.connection_type == 'TIN': # time in
            # s_para_1 > d_para_1 & < d_para_2 源事件的时间包含在目标区间内
            # 定义两个源字段一个目标字段
                if ValidInt(ca.__dict__["field_"+str(conn.s_para_1)]) :
                    condition["field_"+str(conn.d_para_2)+"__int__gte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                    condition["field_"+str(conn.d_para_1)+"__int__lte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                    print(condition)
                    diag['cards'] = list(conn.d_game.game_card.filter(**condition).all())[0:8]
                    diag['cards'] = list(set(diag['cards']))
            elif conn.connection_type == 'TCR': # time cross
            # d_para_1 d_para_2 s_para_1 s_para_2相交 源事件发生在目的事件的一定区间内
            # 定义两个源字段两个目标字段
                if ValidInt(ca.__dict__["field_"+str(conn.s_para_1)]) and ValidInt(ca.__dict__["field_"+str(conn.s_para_2)]):
                    condition1["field_"+str(conn.d_para_2)+"__int__gte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                    condition1["field_"+str(conn.d_para_1)+"__int__lte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                    qs1 = list(conn.d_game.game_card.filter(**condition1).all())[0:5]
                    condition2["field_"+str(conn.d_para_2)+"__int__gte"] = int(float(ca.__dict__["field_"+str(conn.s_para_2)]))
                    condition2["field_"+str(conn.d_para_1)+"__int__lte"] = int(float(ca.__dict__["field_"+str(conn.s_para_2)]))
                    qs2 = list(conn.d_game.game_card.filter(**condition2).all())[0:5]
                    diag['cards'] = list(set(qs1 + qs2))[0:8]

            if ca in diag['cards']:
                diag['cards'].remove(ca)
            diag['count'] = len(diag['cards'])
            if diag['count'] != 0 :
                card_diags[ca.id]["calist"].append(diag)
                card_diags[ca.id]["count"] += 1

        setattr(ca,'diaglist',card_diags[ca.id]["calist"])
        setattr(ca,'diagcount',card_diags[ca.id]["count"])

    context = {
        'game': game,
        'cards': cards,
        'games': games
    }
    return render(request, 'games/detail.html', context)
