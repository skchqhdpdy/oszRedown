import os
import sys
import requests
from tqdm import tqdm
import zipfile
import threading
import time
import traceback
import logUtils as log
import tkinter as tk
from tkinter import filedialog
import hashlib

class calculate_md5:
    @classmethod
    def file(cls, fn) -> str:
        md5 = hashlib.md5()
        with open(fn, "rb") as f:
            md5.update(f.read())
        return md5.hexdigest()

    @classmethod
    def text(cls, t) -> str:
        md5 = hashlib.md5()
        md5.update(t.encode("utf-8"))
        return md5.hexdigest()

version = "1.1.0"
st = int(time.time())
requestHeaders = {"User-Agent": "oszRedown.py"}
ProcessName = os.popen(f'tasklist /svc /FI "PID eq {os.getpid()}"').read().strip().split("\n")[2].split(" ")[0]
ProcessPath = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0]) #환경 변수 세팅시에 경로가 cmd의 현재 경로로 설정되는 것 방지
version_hash = calculate_md5.file(ProcessPath) if ProcessName != "python.exe" else ""

def exceptionE(e):
    log.error(e); e = f"{e}\n{traceback.format_exc()}"
    with open("logs.txt", "a", encoding="utf-8") as f: f.write(f"{e}\n\n")

def KillProgram(): os.system(f"taskkill /f /pid {os.getpid()}")

try:
    print(f"\npid : {os.getpid()} | ProcessName : {ProcessName} | ProcessPath : {ProcessPath} | version : {version} | version_hash : {version_hash}")
    def update_oszRedown(): #자동 업데이트
        os.rename(ProcessPath, f"{ProcessPath.replace('oszRedown.exe', f'oszRedown-v{version}.exe')}")
        dl("https://github.com/skchqhdpdy/oszRedown/raw/master/oszRedown.exe", ProcessPath)
        os.remove(f"{ProcessPath.replace('.exe', f'-v{version}.exe')}")
        input("\n신 버전으로 다시 키세요!"); KillProgram()
    nv = requests.get("https://github.com/skchqhdpdy/oszRedown/raw/master/version.txt", headers=requestHeaders, timeout=10).text.split("\n")
    if ProcessName != "python.exe": #개발시에 업데이트 체크 무시
        if version != nv[0]:
            print(f"업데이트 있음! \n현재버전 : {version} \n최신버전 : {nv[0]}")
            print("https://github.com/skchqhdpdy/oszRedown")
            if input("Update Program? (y/n) : ") != "y": os.system("start https://github.com/skchqhdpdy/oszRedown") #KillProgram()
            else: update_oszRedown()
        elif ProcessName != "python.exe" and version_hash != nv[1]:
            print(f"업데이트 있음! \n버전은 같지만 파일 Hash 값이 다름! \n현재 Hash 값 : {version_hash} \n최신 Hash 값 : {nv[1]}")
            print("https://github.com/skchqhdpdy/oszRedown")
            if input("Update Program? (y/n) : ") != "y": os.system("start https://github.com/skchqhdpdy/oszRedown") #KillProgram()
            else: update_oszRedown()
except Exception as e:
    print(e)
    if input("version Check Fail! ignore? (y/n) : ") == "n": KillProgram()

MT = input("멀티쓰레딩 활성화? (0/1 (0)) : ") == "1"
root = tk.Tk().withdraw()  #Tkinter 창 숨기기
osu_path = os.popen(f'reg query HKEY_CLASSES_ROOT\osu\Shell\Open\Command').read().strip().split('"')[1].replace("\\", "/").replace("/osu!.exe", "")
if not input(f"{osu_path} | 해당 경로가 osu!.exe 가 위치한 폴더가 맞나요? (0/1 (1)) : ") == "0": pass
else: osu_path = filedialog.askopenfilename(title="Error! Not Found osu! Path! | Select osu!.exe", filetypes=[("osu! executable", "osu!.exe")]).replace("/osu!.exe", "")

if not os.path.isdir(f"{osu_path}/#oszRedown"): os.mkdir(f"{osu_path}/#oszRedown")
songs = os.listdir(f"{osu_path}/Songs")
def dl(s):
    try:
        try: setID = int(s.split(" ")[0])
        except: setID = None
        if not setID: return
        elif f"{s}.osz" in os.listdir(f"{osu_path}/#oszRedown"): log.warning(f"{setID} pass"); return

        url = [
            f'https://api.nerinyan.moe/d/{setID}',
            f"https://catboy.best/d/{setID}",
            f"https://osu.direct/d/{setID}",
            f"https://beatconnect.io/b/{setID}",
            f"https://txy1.sayobot.cn/beatmaps/download/full/{setID}",
            f"https://storage.ripple.moe/d/{setID}"
        ]
        urlName = ["Nerinyan", "catboy", "osu.direct", "beatconnect", "sayobot", "Ripple"]

        file_name = f'{setID}.osz'
        for i, (link, mn) in enumerate(zip(url, urlName)):
            try:
                res = requests.get(link, headers=requestHeaders, timeout=5, stream=True)
                statusCode = res.status_code
            except: statusCode = 500

            if statusCode == 200:
                file_size = int(res.headers.get('Content-Length', 0))
                with open(f"{osu_path}/#oszRedown/{s}.osz", 'wb') as file:
                    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, ncols=100) as pbar:
                        for data in res.iter_content(1024):
                            file.write(data)
                            pbar.update(len(data))
                log.info(f'{file_name} --> {s} 다운로드 완료\n'); break
            else:
                if i < len(url) - 1:
                    log.warning(f'{statusCode}. {mn} 에서 {setID} 파일을 다운로드할 수 없습니다. {urlName[i + 1]} 로 재시도!')
                else:
                    log.warning(f'{statusCode}. {mn} 에서 {setID} 파일을 다운로드할 수 없습니다!')
        zipfile.ZipFile(f"{osu_path}/#oszRedown/{s}.osz").extractall(f"{osu_path}/Songs/{s}")
    except Exception as e: exceptionE(e)

thrs = []
for s in songs:
    tr = threading.Thread(target=dl, args=(s,))
    thrs.append(tr); tr.start(); time.sleep(2) if MT else tr.join()
log.chat(f"{int(time.time() - st)} Sec | {osu_path}/#oszRedown 폴더는 삭제하고, logs.txt 존재시 확인 바람 (존재할 경우 자동 실행)"); input()
if os.path.exists("logs.txt"): os.system("start logs.txt")