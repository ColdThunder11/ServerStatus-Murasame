# ServerStatus-Murasame

感谢ServerStatus-Hotaru，又一个云探针诞生了（大雾  
本项目在ServerStatus-Hotaru的基础上使用fastapi重构了服务端，部分修改了客户端与前端  
项目还在非常原始的阶段，可能存在严重的问题  
演示站：https://status.coldthunder11.com/

## 与ServerStatus-Hotaru的对比
* 纯python实现
* 同时支持websocket与轮询两种查询方式
* 性能更差，bug更多(
* 好像没了

## 兼容性
* 服务端配置文件 √
* 前端网页 基本兼容，需要对在线时间的显示做修改
* 服务端 ×
* 客户端 ×

## ToDo
* 前端websocket自动重连 √
* 更完善的错误处理机制
* 为前端添加服务器管理功能
* 一键部署脚本

## 安装方法
### 警告：本项目还在非常原始的阶段，协议随时可能发生更改，可能会有严重的问题，暂时不建议在生产环境下部署，仅在Python3.7+下测试通过

### 手动安装
服务端：  
1.clone本项目  
2.使用你喜欢的方式构建前端（Murasame_theme），并将构建生产dist文件夹置于server_fastapi内  
3.进入server_fastapi目录  
4.将config.json.example复制一份并且重命名为config.json，修改相关配置，也可以直接使用ServerStatus-Hotaru的配置文件  
5.pip install -r requirements.txt  
6.python server.py或uvicorn server:app --host 监听IP --port 端口号   
服务端默认监听0.0.0.0:28094，可自行在server.py修改。建议监听本地并在公网使用反代（需要同时反代http和websocket）  
或  
1.去release里下载server.zip，解压并进入ServerStatus-Murasame目录  
2.将config.json.example复制一份并且重命名为config.json，修改相关配置，也可以直接使用ServerStatus-Hotaru的配置文件  
3.pip install -r requirements.txt  
4.python server.py或uvicorn server:app --host 监听IP --port 端口号   
服务端默认监听0.0.0.0:28094，可自行在server.py修改。建议监听本地并在公网使用反代（需要同时反代http和websocket）  

客户端：  
linux版：  
```shell
wget https://raw.githubusercontent.com/ColdThunder11/ServerStatus-Murasame/master/install_client.sh
bash install_client.sh
```
psutil版：  
1.下载https://github.com/ColdThunder11/ServerStatus-Murasame/raw/master/client_ws/status-psutil.py 以及https://github.com/ColdThunder11/ServerStatus-Murasame/raw/master/client_ws/config.json  
2.pip install psutil websocket-client  
3.修改config.json  
4.python status-psutil.py  

## 相关开源项目 ： 
* ServerStatus-Hotaru：https://github.com/CokeMine/ServerStatus-Hotaru
* Hotaru_theme：https://github.com/CokeMine/Hotaru_theme
* ServerStatus-Toyo：https://github.com/ToyoDAdoubiBackup/ServerStatus-Toyo
* ServerStatus：https://github.com/BotoX/ServerStatus
* mojeda's ServerStatus: https://github.com/mojeda/ServerStatus
* BlueVM's project: http://www.lowendtalk.com/discussion/comment/169690#Comment_169690