#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# EjeCasher

import os
import sys
import time
import json
from guizero import App, Box, PushButton, Text, ListBox
from escpos import printer
from receipt import receipt_print

# common
def update_total(label):
    label.clear()
    label.append("合計: %s 円" % total)

def clear_cart():
    global cart, total
    cart = dict()
    total = 0
    main_listbox.clear()
    main_pay_button.enabled = False
    update_total(main_total)

# screen_main
def start_without_printer():
    page_reset()

def category_clicked(c):
    global item_category
    if item_category == c:
        return
    main_itemboxes[item_category].visible = False
    main_itemboxes[c].visible = True
    item_category = c

def item_clicked(c):
    global total
    total = 0

    if c in cart:
        cart[c] += 1
    else:
        cart[c] = 1

    main_listbox.clear()
    for i,c in cart.items():
        subtotal = c * int(items[i]['price'])
        total = total + subtotal
        main_listbox.append(items[i]['short'] + ' x ' + str(c) + "  ￥" + str(subtotal))
        if len(cart) == 1 and 'not_allow_single' in items[i]:
            main_pay_button.enabled = False
        else:
            main_pay_button.enabled = True
    update_total(main_total)

# screen_pay_method
def page_2():
    if not total:
        return
    screen_main.visible = False
    screen_pay_method.visible = True
    update_total(pay_method_total)

def pay_selected(method):
    # 支払い選択画面から各画面への遷移
    screen_pay_method.visible = False
    if method == 1:
        page_3_japanpay()
    elif method == 2:
        page_3_card()
    else:
        # back
        screen_main.visible = True

# screen_pay_japanpay
def page_3_japanpay():
    update_total(pay_japanpay_total)
    screen_pay_japanpay.visible = True
    # JSでいうsetTimeoutみたいなやつ
    pay_japanpay_total.after(5000, page_3_japanpay_keypad)

def page_3_japanpay_keypad():
    screen_pay_japanpay.visible = False
    screen_keypad.visible = True
    keypad_change.clear()
    update_total(keypad_total)

def keypad_update():
    keypad_result_label.clear()
    keypad_result_label.append("¥{:,}".format(int(keypad_buf)))

def keypad_input(i):
    global keypad_buf
    if i < 10:
        if keypad_buf == "0":
            keypad_buf = ""
        keypad_buf += str(i)
    elif i == 10:
        keypad_buf = "0"
        keypad_change.clear()
    elif i == 11:
        l = int(keypad_buf)
        if l >= total:
            keypad_buf = "0"
            screen_keypad.visible = False
            page_4("現金預かり", l)
    elif i == 12:
        keypad_buf = "0"
        screen_keypad.visible = False
        screen_pay_method.visible = True
        
    keypad_update()
    change = int(keypad_buf) - total
    keypad_change.clear()
    if 0 <= change:
        keypad_change.append("お釣り: %s円" % (change))
    elif change < 0:
        keypad_change.append("金額が不足しています")


# screen_pay_japanpay
def page_3_card():
    update_total(pay_card_total)
    screen_pay_card.visible = True
    pay_japanpay_total.after(5000, page_3_card_confirm)

def page_3_card_confirm():
    update_total(pay_card_confirm_total)
    screen_pay_card.visible = False
    screen_pay_card_confirm.visible = True

def page_3_card_cancel():
    screen_pay_card_confirm.visible = False
    screen_pay_method.visible = True

def page_3_card_confirmed():
    screen_pay_card_confirm.visible = False
    # カード払いは全額受け取った扱いにする
    page_4("クレカ/交通IC/iD", total)

# screen_thanks
def page_4(m, received):
    screen_thanks.visible = True
    thanks_label.after(5000, page_reset)

    # ウリアージュをレコードする
    now = time.strftime("%Y-%m-%d,%H:%M:%S")
    with open(os.path.join(os.path.dirname(__file__), "uriage-items.csv"), "a") as f:
        for i,c in cart.items():
            item = items[i]
            name = item["name"].replace("\n", "")
            subtotal = c * int(item["price"])
            f.write("%s,%s,%s,%s\n" % (now, name, c, subtotal))
    with open(os.path.join(os.path.dirname(__file__), "uriage-transaction.csv"), "a") as f:
        f.write("%s,%s,%s\n" % (now, m, total))

    # レシートを印刷する
    if Printer:
        receipt_print(Printer, items, cart, total, m, received)

def page_reset():
    clear_cart()
    screen_thanks.visible = False
    screen_main.visible = True

def page_0():
    global Printer
    try:
        Printer = printer.Usb(0x08a6,0x0041)
        screen_check.visible = False
        screen_main.visible = True
    except:
        check_printer_status.clear()
        check_printer_status.append("プリンターが見つかりません")
        check_printer_status.after(1000, page_0)

def page_0_noprinter():
    screen_check.visible = False
    screen_main.visible = True


#####

cart = dict()
total = 0
keypad_buf = "0"
Printer = False

with open(os.path.join(os.path.dirname(__file__), 'items.json')) as f:
    items = json.loads(f.read())

with open(os.path.join(os.path.dirname(__file__), 'categories.json')) as f:
    categories = json.loads(f.read())

app = App(title="EjeCasher")
app.full_screen = True

screen_check = Box(app, visible=False, width="fill", align="left")
check_printer_status = Text(screen_check, text="レシートプリンターを\n接続してください", size=36, height=2)
b = PushButton(screen_check, text="プリンターなしではじめる", command=page_0_noprinter)
b.text_size = 20

# main screen
item_category = 0
screen_main = Box(app, visible=False, width="fill", height="fill")
main_left = Box(screen_main, layout="grid", width="fill", height="fill", align="left")
main_cartbox = Box(screen_main, width="fill", align="right")

main_categorybox = Box(main_left, grid=[0,0], layout="grid", width="fill", align="left")
Text(main_categorybox, grid=[0,0], text="カテゴリー: ")
category_button = list()
main_itemboxes = list()
for cat_c,i in enumerate(categories):
    category_button.append(PushButton(main_categorybox, grid=[cat_c+1,0], text=i['name'], command=category_clicked, args=[cat_c]))
    category_button[cat_c].text_size = 14
    main_itemboxes.append(Box(main_left, grid=[0,1], layout="grid", width="fill", align="left", visible=False))
    button = list()
    coordinate_count = 0
    for c,i in enumerate(items):
        if i['category'] != cat_c:
            continue
        x = coordinate_count % 4
        y = int(coordinate_count / 4) * 4
        coordinate_count += 1
        image = os.path.join(os.path.dirname(__file__), i['image'])
        button.append(PushButton(main_itemboxes[cat_c], grid=[x,y], image=image, command=item_clicked, args=[c]))
        Text(main_itemboxes[cat_c], grid=[x,y+1], text=i['name'])
        Text(main_itemboxes[cat_c], grid=[x,y+2], text="￥"+i['price'])
main_itemboxes[item_category].visible = True

Text(main_cartbox, text="選択した商品:")
main_listbox = ListBox(main_cartbox, items=[], width="fill")
b = PushButton(main_cartbox, width="fill", text="キャンセル", command=clear_cart)
b.text_size = 20
main_total = Text(main_cartbox, text="")
update_total(main_total)
main_total.text_size = 20
main_pay_button = PushButton(main_cartbox, width="fill", text="購入", command=page_2, enabled=False)
main_pay_button.text_size = 20

# select pay method screen
screen_pay_method = Box(app, visible=False)
pay_method_total = Text(screen_pay_method, text="", size=36)
Text(screen_pay_method, text="支払い方法をえらんでください", size=36, height=2)
pay_method_labels = ["もどる", "現金トレイ渡し", "クレジットカード/交通IC/iD"]
for i in range(1, 4):
    j = i % 3
    b = PushButton(screen_pay_method, text=pay_method_labels[j], padx=30, pady=30, command=pay_selected, args=[j])
    b.text_size = 24

# pay japanpay screen
screen_pay_japanpay = Box(app, visible=False)
Text(screen_pay_japanpay, text="\nトレイにお金をおいてください", size=40, height=2)
pay_japanpay_total = Text(screen_pay_japanpay, text="", size=40)

# keypad screen
screen_keypad = Box(app, visible=False)
Box(screen_keypad, width=30, height="fill", align="left")
keypad_top = Box(screen_keypad, width="fill", align="top")
keypad_button = Box(screen_keypad, layout="grid", width="fill", align="left")
Box(screen_keypad, width=30, height="fill", align="left")
keypad_result = Box(screen_keypad, layout="grid", width="fill", align="left")
Box(screen_keypad, width=30, height="fill", align="left")
button = list()
for i in range(0,10):
    x = int((i + 2) % 3) if i else 0
    y = 3 - int((i + 2) / 3)
    button.append(PushButton(keypad_button, text=str(i), grid=[x,y], padx=30, command=keypad_input, args=[i]))
Text(keypad_top, text="金額入力", size=40)
button.append(PushButton(keypad_button, text="X", grid=[1,3], padx=30, command=keypad_input, args=[12]))
button.append(PushButton(keypad_button, text="C", grid=[2,3], padx=30, command=keypad_input, args=[10]))
keypad_total = Text(keypad_result, text="", size=20, grid=[0,0], align="left")
keypad_change = Text(keypad_result, text="", size=20, grid=[0,1], align="left")
Text(keypad_result, text="お預かり金額:", size=40, grid=[0,2], align="left")
keypad_result_label = Text(keypad_result, text="¥0", size=40, grid=[0,3], align="right")

button.append(PushButton(keypad_result, text="決　定", grid=[0,4], padx=120, command=keypad_input, args=[11]))
for b in button:
    b.text_size = 40

# pay card screen
screen_pay_card = Box(app, visible=False)
Text(screen_pay_card, text=" \n端末を用意します。\nお待ちください。", size=40)
pay_card_total = Text(screen_pay_card, text="", size=40)

# pay card confirm screen
screen_pay_card_confirm = Box(app, visible=False)
Text(screen_pay_card_confirm, text=" ", size=20)
pay_card_confirm_total = Text(screen_pay_card_confirm, text="", size=40)
Text(screen_pay_card_confirm, text=" ", size=40)
b = PushButton(screen_pay_card_confirm, text="支払い終わったら押す", command=page_3_card_confirmed)
b.text_size = 40
Text(screen_pay_card_confirm, text=" ", size=20)
b = PushButton(screen_pay_card_confirm, text="もどる", command=page_3_card_cancel)
b.text_size = 40

# thanks screen
screen_thanks = Box(app, visible=False)
Text(screen_thanks, text="商品とレシートをお渡しします", size=40, height=2)
thanks_label = Text(screen_thanks, text="ご購入ありがとうございました", size=40, height=2)

screen_check.visible = True
check_printer_status.after(10, page_0)
app.display()
