# ServerStatus-Murasame

感谢ServerStatus-Hotaru，又一个云探针诞生了（大雾  
本项目在ServerStatus-Hotaru的基础上使用fastapi重构了服务端，部分修改了客户端与前端  
项目还在非常原始的阶段，可能存在严重的问题

## 与ServerStatus-Hotaru的对比
* 纯python实现
* 同时支持websocket与轮询两种查询方式
* 好像没了

## 兼容性
* 服务端配置文件 √
* 前端网页 √
* 服务端 ×
* 客户端 ×

## 安装方法
### 警告：本项目还在非常原始的阶段（耗时一天），可能会有严重的问题，不建议在生产环境下部署，仅在Python3.8下测试通过

### 手动安装
服务端：  
1.clone本项目  
2.构建前端（Hotaru_theme与本项目的Murasame_theme皆可），并将构建生产dist文件夹置于server_fastapi内  
3.进入server_fastapi目录  
4.将config.json.example复制一份并且重命名为config.json，修改相关配置，也可以直接使用ServerStatus-Hotaru的配置文件  
5.pip install -r requirements.txt  
6.python server.py或uvicorn server:app --reload  
服务端默认监听0.0.0.0:28094，可自行在server.py修改。建议监听本地并在公网使用反代（需要同时反代http和websocket）

客户端：  
1.
```shell
wget https://github.com/ColdThunder11/ServerStatus-Murasame/raw/master/client_ws/status-psutil.py  
pip install psutil websocket-client
```
2.修改文件开头的SERVER（如反代使用了tls加密，请将ws改为wss）,USER,PASSWORD,INTERVAL(可选),使之与服务端配置相同  
3.python status-psutil.py  

## 相关开源项目 ： 
* ServerStatus-Hotaru：https://github.com/CokeMine/ServerStatus-Hotaru
* ServerStatus-Toyo：https://github.com/ToyoDAdoubiBackup/ServerStatus-Toyo
* ServerStatus：https://github.com/BotoX/ServerStatus
* mojeda's ServerStatus: https://github.com/mojeda/ServerStatus
* BlueVM's project: http://www.lowendtalk.com/discussion/comment/169690#Comment_169690