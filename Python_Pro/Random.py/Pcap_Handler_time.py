# -- conding:utf-8 --

import dpkt
import socket
import sys
import time
import  math

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
    return  flags_trans(flag) == "SYN" or flags_trans(flag) == "SYN + ACK" or flags_trans(flag) == "FIN + ACK"

def class_trace(num):
    if num >= 0 and num <= 606:
        return 1
    if num >= 607 and num <= 1195:
        return 2
    if num >= 1196 and num <= 1681:
        return 3
    if num >= 1682 and num <= 1883:
        return 4

    return 5


# 有效载荷的相关统计量， 去掉载荷是0的数据包
def pcap_math(packet):
    sum_payload = sum(packet)

    i = 0
    while i < len(packet):
        if packet[i] == 0:
            packet.pop(i)
            i -= 1
        i += 1

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
    return ret

# pcap文件的处理
def printPcap(pcap, class_value):
    #file = open('flow.txt', 'w+')
    temp = 0.0
    flow_map = {}
    time_map = {}
    flow_stat = []
    flow_info = []
    global time_interval
    for (ts, buf) in pcap:
        time_local = time.localtime(ts)
        print(ts, time.strftime("%Y-%m-%d %H:%M:%S",time_local))
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data
        ip_src = socket.inet_ntoa(ip.src)
        ip_dst = socket.inet_ntoa(ip.dst)
        #print(ts, temp)
        if ip.data.__class__.__name__ =='TCP':
            tcp = ip.data
            ip_string = str(ip_src) + ':' + str(tcp.sport) + '--' + str(ip_dst) + ':' + str(tcp.dport)
            #class_value = class_trace()
            if ts-temp <= 1.0 :
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
                        flow_info[0] = flow_info[0] + 1    # 流内包数据量
                        flow_info[1].append(len(tcp.data))   # 流内包载荷
                    else:
                        flow_map.setdefault(ip_string, [1, [len(tcp.data)]])

                else:
                    time_interval = time_interval + 1
                    temp = ts
                    #print("this is a test")

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

            else:
                time_interval = time_interval + 1
                temp = ts
                if len(flow_map) != 0:
                    flow_stat.append(flow_statics(flow_map))

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


    for key, value in time_map.items():
        ack_num = 0  # ack数量
        for ack in value[2]:
            if ack == "ACK":
                ack_num = ack_num + 1

        packet_num = len(value[0])          # 数据包的数量
        math_statics = pcap_math(value[0])      # 载荷的相关统计量
        time_duration = (value[1][-1] - value[1][0])    # 持续时间
        #print(time_duration)
        if time_duration != 0:
            avg_byte = sum(value[0])/time_duration      # 平均包大小
        else:
            avg_byte = 0

        #流信息
        i = 0
        for i in flow_stat[i]:
            result.write(str(i))
        i += 1

        result.write(',' + str(packet_num) + ',' + str(ack_num) + ',' + str(math_statics) + ',' + str(time_duration) + ',' + str(avg_byte) + ','
                     + str(value[-1]) + '\n')
        print(ack_num, math_statics, time_duration, avg_byte, value[-1])


#filename = sys.argv[1]
f1 = open('./data_first_step/train_txt_1116.pcap', 'rb')
f2 = open('./data_first_step/train_pic_1116.pcap', 'rb')
f3 = open('./data_first_step/train_red_1117.pcap', 'rb')
f4 = open('./data_first_step/train_transfer_1116.pcap', 'rb')

result = open('flow.csv', 'w+')


time_interval = 0
printPcap(dpkt.pcap.Reader(f1), 1)
printPcap(dpkt.pcap.Reader(f2), 2)
printPcap(dpkt.pcap.Reader(f3), 3)
printPcap(dpkt.pcap.Reader(f4), 4)


