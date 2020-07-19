#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 展示小区图表信息（仅仅支持MAC）
# 1. 杀死之前启动的http服务器
# 2. 启动一个新的http服务器
# 3. 用浏览器打开生成的数据html文件

import pandas as pd
import argparse
from pyecharts import Bar

import os
import string
import time
from lib.utility.version import PYTHON_3

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='regression vm')
    parser.add_argument('--csv_file', help='csv file', default='xiaoqu.csv')
    parser.add_argument('--range', help='range', default='0,5')

    args = parser.parse_args()
    csv_file = args.csv_file
    [min_num, max_num] = args.range.split(',')
    min_num = int(min_num)
    max_num = int(max_num)

    try:
        import webbrowser as web
        auto_browse = True
    except Exception as e:
        auto_browse = False

    if auto_browse:
        try:
            if PYTHON_3:
                os.system("ps aux | grep python | grep http.server | grep -v grep | awk '{print $2}' | xargs kill")
                os.system("python3 -m http.server 8080 & > /dev/null 2>&1 ")
            else:
                os.system("ps aux | grep python | grep SimpleHTTPServer | grep -v grep | awk '{print $2}' | xargs kill")
                os.system("python -m SimpleHTTPServer 8080 & > /dev/null 2>&1 ")
        except Exception as e:
            print(e)

    # 注意，已经将分割符号转换成分号，因为有的小区名中有逗号
    names = ['district', 'area', 'name', 'price', 'on_sale']
    df = pd.read_csv(csv_file, encoding="utf-8", sep=";", names=names)
    # 打印总行数
    print("row number is {0}".format(len(df.index)))

    def format_price(price):
        formated_price = ''
        formated_price_number = -1
        for c in price:
            if c not in string.digits:
                break
            formated_price = formated_price + c
        if formated_price:
            formated_price_number = int(formated_price)
        return formated_price_number

    df.price = df.price.map(format_price)
    print(df.price)

    # 过滤房价为0的无效数据
    df = df[df.price > 0]
    # # 去除重复行
    # df = df.drop_duplicates()
    print("row number is {0}".format(len(df.index)))

    ####################################################
    # 最贵的小区排名
    ####################################################
    df.sort_values("price", ascending=False, inplace=True)
    city = df["area"][0]
    xqs = df["name"][min_num:max_num]
    prices = df["price"][min_num:max_num]
    bar = Bar("{0}小区均价".format(city))
    bar.add("小区均价前{},{}名".format(min_num+1, max_num), xqs, prices, is_stack=True, is_label_show=True, xaxis_interval=0, xaxis_rotate=45)
    bar.render(path="xiaoqu.html")

    ####################################################
    # 区县均价排名
    ####################################################
    district_df = df.groupby('district').mean()
    district_df = district_df.round(0)
    district_df.sort_values("price", ascending=False, inplace=True)
    print(district_df)
    districts = district_df.index.tolist()
    prices = district_df["price"]
    bar = Bar("{0}区县均价".format(city))
    bar.add("区县均价排名", districts, prices, is_stack=True, is_label_show=True, xaxis_interval=0, xaxis_rotate=45)
    bar.render(path="district.html")

    if auto_browse:
        web.open("http://localhost:8080/xiaoqu.html", new=0, autoraise=True)
        # web.open("http://localhost:8080/district.html", new=0, autoraise=True)
        # 确保页面打开
        time.sleep(15)


