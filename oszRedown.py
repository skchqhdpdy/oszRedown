import os
import requests
from tqdm import tqdm
import zipfile
import threading
import time
import traceback
import logUtils as log
import tkinter as tk
from tkinter import filedialog

def ExceptionE(e):
    log.error(e); e = f"{e}\n{traceback.format_exc()}"
    with open("logs.txt", "a", encoding="utf-8") as f: f.write(f"{e}\n\n")

st = int(time.time())
requestHeaders = {"User-Agent": "oszRedown.py"}
MT = input("멀티쓰레딩 활성화? (0/1 (0)) : ") == "1"
root = tk.Tk().withdraw()  #Tkinter 창 숨기기
osu_path = os.popen(f'reg query HKEY_CLASSES_ROOT\osu\Shell\Open\Command').read().strip().split('"')[1].replace("\\", "/").replace("/osu!.exe", "")
if not input(f"{osu_path} | 해당 경로가 osu!.exe 가 위치한 폴더가 맞나요? (0/1 (1)) : ") == "0": pass
else:
    osu_path = filedialog.askopenfilename(title="Error! Not Found osu! Path! | Select osu!.exe", filetypes=[("osu! executable", "osu!.exe")]).replace("/osu!.exe", "")

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
                    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, ncols=120) as pbar:
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
    except Exception as e: ExceptionE(e)

thrs = []
for s in songs:
    tr = threading.Thread(target=dl, args=(s,))
    thrs.append(tr); tr.start(); time.sleep(2) if MT else tr.join()
log.chat(f"{int(time.time() - st)} Sec | {osu_path}/#oszRedown 폴더는 삭제하고, logs.txt 존재시 확인 바람"); os.system("start logs.txt")
