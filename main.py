import asyncio
from tracemalloc import start
import websockets
import json
import requests
from urllib.parse import urljoin, urlparse

def untracked(url):
    try:
        r = requests.get(url, timeout=5)
    except:
        return "failed"
    u = urlparse(r.url)
    ret = urljoin(r.url, u.path)
    return "Untracked: "+ret


async def show():
    async with websockets.connect("ws://localhost:9869") as websocket:
        while 1:
            str = await websocket.recv()
            str_loaded = json.loads(str)
            if "message" in str_loaded:
                msg = str_loaded["message"]
                msg.replace("\u0026", "&")
                cqcodestr = ""
                startcapture = False
                cqcodestrlist = []
                for char in msg:
                    if char == '[':
                        startcapture = True
                    if startcapture:
                        cqcodestr += char
                    if char == ']':
                        startcapture = False
                        cqcodestrlist.append(cqcodestr)
                        cqcodestr = ""
                for cqcode in cqcodestrlist:
                    if cqcode.startswith("[CQ:json"):
                        s = cqcode.replace("[CQ:json,data=", "")
                        s = s.replace("]", "")
                        s = s.replace("&#44;", ",")
                        s = s.replace("&#91;", "[")
                        s = s.replace("&#93;", "]")
                        s = s.replace("&#123;", "{")
                        s = s.replace("&#125;", "}")
                        s = s.replace("&amp;", "&")
                        print(s)
                        jsondata=json.loads(s)
                        print(jsondata)
                        if "meta" in jsondata:
                            try:
                                if jsondata["app"] == "com.tencent.structmsg":
                                    notrack = untracked(jsondata["meta"]["news"]["jumpUrl"])
                                if jsondata["app"] == "com.tencent.miniapp_01":
                                    notrack = untracked(jsondata["meta"]["detail_1"]["qqdocurl"])
                            except:
                                notrack = "error"
                            await websocket.send(json.dumps({"action": "send_group_msg", "params": {"group_id": str_loaded["group_id"], "message": notrack}}))
   

asyncio.run(show())
