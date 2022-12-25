#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from jptext import jptext
from unicodedata import east_asian_width

# https://note.nkmk.me/python-unicodedata-east-asian-width-count/
def mb_len(text):
    count = 0
    for c in text:
        if east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count

def receipt_print(Printer, items, cart, total, m, receive):
    # 1行32文字(太文字は0.1くらい増えるので注意)
    Printer.set(align="center",width=2,height=2,custom_size=True)
    Printer._raw(jptext("こくだランド\n"))
    Printer.set(align="center",width=1,height=1)
    Printer._raw(jptext("https://l.kokuda.org/\n"))
    Printer._raw(jptext("コミックマーケット101 西さ26b\n\n"))
    Printer.set(align="left",width=1,height=1)
    Printer._raw(jptext("ミ★こくだランドでお買い上げ\n"))
    Printer._raw(jptext("　　ありがとうございます。\n"))
    Printer._raw(jptext("来年はオフラインイベント復活の\n"))
    Printer._raw(jptext("兆し？またあちこちに参加できる\n"))
    Printer._raw(jptext("ようになるといいですねえ〜！\n\n"))

    now = time.strftime("%Y年%m月%d日 %H:%M\n\n")
    Printer._raw(jptext(now))

    for i,c in cart.items():
        item = items[i]["receipt"]
        subtotal = "{:,}".format(c * int(items[i]['price']))
        multi = ""
        m_len = 1
        if 1 < c:
            multi = "X%s " % c
            m_len = len(multi) + 1
        space_length = 32 - mb_len(item) - m_len - len(subtotal)
        space = " "*space_length
        Printer._raw(jptext("%s%s" % (item, space)))
        Printer.set(bold=True)
        Printer._raw(jptext(multi))
        Printer.set(bold=False)
        Printer._raw(jptext("%s\n" % subtotal))

    Printer._raw(jptext("-"*32 + "\n"))

    # 合計
    print_total = "￥{:,}".format(total)
    space = " "*(16 - 6 - mb_len(print_total))
    Printer.set(width=2,height=1,custom_size=True)
    Printer._raw(jptext("合　計%s%s\n" % (space, print_total)))
    Printer.set(width=1,height=1,custom_size=True)

    # 預かり
    print_receive = "￥{:,}".format(receive)
    space = " "*(32 - mb_len(m) - mb_len(print_receive))
    Printer._raw(jptext("%s%s%s\n" % (m, space, print_receive)))

    # あればお釣り
    change = receive - total
    if change:
        # お釣り計算
        print_change = "￥{:,}".format(change)
        space = " "*(16 - 6 - mb_len(print_change))
        Printer.set(width=2,height=1,custom_size=True)
        Printer._raw(jptext("お　釣%s%s\n" % (space, print_change)))
        Printer.set(width=1,height=1,custom_size=True)

    Printer._raw(jptext("上記領収致しました。\n\n\n"))
