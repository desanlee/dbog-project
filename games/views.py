from django.shortcuts import get_object_or_404, render, HttpResponse
from io import BytesIO
import xlwt
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

def getDirectComments(ca): #ca is with type of GameCard
    comments = {}
    setattr(ca,'comments_count',0)
    comments[ca.id] = {"count":0, "comments":[]}
    out_connections = ca.game.connection_from.all()

    for conn in out_connections: # each connection raises a comment which has several  cards
        comment = {}
        comment['game'] = conn.d_game
        comment['conn'] = conn.name
        comment['cards'] = []
        condition,condition1,condition2 = {},{},{}
        if conn.connection_type == 'FIS': # field is. it is  a one to one connection
        # d_para_1 is s_para_1 两个字段数据相同
            condition["field_"+str(conn.d_para_1)] = ca.__dict__["field_"+str(conn.s_para_1)]
            comment['cards'] += list(conn.d_game.game_card.filter(**condition).all())[0:5]
            comment['cards'] = list(set(comment['cards']))
        elif conn.connection_type == 'FIN': # field in
        # d_para_1 has s_para_1 目标字段数据包含原字段数据
            condition["field_"+str(conn.d_para_1)+"__icontains"] = ca.__dict__["field_"+str(conn.s_para_1)]
            comment['cards'] += list(conn.d_game.game_card.filter(**condition).all())[0:5]
            comment['cards'] = list(set(comment['cards']))
        elif conn.connection_type == 'THS': # time has
        # d_para_1 > s_para_1 & < s_para_2 源事件的区间包括目的事件
        # 定义两个源字段一个目标字段
            if ValidInt(ca.__dict__["field_"+str(conn.s_para_1)]) and ValidInt(ca.__dict__["field_"+str(conn.s_para_2)]) :
                condition["field_"+str(conn.d_para_1)+"__int__gte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                condition["field_"+str(conn.d_para_1)+"__int__lte"] = int(float(ca.__dict__["field_"+str(conn.s_para_2)]))
                comment['cards'] = list(conn.d_game.game_card.filter(**condition).all())[0:5]
                comment['cards'] = list(set(comment['cards']))
        elif conn.connection_type == 'TIN': # time in
        # s_para_1 > d_para_1 & < d_para_2 源事件的时间包含在目标区间内
        # 定义两个源字段一个目标字段
            if ValidInt(ca.__dict__["field_"+str(conn.s_para_1)]) :
                condition["field_"+str(conn.d_para_2)+"__int__gte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                condition["field_"+str(conn.d_para_1)+"__int__lte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                comment['cards'] = list(conn.d_game.game_card.filter(**condition).all())[0:5]
                comment['cards'] = list(set(comment['cards']))
        elif conn.connection_type == 'TCR': # time cross
        # d_para_1 d_para_2 s_para_1 s_para_2相交 源事件发生在目的事件的一定区间内
        # 定义两个源字段两个目标字段
            if ValidInt(ca.__dict__["field_"+str(conn.s_para_1)]) and ValidInt(ca.__dict__["field_"+str(conn.s_para_2)]):
                condition1["field_"+str(conn.d_para_2)+"__int__gte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                condition1["field_"+str(conn.d_para_1)+"__int__lte"] = int(float(ca.__dict__["field_"+str(conn.s_para_1)]))
                qs1 = list(conn.d_game.game_card.filter(**condition1).all())[0:3]
                condition2["field_"+str(conn.d_para_2)+"__int__gte"] = int(float(ca.__dict__["field_"+str(conn.s_para_2)]))
                condition2["field_"+str(conn.d_para_1)+"__int__lte"] = int(float(ca.__dict__["field_"+str(conn.s_para_2)]))
                qs2 = list(conn.d_game.game_card.filter(**condition2).all())[0:3]
                comment['cards'] = list(set(qs1 + qs2))[0:5]
        # remove self from comments
        if ca in comment['cards']:
            comment['cards'].remove(ca)
        comment['count'] = len(comment['cards'])
        if comment['count'] != 0 :
            comments[ca.id]["comments"].append(comment)
            comments[ca.id]["count"] += 1

    return comments

# if two comment have same game and same connection, then merge their card list
# para 1: alist
# para 2: blist
def mergeComment(alist, blist):
    if len(blist) == 0 :
        return alist
    if len(alist) == 0 :
        return blist

    tlist = []
    for b in blist:
        for a in alist :
            if a['game'] == b['game'] and a['conn'] == b['conn']:
                a['cards'].extend(b['cards'])
                a['cards'] = list(set(a['cards']))
                break
            else :
                tlist.append(b)
                break
    alist.extend(tlist)
    return alist


# if the card id of a comment is para card_id, then delete this comment from comments
# para 1: comments, comments list
# para 2: card_id, the id of a card
def removeTransBack(comments, card_id):
    retComments = comments
    for comment in retComments :
        for card in comment['cards']:
            if card.id == card_id :
                comment['cards'].remove(card)
    return retComments

def commentsContain(comments, comment):
    for c in comments :
        if c['game'] == comment['game'] and c['conn'] == comment['conn']:
            return True
    return False

def removeDuplicate(comments):
    retComments = []
    for c in comments:
        if commentsContain(retComments, c) :
            continue
        else :
            retComments.append(c)
    return retComments

def updateInitialConn(comments_list, initial_conn):
    retComments_list = comments_list
    for k,v in retComments_list.items() :
        if v != None :
            if len(v) > 0 :
                for comment in v['comments'] :
                    comment["conn"] = initial_conn + '-' + comment["conn"]
    return retComments_list

# show the detail info of a game.
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

    # for all A card in card list find their connected B card and through B card to C cards if there are any
    for ca in cards:
        direct_comments_list = getDirectComments(ca)
        indirect_comments = []
        for comment in direct_comments_list[ca.id]['comments']:
            for card in comment['cards']:
                initial_conn = comment["conn"]
                trans_comments_list = getDirectComments(card)
                trans_comments_list = updateInitialConn(trans_comments_list, initial_conn)
                indirect_comments = mergeComment(indirect_comments, trans_comments_list[card.id]["comments"])
        # if a transferd comment points back to the initial card, remove this comment.
        indirect_comments = removeTransBack(indirect_comments, ca.id)
        indirect_comments = removeDuplicate(indirect_comments)
        # append indirect comments to direct_comments, merge two dictionaries with same label,the label is the id of the card.
        direct_comments_list[ca.id]["comments"].extend(indirect_comments)
        direct_comments_list[ca.id]["count"] += len(indirect_comments)

        setattr(ca,'comments_list',direct_comments_list[ca.id]["comments"])
        setattr(ca,'comments_count',direct_comments_list[ca.id]["count"])

    context = {
        'game': game,
        'cards': cards,
        'games': games
    }
    return render(request, 'games/detail.html', context)

def download(request, game_id):
    game = get_object_or_404(Game, pk = game_id)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = "attachment;filename=dataset.xls"

    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet('sheet1')
    sheet.write(0, 0, game.field_name_1)
    sheet.write(0, 1, game.field_name_2)
    sheet.write(0, 2, game.field_name_3)
    sheet.write(0, 3, game.field_name_4)
    sheet.write(0, 4, game.field_name_5)
    sheet.write(0, 5, game.field_name_6)

    data_row = 1
    a = game.game_card.all()
    for i in a:
        sheet.write(data_row, 0, i.field_1)
        sheet.write(data_row, 1, i.field_2)
        sheet.write(data_row, 2, i.field_3)
        sheet.write(data_row, 3, i.field_4)
        sheet.write(data_row, 4, i.field_5)
        sheet.write(data_row, 5, i.field_6)
        data_row = data_row + 1

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response
