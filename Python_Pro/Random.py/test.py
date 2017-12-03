# import dpkt
# import socket
# import sys
# import time
# import  math
# import csv
#
# def printPacp(f1, f2):
#     ts_1 = []
#     ts_2 = []
#     ts_3 = []
#     for (ts,buf) in f1:
#         ts_1.append(ts)
#     for ts,buf in f2:
#         ts_2.append(ts)
#
#     for i in ts_1:
#         if i in ts_2:
#             ts_3.append(i)
#
#     print(ts_2)
#     print(ts_3)
#
# f1 = open('./data_test/red_packet_1122.pcap', 'rb')
# f2 = open('./data_test/red_packet_1123.pcap', 'rb')
# printPacp(dpkt.pcap.Reader(f1), dpkt.pcap.Reader(f2))

# class_value = [1, 4, 7]
# unique = set(class_value)
# lookup = dict()
#
# for index, value in enumerate(unique):
#     lookup[value] = index
#     class_value[index] = index+1
#
# print(lookup)
#
# print(class_value)

# def test():
#     l1 = []
#     l2 = [2]
#     if not l1:
#         print("this is a test")
#     return l1, l2
#
# l = test()

map = {1:2, 2:2}
print(len(map))