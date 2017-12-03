#!/usr/bin/python2.7

# 1. 用于处理流文件，统计统计量
#       1. 均值，最值， 方差， 标准差

# 2. 更改类标签。
#        1. txt -> 1
#        2. pic -> 2
#        3. red_wallet -> 3
#        4. trans_money -> 4
#        5. other -> 5



from sys import argv
class Ob(object):
    def __init__(self, ip, str1, str2, str3, str4, str5, str6, str7):
        self.str_pre = ip + "  " + str1 + "  " + str2 + "  " + str3
        self.str4 = str4
        self.str5 = str5
        self.str6 = str6
        self.str7 = str7

    def __str__(self):
        return self.str_pre


def create_ob(split_strs):
    ob = Ob(split_strs[0], split_strs[1], split_strs[2], split_strs[3], split_strs[4], split_strs[5], split_strs[6], split_strs[7])
    return ob

def print_math(*tup):
    if len(tup) != 0:
        avg = sum(tup)/len(tup)
    else:
        return;
    var = 0
    for i in range(len(tup)):
        var += (tup[i] - avg) * (tup[i] - avg)

    var = var/len(tup)
    sta_var = var ** 0.5

    #print("max = %d, min = %d, avg = %d, var = %d, sta_var = %d" % (max(tup), min(tup), avg, var, sta_var))

    str1 = str(max(tup)) + ' ' + str(min(tup)) +  ' ' + str(avg) + ' ' + str(var) + ' ' + str(sta_var) + ' '
    result.write(str1)
    #print(str1)

def char_int(s):
    if s == "txt":
        return "1"
    if s == "pic":
        return "3"
    if s == "red_wallet":
        return "3"
    if s == "trans_money":
        return "4"

    return "5"


def handle():
    obs_map = {}
    obs = []
    l = []
    tup = ()
    
    with open(first) as file:
        for line in file:
            line = line.strip('\n')
            split_strs = line.split('  ')
            ob = create_ob(split_strs)
            obs.append(ob)
 
    for ob_iter in obs:
        if obs_map.get(ob_iter.str_pre):
            l = obs_map.get(ob_iter.str_pre)
            l[0] = l[0] + 1
            if (ob_iter.str5 == "SYN" or ob_iter.str5 == "SYN + ACK"):
                l[2] = l[2] + 1
            else :
                l[1].append(int(ob_iter.str6))
        else:
            #size = [int(ob_iter.str6)]
            #print(size)
            if (ob_iter.str5 == "SYN" or ob_iter.str5 == "SYN + ACK"):
                obs_map.setdefault(ob_iter.str_pre, [1, [], 1, ob_iter.str7])
            else:
                obs_map.setdefault(ob_iter.str_pre, [1, [int(ob_iter.str6)], 0, ob_iter.str7])


    for key, value in obs_map.items():

        #print(key, value[0], value[1], value[2])
        #result.writelines(key + '\n')
        #print(value[1])

        str_con = ''
        for i in value[1]:
            str_con +=  str(i) + ' '
 
       
        if value[3] == "other":
            continue

        if value[3] == "txt":
            str3 = "1"
        if value[3] == "pic":
            str3 = "2"
        if value[3] == "red_wallet":
            str3 = "3"
        if value[3] == "trans_money":
            str3 = "4"
        

        print_math(*tuple(value[1]))

        string = str(value[0]) + ' ' + str(value[2]) + ' ' + str3 + '\n'
        result.writelines(string)
        #print(string)
        


script, first, second = argv
result = open(second, "w+")
handle()
