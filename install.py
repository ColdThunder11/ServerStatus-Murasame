# -*- coding: UTF-8 -*-
import json
import sys
import os
from os import linesep, system, path

if len(sys.argv) == 1:
    print('''
该脚本需要参数才能正常运行
-c 安装客户端
-nopip 不使用pip来安装依赖
    '''.strip())
action = None
use_pip = True
for arg in sys.argv:
    if arg == "-c":
        action = "ic"
    if arg == "-nopip":
        use_pip =False
if action == None:
    print("参数不完整或者不正确")
    exit(0)
if not os.path.isfile("/proc/version"):
    print("您运行的可能不是标准的linux系统，请手动安装")
    exit(0)
system_type = "debian"
with open("/proc/version", 'r') as f:
    version = f.read()
if "Debian" in version:
    system_type = "debian"
else:
    print("目标系统暂不支持一键安装，请手动安装")    
    exit(0)
if system_type == "debian" and action == "ic":
    print("正在安装依赖...")
    system("apt update")
    system("apt install -y wget git")
    current_path = path.dirname(path.abspath(__file__))
    print("安装目录 "+current_path)
    system("wget -P "+ current_path + " https://raw.githubusercontent.com/ColdThunder11/ServerStatus-Murasame/master/client_ws/status-client.py -O status-client.py")
    #system("wget -P "+ current_path + " https://raw.githubusercontent.com/ColdThunder11/ServerStatus-Murasame/master/client_ws/config.json")
    if use_pip:
        system("python3 -m pip install websocket-client")
    else:
        system("git clone --depth=1 https://github.com/websocket-client/websocket-client.git")
        system("cd "+path.join(current_path,"websocket-client")+" && python3 setup.py install")
    print("请输入服务端的连接地址，应当以ws://或wss://开头（例如ws://127.0.0.1:28094）")
    server_addr = input()
    print("请输入连接的用户名")
    user = input()
    print("请输入连接的密码")
    password = input()
    print("正在创建配置文件...")
    config = {
        "server": server_addr,
        "user": user,
        "password": password,
        "interval": 2 
    }
    with open(path.join(current_path,"config.json"),'w',encoding='utf8')as fp:
        fp.seek(0)
        fp.truncate()
        json.dump(config,fp)
    print("配置文件创建完成")
    print("正在安装服务...")
    system("wget -P "+ current_path + " https://raw.githubusercontent.com/ColdThunder11/ServerStatus-Murasame/master/service/debian_client.service -O debian_client.service")
    system("mv -f "+path.join(current_path,"debian_client.service")+" /etc/systemd/system/statusc.service")
    with open("/etc/systemd/system/statusc.service",'r+',encoding='utf8')as fp:
        fp.seek(0)
        lines = fp.readlines()
        for i in range(len(lines)):
            if r"${ClientPath}" in lines[i]:
                lines[i] = lines[i].replace(r"${ClientPath}",current_path)
            if r"${ClientFile}" in lines[i]:
                lines[i] = lines[i].replace(r"${ClientFile}",path.join(current_path,"status-client.py"))
        fp.seek(0)
        fp.truncate()
        fp.writelines(lines)
    print("服务安装完成")
    system("systemctl daemon-reload")
    system("systemctl restart statusc")
    system("systemctl enable statusc")
    print("服务启动完成")
    print("客户端安装完成")

    

    
    
    


