#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import time
import re

KEY_WORD1 = "砂"
KEY_WORD2 = "砂质"
KEY_WORD3 = "含砂"
RANGE_LEFT = -50
RANGE_RIGHT = -15

def is_sand(single_data):
    """判断数据点是否为砂

    :param single_data: 单个数据点
    :return: 布尔值，真，则该数据点为砂，假，则该数据点不为砂
    """
    global KEY_WORD1, KEY_WORD2, KEY_WORD3

    ismatch1 = re.search(KEY_WORD1, single_data)
    flag = True if ismatch1 is not None else False
    ismatch2 = re.search(KEY_WORD2, single_data)
    ismatch3 = re.search(KEY_WORD3, single_data)
    if ismatch2 or ismatch3 is not None:
        flag = False
    return flag

def extract(data):
    """筛选出岩性为砂的数据

    :param data: 待筛选的数据集
    :return: 岩石为砂的数据集
    """
    flag = data['岩石名称'].map(is_sand)
    return data[flag]

def real_depth(strat_data, basic_data):
    """计算实际层顶埋深和实际层底埋深

    :param strat_data: 名为分层信息的数据集
    :param basic_data: 名为基本信息的数据集
    :return: 含有实际层顶埋深、实际层底埋深、孔口高程、x坐标、y坐标的数据集（原数据集为分层信息的数据集）
    """
    orifice_elev = []
    x_coordinate = []
    y_coordinate = []
    basic_data["孔口高程"] = basic_data["孔口高程"].fillna(0)
    for i in range(strat_data.shape[0]):
        for j in range(basic_data.shape[0]):
            if strat_data["钻孔编号"].iloc[i] == basic_data["钻孔编号"].iloc[j]:
                orifice_elev.append(basic_data["孔口高程"].iloc[j])
                x_coordinate.append(basic_data["X坐标"].iloc[j])
                y_coordinate.append(basic_data["Y坐标"].iloc[j])
    strat_data.loc[:, "孔口高程"] = np.array(orifice_elev).reshape(-1, 1)
    strat_data.loc[:, "X坐标"] = np.array(x_coordinate).reshape(-1, 1)
    strat_data.loc[:, "Y坐标"] = np.array(y_coordinate).reshape(-1, 1)
    strat_data.loc[:, "实际层顶埋深"] = strat_data["孔口高程"] - strat_data["层顶埋深"]
    strat_data.loc[:, "实际层底埋深"] = strat_data["孔口高程"] - strat_data["层底埋深"]
    return strat_data

def range_filter(data):
    """筛选出指定范围内的数据

    :param data: 含有实际层顶埋深和实际层底埋深数据的待筛选的数据集
    :return: 在指定范围内的数据集
    """
    global RANGE_LEFT, RANGE_RIGHT

    flag1 = data["实际层顶埋深"].map(lambda x: RANGE_LEFT <= x <= RANGE_RIGHT)
    flag2 = data["实际层底埋深"].map(lambda x: RANGE_LEFT <= x <= RANGE_RIGHT)
    flag = flag1.copy()
    for i in range(flag1.shape[0]):
        if (flag1.iloc[i] == True) and (flag2.iloc[i] == True):
            flag.iloc[i] = True
        else:
            flag.iloc[i] = False
    return data[flag]

def df2excel(data, sheet_name):
    """以xlsx的格式导出数据集

    :param data: 待导出的数据集
    :param sheet_name: 表格名
    """
    writer = pd.ExcelWriter(sheet_name + ".xlsx")
    data.to_excel(writer)
    writer.save()


def main():

    start = time.time()
    print("-"*20, "RUNNING", "-"*20)

    # 忽略警告
    pd.set_option('mode.chained_assignment', None)

    # 读取数据
    strat_data = pd.read_excel("分层信息.xlsx")
    basic_data = pd.read_excel("基本信息.xlsx")

    # 筛选出实际的砂层数据
    data_extracted = extract(strat_data)

    # 计算实际层顶埋深和实际层底埋深，将前两者、孔口高程、xy坐标附加在表后
    data_real = real_depth(data_extracted, basic_data)

    # 按照指定的范围进一步筛选数据
    data_range = range_filter(data_real)

    # 将数据以excel表格的形式输出
    df2excel(data_range, "砂层")

    end = time.time()
    print("RUN SUCCESSFULLY")
    print("Time:{}s".format(end - start))
    print("-" * 49)

if __name__ == '__main__':
    main()
