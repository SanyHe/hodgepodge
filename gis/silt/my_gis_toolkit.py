#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by 何灿 Sany 2020/11/21

import numpy as np
import pandas as pd
import re

KEY_WORD1 = "淤泥"
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

def find_zero(data_filtered, basic_data):
    """区分非零值的钻孔编号和零值的钻孔编号

    :param data_filtered: 筛选出的在一定范围内的数据集
    :param basic_data: 基本信息的数据集
    :return: list，非零值的钻孔编号，零值的钻孔编号
    """
    none_zero_serial = data_filtered["钻孔编号"].unique()
    serial = basic_data["钻孔编号"].unique()
    none_zero_index = []
    for i in range(none_zero_serial.shape[0]):
        for j in range(serial.shape[0]):
            if none_zero_serial[i] == serial[j]:
                none_zero_index.append(j)
    zero_index = [k for k in range(serial.shape[0]) if k not in none_zero_index]
    zero_serial = [serial[zero_index[h]] for h in range(len(zero_index))]
    return zero_serial, none_zero_serial

def list2dict(zero_serial, none_zero_serial):
    """建立钻孔编号数据字典，初始值为0

    :param zero_serial: list，零值的钻孔编号
    :param none_zero_serial: list，非零值的钻孔编号
    :return: dict，零值的钻孔编号，非零值的钻孔编号
    """
    zero_dict = {}
    none_zero_dict = {}
    for i in range(len(zero_serial)):
        zero_dict[zero_serial[i]] = 0
    for j in range(len(none_zero_serial)):
        none_zero_dict[none_zero_serial[j]] = 0
    return zero_dict, none_zero_dict

def merge_thickness(data_filtered, basic_data):
    """计算各钻孔编号，指定范围内砂层的累计厚度

    :param data_filtered: 筛选出的在一定范围内的数据集
    :param basic_data: 基本信息的数据集
    :return: 含有累计厚度的各钻孔的数据集
    """
    zero_serial, none_zero_serial = find_zero(data_filtered, basic_data)
    zero_dict, none_zero_dict = list2dict(zero_serial, none_zero_serial)
    for i in range(data_filtered["钻孔编号"].shape[0]):
        none_zero_dict[data_filtered["钻孔编号"].iloc[i]] += data_filtered["分层厚度"].iloc[i]
    none_zero_dict.update(zero_dict)
    temp = [none_zero_dict[basic_data["钻孔编号"].iloc[j]] for j in range(basic_data["钻孔编号"].shape[0])]
    basic_data["淤泥的厚度"] = np.array(temp)
    return basic_data

def is_thick(data_thick):
    """以1和0形式给非零值的钻孔编号和零值的钻孔编号打上标签

    :param data_thick: 含有累计厚度的各钻孔信息的数据集
    :return: 含有累计厚度、标签值的各钻孔信息的数据集
    """
    temp = []
    for i in range(data_thick["淤泥的厚度"].shape[0]):
        if data_thick["淤泥的厚度"].iloc[i] != 0:
            temp.append(1)
        else:
            temp.append(0)
    data_thick["厚度类型"] = np.array(temp)
    return data_thick

def df2excel(data, sheet_name):
    """以xlsx的格式导出数据集

    :param data: 待导出的数据集
    :param sheet_name: 表格名
    """
    writer = pd.ExcelWriter(sheet_name + ".xlsx")
    data.to_excel(writer)
    writer.save()


