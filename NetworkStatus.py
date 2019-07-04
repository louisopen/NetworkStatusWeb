#!/usr/bin/env python
#coding:utf-8 
#
#pip install psutil
#
import time
import sys
try:
    import psutil
except ImportError:
    print('Error: psutil module not found!')
    exit()

def get_key():      #每個介面累積流量Bytes
    key_info = psutil.net_io_counters(pernic=True).keys()  # 網路介面訊息區域網路,bluebooth,WiFi
    recv = {}
    sent = {}
    #recv.setdefault(key, psutil.net_io_counters(pernic=False).bytes_recv)   #總接收數
    #sent.setdefault(key, psutil.net_io_counters(pernic=False).bytes_sent)   #總發射數
    for key in key_info:
        recv.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_recv)  #各個介面累積流量Bytes
        sent.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_sent)  #各個介面累積流量Bytes
    return key_info, recv, sent

def get_rate(func): #計算每個介面每秒收送速率MB/1s
    key_info, old_recv, old_sent = func()  # 上一秒收集的数据
    time.sleep(1) 
    key_info, now_recv, now_sent = func()  # 当前所收集的数据
    net_in = {}
    net_out = {}
    for key in key_info:
        net_in.setdefault(key, (now_recv.get(key) - old_recv.get(key)) / 1024 / 1024)  #每秒接收速率MB
        net_out.setdefault(key, (now_sent.get(key) - old_sent.get(key)) / 1024 / 1024) #每秒发送速率MB    
        #old_recv.setdefault(key, now_recv.get(key))
        #old_sent.setdefault(key, now_sent.get(key))
    return key_info, net_in, net_out

def get_process_info(): #取得PID info
    from os.path import basename
    from psutil import net_connections,Process
    msg=""
    for x in net_connections('all'):
        laddr, raddr, status, pid=x[3:]
        if not raddr:
            continue
        try:
            filename = basename(Process(pid).exe()) #專注於exe程序
        except:
            pass
        else:
            #msg += '''Process = {} Local = {} Remote = {} Connection = {}\n'''.format(filename, laddr, raddr, status)    
            msg += '''Process: {} Local: {} Remote: {} Connection: {}\n'''.format(filename, laddr, raddr, status)       
    return msg

#net = psutil.net_io_counters() # 目前網路連線訊息(可能很多)
#print(net)
#net = psutil.net_connections() # 目前網路連線訊息(可能很多)
#print(net)
while True:
    time.sleep(10)      #每10秒鐘運行此程序
    try:
        ip_file = open('networkstatus.txt','a')
        key_info, net_in, net_out = get_rate(get_key)   #每秒收送速率MB
        #key_info, net_in, net_out = get_key()          #取出收送累積總量Bytes
        for key in key_info:                #各網路介面(區域網路2,bluebooth,WiFi,vEthernet)
        
            if net_in.get(key) >2 or net_out.get(key) >2:  #2MB/unit
                ip_file.write(time.strftime("[%Y-%m-%d %H:%M:%S]")+'\n')
                msg='''Interface: {}\nReceived: {} MB/s\nTransmit: {} MB/s\n'''.format( key, net_in.get(key), net_out.get(key))
                ip_file.write(msg)

                msg = get_process_info()    #目前運行程序/local:IP/remote:IP
                ip_file.write(msg)
                ip_file.write('\n')
            #msg='''Interface = {}\nReceived = {} MB/s\nTransmit = {} MB/s\n'''.format( key, net_in.get(key), net_out.get(key))  #for get_rate
            #msg='''Interface = {}\nReceived = {} Byte\nTransmit = {} Byte\n'''.format( key, net_in.get(key), net_out.get(key))   
            #ip_file.write(msg)
         
        ip_file.close() 
    except KeyboardInterrupt:
        exit()