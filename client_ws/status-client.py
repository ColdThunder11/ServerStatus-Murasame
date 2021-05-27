# -*- coding: utf-8 -*-
# Oringin: https://github.com/CokeMine/ServerStatus-Hotaru

import socket
import time
import re
import os
import json
import subprocess
from collections import deque
import websocket
try:
    import ujson as json
except ImportError:
    import json
try:
    import thread
except ImportError:
    import _thread as thread

SERVER = "ws://127.0.0.1:28094"
#PORT = 35601
USER = "Local"
PASSWORD = "Local"
INTERVAL = 2  # 更新间隔，单位：秒

def check_interface(net_name):
    net_name = net_name.strip()
    invalid_name = ['lo', 'tun', 'kube', 'docker', 'vmbr', 'br-', 'vnet', 'veth']
    return not any(name in net_name for name in invalid_name)


def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime = f.readline().split('.')
    return int(uptime[0])


def get_memory():
    re_parser = re.compile(r'(\S*):\s*(\d*)\s*kB')
    result = dict()
    for line in open('/proc/meminfo'):
        match = re_parser.match(line)
        if match:
            result[match.group(1)] = int(match.group(2))

    mem_total = float(result['MemTotal'])
    mem_free = float(result['MemFree'])
    cached = float(result['Cached'])
    mem_used = mem_total - (cached + mem_free)
    swap_total = float(result['SwapTotal'])
    swap_free = float(result['SwapFree'])
    return int(mem_total), int(mem_used), int(swap_total), int(swap_free)


def get_hdd():
    p = subprocess.check_output(
        ['df', '-Tlm', '--total', '-t', 'ext4', '-t', 'ext3', '-t', 'ext2', '-t', 'reiserfs', '-t', 'jfs', '-t', 'ntfs',
         '-t', 'fat32', '-t', 'btrfs', '-t', 'fuseblk', '-t', 'zfs', '-t', 'simfs', '-t', 'xfs']).decode('utf-8')
    total = p.splitlines()[-1]
    used = total.split()[3]
    size = total.split()[2]
    return int(size), int(used)


def get_load():
    return round(os.getloadavg()[0], 1)


def get_cpu_time():
    with open('/proc/stat', 'r') as stat_file:
        time_list = stat_file.readline().split()[1:]
    time_list = list(map(int, time_list))
    return sum(time_list), time_list[3]


def get_cpu():
    old_total, old_idle = get_cpu_time()
    time.sleep(INTERVAL)
    total, idle = get_cpu_time()
    return round(100 - float(idle - old_idle) / (total - old_total) * 100.00, 1)


def get_traffic_vnstat():
    vnstat = os.popen('vnstat --oneline b').readline()
    v_data = vnstat.split(';')
    net_in = int(v_data[8])
    net_out = int(v_data[9])
    return net_in, net_out


class Network:
    def __init__(self):
        self.rx = deque(maxlen=10)
        self.tx = deque(maxlen=10)
        self._get_traffic()

    def _get_traffic(self):
        net_in = 0
        net_out = 0
        re_parser = re.compile(r'([^\s]+):[\s]*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+('
                               r'\d+)\s+(\d+)\s+(\d+)')
        with open('/proc/net/dev') as f:
            for line in f.readlines():
                net_info = re_parser.findall(line)
                if net_info:
                    if check_interface(net_info[0][0]):
                        net_in += int(net_info[0][1])
                        net_out += int(net_info[0][9])
        self.rx.append(net_in)
        self.tx.append(net_out)

    def get_speed(self):
        self._get_traffic()
        avg_rx = 0
        avg_tx = 0
        queue_len = len(self.rx)
        for x in range(queue_len - 1):
            avg_rx += self.rx[x + 1] - self.rx[x]
            avg_tx += self.tx[x + 1] - self.tx[x]
        avg_rx = int(avg_rx / queue_len / INTERVAL)
        avg_tx = int(avg_tx / queue_len / INTERVAL)
        return avg_rx, avg_tx

    def get_traffic(self):
        queue_len = len(self.rx)
        return self.rx[queue_len - 1], self.tx[queue_len - 1]


def get_network(ip_version):
    if ip_version == 4:
        host = 'ipv4.google.com'
    elif ip_version == 6:
        host = 'ipv6.google.com'
    else:
        return False
    try:
        socket.create_connection((host, 80), 2).close()
        return True
    except Exception:
        return False

def on_message(ws:websocket.WebSocketApp, message):
    #print(ws)
    print(message)
    if message != "Authentication success":
        print("Auth fail, err message :" + message)
        ws.close()

def on_error(ws, error):
    #print(ws)
    print(error)
    global is_ws_alive
    is_ws_alive = False
    print("Websocket got a error")


def on_close(ws):
    global is_ws_alive
    is_ws_alive = False
    #print(ws)
    print("Websocket connection closed")

def on_open(ws:websocket.WebSocketApp):
    print("Websocket crearte sucess")
    def run(*args):
        global is_ws_alive
        is_ws_alive = True
        ws.send(PASSWORD)
        time.sleep(1)
        traffic = Network()
        while True:
            CPU = get_cpu()
            NetRx, NetTx = traffic.get_speed()
            NET_IN, NET_OUT = traffic.get_traffic()
            Uptime = get_uptime()
            Load = get_load()
            MemoryTotal, MemoryUsed, SwapTotal, SwapFree = get_memory()
            HDDTotal, HDDUsed = get_hdd()
            ws.send(json.dumps({
                "uptime" : Uptime,
                "load" : Load,
                "memory_total" : MemoryTotal,
                "memory_used" : MemoryUsed,
                "swap_total" : SwapTotal,
                "swap_used" : SwapTotal - SwapFree,
                "hdd_total" : HDDTotal,
                "hdd_used" : HDDUsed,
                "cpu": CPU,
                "network_rx": NetRx,
                "network_tx": NetTx,
                "network_in": NET_IN,
                "network_out": NET_OUT
            }))
            time.sleep(INTERVAL)
    thread.start_new_thread(run, ())

if __name__ == '__main__':
    while True:
        try:
            print("Connecting to "+SERVER+"/ws/client/"+USER)
            ws = websocket.WebSocketApp(SERVER+"/ws/client/"+USER,
                                        on_open = on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever()
            time.sleep(3)
        except Exception as e:
            time.sleep(3)
            print("Caught Exception:", e)