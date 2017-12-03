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
    if flag == 16:
        return "ACK"

def is_hand(flag):
    return  flags_trans(flag) == "SYN" or flags_trans(flag) == "SYN + ACK" or flags_trans(flag) == "FIN + ACK"

def class_result(num):
    if num >= 0 and num <= 606:
        return 1
    if num >= 607 and num <= 1195:
        return 2
    if num >= 1196 and num <= 1681:
        return 3
    if num >= 1682 and num <= 1883:
        return 4

    return 5


def pcap_math(packet):
    sum_payload = sum(packet)


    avg = sum_payload / len(packet)
    div = 0
    for i in packet:
        div += (i - avg) * (i - avg)

    stand = div ** 0.5

    return str(sum_payload) + ',' + str(avg) + ',' + str(max(packet)) + ',' + str(min(packet)) + ',' + str(div) + ',' + str(stand)


def printPcap(pcap):
    #file = open('flow.txt', 'w+')
    flow_map = {}
    flow_info = []
    for (ts, buf) in pcap:
        print(int(ts))
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            ip_src = socket.inet_ntoa(ip.src)
            ip_dst = socket.inet_ntoa(ip.dst)

            if ip.data.__class__.__name__ =='TCP':
                tcp = ip.data
                #time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
                key_string = str(ip_src) + ':' + str(tcp.sport) + '--' + str(ip_dst) + ':' + str(tcp.dport)
                value_string = flags_trans(tcp.flags) + ' ' + str(len(tcp.data)) + ' ' + str(time_stamp)
                #file.write(key_string, value_string)
                #print(key_string, value_string)

                if flow_map.get(key_string):
                    flow_info = flow_map.get(key_string)
                    flow_info[1] = flow_info[1] + 1   # packet number
                    if is_hand(tcp.flags):
                        flow_info[2] = flow_info[2] + 1  #  tcp connection
                    else:
                        if len(tcp.data):
                            flow_info[3].append(int(len(tcp.data)))  # payload length

                else:
                    if is_hand(tcp.flags):
                        flow_map.setdefault(key_string, [value_string, 1, 1, []])
                    else:
                        flow_map.setdefault(key_string, [value_string, 1, 0, [int(len(tcp.data))]])

        except:
            pass

    for key, value in flow_map.items():
        if len(value[3]):
            #print(key, value[3])
            string = ',' + str(value[1]) + ',' + str(value[2]) + ',' + pcap_math(value[3]) + ',' + str(num) + '\n'
            result.write(key)
            result.write(string)



#filename = sys.argv[1]
f1 = open('train_txt_1116.pcap', 'rb')
f2 = open('train_pic_1116.pcap', 'rb')
f3 = open('train_red_1117.pcap', 'rb')
f4 = open('train_transfer_1116.pcap', 'rb')

result = open('flow.csv', 'w+')

print("start work")
num = 1
printPcap(dpkt.pcap.Reader(f1))
num = 2
#result.write(str(1) + '\n')
printPcap(dpkt.pcap.Reader(f2))
num = 3
#result.write(str(2) + '\n')
printPcap(dpkt.pcap.Reader(f3))
num = 4
#result.write(str(3) + '\n')
printPcap(dpkt.pcap.Reader(f4))
#result.write(str(4) + '\n')


