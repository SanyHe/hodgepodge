#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by 何灿 Sany 2020/11/21

from my_gis_toolkit import *
import pandas as pd
import time

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
    data_filtered = range_filter(data_real)

    # 算出各钻孔指定范围内砂层的累计厚度，并将累计厚度附在表后
    data_thick = merge_thickness(data_filtered, basic_data)

    # 以1和0区分有累计厚度和无厚度两类，并将标签附在表后
    data_thick_type = is_thick(data_thick)

    # 将数据以excel表格的形式输出，"砂层"是各钻孔多层砂岩的详细数据，"arcgis_data"是用于arcgis处理的数据
    df2excel(data_filtered, "砂层")
    df2excel(data_thick_type, "arcgis_data")

    end = time.time()
    print("RUN SUCCESSFULLY")
    print("Time:{}s".format(end - start))
    print("-" * 49)

if __name__ == '__main__':
    main()



