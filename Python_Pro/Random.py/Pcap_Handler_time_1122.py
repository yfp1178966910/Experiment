# -- conding:utf-8 --

import dpkt
import socket
import sys
import time
import  math
import csv

def flags_trans(flag):
    if flag == 16:
        return "ACK"
    if flag == 24:
        return "PSH + ACK"
    if flag == 17:
        return "FIN + ACK"
    if flag == 2:
        return "SYN"
    if flag == 18:
        return "SYN + ACK"

    return "else"

def is_hand(flag):
    return  flags_trans(flag) == "SYN" or flags_trans(flag) == "SYN + ACK" \
            or flags_trans(flag) == "FIN + ACK"

# 去除tcp载荷中为0的元素，返回最终的列表长度
def list_no_Zero(list):
    i = 0
    while i < len(list):
        if list[i] == 0:
            list.pop(i)
            i -= 1
        i += 1
    return len(list)

def class_judge(file):
    col = []
    reader = csv.reader(file)
    for row in reader:
        for i in range(len(row)-1):
            col.append([])
            col[i].append(int(row[i]))
            col[i].append(int(row[i+1]))

    i = 0
    while i < len(col):
        if len(col[i]) == 0:
            col.pop(i)
            i -= 1
        i += 1
    return col

# 红包和转账分为接收和发送两类
def class_Coarse_Grained(class_value):
    if class_value >=0 and class_value <= 4:
        return 1
    if class_value >4 and class_value <=9:
        return 2

# 红包和转账步骤分为多类
def class_Fine_Grained(class_value):
    if class_value == 1 or class_value == 0:  # red_send
        return 1
    if class_value == 2 or class_value == 3:
        return 2
    if class_value == 4:
        return 3
    if class_value == 5:
        return 4
    if class_value == 6:
        return 5
    if class_value == 7 or class_value == 8:
        return 6
    if class_value == 9:
        return 7

    return -100


# 红包分类标记，根据数据包序号
def class_red(num):
    for class_value in range(len(csv_red)):
        i = 0
        while i < len(csv_red[class_value]):
            if num >= csv_red[class_value][i] and num <= csv_red[class_value][i+1]:
                #print(csv_red[class_value][i]+1, csv_red[class_value][i + 1], num, class_value)
                #return 3
                return 30 + class_Fine_Grained(class_value)
                #return 30 + class_Coarse_Grained(class_value)

            i = i + 2
    return -1

# 转账分类标记，根据数据包序号
def class_transfer(num):
    for class_value in range(len(csv_trans)):
        i = 0
        while i < len(csv_trans[class_value]):
            if num > csv_trans[class_value][i] and num <= csv_trans[class_value][i+1]:
                print(csv_trans[class_value][i], csv_trans[class_value][i + 1], num, class_value)
                #return 4
                return 40 + class_Fine_Grained(class_value)
                #return 40 + class_Coarse_Grained(class_value)

            i = i + 2
    return -1

# 有效载荷的相关统计量， 去掉载荷是0的数据包
def pcap_math(packet):
    sum_payload = sum(packet)
    avg = sum_payload / len(packet)
    div = 0
    for i in packet:
        div += (i - avg) * (i - avg)
    stand = div ** 0.5
    return str(sum_payload) + ',' + str(avg) + ',' + str(max(packet)) + ',' + str(min(packet)) + ',' + str(div) + ',' + str(stand)

# 流的相关统计量
def flow_statics(flow):
    ret = []
    ret.append(len(flow))
    #print(ret)
    return ret

# pcap文件的处理
def printPcap(pcap, file_class):
    #file = open('flow.txt', 'w+')
    class_value = -1
    num = 0
    temp = -2.0
    flow_map = {}
    time_map = {}
    flow_stat = []
    flow_info = []
    tcp_seq = []
    tcp_ack = []
    global time_interval
    global else_class
    for (ts, buf) in pcap:
        num += 1
        #print(num)
        time_local = time.localtime(ts)
        #print(ts, time.strftime("%Y-%m-%d %H:%M:%S",time_local))
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data

        #print(ts, temp)
        if ip.data.__class__.__name__ =='TCP':
            ip_src = socket.inet_ntoa(ip.src)
            ip_dst = socket.inet_ntoa(ip.dst)

            # 对不同的流量类型采用不同的分类标记方法
            if file_class == 3:
                class_value = class_red(num)
            if file_class == 4:
                class_value = class_transfer(num)
            if file_class == 1:
                class_value = 1
            if file_class == 2:
                class_value = 2

            tcp = ip.data
            ip_string = str(ip_src) + ':' + str(tcp.sport) + '--' + str(ip_dst) + ':' + str(tcp.dport)



            #class_value = class_trace()
            if ts-temp <= 1 :
                temp = ts
                if time_map.get(time_interval):
                    packet = time_map.get(time_interval)
                    packet[0].append(len(tcp.data))  # 载荷长度
                    packet[1].append(ts)             # 时间戳信息
                    packet[2].append(flags_trans(tcp.flags))   # tcp标志
                    if is_hand(tcp.flags):
                        packet[3] = packet[3] + 1              # tcp连接数量

                    if flow_map.get(ip_string):
                        flow_info = flow_map.get(ip_string)
                        flow_info[0] = flow_info[0] + 1    # 流内数据包数量
                        flow_info[1].append(len(tcp.data))   # 流内包载荷
                    else:
                        flow_map.setdefault(ip_string, [1, [len(tcp.data)]])

                # else:
                #     print("this is a test")
                #     return
                #     time_interval = time_interval + 1
                #     temp = ts
                #     #print("this is a test")
                #
                #     if flow_map.get(ip_string):
                #         flow_info = flow_map.get(ip_string)
                #         flow_info[0] = flow_info[0] + 1
                #         flow_info[1].append(len(tcp.data))
                #     else:
                #         flow_map.setdefault(ip_string, [1, [len(tcp.data)]])
                #
                #     if is_hand(tcp.flags):
                #         time_map.setdefault(time_interval, [[len(tcp.data)], [ts], [flags_trans(tcp.flags)], 1, class_value])
                #     else:
                #         time_map.setdefault(time_interval, [[len(tcp.data)], [ts], [flags_trans(tcp.flags)], 0, class_value])

            else:
                time_interval = time_interval + 1
                temp = ts
                if len(flow_map) != 0:
                    flow_stat.append(flow_statics(flow_map))
                    print(flow_map, num)
                    flow_map = {}               # 上一个dialog的流信息记录到flow_stat

                if flow_map.get(ip_string):
                    flow_info = flow_map.get(ip_string)
                    flow_info[0] = flow_info[0] + 1
                    flow_info[1].append(len(tcp.data))
                else:
                    flow_map.setdefault(ip_string, [1, [len(tcp.data)]])

                if is_hand(tcp.flags):
                    time_map.setdefault(time_interval, [[len(tcp.data)], [ts], [flags_trans(tcp.flags)], 1, class_value])
                else:
                    time_map.setdefault(time_interval, [[len(tcp.data)], [ts], [flags_trans(tcp.flags)], 0, class_value])

    flow_stat.append(flow_statics(flow_map))

    #print(flow_stat)
    txt_num = 0
    pic_num = 0
    red_num = 0
    trans_num = 0
    i = 0
    for key, value in time_map.items():
        #pass
       # print(value[-1])
        #print(key, value[0], value[-1])
        packet_num = len(value[0])  # 数据包的数量

        if value[-1] == 1:
            txt_num += 1
        if value[-1] == 2:
            pic_num += 1
        if value[-1]/30 < 4 and value[-1]/30 >= 3:
            red_num += 1
        if value[-1]/40 >= 4:
            trans_num += 1

        if value[-1] == -1:
            i += 1
            continue
        # else:
        #     print(value[-1], value)
        if list_no_Zero(value[0]) == 0:   # 如果tcp载荷全部为0， 则剪枝，数据包数量仍然是真实的数据包数量
            continue

        ack_num = 0  # ack数量
        tcp_num = 0
        for ack in value[2]:
            if ack == "ACK":
                ack_num = ack_num + 1
            if ack == "FIN + ACK" or ack == "SYN" or ack == "SYN + ACK":
                tcp_num = tcp_num + 1

        math_statics = pcap_math(value[0])      # 载荷的相关统计量

        time_duration = (value[1][-1] - value[1][0])    # 持续时间

        #print(time_duration)
        if time_duration != 0:
            avg_byte = sum(value[0])/time_duration      # 平均包大小
        else:
            avg_byte = 0

        #流信息， 存储的方式是字典
        #print(flow_stat[i][-1])
        result.write(str(flow_stat[i][-1]))
        # if value[-1] >= 30 and value[-1] < 35:
        #     red_send.write(str(i))
        # if value[-1] >= 35 and value[-1] <= 39:
        #     red_rev.write(str(i))
        # if value[-1] >= 40 and value[-1] < 45:
        #     transfer_send.write(str(i))
        # if value[-1] >= 45 and value[-1] <= 49:
    #     transfer_rev.write(str(i))
        i += 1

        result.write(',' + str(packet_num) + ',' + str(value[3]) + ',' + str(ack_num) + ',' + str(math_statics) + ',' + str(time_duration) + ',' + str(avg_byte) + ','
                     + str(value[-1]) + '\n')
        # if value[-1] >= 30 and value[-1] < 35:
        #     red_send.write(',' + str(packet_num) + ',' + str(ack_num) + ',' +
        #                    str(math_statics) + ',' + str(time_duration) + ',' + str(avg_byte) + ','+
        #                    str(value[-1] - 30) + '\n')
        # if value[-1] >= 35 and value[-1] < 40:
        #     red_rev.write(',' + str(packet_num) + ',' + str(ack_num) + ',' +
        #                   str(math_statics) + ',' + str(time_duration) + ',' + str(avg_byte) + ','+
        #                   str(value[-1] - 30) + '\n')
        #
        # if value[-1] >= 40 and value[-1] <= 44:
        #     transfer_send.write(',' + str(packet_num) + ',' + str(ack_num) + ',' +
        #                         str(math_statics) + ',' + str(time_duration) + ',' + str(avg_byte) + ','+
        #                         str(value[-1] - 40) + '\n')
        # if value[-1] >= 45 and value[-1] <= 50:
        #     transfer_rev.write(',' + str(packet_num) + ',' + str(ack_num) + ',' +
        #                        str(math_statics) + ',' + str(time_duration) + ',' + str(avg_byte) + ',' +
        #                        str(value[-1] - 40) + '\n')
        #print(ack_num, math_statics, time_duration, avg_byte, value[-1])
    #print(txt_num, pic_num, red_num, trans_num)


#filename = sys.argv[1]
f1 = open('./data_second_step/txt_1122.pcap', 'rb')
f2 = open('./data_second_step/pic_1126.pcap', 'rb')
f3 = open('./data_second_step/red_packet_1126.pcap', 'rb')
f4 = open('./data_second_step/transfer_1126.pcap', 'rb')

csv_1 = open('./data_second_step/red_send_1126.csv', 'r')
csv_2 = open('./data_second_step/red_rev_1126.csv', 'r')
csv_3 = open('./data_second_step/transfer_send_1126.csv', 'r')
csv_4 = open('./data_second_step/transfer_rev_1126.csv', 'r')

csv_red= class_judge(csv_1)
for red in class_judge(csv_2):
    csv_red.append(red)

csv_trans = class_judge(csv_3)
for trans in class_judge(csv_4):
    csv_trans.append(trans)



result = open('flow_1201.csv', 'w+')
# red_send = open('red_send.csv', 'w+')
# red_rev = open('red_rev.csv', 'w+')
# transfer_send = open('trans_send.csv', 'w+')
# transfer_rev = open('trans_rev.csv', 'w+')

# red = open('red.csv', 'w+')
# trans = open('trans.csv', 'w+')

time_interval = 0
else_class = 0
printPcap(dpkt.pcap.Reader(f1), 1)
printPcap(dpkt.pcap.Reader(f2), 2)
printPcap(dpkt.pcap.Reader(f3), 3)
printPcap(dpkt.pcap.Reader(f4), 4)


