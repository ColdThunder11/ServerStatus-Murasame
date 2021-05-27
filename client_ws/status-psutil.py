# -*- coding: utf-8 -*-
# Oringin: https://github.com/CokeMine/ServerStatus-Hotaru

import socket
from sys import is_finalizing
import time
import string
import math
import os
import json
import collections
import psutil
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

def get_uptime():
    return int(time.time() - psutil.boot_time())


def get_memory():
    Mem = psutil.virtual_memory()
    try:
        MemUsed = Mem.total - (Mem.cached + Mem.free)
    except:
        MemUsed = Mem.total - Mem.free
    return int(Mem.total / 1024.0), int(MemUsed / 1024.0)


def get_swap():
    Mem = psutil.swap_memory()
    return int(Mem.total / 1024.0), int(Mem.used / 1024.0)


def get_hdd():
    valid_fs = ["ext4", "ext3", "ext2", "reiserfs", "jfs", "btrfs", "fuseblk", "zfs", "simfs", "ntfs", "fat32", "exfat",
                "xfs"]
    disks = dict()
    size = 0
    used = 0
    for disk in psutil.disk_partitions():
        if not disk.device in disks and disk.fstype.lower() in valid_fs:
            disks[disk.device] = disk.mountpoint
    for disk in disks.values():
        usage = psutil.disk_usage(disk)
        size += usage.total
        used += usage.used
    return int(size / 1024.0 / 1024.0), int(used / 1024.0 / 1024.0)


def get_load():
    try:
        return round(os.getloadavg()[0] * 2) / 2
    except:
        return -1.0


def get_cpu():
    return psutil.cpu_percent(interval=INTERVAL)


class Traffic:
    def __init__(self):
        self.rx = collections.deque(maxlen=10)
        self.tx = collections.deque(maxlen=10)

    def get(self):
        avgrx = 0
        avgtx = 0
        for name, stats in psutil.net_io_counters(pernic=True).items():
            if name == "lo" or name.find("tun") > -1:
                continue
            avgrx += stats.bytes_recv
            avgtx += stats.bytes_sent

        self.rx.append(avgrx)
        self.tx.append(avgtx)
        avgrx = 0
        avgtx = 0

        l = len(self.rx)
        for x in range(l - 1):
            avgrx += self.rx[x + 1] - self.rx[x]
            avgtx += self.tx[x + 1] - self.tx[x]

        avgrx = int(avgrx / l / INTERVAL)
        avgtx = int(avgtx / l / INTERVAL)

        return avgrx, avgtx


def liuliang():
    NET_IN = 0
    NET_OUT = 0
    net = psutil.net_io_counters(pernic=True)
    for k, v in net.items():
        if 'lo' in k or 'tun' in k:
            continue
        else:
            NET_IN += v[1]
            NET_OUT += v[0]
    return NET_IN, NET_OUT


def get_network(ip_version):
    if (ip_version == 4):
        HOST = "ipv4.google.com"
    elif (ip_version == 6):
        HOST = "ipv6.google.com"
    else:
        return False
    try:
        s = socket.create_connection((HOST, 80), 2).close()
        return True
    except:
        pass
    return False

def on_message(ws:websocket.WebSocketApp, message):
    #print(ws)
    print(message)
    if message != "Authentication success":
        print(f"Auth fail, err message :{message}")
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
        traffic = Traffic()
        traffic.get()
        while True:
            CPU = get_cpu()
            NetRx, NetTx = traffic.get()
            NET_IN, NET_OUT = liuliang()
            Uptime = get_uptime()
            Load = get_load()
            MemoryTotal, MemoryUsed = get_memory()
            SwapTotal, SwapUsed = get_swap()
            HDDTotal, HDDUsed = get_hdd()
            ws.send(json.dumps({
                "uptime" : Uptime,
                "load" : Load,
                "memory_total" : MemoryTotal,
                "memory_used" : MemoryUsed,
                "swap_total" : SwapTotal,
                "swap_used" : SwapUsed,
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
            print(f"Connecting to {SERVER}/ws/client/{USER}")
            ws = websocket.WebSocketApp(f"{SERVER}/ws/client/{USER}",
                                        on_open = on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever()
            time.sleep(3)
        except Exception as e:
            time.sleep(3)
            print("Caught Exception:", e)
            

