#!/bin/bash
echo "ColdThunder11/ServerStatus-Murasame一键安装脚本"
github_raw_addr="https://raw.githubusercontent.com/ColdThunder11/ServerStatus-Murasame/master"
server_path="/usr/local/ServerStatus/server"
client_path="/usr/local/ServerStatus/client"
root_path="/usr/local/ServerStatus"
link_prefix=${github_raw_addr}
server_release="https://github.com/ColdThunder11/ServerStatus-Murasame/releases/download/0.0.2/ServerStatus-Murasame.zip"

Green_font_prefix="\033[32m" && Red_font_prefix="\033[31m" && Red_background_prefix="\033[41;37m" && Font_color_suffix="\033[0m"
Info="${Green_font_prefix}[信息]${Font_color_suffix}"
Error="${Red_font_prefix}[错误]${Font_color_suffix}"
Tip="${Green_font_prefix}[注意]${Font_color_suffix}"

check_sys() {
  if [[ -f /etc/redhat-release ]]; then
    release="centos"
  elif grep -q -E -i "debian" /etc/issue; then
    release="debian"
  elif grep -q -E -i "ubuntu" /etc/issue; then
    release="ubuntu"
  elif grep -q -E -i "centos|red hat|redhat" /etc/issue; then
    release="centos"
  elif grep -q -E -i "debian" /proc/version; then
    release="debian"
  elif grep -q -E -i "ubuntu" /proc/version; then
    release="ubuntu"
  elif grep -q -E -i "centos|red hat|redhat" /proc/version; then
    release="centos"
  fi
  bit=$(uname -m)
}
Download_Server_Status_client() {
  if ! wget --no-check-certificate "${link_prefix}/client_ws/status-client.py" -O "${client_path}/status-client.py"; then
    echo -e "${Error} ServerStatus 客户端下载失败 !" && exit 1
  fi
  if ! wget --no-check-certificate "${link_prefix}/service/server_status_client_debian" -O /etc/systemd/system/statusc.service; then
    echo -e "${Error} ServerStatus 客户端下载失败 !" && exit 1
  fi
  echo -e "${Info} ServerStatus 客户端下载完成 !"
  chmod 755 /etc/systemd/system/statusc.service
}
Create_dir(){
    if [ ! -d ${root_path} ]; then
        mkdir ${root_path}
    fi
    if [ ! -d ${client_path} ]; then
        mkdir ${client_path}
    fi
}
Installation_dependency() {
  if python3 --help >/dev/null 2>&1; then
    python_status=1
  else
    python_status=0
  fi
  if [ ${release} == "centos" ]; then
      if [ "${python_status}" -eq 0 ]; then
      yum -y update
      yum -y install python3 wget
      fi
  else
      if [ "${python_status}" -eq 0 ]; then
      apt-get -y update
      apt-get -y install python3 wget
      fi
  fi
}
Config_client(){
  echo -e "请输入服务端地址"
  read -erp "(默认: 取消):" server_address
  [[ -z "${server_address}" ]] && echo -e "已取消..." && exit 1
  echo -e "请输入连接的用户名"
  read -erp "(默认: 取消):" username
  [[ -z "${username}" ]] && echo -e "已取消..." && exit 1
  echo -e "请输入连接的密码"
  read -erp "(默认: 取消):" password
  [[ -z "${password}" ]] && echo -e "已取消..." && exit 1
  cat >"${client_path}/config.json"<<EOF
{
    "server": "${server_address}",
    "user": "${username}",
    "password": "${username}",
    "interval": 2,
    "invalid_interface_name": ["lo", "tun", "kube", "docker", "vmbr", "br-", "vnet", "veth"]
}
EOF
}
check_sys
Create_dir
Installation_dependency
Download_Server_Status_client
Config_client
echo -e "安装完成"

