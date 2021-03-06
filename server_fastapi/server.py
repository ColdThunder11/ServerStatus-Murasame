# -*- coding: utf-8 -*-
from logging import ERROR, Manager, debug, error, setLogRecordFactory
import async_timeout
from fastapi import FastAPI, Header, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from starlette.routing import websocket_session
import uvicorn
import threading
from pydantic import BaseModel
from typing import Dict, Optional, SupportsComplex, List
import json
import asyncio
import traceback
import copy
from os import path
import time
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from async_timeout import timeout
import sys
import _thread

class SetClientItem(BaseModel):
    key: str
    username: str
    password: str
    name:str 
    type: str
    location: str
    disabled: Optional[bool] = True
    region: str

class ClientItem(BaseModel):
    username: str
    password: str
    type: str
    location: str
    disabled: Optional[bool] = True
    region: str

app = FastAPI(docs_url=None, redoc_url=None)

scheduler = None

status_json = {}

'''status json
{
"servers": [
{ "name": "CN Shanghai", "type": "KVM", "host": "None", "location": "China", "online4": true, "online6": false, "uptime": "27 天", "load": -1.00, "network_rx": 17796, "network_tx": 5398, "network_in": 36721572634, "network_out": 11287322603, "cpu": 0, "memory_total": 4193772, "memory_used": 3557168, "swap_total": 7643660, "swap_used": 4787948, "hdd_total": 81566, "hdd_used": 49119, "custom": "" ,"region": "CN"},
{ "name": "CN Guangzhou", "type": "KVM", "host": "None", "location": "China", "online4": true, "online6": false, "uptime": "49 天", "load": 0.20, "network_rx": 2019, "network_tx": 3358, "network_in": 3886932544, "network_out": 3697049598, "cpu": 0, "memory_total": 3910400, "memory_used": 2006232, "swap_total": 2047996, "swap_used": 240384, "hdd_total": 352711, "hdd_used": 17629, "custom": "" ,"region": "CN"},
{ "name": "JP tsukaeru", "type": "OpenVZ", "host": "None", "location": "Japan", "online4": true, "online6": false, "uptime": "44 天", "load": 0.00, "network_rx": 7584, "network_tx": 1426, "network_in": 69187491862, "network_out": 58138491984, "cpu": 0, "memory_total": 524288, "memory_used": 81676, "swap_total": 0, "swap_used": 0, "hdd_total": 20029, "hdd_used": 1167, "custom": "" ,"region": "JP"},
{ "name": "Hong Kong", "type": "OpenVZ", "host": "None", "location": "Hong Kong", "online4": true, "online6": false, "uptime": "9 天", "load": 0.00, "network_rx": 44, "network_tx": 274, "network_in": 5374511674, "network_out": 5455829260, "cpu": 0, "memory_total": 524288, "memory_used": 74736, "swap_total": 0, "swap_used": 0, "hdd_total": 1916, "hdd_used": 902, "custom": "" ,"region": "HK"},
{ "name": "Russia", "type": "OpenVZ", "host": "None", "location": "Russia", "online4": true, "online6": false, "uptime": "6 天", "load": 0.00, "network_rx": 411, "network_tx": 380, "network_in": 354127543, "network_out": 215601426, "cpu": 2, "memory_total": 524288, "memory_used": 43544, "swap_total": 0, "swap_used": 0, "hdd_total": 892, "hdd_used": 876, "custom": "" ,"region": "RU"},
{ "name": "Local", "type": "None", "host": "None", "location": "Paris", "online4": true, "online6": false, "uptime": "22 天", "load": 0.00, "network_rx": 4747, "network_tx": 10833, "network_in": 107332072734, "network_out": 56467775162, "cpu": 4, "memory_total": 8138776, "memory_used": 2101144, "swap_total": 4294652, "swap_used": 1961472, "hdd_total": 933210, "hdd_used": 55347, "custom": "" ,"region": "FR"}
],
"updated": "1622026550"
}
'''

'''report json
    {
        "uptime" : "",
        "load" : "",
        "memory_total" : "",
        "memory_used" : "",
        "swap_total" : "",
        "swap_used" : "",
        "hdd_total" : "",
        "hdd_used" : "",
        "cpu": "",
        "network_rx": "",
        "network_tx": "",
        "network_in": "",
        "network_out": ""
    }
'''
user_list = {
    "servers": [
        {
            "username": "Local",
            "password": "Local",
            "name": "Local",
            "type": "None",
            "host": "None",
            "location": "China",
            "disabled": False,
            "region": "CN"
        }
    ]
}
config = {
        "listen_host": "0.0.0.0",
        "listen_port": 28094,
        "uvicorn_debug_mode": True,
        "admin_key": "114514"
}

class ClientManager:
    def __init__(self, username: str, ws: WebSocket):
        self.username = username
        self.ws = ws
        self.status = {
            "uptime": "",
            "load": "",
            "memory_total": "",
            "memory_used": "",
            "swap_total": "",
            "swap_used": "",
            "hdd_total": "",
            "hdd_used": "",
            "cpu": "",
            "network_rx": "",
            "network_tx": "",
            "network_in": "",
            "network_out": "",
            "update_time": None
        }

    async def close_ws(self):
        await self.ws.close()

    def get_status(self) -> Dict:
        status = copy.copy(self.status)
        return status

    def set_status(self, data):
        self.status["uptime"] = data["uptime"]
        self.status["load"] = data["load"]
        self.status["memory_total"] = data["memory_total"]
        self.status["memory_used"] = data["memory_used"]
        self.status["swap_total"] = data["swap_total"]
        self.status["swap_used"] = data["swap_used"]
        self.status["hdd_total"] = data["hdd_total"]
        self.status["hdd_used"] = data["hdd_used"]
        self.status["cpu"] = data["cpu"]
        self.status["network_rx"] = data["network_rx"]
        self.status["network_tx"] = data["network_tx"]
        self.status["network_in"] = data["network_in"]
        self.status["network_out"] = data["network_out"]
        self.status["update_time"] = int(time.time())

    async def close_ws(self):
        try:
            await self.ws.close()
        except:
            pass

class ServerManager:
    def __init__(self):
        self.active_clients: Dict = {}
        #self.lock = threading.Lock()
        #self.auth_lock = threading.Lock()
    def save_config(self):
        with open(path.join(path.dirname(__file__),"config.json"),"r+",encoding="utf8")as fp:
            fp.seek(0)
            fp.truncate()
            json.dump(user_list,fp)

    def get_user_obj(self, username: str):
        for user in user_list["servers"]:
            if user["username"] == username:
                return user
        return None

    async def auth_connection(self, ws: WebSocket, username: str) -> bool:
        print("Start auth")
        user = self.get_user_obj(username)
        #print(user)
        if user == None:
            return False
        try:
            await ws.accept()
            password = await ws.receive_text()
            if password != user["password"]:
                print("Authentication failed")
                await ws.send_text("Authentication failed")
                await ws.close()
                return False
            else:
                print("Authentication success")
                await ws.send_text("Authentication success")
                if username in self.active_clients.keys():
                    print("A exsisting connection will be closed")
                    try:
                        await self.active_clients[username].close_ws()
                    except:
                        pass
                self.active_clients[username] = ClientManager(username, ws)
                return True
        except:
            traceback.print_exc()
            return False

    def get_client_manager(self, username: str) -> ClientManager:
        manager = None
        if username in self.active_clients.keys():
            manager = self.active_clients[username]
        return manager

    def get_all_client_manager(self):
        managers = copy.copy(self.active_clients)
        return managers

    async def get_status_json(self):
        build_json = {
            "servers":  [],
            "updated": str(int(time.time()))
        }
        for user in user_list["servers"]:
            if user["disabled"] == True:
                continue
            username = user["username"]
            active_clients_copy = self.active_clients.copy()
            if username in active_clients_copy.keys():
                status = active_clients_copy[username].get_status()
                if status["update_time"] != None and int(time.time()) - status["update_time"] > 20:#as offline
                    try:
                        await active_clients_copy[username].close_ws()
                    except:
                        pass
                    if username in active_clients_copy.keys():
                        del self.active_clients[username]
                    build_json["servers"].append({
                        "name": user["name"],
                        "type": user["type"],
                        "host": user["host"],
                        "location": user["location"],
                        "online4": False,
                        "online6": False,
                        "region": user["region"]
                    })
                    continue
                build_json["servers"].append({
                    "name": user["name"],
                    "type": user["type"],
                    "host": user["host"],
                    "location": user["location"],
                    "online4": True,
                    "online6": False,
                    "uptime": status["uptime"],
                    "load": status["load"],
                    "network_rx": status["network_rx"],
                    "network_tx": status["network_tx"],
                    "network_in": status["network_in"],
                    "network_out": status["network_out"],
                    "cpu": status["cpu"],
                    "memory_total": status["memory_total"],
                    "memory_used": status["memory_used"],
                    "swap_total": status["swap_total"],
                    "swap_used": status["swap_used"],
                    "hdd_total": status["hdd_total"],
                    "hdd_used": status["hdd_used"],
                    "custom": "",
                    "region": user["region"]
                })
            else:
                build_json["servers"].append({
                    "name": user["name"],
                    "type": user["type"],
                    "host": user["host"],
                    "location": user["location"],
                    "online4": False,
                    "online6": False,
                    "region": user["region"]
                })
        return build_json

    def remove_user(self, username: str):
        try:
            if username in self.active_clients.keys():
                del self.active_clients[username]
            return
        except:
            return

manager = ServerManager()

async def refesh_status():
    global status_json
    status = await manager.get_status_json()
    if status != None:
        status_json = status
    #print("refesh_status success")

@app.get("/")
async def get_root_index():
    return await get_index()

@app.get("/index.html")
async def get_index():
    with open(path.join(path.dirname(__file__),"dist","index.html"),"r",encoding="utf8")as fp:
        html_content = fp.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse(path.join(path.dirname(__file__),"dist","favicon.ico"))

@app.get("/robots.txt")
async def get_robots_txt():
    return FileResponse(path.join(path.dirname(__file__),"dist","robots.txt"))

@app.websocket("/ws/client/{user_name}")
async def report_ws_endpoint(websocket: WebSocket, user_name: str):
    print(f"Get new client ws connection USER={user_name}")
    try:
        async with timeout(20):
            if not (await manager.auth_connection(websocket, user_name)):
                return
        cmanager = manager.get_client_manager(user_name)
    except:
        print("A websocket connection has been closed")
        traceback.print_exc()
        #manager.remove_user(user_name)
        return
    while True:
        try:
            async with timeout(15):
                try:
                    res = await websocket.receive_json()
                except:
                    return
            #print(f"Get status report from {user_name}")
            cmanager.set_status(res)
        except:
            print("A websocket connection has been closed")
            traceback.print_exc()
            #manager.remove_user(user_name)
            return

@app.websocket("/ws/stats")
async def get_status_ws(websocket: WebSocket):
    try:
        async with timeout(10):
            await websocket.accept()
        while True:
            res = await websocket.receive_text()
            if res == "get satats":
                async with timeout(10):
                    await websocket.send_json(status_json)
                await asyncio.sleep(0.3)
            else:
                websocket.close()
                return
    except:
        print("Stats ws connection close")

@app.get("/json/stats.json")
async def get_json_status():
    return JSONResponse(content=jsonable_encoder(status_json))

@app.get("/admin/getclientsinfo")
async def get_clients_info(key:str):
    if key != config["admin_key"]:
        return JSONResponse(content=jsonable_encoder({
            "code": 403,
            "msg": "auth failed"
        }))
    else:
        server_config = user_list
        return JSONResponse(content=jsonable_encoder(server_config))

@app.post("/admin/setclient")
async def set_client(postbody:SetClientItem):
    if postbody.key != config["admin_key"]:
        return JSONResponse(content=jsonable_encoder({
            "code": 403,
            "msg": "auth failed"
        }))
    else:
        global user_list
        for i in range(len(user_list["servers"])):
            if user_list["servers"][i]["username"] == postbody.username:
                user_list["servers"][i]["password"] = postbody.password
                user_list["servers"][i]["name"] = postbody.name
                user_list["servers"][i]["type"] = postbody.type
                user_list["servers"][i]["host"] = "None"
                user_list["servers"][i]["location"] = postbody.location
                user_list["servers"][i]["disabled"] = postbody.disabled
                user_list["servers"][i]["region"] = postbody.region
                manager.save_config()
                return JSONResponse(content=jsonable_encoder({
                    "code": 0,
                    "msg": "success"
                }))
        user_list["servers"].append(
            {
                "username": postbody.username,
                "password": postbody.password,
                "name": postbody.name,
                "type": postbody.type,
                "host": "None",
                "location": postbody.location,
                "disabled": postbody.disabled,
                "region": postbody.region
            }
        )
        manager.save_config()
        return JSONResponse(content=jsonable_encoder({
            "code": 0,
            "msg": "success"
        }))

@app.on_event("startup")
def init_server():
    global scheduler
    global user_list
    global config
    with open(path.join(path.dirname(__file__),"config.json"),"r",encoding="utf8")as fp:
        user_list = json.load(fp)
    if "config" in user_list:
        config = user_list["config"]
    scheduler = AsyncIOScheduler()
    scheduler.add_job(refesh_status, "interval", seconds=1)
    scheduler.start()
    print("Fastapi init success")
    app.mount("/js", StaticFiles(directory=path.join(path.dirname(__file__),"dist","js")), name="js")
    app.mount("/img", StaticFiles(directory=path.join(path.dirname(__file__),"dist","img")), name="js")
    app.mount("/css", StaticFiles(directory=path.join(path.dirname(__file__),"dist","css")), name="js")

if __name__ == "__main__":
    import uvicorn
    with open(path.join(path.dirname(__file__),"config.json"),"r",encoding="utf8")as fp:
        user_list = json.load(fp)
    if "config" in user_list:
        config = user_list["config"]
    uvicorn.Config(app)
    uvicorn.run(app, host=config["listen_host"], port=config["listen_port"], debug=config["uvicorn_debug_mode"])
