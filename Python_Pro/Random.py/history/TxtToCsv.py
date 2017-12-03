# -- coding: utf-8 --

'''
txt -> csv。

csv文件：实际上就是使用逗号将每行的每个元素隔开
'''

import numpy as np
import pandas as pd

from sys import argv

script, first, second = argv
with open(first) as f:
    file = open(second, "w+")
    for line in f:
        str1 = line.replace(" ", ",")
        file.write(str1)







