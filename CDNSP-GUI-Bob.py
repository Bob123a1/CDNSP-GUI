#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Credit:
# Thanks to Zotan (DB and script), Big Poppa Panda, AnalogMan, F!rsT-S0uL
# Design inspiration: Lucas Rey's GUI (https://darkumbra.net/forums/topic/174470-app-cdnsp-gui-v105-download-nsp-gamez-using-a-gui/)
# Thanks to the developer(s) that worked on CDNSP_Next for the cert fix!
# Thanks to the help of devloper NighTime, kvn1351, gizmomelb, theLorknessMonster
# CDNSP - GUI - Bob - v4.1.1
import sys
import time
import random
import gettext
import platform
import locale
import json
import os

global sys_locale

if platform.system() != 'Darwin':
    sys_locale = locale.getdefaultlocale() # Detect system locale to fix Window size on Chinese Windows Computer
    sys_locale = sys_locale[0]
else:
    sys_locale = "Mac"

if sys_locale != "zh_CN":
    main_win = "1076x684+100+100"
    queue_win = "620x300+1177+100"
    scan_win = "415x100+100+170"
    base64_win = "497x100+95+176"
else:
    main_win = "1000x660+100+100"
    queue_win = "720x300+770+100"
    scan_win = "420x85+100+100"
    base64_win = "500x105+100+100"
        
config = {"Options": {
            "Download_location":  "",
            "Game_location": "",
            "NSP_repack":         "True",
            "Mute":               "False",
            "Titlekey_check":     "True",
            "noaria":             "True",
            "Disable_game_image": "False",
            "Shorten": "False",
            "Tinfoil": "False",
            "SysVerZero": "False",
            "Main_win": main_win,
            "Queue_win": queue_win,
            "Update_win": "600x400+120+200",
            "Scan_win": scan_win,
            "Base64_win": base64_win,
            "Language": "en"}
          }

try:
    f = open("CDNSP-GUI-config.json", 'r')
except FileNotFoundError:
    f = open("CDNSP-GUI-config.json", 'w')
    json.dump(config, f, indent=4)
    f.close()
    f = open("CDNSP-GUI-config.json", 'r')

j = json.load(f)

try:
    chosen_lang = j["Options"]["Language"]
except:
    f.close()
    j["Options"]["Language"] = "en" # Default to English language
    with open("CDNSP-GUI-config.json", 'w') as f:
        json.dump(j, f, indent=4)
    f.close()
    chosen_lang = "en"

def set_lang(default_lang = "en"):
    try:
        lang = gettext.translation('language', localedir='locales', languages=[default_lang])
        lang.install()
        print("Current language: {}".format(default_lang))
    except:
        lang = gettext.translation('language', localedir='locales', languages=["en"])
        lang.install()
        print("Language files not available yet!")
set_lang(chosen_lang)

if not os.path.isdir("Config"):
    os.mkdir("Config")

build_text = _("\nBuilding the current state file... Please wait, this may take some time \
depending on how many games you have.")

# Check that user is using Python 3
if (sys.version_info > (3, 0)):
    # Python 3 code in this block
    pass
else:
    # Python 2 code in this block
    print(_("\n\nError - Application launched with Python 2, please install Python 3 and delete Python 2\n"))
    time.sleep(1000)
    sys.exit()

from tkinter import *
import os
from tkinter import messagebox
import tkinter.ttk as ttk
from importlib import util
import subprocess
import urllib.request
import pip
from pathlib import Path

def check_req_file(file):
    if not os.path.exists(file):
        url = 'https://raw.githubusercontent.com/Bob123a1/CDNSP-GUI-Files/master/{}'.format(file)  
        urllib.request.urlretrieve(url, file)

def install_module(module):
    try:
        subprocess.check_output("pip3 install {}".format(module), shell=True)
    except:
        print(_("Error installing {0}, close the application and you can install the module manually by typing in CMD: pip3 install {0}").format(module))

def add_to_installed(tid, ver):
    installed_tid = []
    installed_ver = []
    
    if os.path.isfile("Config/installed.txt"):
        file = open("Config/installed.txt", "r", encoding="utf8")
        for game in file.readlines():
            installed_tid.append(game.split(",")[0].strip())
            installed_ver.append(game.split(",")[1].strip())
        file.close()
        if tid in installed_tid:
            if int(ver) > int(installed_ver[installed_tid.index(tid)]):
                installed_ver[installed_tid.index(tid)] = ver
                
        else:
            installed_tid.append(tid)
            installed_ver.append(ver)
        file = open("Config/installed.txt", "w", encoding="utf8")
        for i in range(len(installed_tid)):
            file.write("{}, {}\n".format(installed_tid[i], installed_ver[i]))
        file.close()
    
    
print(_("\nChecking if all required modules are installed!\n\n"))
try:
    import requests
except ImportError:
    install_module("requests")
    import requests       

try:
    from tqdm import tqdm
except ImportError:
    install_module("tqdm")
    from tqdm import tqdm  

try:
    import unidecode   
except ImportError:
    install_module("unidecode")
    import unidecode    

try:
    from PIL import Image, ImageTk   
except ImportError:
    install_module("Pillow")
    from PIL import Image, ImageTk

try:
    from bs4 import BeautifulSoup
except ImportError:
    install_module("beautifulsoup4")
    from bs4 import BeautifulSoup

try:
    import ssl
except:
    install_module("pyopenssl")
    import ssl

ssl._create_default_https_context = ssl._create_unverified_context # Thanks to user rdmrocha on Github

req_file = ["CDNSPconfig.json", "keys.txt", "nx_tls_client_cert.pem", "titlekeys.txt", "titlekeys_overwrite.txt"]
try:
    for file in req_file:
        check_req_file(file)
    print(_("Everything looks good!"))
except Exception as e:
    print(_("Unable to get required files! Check your internet connection: [{}]".format(str(e))))

# CDNSP script

import argparse
import base64
import platform
import re
import shlex
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from binascii import hexlify as hx, unhexlify as uhx
from io import TextIOWrapper
import os, sys
import subprocess
import urllib3
import json
import shutil
import argparse
import configparser
from hashlib import sha256
from struct import pack as pk, unpack as upk
from binascii import hexlify as hx, unhexlify as uhx
import xml.etree.ElementTree as ET, xml.dom.minidom as minidom    
import re
import datetime
import calendar
import operator
import base64
import shlex

from tkinter import filedialog
import threading
sys_name = "Win"
global noaria
noaria = True
import webbrowser
titlekey_list = []

global tqdmProgBar
tqdmProgBar = True

sysver0 = False

#Global Vars
truncateName = False
tinfoil = False
enxhop = False
    
import os, sys
import re
import shutil
import subprocess
import requests
import urllib3
import json
import argparse
import unicodedata as ud
import xml.etree.ElementTree as ET, xml.dom.minidom as minidom
from tqdm import tqdm
from hashlib import sha256
from struct import pack as pk, unpack as upk
from binascii import hexlify as hx, unhexlify as uhx


def read_at(f, off, len):
    f.seek(off)
    return f.read(len)

def read_u8(f, off):
    return upk('<B', read_at(f, off, 1))[0]

def read_u16(f, off):
    return upk('<H', read_at(f, off, 2))[0]

def read_u32(f, off):
    return upk('<I', read_at(f, off, 4))[0]
    
def read_u48(f, off):
    s = upk('<HI', read_at(f, off, 6))
    return s[1] << 16 | s[0]

def read_u64(f, off):
    return upk('<Q', read_at(f, off, 8))[0]
    
def sha256_file(fPath):
    f = open(fPath, 'rb')
    fSize = os.path.getsize(fPath)
    hash = sha256()
    
    if fSize >= 10000:
        t = tqdm(total=fSize, unit='B', unit_scale=True, desc=os.path.basename(fPath), leave=False)
        while True:
            buf = f.read(4096)
            if not buf:
                break
            hash.update(buf)
            t.update(len(buf))
        t.close()
    else:
        hash.update(f.read())
    f.close()
    return hash.hexdigest()
    
def bytes2human(n, f='%(value).3f %(symbol)s'):
    n = int(n)
    if n < 0:
        raise ValueError('n < 0')
    symbols = ('B', 'KB', 'MB', 'GB', 'TB')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return f % locals()
    return f % dict(symbol=symbols[0], value=n)

def get_name(tid):
    try:
        with open('titlekeys.txt',encoding="utf8") as f:
            lines = f.readlines()
    except Exception as e:
        print("Error:", e)
        exit()
    for line in lines:
        if line.strip() == '':
            return
        temp = line.split("|")
        if tid.endswith('800'):
            tid = '%s000' % tid[:-3]
        if tid.strip() == temp[0].strip()[:16]:
            return re.sub(r'[/\\:*?!"|™©®()]+', "", unidecode.unidecode(temp[2].strip()))
    return "UNKNOWN TITLE"
    
def safe_name(name):
    return re.sub('[^\x00-\x7f]', '', ud.normalize('NFD', name))
    
def safe_filename(safe_name):
    return re.sub('[<>.:"/\\|?*]+', '', safe_name)
    
def check_tid(tid):
    return re.match('0100[0-9a-fA-F]{12}', tid)
    
def check_tkey(tkey):
    return re.match('[0-9a-fA-F]{32}', tkey)
    
def load_config(fPath):
    dir = os.path.dirname(__file__)

    config = {'Paths': {
        'hactoolPath': 'hactool',
        'keysPath': 'keys.txt',
        'NXclientPath': 'nx_tls_client_cert.pem',
        'ShopNPath': 'ShopN.pem'},
        'Values': {
            'Region': 'US',
            'Firmware': '5.1.0-3',
            'DeviceID': '6265A5E4140FF804',
            'Environment': 'lp1',
            'TitleKeysURL': 'http://snip.li/newkeydb',
            'NspOut': '_NSPOUT',
            'AutoUpdatedb': 'False'}}
    try:
        f = open(fPath, 'r')
    except FileNotFoundError:
        f = open(fPath, 'w')
        json.dump(config, f)
        f.close()
        f = open(fPath, 'r')

    j = json.load(f)

    hactoolPath = j['Paths']['hactoolPath']
    keysPath = j['Paths']['keysPath']
    NXclientPath = j['Paths']['NXclientPath']
    ShopNPath = j['Paths']['ShopNPath']

    reg = j['Values']['Region']
    fw = j['Values']['Firmware']
    did = j['Values']['DeviceID']
    env = j['Values']['Environment']
    dbURL = j['Values']['TitleKeysURL']
    nspout = j['Values']['NspOut']

    if platform.system() == 'Linux':
        hactoolPath = './' + hactoolPath + '_linux'

    if platform.system() == 'Darwin':
        hactoolPath = './' + hactoolPath + '_mac'

    return hactoolPath, keysPath, NXclientPath, ShopNPath, reg, fw, did, env, dbURL, nspout
    
def gen_tik(fPath, rightsID, tkey, mkeyrev):
    f = open(fPath, 'wb')

    f.write(b'\x04\x00\x01\x00')
    f.write(0x100 * b'\xFF')
    f.write(0x3C  * b'\x00')
    f.write(b'Root-CA00000003-XS00000020')
    f.write(0x6   * b'\x00')
    f.write(0x20  * b'\x00')
    if tkey:
        f.write(uhx(tkey))
    else:
        f.write(0x10 * b'\x00')
    f.write(0xF0  * b'\x00')
    f.write(b'\x02\x00\x00\x00\x00')
    f.write(pk('<B', int(mkeyrev)))
    f.write(0xA   * b'\x00')
    f.write(0x10  * b'\x00')
    f.write(uhx(rightsID))
    f.write(0x8   * b'\x00')
    f.write(b'\xC0\x02\x00\x00\x00\x00\x00\x00')

    f.close()
    return fPath
    
def gen_cert(fPath):
    f = open(fPath, 'wb')
    f.write(uhx(b'''\
00010003704138efbbbda16a987dd901
326d1c9459484c88a2861b91a312587a
e70ef6237ec50e1032dc39dde89a96a8
e859d76a98a6e7e36a0cfe352ca89305
8234ff833fcb3b03811e9f0dc0d9a52f
8045b4b2f9411b67a51c44b5ef8ce77b
d6d56ba75734a1856de6d4bed6d3a242
c7c8791b3422375e5c779abf072f7695
efa0f75bcb83789fc30e3fe4cc839220
7840638949c7f688565f649b74d63d8d
58ffadda571e9554426b1318fc468983
d4c8a5628b06b6fc5d507c13e7a18ac1
511eb6d62ea5448f83501447a9afb3ec
c2903c9dd52f922ac9acdbef58c60218
48d96e208732d3d1d9d9ea440d91621c
7a99db8843c59c1f2e2c7d9b577d512c
166d6f7e1aad4a774a37447e78fe2021
e14a95d112a068ada019f463c7a55685
aabb6888b9246483d18b9c806f474918
331782344a4b8531334b26303263d9d2
eb4f4bb99602b352f6ae4046c69a5e7e
8e4a18ef9bc0a2ded61310417012fd82
4cc116cfb7c4c1f7ec7177a17446cbde
96f3edd88fcd052f0b888a45fdaf2b63
1354f40d16e5fa9c2c4eda98e798d15e
6046dc5363f3096b2c607a9d8dd55b15
02a6ac7d3cc8d8c575998e7d796910c8
04c495235057e91ecd2637c9c1845151
ac6b9a0490ae3ec6f47740a0db0ba36d
075956cee7354ea3e9a4f2720b26550c
7d394324bc0cb7e9317d8a8661f42191
ff10b08256ce3fd25b745e5194906b4d
61cb4c2e000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
526f6f74000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
00000001434130303030303030330000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
000000007be8ef6cb279c9e2eee121c6
eaf44ff639f88f078b4b77ed9f9560b0
358281b50e55ab721115a177703c7a30
fe3ae9ef1c60bc1d974676b23a68cc04
b198525bc968f11de2db50e4d9e7f071
e562dae2092233e9d363f61dd7c19ff3
a4a91e8f6553d471dd7b84b9f1b8ce73
35f0f5540563a1eab83963e09be90101
1f99546361287020e9cc0dab487f140d
6626a1836d27111f2068de4772149151
cf69c61ba60ef9d949a0f71f5499f2d3
9ad28c7005348293c431ffbd33f6bca6
0dc7195ea2bcc56d200baf6d06d09c41
db8de9c720154ca4832b69c08c69cd3b
073a0063602f462d338061a5ea6c915c
d5623579c3eb64ce44ef586d14baaa88
34019b3eebeed3790001000100000000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
00010004969fe8288da6b9dd52c7bd63
642a4a9ae5f053eccb93613fda379920
87bd9199da5e6797618d77098133fd5b
05cd8288139e2e975cd2608003878cda
f020f51a0e5b7692780845561b31c618
08e8a47c3462224d94f736e9a14e56ac
bf71b7f11bbdee38ddb846d6bd8f0ab4
e4948c5434eaf9bf26529b7eb83671d3
ce60a6d7a850dbe6801ec52a7b7a3e5a
27bc675ba3c53377cfc372ebce02062f
59f37003aa23ae35d4880e0e4b69f982
fb1bac806c2f75ba29587f2815fd7783
998c354d52b19e3fad9fbef444c48579
288db0978116afc82ce54dacb9ed7e1b
fd50938f22f85eecf3a4f426ae5feb15
b72f022fb36ecce9314dad131429bfc9
675f58ee000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
526f6f742d4341303030303030303300
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
00000001585330303030303032300000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
0000000000000000d21d3ce67c1069da
049d5e5310e76b907e18eec80b337c47
23e339573f4c664907db2f0832d03df5
ea5f160a4af24100d71afac2e3ae75af
a1228012a9a21616597df71eafcb6594
1470d1b40f5ef83a597e179fcb5b57c2
ee17da3bc3769864cb47856767229d67
328141fc9ab1df149e0c5c15aeb80bc5
8fc71be18966642d68308b506934b8ef
779f78e4ddf30a0dcf93fcafbfa131a8
839fd641949f47ee25ceecf814d55b0b
e6e5677c1effec6f29871ef29aa3ed91
97b0d83852e050908031ef1abbb5afc8
b3dd937a076ff6761ab362405c3f7d86
a3b17a6170a659c16008950f7f5e06a5
de3e5998895efa7deea060be9575668f
78ab1907b3ba1b7d0001000100000000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000'''.replace(b'\n', b'')))
    f.close()
    return fPath
    
def decrypt_NCA(fPath, outDir=''):
    if not outDir:
        outDir = os.path.splitext(fPath)[0]
    os.makedirs(outDir, exist_ok=True)
    
    commandLine = hactoolPath + ' "' + fPath + '"' + keysArg\
                  + ' --exefsdir="'    + outDir + '/exefs"'\
                  + ' --romfsdir="'    + outDir + '/romfs"'\
                  + ' --section0dir="' + outDir + '/section0"'\
                  + ' --section1dir="' + outDir + '/section1"'\
                  + ' --section2dir="' + outDir + '/section2"'\
                  + ' --section3dir="' + outDir + '/section3"'\
                  + ' --header="'      + outDir + '/Header.bin"'
                  
    pipes = subprocess.Popen(commandLine, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    _, std_err = pipes.communicate()

    if pipes.returncode != 0:
        err_msg = '%s. Code: %s' % (std_err.strip(), pipes.returncode)
        raise Exception(err_msg)
    elif len(std_err):
        raise Exception(std_err)
        
    return outDir
    
def get_name_from_nacp(fPath):
    dir = decrypt_NCA(fPath)
    nacpPath = os.path.join(dir, 'romfs', 'control.nacp')
    try: 
        f = open(nacpPath, 'rb')
        name = f.read(0x200).strip(b'\x00').decode()
        f.close()
        return safe_name(name)
    except FileNotFoundError:
        return ''

def make_request(method, url, certificate='', hdArgs={}):
    if not certificate: # Workaround for defining errors
        certificate = NXclientPath
    
    reqHd = {'User-Agent': 'NintendoSDK Firmware/%s (platform:NX; did:%s; eid:%s)' % (fw, did, env),
             'Accept-Encoding': 'gzip, deflate',
             'Accept': '*/*',
             'Connection': 'keep-alive'}
    reqHd.update(hdArgs)
    
    r = requests.request(method, url, cert=certificate, headers=reqHd, verify=False, stream=True)
    
    if r.status_code == 403:
        raise requests.exceptions.SSLError('Request rejected!')
    if r.status_code == 404:
        raise requests.exceptions.HTTPError('File doesn\'t exist!')
    
    return r

def make_request_new(method, url, certificate='', hdArgs={}):
    if certificate == '':  # Workaround for defining errors
        certificate = NXclientPath

    reqHd = {'User-Agent': 'NintendoSDK Firmware/%s (platform:NX; eid:%s)' % (fw, env),
             'Accept-Encoding': 'gzip, deflate',
             'Accept': '*/*',
             'Connection': 'keep-alive'}
    reqHd.update(hdArgs)
    r = requests.request(method, url, cert=certificate, headers=reqHd, verify=False, stream=True)
    
    if r.status_code == 403:
        print('Request rejected by server! Check your cert.')
        return r

    return r
    
def print_info(tid):
    print('\n%s:' % tid)
    if tid.endswith('000'):
        basetid   = tid
        updatetid = '%016x' % (int(tid, 16) + 0x800)
    elif tid.endswith('800'):
        basetid   = '%016x' % (int(tid, 16) & 0xFFFFFFFFFFFFF000)
        updatetid = tid
    else:
        basetid     = '%016x' % (int(tid, 16) - 0x1000 & 0xFFFFFFFFFFFFF000)
        updatetid   = basetid[:-3] + '800'
        
    try:
        _, name, size = get_info(tid=basetid)
    except requests.exceptions.SSLError:
        print('\tCould not get info from Shogun')
        name = ''
        size = 0
        
    if name:
        print('\tName: %s' % name)
    if size:
        print('\tSize: %s' % bytes2human(size))
        
    if tid != basetid:    
        versions = get_versions(tid)
        print('\n\tAvailable versions for %s:' % tid)
        print('\t\tv' + ' v'.join(versions))
    
    print('\n\tBase TID:   %s' % basetid)
    versions = get_versions(basetid)
    print('\tAvailable versions for %s:' % basetid)
    print('\t\tv' + ' v'.join(versions))
    
    print('\n\tUpdate TID: %s' % updatetid)
    versions = get_versions(updatetid)
    print('\tAvailable versions for %s:' % updatetid)
    if versions:
        print('\t\tv' + ' v'.join(versions))
    else:
        print('\t\t%s has no version available' % updatetid)
    
def get_info(tid='', freeword=''):
    print(tid)
    print("HEEELOOO")
    if tid:
        url = 'https://bugyo.hac.%s.eshop.nintendo.net/shogun/v1/contents/ids?shop_id=4&lang=en&country=%s&type=title&title_ids=%s'\
            % (env, reg, tid)
        r = make_request('GET', url, certificate=ShopNPath)
        j = r.json()
        nsuid = j['id_pairs'][0]['id']
        print(nsuid)
    elif freeword:
        url = 'https://bugyo.hac.lp1.eshop.nintendo.net/shogun/v1/titles?shop_id=4&lang=en&offset=0&country=%s&limit=25&sort=popular&freeword=%s'\
               % (reg, freeword)
        r = make_request('GET', url, certificate=ShopNPath)
        j = r.json()
        nsuid = j['contents'][0]['id']
    
    try:
        url = 'https://bugyo.hac.%s.eshop.nintendo.net/shogun/v1/titles/%s?shop_id=4&lang=en&country=%s' % (env, nsuid, reg)
        r = make_request('GET', url, certificate=ShopNPath)
        j = r.json()
        
        if freeword:
            try:
                tid = j['applications'][0]['id']
            except KeyError:
                print('Found no result for %s on Shogun' % freeword)
                raise
        
        try:
            name = j['formal_name']
            name = safe_name(name)
        except IndexError:
            name = ''
        
        try:
            size = j['total_rom_size']
        except IndexError:
            size = 0
            
    except IndexError:
        print('\tTitleID not found on Shogun!')
        
    return tid, name, size
    
def get_versions(tid):
    #url = 'https://tagaya.hac.%s.eshop.nintendo.net/tagaya/hac_versionlist' % env
    url = 'https://superfly.hac.%s.d4c.nintendo.net/v1/t/%s/dv' % (env,tid)
    r = make_request_new('GET', url)
    j = r.json()

    try:
        if j['error']:
            return ['none']
    except Exception as e:
        pass
    try:
        lastestVer = j['version']
        if lastestVer < 65536:
            return ['%s' % lastestVer]
        else:
            versionList = ('%s' % "-".join(str(i) for i in range(0x10000, lastestVer+1, 0x10000))).split('-')
            return versionList
    except Exception as e:
        return ['none']
       
def check_versions(fPath):
    f = open(fPath, 'r')

    old = {}
    for line in f.readlines():
            tid, ver = line.strip().split('-')
            old[tid] = ver
    
    n = 1
    new = {}
    for tid in old:
        sys.stdout.write('\rChecking for updates for title %s of %s...' % (n, len(old)))
        sys.stdout.flush()
        n += 1
        
        latestVer = get_versions(tid)[-1]
        
        if latestVer and int(latestVer) > int(old[tid]):
            new[tid] = latestVer

        if tid.endswith('000'):
            updatetid = '%016x'.lower() % (int(tid, 16) + 0x800)
            if updatetid not in old:
                updateVer = get_versions(updatetid)
                if updateVer:
                    new[updatetid] = updateVer[-1]
    sys.stdout.write('\r\033[F')
    
    if new:
        for tid in new:
            print('New update available for %s: v%s' % (tid, new[tid]))
        
        dl = input('\nType anything to download the new updates: ')
        if dl:
            for tid in new:
                download_game(tid, new[tid], nspRepack=True, verify=True)
    else:
        print('No new update was found for any of the downloaded titles!')
            
    f.close()

def download_file(url, fPath, fSize=0):
    fName = os.path.basename(fPath).split()[0]
    
    if os.path.exists(fPath) and fSize != 0:
        dlded = os.path.getsize(fPath)
            
        if dlded == fSize:
            print('\t\tDownload is already complete, skipping!')
            return fPath
        elif dlded < fSize:
            print('\t\tResuming download...')
            r = make_request('GET', url, hdArgs={'Range': 'bytes=%s-' % dlded})
            f = open(fPath, 'ab')
        else:
            print('\t\tExisting file is bigger than expected (%s/%s), restarting download...' % (dlded, fSize))
            dlded = 0
            r = make_request('GET', url)
            f = open(fPath, "wb")
    else:
        dlded = 0
        r = make_request('GET', url)
        fSize = int(r.headers.get('Content-Length'))
        f = open(fPath, 'wb')
        
    if fSize >= 10000:
        t = tqdm(initial=dlded, total=int(fSize), desc=fName, unit='B', unit_scale=True, leave=False, mininterval=0.5)
        for chunk in r.iter_content(4096):
            f.write(chunk)
            dlded += len(chunk)
            t.update(len(chunk))
        t.close()
    else:
        f.write(r.content)
        dlded += len(r.content)
    
    if fSize != 0 and dlded != fSize:
        raise ValueError('Downloaded data is not as big as expected (%s/%s)!' % (dlded, fSize))
        
    f.close()    
    print('\r\t\tSaved to %s!' % os.path.basename(f.name))
    return fPath
    
def download_cetk(rightsID, fPath):
    url = 'https://atum.hac.%s.d4c.nintendo.net/r/t/%s?device_id=%s' % (env, rightsID, did)
    r = make_request('HEAD', url)
    id = r.headers.get('X-Nintendo-Content-ID')
    
    url = 'https://atum.hac.%s.d4c.nintendo.net/c/t/%s?device_id=%s' % (env, id, did)
    cetk = download_file(url, fPath, fSize=2496)
    
    return cetk
        
def download_title(gameDir, tid, ver, tkey='', nspRepack=False, verify=False, n=''):
    print('\n%s v%s:' % (tid, ver))
    if len(tid) != 16:
        tid = (16-len(tid)) * '0' + tid
    
    url = 'https://atum%s.hac.%s.d4c.nintendo.net/t/a/%s/%s?device_id=%s' % (n, env, tid, ver, did)
    r = make_request('HEAD', url)
    CNMTid = r.headers.get('X-Nintendo-Content-ID')
    
    print('\tDownloading CNMT (%s.cnmt.nca)...' % CNMTid)
    url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/a/%s?device_id=%s' % (n, env, CNMTid, did)
    fPath = os.path.join(gameDir, CNMTid + '.cnmt.nca')
    cnmtNCA = download_file(url, fPath)
    
    cnmtDir = decrypt_NCA(cnmtNCA)
    CNMT = cnmt(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]), 
                os.path.join(cnmtDir, 'Header.bin'))
    
    if nspRepack:
        outf = os.path.join(gameDir, '%s.xml' % os.path.basename(cnmtNCA).strip('.nca'))
        cnmtXML = CNMT.gen_xml(cnmtNCA, outf)
        
        rightsID = '%032x' % ((int(tid, 16) << 64) + int(CNMT.mkeyrev))
        
        tikPath  = os.path.join(gameDir, rightsID+'.tik')
        certPath = os.path.join(gameDir, rightsID+'.cert')
        if CNMT.type == 'Application' or CNMT.type == 'AddOnContent':
            gen_cert(certPath)
            gen_tik(tikPath, rightsID, tkey, CNMT.mkeyrev)
            
            print('\t\tGenerated %s and %s!' % (os.path.basename(certPath), os.path.basename(tikPath)))
        elif CNMT.type == 'Patch':
            print('\tDownloading CETK...')
            
            with open(download_cetk(rightsID, os.path.join(gameDir, rightsID+'.cetk')), 'rb') as cetk:
                cetk.seek(0x180)
                tkey = hx(cetk.read(0x10)).decode()
                print('\t\t\tTitlekey: %s' % tkey)
                
                with open(tikPath, 'wb') as tik:
                    cetk.seek(0x0)
                    tik.write(cetk.read(0x2C0))
                    
                with open(certPath, 'wb') as cert:
                    cetk.seek(0x2C0)
                    cert.write(cetk.read(0x700))
                    
            print('\t\tExtracted %s and %s from CETK!' % (os.path.basename(certPath), os.path.basename(tikPath)))
            
    NCAs = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
    }
    
    name = ''
    for type in [0, 3, 4, 5, 1, 2, 6]: # Download smaller files first
        list = CNMT.parse(CNMT.contentTypes[type])
        for ncaID in list:
            print('\tDownloading %s entry (%s.nca)...' % (CNMT.contentTypes[type], ncaID))
            url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/c/%s?device_id=%s' % (n, env, ncaID, did)
            fPath = os.path.join(gameDir, ncaID + '.nca')
            fSize = list[ncaID][1]
            
            NCAs[type].append(download_file(url, fPath, fSize))
            
            if verify:
                print('\t\tVerifying file...')
                if sha256_file(fPath) == list[ncaID][2]:
                    print('\t\t\tHashes match, file is correct!')
                else:
                    print('\t\t\t%s is corrupted, hashes don\'t match!' % os.path.basename(fPath))
           
            if type == 3:
                name = get_name_from_nacp(NCAs[type][-1])
    
    if not name:
        name = ''
        
    if nspRepack:
        files = []
        if tkey:
            files.append(certPath)
            files.append(tikPath)
        for key in [1, 5, 2, 4, 6]:
            if NCAs[key]:
                files.extend(NCAs[key])
        files.append(cnmtNCA)
        files.append(cnmtXML)
        if NCAs[3]:
            files.extend(NCAs[3])
        
        return files, name
    else:
        return gameDir, name

def download_title_tinfoil(gameDir, tid, ver, tkey='', nspRepack=False, n='', verify=False):
    print('\n%s v%s:' % (tid, ver))
    tid = tid.lower();
    tkey = tkey.lower();
    if len(tid) != 16:
        tid = (16 - len(tid)) * '0' + tid

    url = 'https://atum.hac.%s.d4c.nintendo.net/t/a/%s/%s?device_id=%s' % (env, tid, ver, did)
    print(url)
    try:
        r = make_request_new('HEAD', url)
    except Exception as e:
        print("Error downloading title. Check for incorrect titleid or version.")
        return
    CNMTid = r.headers.get('X-Nintendo-Content-ID')

    if CNMTid == None:
        print('title not available on CDN')
        return

    print('\nDownloading CNMT (%s.cnmt.nca)...' % CNMTid)
    url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/a/%s?device_id=%s' % (n, env, CNMTid, did)
    fPath = os.path.join(gameDir, CNMTid + '.cnmt.nca')
    cnmtNCA = download_file(url, fPath)
    cnmtDir = decrypt_NCA(cnmtNCA)
    CNMT = cnmt(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]),
                os.path.join(cnmtDir, 'Header.bin'))

    if nspRepack == True:
        outf = os.path.join(gameDir, '%s.xml' % os.path.basename(cnmtNCA.strip('.nca')))
        cnmtXML = CNMT.gen_xml_tinfoil(cnmtNCA, outf)

        rightsID = '%s%s%s' % (tid, (16 - len(CNMT.mkeyrev)) * '0', CNMT.mkeyrev)

        tikPath = os.path.join(gameDir, '%s.tik' % rightsID)
        certPath = os.path.join(gameDir, '%s.cert' % rightsID)
        if CNMT.type == 'Application' or CNMT.type == 'AddOnContent':
            shutil.copy(os.path.join(os.path.dirname(__file__), 'Certificate.cert'), certPath)

            if tkey != '':
                with open(os.path.join(os.path.dirname(__file__), 'Ticket.tik'), 'rb') as intik:
                    data = bytearray(intik.read())
                    data[0x180:0x190] = uhx(tkey)
                    data[0x286] = int(CNMT.mkeyrev)
                    data[0x2A0:0x2B0] = uhx(rightsID)

                    with open(tikPath, 'wb') as outtik:
                        outtik.write(data)
                print('\nGenerated %s and %s!' % (os.path.basename(certPath), os.path.basename(tikPath)))
            else:
                print('\nGenerated %s!' % os.path.basename(certPath))
        elif CNMT.type == 'Patch':
            print('\nDownloading cetk...')

            with open(download_cetk(rightsID, os.path.join(gameDir, '%s.cetk' % rightsID)), 'rb') as cetk:
                cetk.seek(0x180)
                tkey = hx(cetk.read(0x10)).decode()
                print('\nTitlekey: %s' % tkey)

                with open(tikPath, 'wb') as tik:
                    cetk.seek(0x0)
                    tik.write(cetk.read(0x2C0))

                with open(certPath, 'wb') as cert:
                    cetk.seek(0x2C0)
                    cert.write(cetk.read(0x700))

            print('\nExtracted %s and %s from cetk!' % (os.path.basename(certPath), os.path.basename(tikPath)))

    NCAs = {}
    for type in [3]:  # Download smaller files first
        for ncaID in CNMT.parse(CNMT.ncaTypes[type]):
            print('\nDownloading %s entry (%s.nca)...' % (CNMT.ncaTypes[type], ncaID))
            url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/c/%s?device_id=%s' % (n, env, ncaID, did)
            fPath = os.path.join(gameDir, ncaID + '.nca')
            NCAs.update({type: download_file(url, fPath)})
            if verify:
                if calc_sha256(fPath) != CNMT.parse(CNMT.ncaTypes[type])[ncaID][2]:
                    print('\n\n%s is corrupted, hashes don\'t match!' % os.path.basename(fPath))
                else:
                    print('\nVerified %s...' % os.path.basename(fPath))

    if nspRepack == True:
        files = []
        files.append(certPath)
        if tkey != '':
            files.append(tikPath)
        files.append(cnmtXML)
        try:
            files.append(NCAs[3])
        except KeyError:
            pass

        return files
    
def download_game(tid, ver, tkey='', nspRepack=False, verify=False, clean=False, path_Dir=""):
    name = get_name(tid)
    global titlekey_check
    gameType = ''
    basetid = ''
    
    if name == 'Unknown Title':
        temp = "[" + tid + "]"
    else:
        temp = name + " [" + tid + "]"

    if tid.endswith('000'):  # Base game
        gameType = 'BASE'
    elif tid.endswith('800'):  # Update
        basetid = '%s000' % tid[:-3]
        gameType = 'UPD'
    else:  # DLC
        basetid = '%s%s000' % (tid[:-4], str(int(tid[-4], 16) - 1))
        gameType = 'DLC'
        
    if path_Dir == "":
        path_Dir = os.path.join(os.path.dirname(__file__), "_NSPOUT")
    
    gameDir = os.path.join(path_Dir, tid)

    if not os.path.exists(gameDir):
        os.makedirs(gameDir, exist_ok=True)
        
    outputDir = path_Dir

    if not os.path.exists(outputDir):
        os.makedirs(outputDir, exist_ok=True)

   
    if name != "":
        if gameType == "DLC":
            outf = os.path.join(outputDir, '%s [%s][v%s]' % (name,tid,ver))
        elif gameType == 'BASE':
            outf = os.path.join(outputDir, '%s [%s][v%s]' % (name,tid,ver))
        else:
            outf = os.path.join(outputDir, '%s [%s][%s][v%s]' % (name,gameType,tid,ver))
    else:
        if gameType == "DLC":
            outf = os.path.join(outputDir, '%s [%s][v%s]' % (name,tid,ver))
        elif gameType == 'BASE':
            outf = os.path.join(outputDir, '%s [v%s]' % (tid,ver))
        else:
            outf = os.path.join(outputDir, '%s [%s][v%s]' % (tid,gameType,ver))
    outname = outf.split(outputDir)[1][1:]

    if truncateName:
        name = name.replace(' ','')[0:20]
        outf = os.path.join(outputDir, '%s%sv%s' % (name,tid,ver))

    if tinfoil:
        outf = outf + '[tf]'

    outf = outf + '.nsp'

    for item in os.listdir(outputDir):
        if item.find('%s' % tid) != -1:
            if item.find('v%s' % ver) != -1:
                if not tinfoil:
                    print('%s already exists, skipping download' % outf)
                    shutil.rmtree(gameDir)
                    return
    os.makedirs(gameDir, exist_ok=True)
    
    if tid.endswith('800'):
        basetid = '%016x' % (int(tid, 16) & 0xFFFFFFFFFFFFF000)
    elif not tid.endswith('000'):
        basetid = '%016x' % (int(tid, 16) - 0x1000 & 0xFFFFFFFFFFFFF000)
    else:
        basetid = tid
    if tinfoil:
        files = download_title_tinfoil(gameDir, tid, ver, tkey, nspRepack, verify=verify)
    else:
        files, name = download_title(gameDir, tid, ver, tkey, nspRepack, verify)

    
    if nspRepack:
        os.makedirs(path_Dir, exist_ok=True)
        NSP = nsp(outf, files)
        NSP.repack()
        shutil.rmtree(gameDir, ignore_errors=True)

    add_to_installed(tid, ver)
    return gameDir
    
def download_sysupdate(ver):
    if ver == 'LTST':
        url = 'https://sun.hac.%s.d4c.nintendo.net/v1/system_update_meta?device_id=%s' % (env, did)
        r = make_request('GET', url)
        j = r.json()
        ver = str(j['system_update_metas'][0]['title_version'])
    
    sysupdateDir = os.path.join(os.path.dirname(__file__), '0100000000000816-SysUpdate', ver)
    os.makedirs(sysupdateDir, exist_ok=True)
    
    url = 'https://atumn.hac.%s.d4c.nintendo.net/t/s/0100000000000816/%s?device_id=%s' % (env, ver, did)
    r = make_request('HEAD', url)
    cnmtID = r.headers.get('X-Nintendo-Content-ID')
    
    print('\nDownloading CNMT (%s)...' % cnmtID)
    url = 'https://atumn.hac.%s.d4c.nintendo.net/c/s/%s?device_id=%s' % (env, cnmtID, did)
    fPath = os.path.join(sysupdateDir, '%s.cnmt.nca' % cnmtID)
    cnmtNCA = download_file(url, fPath)
    
    cnmtDir = decrypt_NCA(cnmtNCA)
    CNMT = cnmt(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]), 
                os.path.join(cnmtDir, 'Header.bin'))
    
    titles = CNMT.parse()
    for title in titles:
        dir = os.path.join(sysupdateDir, title)
        os.makedirs(dir, exist_ok=True)
        download_title(dir, title, titles[title][0], n='n')
        
    return sysupdateDir    
    
class cnmt:
    titleTypes = {
        0x1: 'SystemProgram',
        0x2: 'SystemData',
        0x3: 'SystemUpdate',
        0x4: 'BootImagePackage',
        0x5: 'BootImagePackageSafe',
        0x80:'Application',
        0x81:'Patch',
        0x82:'AddOnContent',
        0x83:'Delta'
    }
    contentTypes  = {
        0:'Meta', 
        1:'Program', 
        2:'Data', 
        3:'Control', 
        4:'HtmlDocument', 
        5:'LegalInformation', 
        6:'DeltaFragment'
    }

    def __init__(self, fPath, hdPath):                    
        f = open(fPath, 'rb')
        
        self.path     = fPath
        self.type     = self.titleTypes[read_u8(f, 0xC)]
        self.id       = '%016x' % read_u64(f, 0x0)
        self.ver      = str(read_u32(f, 0x8))
        self.sysver   = str(read_u64(f, 0x28))
        self.dlsysver = str(read_u64(f, 0x18))
        self.digest   = hx(read_at(f, f.seek(0, 2)-0x20, f.seek(0, 2))).decode()

        self.packTypes = {0x1: 'SystemProgram',
                          0x2: 'SystemData',
                          0x3: 'SystemUpdate',
                          0x4: 'BootImagePackage',
                          0x5: 'BootImagePackageSafe',
                          0x80: 'Application',
                          0x81: 'Patch',
                          0x82: 'AddOnContent',
                          0x83: 'Delta'}

        self.ncaTypes = {0: 'Meta', 1: 'Program', 2: 'Data', 3: 'Control',
                         4: 'HtmlDocument', 5: 'LegalInformation', 6: 'DeltaFragment'}

        
        with open(hdPath, 'rb') as ncaHd:
            self.mkeyrev = str(read_u8(ncaHd, 0x220))
        
        f.close()

    def parse(self, contentType=''):
        f = open(self.path, 'rb')
        
        data = {}
        if self.type == 'SystemUpdate':
            metaEntriesNB = read_u16(f, 0x12)
            for n in range(metaEntriesNB):
                offset = 0x20 + 0x10*n
                tid  = '%016x' % read_u64(f, offset)
                ver  = str(read_u32(f, offset+0x8))
                titleType = self.titleTypes[read_u8(f, offset+0xC)]
                
                data[tid] = ver, titleType
        else:
            tableOffset = read_u16(f,0xE)
            contentEntriesNB = read_u16(f, 0x10)
            for n in range(contentEntriesNB):
                offset = 0x20 + tableOffset + 0x38*n
                hash = hx(read_at(f, offset, 0x20)).decode()
                tid  = hx(read_at(f, offset+0x20, 0x10)).decode()
                size = read_u48(f, offset+0x30)
                type = self.contentTypes[read_u16(f, offset+0x36)]
                
                if type == contentType or contentType == '':
                    data[tid] = type, size, hash
    
        f.close()
        return data
     
    def gen_xml(self, ncaPath, outf):
        data = self.parse()
            
        ContentMeta = ET.Element('ContentMeta')
        
        ET.SubElement(ContentMeta, 'Type').text                          = self.type
        ET.SubElement(ContentMeta, 'Id').text                            = '0x' + self.id
        ET.SubElement(ContentMeta, 'Version').text                       = self.ver
        ET.SubElement(ContentMeta, 'RequiredDownloadSystemVersion').text = self.dlsysver
        
        n = 1
        for tid in data:
            locals()["Content"+str(n)] = ET.SubElement(ContentMeta, 'Content')
            ET.SubElement(locals()["Content"+str(n)], 'Type').text          = data[tid][0]
            ET.SubElement(locals()["Content"+str(n)], 'Id').text            = tid
            ET.SubElement(locals()["Content"+str(n)], 'Size').text          = str(data[tid][1])
            ET.SubElement(locals()["Content"+str(n)], 'Hash').text          = data[tid][2]
            ET.SubElement(locals()["Content"+str(n)], 'KeyGeneration').text = self.mkeyrev
            n += 1
            
        # cnmt.nca itself
        cnmt = ET.SubElement(ContentMeta, 'Content')
        ET.SubElement(cnmt, 'Type').text          = 'Meta'
        ET.SubElement(cnmt, 'Id').text            = os.path.basename(ncaPath).split('.')[0]
        ET.SubElement(cnmt, 'Size').text          = str(os.path.getsize(ncaPath))
        ET.SubElement(cnmt, 'Hash').text          = sha256_file(ncaPath)
        ET.SubElement(cnmt, 'KeyGeneration').text = self.mkeyrev
            
        ET.SubElement(ContentMeta, 'Digest').text                = self.digest
        ET.SubElement(ContentMeta, 'KeyGenerationMin').text      = self.mkeyrev
        ET.SubElement(ContentMeta, 'RequiredSystemVersion').text = self.sysver
        if self.type == 'Application':
            ET.SubElement(ContentMeta, 'PatchId').text       = '0x%016x' % (int(self.id, 16) + 0x800)
        elif self.type == 'Patch':
            ET.SubElement(ContentMeta, 'OriginalId').text    = '0x%016x' % (int(self.id, 16) & 0xFFFFFFFFFFFFF000)
        elif self.type == 'AddOnContent':    
            ET.SubElement(ContentMeta, 'ApplicationId').text = '0x%016x' % (int(self.id, 16) - 0x1000 & 0xFFFFFFFFFFFFF000)
        
        string = ET.tostring(ContentMeta, encoding='utf-8')
        reparsed = minidom.parseString(string)
        with open(outf, 'wb') as f:
            f.write(reparsed.toprettyxml(encoding='utf-8', indent='  ')[:-1])
            
        print('\t\tGenerated %s!' % os.path.basename(outf))
        return outf

    def gen_xml_tinfoil(self, ncaPath, outf):
        data = self.parse()
        hdPath = os.path.join(os.path.dirname(ncaPath),
                              '%s.cnmt' % os.path.basename(ncaPath).split('.')[0], 'Header.bin')
        print(hdPath)
        with open(hdPath, 'rb') as ncaHd:
            mKeyRev = str(read_u8(ncaHd, 0x220))
        print(mKeyRev)
        ContentMeta = ET.Element('ContentMeta')

        ET.SubElement(ContentMeta, 'Type').text = self.type
        ET.SubElement(ContentMeta, 'Id').text = '0x%s' % self.id
        ET.SubElement(ContentMeta, 'Version').text = self.ver
        ET.SubElement(ContentMeta, 'RequiredDownloadSystemVersion').text = self.dlsysver

        n = 1
        for tid in data:
            if data[tid][0] == 'Control':
                locals()["Content" + str(n)] = ET.SubElement(ContentMeta, 'Content')
                ET.SubElement(locals()["Content" + str(n)], 'Type').text = data[tid][0]
                ET.SubElement(locals()["Content" + str(n)], 'Id').text = tid
                ET.SubElement(locals()["Content" + str(n)], 'Size').text = str(data[tid][1])
                ET.SubElement(locals()["Content" + str(n)], 'Hash').text = str(data[tid][2])
                ET.SubElement(locals()["Content" + str(n)], 'KeyGeneration').text = mKeyRev
                n += 1

        # cnmt.nca itself
        hash = sha256()
        with open(ncaPath, 'rb') as nca:
            hash.update(nca.read())  # Buffer not needed
        ET.SubElement(ContentMeta, 'Digest').text = self.digest
        ET.SubElement(ContentMeta, 'KeyGenerationMin').text = self.mkeyrev
        global sysver0
        ET.SubElement(ContentMeta, 'RequiredSystemVersion').text = ('0' if sysver0 else self.sysver)
        if self.id.endswith('800'):
            ET.SubElement(ContentMeta, 'PatchId').text = '0x%s000' % self.id[:-3]
        else:
            ET.SubElement(ContentMeta, 'PatchId').text = '0x%s800' % self.id[:-3]
        string = ET.tostring(ContentMeta, encoding='utf-8')
        reparsed = minidom.parseString(string)
        with open(outf, 'w') as f:
            f.write(reparsed.toprettyxml(encoding='utf-8', indent='  ').decode()[:-1])

        print('\nGenerated %s!' % os.path.basename(outf))
        return outf

class nsp:
    def __init__(self, outf, files):
        self.path = outf
        self.files = files
        
    def repack(self):
        print('\tRepacking to NSP...')
        
        hd = self._gen_header()
        
        totSize = len(hd) + sum(os.path.getsize(file) for file in self.files)
        if os.path.exists(self.path) and os.path.getsize(self.path) == totSize:
            print('\t\tRepack %s is already complete!' % self.path)
            return
            
        t = tqdm(total=totSize, unit='B', unit_scale=True, desc=os.path.basename(self.path), leave=False)
        
        t.write('\t\tWriting header...')
        outf = open(self.path, 'wb')
        outf.write(hd)
        t.update(len(hd))
        
        for file in self.files:
            t.write('\t\tAppending %s...' % os.path.basename(file))
            with open(file, 'rb') as inf:
                while True:
                    buf = inf.read(4096)
                    if not buf:
                        break
                    outf.write(buf)
                    t.update(len(buf))
        t.close()
        
        outf.close()
        print('\t\tRepacked to %s!' % outf.name)
        
    def _gen_header(self):
        filesNb = len(self.files)
        stringTable = '\x00'.join(os.path.basename(file) for file in self.files)
        headerSize = 0x10 + filesNb*0x18 + len(stringTable)
        remainder = 0x10 - headerSize%0x10
        headerSize += remainder
        
        fileSizes = [os.path.getsize(file) for file in self.files]
        fileOffsets = [sum(fileSizes[:n]) for n in range(filesNb)]
        
        fileNamesLengths = [len(os.path.basename(file))+1 for file in self.files] # +1 for the \x00
        stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(filesNb)]
        
        header =  b''
        header += b'PFS0'
        header += pk('<I', filesNb)
        header += pk('<I', len(stringTable)+remainder)
        header += b'\x00\x00\x00\x00'
        for n in range(filesNb):
            header += pk('<Q', fileOffsets[n])
            header += pk('<Q', fileSizes[n])
            header += pk('<I', stringTableOffsets[n])
            header += b'\x00\x00\x00\x00'
        header += stringTable.encode()
        header += remainder * b'\x00'
        
        return header

  
# End of CDNSP script
# --------------------------
# GUI code begins

def game_image(tid, ver, tkey="", nspRepack=False, n='',verify=False):
    import glob
    if not os.path.isdir("Images"):
        os.mkdir("Images")
    if not os.path.isdir("Images/{}".format(tid)):
        os.mkdir("Images/{}".format(tid))
    
    gameDir = "Images/{}".format(tid)
    
    if os.path.isdir(os.path.dirname(os.path.abspath(__file__))+'/Images/{}/section0/'.format(tid)):
        for fname in os.listdir(os.path.dirname(os.path.abspath(__file__))+'/Images/{}/section0/'.format(tid)):
            if fname.endswith('.jpg'):
                return (gameDir, "Exist")
        
    tid = tid.lower();
    tkey = tkey.lower();
    if len(tid) != 16:
        tid = (16-len(tid)) * '0' + tid
        
    url = 'https://atum%s.hac.%s.d4c.nintendo.net/t/a/%s/%s?device_id=%s' % (n, env, tid, ver, did)
    try:
        r = make_request('HEAD', url)
    except Exception as e:
        pass
    CNMTid = r.headers.get('X-Nintendo-Content-ID')

    if CNMTid is None:
        print("not a valid title")
        
    fPath = os.path.join(gameDir, CNMTid + '.cnmt.nca')
    cnmtNCA = download_file(url, fPath)
    cnmtDir = decrypt_NCA(cnmtNCA)
##    print(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]), 
##                os.path.join(cnmtDir, 'Header.bin'))
##    sys.exit()
    CNMT = cnmt(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]), 
                os.path.join(cnmtDir, 'Header.bin'))
    
    NCAs = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
    }
    for type in [3]: # Download smaller files first
        list = CNMT.parse(CNMT.contentTypes[type])
        for ncaID in list:
            print('\tDownloading %s entry (%s.nca)...' % (CNMT.contentTypes[type], ncaID))
            url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/c/%s?device_id=%s' % (n, env, ncaID, did)
            fPath = os.path.join(gameDir, "control" + '.nca')
            fSize = list[ncaID][1]
            
            NCAs[type].append(download_file(url, fPath, fSize))
            
            if verify:
                print('\t\tVerifying file...')
                if sha256_file(fPath) == list[ncaID][2]:
                    print('\t\t\tHashes match, file is correct!')
                else:
                    print('\t\t\t%s is corrupted, hashes don\'t match!' % os.path.basename(fPath))
    return (gameDir, "N")


def read_game_info():
    try:
        file = open("Config/Game_info.json", "r", encoding="utf8")
        global game_info_json
        game_info_json = json.load(file)
        file.close()
    except:
        print(_("Missing Game_info.json file in the Config folder, attempting to download one for you"))
        urllib.request.urlretrieve("https://raw.githubusercontent.com/Bob123a1/CDNSP-GUI-Files/master/Config/Game_info.json", "Config/Game_info.json")

        if os.path.isfile("Config/Game_info.json"):
            file = open("Config/Game_info.json", "r", encoding="utf8")
            game_info_json = json.load(file)
            file.close()
        else:
            file = open("Config/Game_info.json", "w", encoding="utf8")
            file.write("{}")
            file.close()
            read_game_info()

read_game_info()

def updateJsonFile(key, value, root=""):
    if os.path.isfile("CDNSP-GUI-config.json"):
        with open("CDNSP-GUI-config.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["Options"]["{}".format(key)] = value

        with open("CDNSP-GUI-config.json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
    else:
        print(_("Error!, Missing CDNSP-GUI-config.json file"))

    if key == "Language":
        root.destroy()
        set_lang(value)
        main()

def GUI_config(fPath):
    if sys_locale != "zh_CN":
        main_win = "650x530+100+100"
        queue_win = "620x300+770+100"
        scan_win = "450x100+100+100"
        base64_win = "530x100+100+100"
    else:
        main_win = "750x550+100+100"
        queue_win = "720x300+770+100"
        scan_win = "391x85+100+100"
        base64_win = "467x104+100+100"
            
    config = {"Options": {
                "Download_location":  "",
                "Game_location": "",
                "NSP_repack":         "True",
                "Mute":               "False",
                "Titlekey_check":     "True",
                "noaria":             "True",
                "Disable_game_image": "False",
                "Shorten": "False",
                "Tinfoil": "False",
                "SysVerZero": "False",
                "Main_win": main_win,
                "Queue_win": queue_win,
                "Update_win": "600x400+120+200",
                "Scan_win": scan_win,
                "Base64_win": base64_win,
                "Language": "en"}}

    try:
        f = open(fPath, 'r')
    except FileNotFoundError:
        f = open(fPath, 'w')
        json.dump(config, f, indent=4)
        f.close()
        f = open(fPath, 'r')

    j = json.load(f)

    def str2bool(v):
        return v.lower() == "true"
    
    download_location  = j['Options']['Download_location']
    game_location = j['Options']['Game_location']
    repack  = str2bool(j['Options']['NSP_repack'])
    mute  = str2bool(j['Options']['Mute'])
    titlekey_check  = str2bool(j['Options']['Titlekey_check'])
    noaria  = str2bool(j['Options']['noaria'])
    disable_game_image  = str2bool(j['Options']['Disable_game_image'])
    shorten = str2bool(j['Options']['Shorten'])
    tinfoil = str2bool(j['Options']['Tinfoil'])
    sysver0 = str2bool(j['Options']['SysVerZero'])
    main_win  = j['Options']['Main_win']
    queue_win  = j['Options']['Queue_win']
    update_win  = j['Options']['Update_win']
    scan_win = j['Options']['Scan_win']
    base64_win = j['Options']['Base64_win']
    language = j['Options']['Language']

    if not os.path.exists(download_location): # If the custom download directory doesn't exist then use default path
        download_location = ""
        updateJsonFile("Download_location", download_location)
    return download_location, game_location, repack, mute, titlekey_check, noaria, \
           disable_game_image, shorten, tinfoil, sysver0, main_win, queue_win, update_win, \
           scan_win, base64_win, language

class Application():

    def __init__(self, root, titleID, titleKey, title, dbURL):

        global main_win
        global queue_win
        global update_win_size
        global scan_win
        global base64_win
        global langauge
        
        configGUIPath = os.path.join(os.path.dirname(__file__), 'CDNSP-GUI-config.json') # Load config file
        self.path, self.game_location, self.repack, self.mute, self.titlekey_check, noaria_temp, \
                   self.game_image_disable, shorten_temp, tinfoil_temp, sysver0_temp, main_win, \
                   queue_win, update_win, scan_win, \
                   base64_win, language = GUI_config(configGUIPath) # Get config values

        
        update_win_size = update_win
        
        self.root = root
        self.root.geometry(main_win)
        self.titleID = titleID
        self.titleKey = titleKey
        self.title = title
        self.first_queue = True
        self.queue_list = []
        self.persistent_queue = []
        self.db_URL = dbURL
        self.current_status = []
        self.installed = [] # List of TID already installed
        self.installed_ver = []
        if os.path.exists(r"Config/installed.txt"):
            f = open(r"Config/installed.txt", "r")
            for line in f.readlines():
                tid = line.split(",")[0].strip()
                ver = line.split(",")[1].strip()
                if ver != "0":
                    tid = "{}800".format(tid[:13])
                self.installed.append(tid)
                self.installed_ver.append(ver)
        
        self.listWidth = 67
        global sys_name
        
##        global save_game_folder
##        save_game_folder = False -- To be worked on in the future
        
        global titlekey_check
        titlekey_check = self.titlekey_check

        if platform.system() == 'Linux':
            sys_name = "Linux"

        if platform.system() == 'Darwin':
            sys_name = "Mac"
            self.listWidth = 39
        self.sys_name = sys_name

        global noaria
        noaria = True

        global truncateName
        truncateName = shorten_temp
        
        global tinfoil
        tinfoil = tinfoil_temp

        global sysver0
        sysver0 = sysver0_temp

        # Top Menu bar
        self.menubar = Menu(self.root)

        # Download Menu Tab
        self.downloadMenu = Menu(self.menubar, tearoff=0)
        self.downloadMenu.add_command(label=_("Select Download Location"), command=self.change_dl_path)
        self.downloadMenu.add_command(label=_("Preload Game Images"), command=self.preload_images)
        self.downloadMenu.add_command(label=_("Update Version List"), command=self.update_ver_list)
##        self.downloadMenu.add_command(label=_("Preload Game Descriptions"), command=self.preload_desc)
        # Not if I want to preload game description, since some games can't be found on the CDN
        self.downloadMenu.add_separator() # Add separator to the menu dropdown
        self.downloadMenu.add_command(label=_("Load Saved Queue"), command=self.import_persistent_queue)
        self.downloadMenu.add_command(label=_("Save Queue"), command=self.export_persistent_queue)

        # Options Menu Tab
        self.optionMenu = Menu(self.menubar, tearoff=0)
        self.optionMenu.add_command(label=_("Aria2c will be missed"), command=self.disable_aria2c)
        self.optionMenu.add_command(label=_("DISABLE GAME IMAGE"), command=self.disable_game_image)
        
        self.optionMenu.add_separator() # Add separator to the menu dropdown
        
        self.optionMenu.add_command(label=_("Mute All Pop-ups"), command=self.mute_all)
        self.optionMenu.add_command(label=_("Disable NSP Repack"), command=self.nsp_repack_option)
        self.optionMenu.add_command(label=_("Disable Titlekey check"), command=self.titlekey_check_option)
        
        self.optionMenu.add_separator() # Add separator to the menu dropdown
        
        self.optionMenu.add_command(label=_("Enable Shorten Name"), command=self.shorten)
        self.optionMenu.add_command(label=_("Enable Tinfoil Download"), command=self.tinfoil_change)
        self.optionMenu.add_command(label=_("Enable SysVer 0 Patch"), command=self.sysver_zero)
        
        self.optionMenu.add_separator() # Add separator to the menu dropdown
        
        self.optionMenu.add_command(label=_("Save Windows Location and Size"), command=self.window_save)

        
        # Tool Menu Tab
        self.toolMenu = Menu(self.menubar, tearoff=0)
        self.toolMenu.add_command(label=_("Scan for existing games"), command=self.my_game_GUI)
        self.toolMenu.add_command(label=_("Base64 Decoder"), command=self.base_64_GUI)

        # Language Menu Tab
        self.langMenu = Menu(self.menubar, tearoff=0)
        self.langMenu.add_command(label='Afrikaans (Afrikaans)', command=lambda: updateJsonFile('Language', 'af', root=self.root))
        self.langMenu.add_command(label='Arabic (العربية)', command=lambda: updateJsonFile('Language', 'ar', root=self.root))
        self.langMenu.add_command(label='Chinese Simplified (简体中文)', command=lambda: updateJsonFile('Language', 'zh-cn', root=self.root))
        self.langMenu.add_command(label='Chinese Traditional (繁體中文)', command=lambda: updateJsonFile('Language', 'zh-tw', root=self.root))
        self.langMenu.add_command(label='Dutch (Nederlands)', command=lambda: updateJsonFile('Language', 'nl', root=self.root))
        self.langMenu.add_command(label='English', command=lambda: updateJsonFile('Language', 'en', root=self.root))
        self.langMenu.add_command(label='French (Français)', command=lambda: updateJsonFile('Language', 'fr', root=self.root))
        self.langMenu.add_command(label='German (Deutsch)', command=lambda: updateJsonFile('Language', 'de', root=self.root))
        self.langMenu.add_command(label='Greek (Ελληνικά)', command=lambda: updateJsonFile('Language', 'el', root=self.root))
        self.langMenu.add_command(label='Hebrew (עברית)', command=lambda: updateJsonFile('Language', 'he', root=self.root))
        self.langMenu.add_command(label='Hungarian (Magyar)', command=lambda: updateJsonFile('Language', 'hu', root=self.root))
        self.langMenu.add_command(label='Indonesian (Bahasa Indonesia)', command=lambda: updateJsonFile('Language', 'id', root=self.root))
        self.langMenu.add_command(label='Italian (Italiano)', command=lambda: updateJsonFile('Language', 'it', root=self.root))
        self.langMenu.add_command(label='Japanese (日本語)', command=lambda: updateJsonFile('Language', 'ja', root=self.root))
        self.langMenu.add_command(label='Korean (한국어)', command=lambda: updateJsonFile('Language', 'ko', root=self.root))
        self.langMenu.add_command(label='Malaysian (Bahasa Melayu)', command=lambda: updateJsonFile('Language', 'ms', root=self.root))
        self.langMenu.add_command(label='Persian (پارسی)', command=lambda: updateJsonFile('Language', 'fa', root=self.root))
        self.langMenu.add_command(label='Polish (Polski)', command=lambda: updateJsonFile('Language', 'pl', root=self.root))
        self.langMenu.add_command(label='Portuguese (Português)', command=lambda: updateJsonFile('Language', 'pt', root=self.root))
        self.langMenu.add_command(label='Russian (Русский)', command=lambda: updateJsonFile('Language', 'ru', root=self.root))
        self.langMenu.add_command(label='Spanish (Español)', command=lambda: updateJsonFile('Language', 'es', root=self.root))
        self.langMenu.add_command(label='Thai (ไทย)', command=lambda: updateJsonFile('Language', 'th', root=self.root))
        self.langMenu.add_command(label='Turkish (Merhaba)', command=lambda: updateJsonFile('Language', 'tr', root=self.root))
        self.langMenu.add_command(label='Vietnamese (Tiếng Việt)', command=lambda: updateJsonFile('Language', 'vi', root=self.root))

        # About Menu
        self.aboutMenu = Menu(self.menubar, tearoff=0)
        self.aboutMenu.add_command(label=_('Credits'), command=lambda: self.credit_gui())
        
        # Menubar config
        self.menubar.add_cascade(label=_("Download"), menu=self.downloadMenu)
        self.menubar.add_cascade(label=_("Options"), menu=self.optionMenu)
        self.menubar.add_cascade(label=_("Tools"), menu=self.toolMenu)
        self.menubar.add_cascade(label=_("Language"), menu=self.langMenu)
        self.menubar.add_cascade(label=_("About"), menu=self.aboutMenu)
        self.root.config(menu=self.menubar)

        # Change Menu Label Based on loaded values
        if self.repack == True:
            self.optionMenu.entryconfig(4, label= _("Disable NSP Repack"))
        else:
            self.optionMenu.entryconfig(4, label= _("Enable NSP Repack"))
        if self.mute == True:
            self.optionMenu.entryconfig(3, label= _("Unmute All Pop-ups"))
        else:
            self.optionMenu.entryconfig(3, label= _("Mute All Pop-ups"))
        if self.titlekey_check == True:
            self.optionMenu.entryconfig(5, label= _("Disable Titlekey check"))
        else:
            self.optionMenu.entryconfig(5, label= _("Enable Titlekey check"))
        if self.game_image_disable == True:
            self.optionMenu.entryconfig(1, label= _("ENABLE GAME IMAGE"))
        else:
            self.optionMenu.entryconfig(1, label= _("DISABLE GAME IMAGE"))
        if truncateName == True:
            self.optionMenu.entryconfig(7, label= _("Disable Shorten Name"))
        else:
            self.optionMenu.entryconfig(7, label= _("Enable Shorten Name"))
        if tinfoil == True:
            self.optionMenu.entryconfig(8, label= _("Disable Tinfoil Download"))
        else:
            self.optionMenu.entryconfig(8, label= _("Enable Tinfoil Download"))
        if sysver0 == True:
            self.optionMenu.entryconfig(9, label= _("Disable SysVer 0 Patch"))
        else:
            self.optionMenu.entryconfig(9, label= _("Enable SysVer 0 Patch"))

        # Status Label
        self.status_label = Label(self.root, text=_("Status:"))
        self.status_label.grid(row=0, column=0, columnspan=2, sticky=NS)
        
        # Game selection section
        self.search_var = StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_list(True, label=""))

        game_selection_frame = Frame(self.root)
        game_selection_frame.grid(row=1, column=0, padx=20, pady=20, sticky=N)

        # Filter entrybox
        if sys_name != "Mac":
            entryWidth = self.listWidth + 3
        else:
            entryWidth = self.listWidth
        self.entry = Entry(game_selection_frame, textvariable=self.search_var, width=entryWidth)
        self.entry.grid(row=0, column=0, columnspan=2, sticky=N)

        # Setup Listbox and scrollbar
        self.scrollbar = Scrollbar(game_selection_frame)
##        self.scrollbar.grid(row=1, column=1, sticky=N+S+W)
        self.title_list = Listbox(game_selection_frame, exportselection = False,\
                                  yscrollcommand = self.scrollbar.set, width=self.listWidth, selectmode=EXTENDED)
        self.title_list.bind('<<ListboxSelect>>', self.game_info)
##        self.title_list.grid(row=1, column=0, sticky=W)
        self.scrollbar.config(command = self.title_list.yview)

        # Setup Treeview and Two Scrollbars
        container = ttk.Frame(game_selection_frame)
        container.grid(row=1, column=0, columnspan=2)
        self.tree = ttk.Treeview(columns=("num", "tid", "G", "S"), show="headings", selectmode=EXTENDED)
        self.tree.bind('<<TreeviewSelect>>', self.game_info)
        self.tree.heading("num", text="#", command=lambda c="num": self.sortby(self.tree, c, 0))
        self.tree.column("num", width=40)
        self.tree.heading("tid", text=_("TitleID"), command=lambda c="tid": self.sortby(self.tree, c, 0))
        self.tree.column("tid", width=140)
        self.tree.heading("G", text=_("Game"), command=lambda c="G": self.sortby(self.tree, c, 0))
        self.tree.column("G", width=590)
        self.tree.heading("S", text=_("State"), command=lambda c="S": self.sortby(self.tree, c, 0))        
        columnWidth_S = 130
        if chosen_lang == "zh-cn":
            columnWidth_S = 45
        elif chosen_lang == "en":
            columnWidth_S = 55
        self.tree.column("S", width=columnWidth_S)
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container, columnspan=2)
        vsb.grid(column=2, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Game image section
        self.image_text_label = Label(game_selection_frame, text=_("Game Image:"))
        self.image_text_label.grid(row=2, column=0, pady=(20, 0))

        self.update_list(label="")

        self.image = Image.open("blank.jpg")
        self.photo = ImageTk.PhotoImage(self.image)
        self.imageLabel = Label(game_selection_frame, image=self.photo, borderwidth=0, highlightthickness=0, cursor="hand2")
        self.imageLabel.bind("<Button-1>", self.eShop_link)
        self.imageLabel.image = self.photo # keep a reference!
        self.imageLabel.grid(row=3, column=0, sticky=N, pady=0)

        Label(game_selection_frame, text=_("Click the game image above \nto open the game in the eShop!")).grid(row=4, column=0)

        # Game info section
        Label(game_selection_frame, text=_("Game Info:")).grid(row=2, column=1, pady=(20, 0))
        game_text = Text(game_selection_frame, width=50, height=17, wrap=WORD)
        
##        scroll_bar = Scrollbar(game_selection_frame, command=game_text.yview)
##        scroll_bar.grid(row=3, column=2, sticky='ns')
##        game_text['yscrollcommand'] = scroll_bar.set
        
        self.game_text = game_text
        game_text.grid(row=3, column=1, sticky=N)
        #-------------------------------------------

        # Game title info section

        game_info_frame = Frame(self.root)
        game_info_frame.grid(row=1, column=1, sticky=N)

        # Demo filter
        filter_frame = Frame(game_info_frame)
        filter_frame.grid(row=0, column=0, columnspan=2, pady=(20,0), sticky=NS)
        self.demo = IntVar()
        Checkbutton(filter_frame, text=_("No Demo"), \
                    variable=self.demo, command=self.filter_game)\
                    .grid(row=0, column=0, sticky=NS)
        self.jap = IntVar()
        Checkbutton(filter_frame, text=_("No Japanese Game"), \
                    variable=self.jap, command=self.filter_game)\
                    .grid(row=1, column=0, pady=(5,0), sticky=NS)
        
        # Title ID info
        self.titleID_label = Label(game_info_frame, text=_("Title ID:"))
        self.titleID_label.grid(row=1, column=0, pady=(20,0), columnspan=2)

        self.game_titleID = StringVar()
        self.gameID_entry = Entry(game_info_frame, textvariable=self.game_titleID)
        self.gameID_entry.grid(row=2, column=0, columnspan=2)

        # Title Key info
        self.titleID_label = Label(game_info_frame, text=_("Title Key:"))
        self.titleID_label.grid(row=3, column=0, pady=(20,0), columnspan=2)

        self.game_titleKey = StringVar()
        self.gameKey_entry = Entry(game_info_frame, textvariable=self.game_titleKey)
        self.gameKey_entry.grid(row=4, column=0, columnspan=2)

        # Select update versions
        self.version_label = Label(game_info_frame, text=_("Select update version:"))
        self.version_label.grid(row=5, column=0, pady=(20,0), columnspan=2)

        self.version_option = StringVar()
        self.version_select = ttk.Combobox(game_info_frame, textvariable=self.version_option, state="readonly", postcommand=self.get_update_ver)
        self.version_select["values"] = ([_('Latest')])
        self.version_select.set(_("Latest"))
        self.version_select.grid(row=6, column=0, columnspan=2)
        
        # Download options
        self.download_label = Label(game_info_frame, text=_("Download options:"))
        self.download_label.grid(row=7, column=0, pady=(20,0), columnspan=2)

        MODES = [
            (_("Base game + Update + DLC"), "B+U+D"),
            (_("Base game + Update"), "B+U"),
            (_("Update + DLC"), "U+D"),
            (_("Base game only"), "B"),
            (_("Update only"), "U"),
            (_("All DLC"), "D")
        ]

        self.updateOptions = StringVar()
        self.updateOptions.set("B+U+D")
        
        self.radio_btn_collection = []
        row_count = 8
        for index in range(len(MODES)):
            a = Radiobutton(game_info_frame, text=MODES[index][0],
                        variable=self.updateOptions, value=MODES[index][1])
            a.grid(row=row_count, column=0, sticky=W, columnspan=2)
            row_count += 1
            self.radio_btn_collection.append(a)

        # Queue and Download button
        queue_btn = Button(game_info_frame, text=_("Add to queue"), command=self.add_selected_items_to_queue)
        queue_btn.grid(row=50, column=0, pady=(20,0))
        if _("Download_bottom") != "Download_bottom":
            download_bottom_txt = _("Download_bottom")
        else:
            download_bottom_txt = _("Download")
        dl_btn = Button(game_info_frame, text=_(download_bottom_txt), command=self.download)
        dl_btn.grid(row=50, column=1, pady=(20,0), padx=(5,0))

        update_btn = Button(game_info_frame, text=_("Update Titlekeys"), command=self.update_titlekeys)
        update_btn.grid(row=51, column=0, pady=(20, 0), columnspan=2)

        #-----------------------------------------
        self.queue_menu_setup()
        #-----------------------------------------

        self.load_persistent_queue() # only load the queue once the UI is initialized

    def queue_menu_setup(self):
        # Queue Menu
        global queue_win
        self.queue_win = Toplevel(self.root)
        self.queue_win.title(_("Queue Menu"))
        self.queue_win.geometry(queue_win)
        self.queue_win.withdraw() # Hide queue window, will show later

        # Top Menu bar
        menubar = Menu(self.queue_win)

        # Download Menu Tab
        downloadMenu = Menu(menubar, tearoff=0)
        downloadMenu.add_command(label=_("Load Saved Queue"), command=self.import_persistent_queue)
        downloadMenu.add_command(label=_("Save Queue"), command=self.export_persistent_queue)
        
        # Menubar config
        menubar.add_cascade(label=_("Download"), menu=downloadMenu)
        self.queue_win.config(menu=menubar)

        # Queue GUI
        self.queue_scrollbar = Scrollbar(self.queue_win)
        self.queue_scrollbar.grid(row=0, column=3, sticky=N+S+W)
        
        if self.sys_name == "Mac":
            self.queue_width = self.listWidth+28
        else:
            self.queue_width = 100 # Windows 
        self.queue_title_list = Listbox(self.queue_win, yscrollcommand = self.queue_scrollbar.set, width=self.queue_width, selectmode=EXTENDED)
        self.queue_title_list.grid(row=0, column=0, sticky=W, columnspan=3)
        self.queue_scrollbar.config(command = self.queue_title_list.yview)

        Button(self.queue_win, text=_("Remove selected game"), command=self.remove_selected_items).grid(row=1, column=0, pady=(30,0))
        Button(self.queue_win, text=_("Remove all"), command=self.remove_all_and_dump).grid(row=1, column=1, pady=(30,0))
        Button(self.queue_win, text=_("Download all"), command=self.download_all).grid(row=1, column=2, pady=(30,0))
        self.stateLabel = Label(self.queue_win, text=_("Click download all to download all games in queue!"))
        self.stateLabel.grid(row=2, column=0, columnspan=3, pady=(20, 0))

    # Sorting function for the treeview widget
    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        # if the data to be sorted is numeric change to float
        #data =  change_numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            self.tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        self.tree.heading(col, command=lambda col=col: self.sortby(tree, col, \
            int(not descending)))

    def remove_all(self, dump_queue = False):
        self.queue_list = []
        self.persistent_queue = []
        self.queue_title_list.delete(0, "end")
        if dump_queue: self.dump_persistent_queue()

    def remove_all_and_dump(self):
        self.remove_all(True)

    def threaded_eShop_link(self, evt):
        tid = self.game_titleID.get()
        isDLC = False
        if not tid.endswith("00"):
            isDLC = True
            tid = "{}".format(tid[0:12])
            indices = [i for i, s in enumerate(self.titleID) if tid in s]
            if len(indices) >= 2:
                for t in indices:
                    if self.titleID[t].endswith("000"):
                        tid = self.titleID[t]
                        break
                if tid.endswith("000"):
                    isDLC = False
        if not isDLC:
            region = ["US", "EU", "GB", "FR", \
                      "JP", "RU", "DE", "BE", "NL",\
                      "ES", "IT", "AT", "PT", "CH",\
                      "ZA", "CA"]
            # Thanks to user szczuru#7105 for find them for me :)
    ##        https://ec.nintendo.com/apps/01000320000cc000/FR
            url = ""
            for c in region:
                r = requests.get("https://ec.nintendo.com/apps/{}/{}".format(tid, c))
                if r.status_code == 200:
                    url = "https://ec.nintendo.com/apps/{}/{}".format(tid, c)
                    break
            if url != "":
                webbrowser.open(url, new=0, autoraise=True)
        self.root.config(cursor="")
        self.imageLabel.config(cursor="hand2")
                
    def eShop_link(self, evt):
        if self.game_titleID.get() != "":
            thread = threading.Thread(target = lambda: self.threaded_eShop_link(evt))
            self.root.config(cursor="watch")
            self.imageLabel.config(cursor="watch")
            thread.start()

    def update_list(self, search=False, rebuild=False, label=_("Status:")):
        label = _("Status:")
        #_("Status: Getting game status... Please wait")
        self.root.config(cursor="watch")
        self.status_label.config(text=label)

        if not os.path.isdir("Config"):
            os.mkdir("Config")
        if not os.path.isfile(r"Config/Current_status.txt"):
            rebuild = True
        
        if rebuild: # Rebuild current_status.txt file
            print(_("\nBuilding the current state file... Please wait, this may take some time \
depending on how many games you have."))
            self.status_label.config(text=_("\nBuilding the current state file... Please wait, this may take some time \
depending on how many games you have."))
            updates_tid = []
            installed = []
            new_tid = []
            known_ver = {}

            if not os.path.isfile("Config/Version_info.json"):
                print(_("\nCan't find Version_info.json file!\n"))
                print(_("Attempting to download the Version_info.json file for you"))
                urllib.request.urlretrieve("https://raw.githubusercontent.com/Bob123a1/CDNSP-GUI-Files/master/Config/Version_info.json", "Config/Version_info.json")
                
            if os.path.isfile("Config/Version_info.json"):
                ver_file = open("Config/Version_info.json", "r", encoding="utf8")
                known_ver = json.load(ver_file)
                ver_file.close()
            file_path = r"Config/installed.txt"
            if os.path.exists(file_path):
                file = open(file_path, "r")
                for line in file.readlines():
                    if line[-1] == "\n":
                        line = line[:-1]
                    installed.append(line)
                file.close()
                for info in installed:
                    tid = info.split(",")[0].strip()
                    ver = info.split(",")[1].strip()
                    if tid in known_ver:
                        try:
                            if int(known_ver[tid]) > int(ver):
                                if tid.endswith("00"):
                                    tid = "{}000".format(tid[0:13])
                                updates_tid.append(tid)
                        except Exception as e:
                            print("Tid: {} has caused an error, it has the version of {}.\nError: {}".format(tid, ver, e))
            else:
                file = open(file_path, "w")
                file.close()

            new_path = r"Config/new.txt"
            if os.path.isfile(new_path):
                file = open(new_path, "r")
                for line in file.readlines():
                    if line[-1] == "\n":
                        line = line[:-1]
                    new_tid.append(line[:16])
                file.close()
            installed = [install.split(",")[0] for install in installed]

            status_file = open(r"Config/Current_status.txt", "w", encoding="utf-8")

            for tid in self.titleID:
                number = int(self.titleID.index(tid))+1
                game_name = self.title[number-1]
                if game_name[-1] == "\n":
                    game_name = game_name[:-1]
                state = ""

                if tid in new_tid:
                    state = "New"
                
                if tid in installed:
                    state = "Own"
                
                if tid in updates_tid:
                    state = "Update"
                tree_row = (str(number), tid, game_name, state)
                status_file.write(str(tree_row)+"\n")
            status_file.close()
            threading.Timer(1, self.done_status).start()    
            status_file.close()
            self.update_list()
            
        elif search:
            search_term = self.search_var.get()
            self.tree.delete(*self.tree.get_children())
            for game_status in self.current_status:
                number = game_status[0].strip()
                tid = game_status[1].strip()
                game_name = game_status[2].strip()
                state = game_status[3].strip()
                
                tree_row = (number, tid, game_name, state)
                if search_term.lower().strip() in game_name.lower() or search_term.lower().strip() in tid.lower():
                    self.tree.insert('', 'end', values=tree_row)
                    
        else:
            if os.path.isfile(r"Config/Current_status.txt"):
                self.current_status = []
                file = open(r"Config/Current_status.txt", "r", encoding="utf-8")
                for line in file.readlines():
                    if line[-1] == "\n":
                        line = line[:-1]
                    if "New" in line:
                        line = line.replace("'New'", "'" + _("New") + "'")
                    if "Own" in line:
                        line = line.replace("'Own'", "'" + _("Own") + "'")
                    if "Update" in line:
                        line = line.replace("'Update'", "'" + _("Update") + "'")
                    status_list = eval(line)
                    self.current_status.append(status_list)
                self.update_list(search=True)
                file.close()
                self.make_list()
            else:
                print(_("Error, Current_status.txt doesn't exist"))
  
        self.tree.yview_moveto(0)
        # Reset the sorting back to default (descending)
        self.tree.heading("num", text="#", command=lambda c="num": self.sortby(self.tree, c, 1))
        self.tree.heading("tid", text=_("TitleID"), command=lambda c="tid": self.sortby(self.tree, c, 0))
        self.tree.heading("G", text=_("Game"), command=lambda c="G": self.sortby(self.tree, c, 1))
        self.tree.heading("S", text=_("State"), command=lambda c="S": self.sortby(self.tree, c, 1))

        # Reset cursor status
        self.root.config(cursor="")
        try:
            self.imageLabel.config(cursor="hand2")
        except:
            pass

##    def update_list(self, search=False):
##        # Set cursor status to waiting 
##        thread = threading.Thread(target = lambda: self.threaded_update_list(search))
##        thread.start()
    def done_status(self):
        self.status_label.config(text=_("Status: Done!"))
        print(_("Status: Done!"))
        
    def threaded_game_info(self, evt):
        selection=self.tree.selection()[0]
        selected = self.tree.item(selection,"value") # Returns the selected value as a dictionary
        if selection:
            w = evt.widget
            self.is_DLC = False
##            try:
            value = selected[1]
            if "[DLC]" in value:
                for radio in self.radio_btn_collection:
                    radio.configure(state = DISABLED)
                self.is_DLC=True
            else:
                for radio in self.radio_btn_collection:
                    radio.configure(state = "normal")
            value = int(selected[0])
            value -= 1
            self.game_titleID.set(self.titleID[value])
            self.game_titleKey.set(self.titleKey[value])
##            except:
##                pass

            tid = self.titleID[value]
            thread = threading.Thread(target = lambda: self.game_desc(tid))
            thread.start()
##            isDLC = False
##            if not tid.endswith('00'):
##                isDLC = True
            isDLC = False
            if not tid.endswith("00"):
                isDLC = True
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                if len(indices) >= 2:
                    for t in indices:
                        if self.titleID[t].endswith("000"):
                            tid = self.titleID[t]
                            break
                    if tid.endswith("000"):
                        isDLC = False
##            try:
            if not self.game_image_disable and not isDLC:
                start = time.time()
                if not os.path.isfile("Images/{}.jpg".format(tid)):
                    global noaria
                    noaria = True
                    base_ver = get_versions(tid)[-1]
                    result = game_image(tid, base_ver, self.titleKey[self.titleID.index(tid)])
                    noaria = False
                    if result[1] != "Exist":
                        if self.sys_name == "Win":
                            subprocess.check_output("{0} -k keys.txt {1}\\control.nca --section0dir={1}\\section0".format(hactoolPath, result[0].replace("/", "\\")), shell=True)
                        else:
                            subprocess.check_output("{0} -k keys.txt '{1}/control.nca' --section0dir='{1}/section0'".format(hactoolPath, result[0]), shell=True)
                        icon_list = ["icon_AmericanEnglish.dat", "icon_BritishEnglish.dat", "icon_CanadianFrench.dat", "icon_German.dat", "icon_Italian.dat", "icon_Japanese.dat", "icon_LatinAmericanSpanish.dat", "icon_Spanish.dat"]
                        file_name = ""
                        dir_content = os.listdir(os.path.dirname(os.path.abspath(__file__))+'/Images/{}/section0/'.format(tid))
                        for i in icon_list:
                            if i in dir_content:
                                file_name = i.split(".")[0]
                                break
                        os.rename('{}/section0/{}.dat'.format(result[0], file_name), '{}/section0/{}.jpg'.format(result[0], file_name))
                        shutil.copyfile('{}/section0/{}.jpg'.format(result[0], file_name), 'Images/{}.jpg'.format(tid))
                        shutil.rmtree(os.path.dirname(os.path.abspath(__file__))+'/Images/{}'.format(tid))
                img2 = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.abspath(__file__))+'/Images/{}.jpg'.format(tid)))
                self.imageLabel.configure(image=img2, text="")
                self.imageLabel.image = img2
                end = time.time()
                # print("\nIt took {} seconds to get the image\n".format(end - start))
            else:
                img2 = ImageTk.PhotoImage(Image.open('blank.jpg'))
                self.imageLabel.configure(image=img2, text="")
                self.imageLabel.image = img2
##            
##            except:
##                pass
    def game_info(self, evt):
        self.imageLabel.config(image="", text=_("\n\n\nDownloading game image..."))
        thread = threading.Thread(target = lambda: self.threaded_game_info(evt))
        thread.start()

    def game_desc(self, tid):
        #self.infoLabel.config(image="", text=_("\n\n\nDownloading game info..."))
        global game_info_json
        if not tid.endswith("00"):
            tid = "{}".format(tid[0:12])
            indices = [i for i, s in enumerate(self.titleID) if tid in s]
            if len(indices) >= 2:
                for t in indices:
                    if self.titleID[t].endswith("000"):
                        tid = self.titleID[t]
                        break
        if tid in game_info_json:
            description = ""
            if game_info_json[tid]["intro"].replace("\n", "") == "":
                description += "No intro\n"
            else:
                description += "{}\n".format(game_info_json[tid]["intro"]\
                                             .replace("\n\n", " ").replace("\n", "").strip())

            info_name = {"\nGame Description": "description",
                         "Release Date": "release_date_string",
                         "Publisher": "publisher",
                         "Category": "category",
                         "Rating": "rating",
                         "Game Size": "Game_size",
                         "Number of Players": "number_of_players",
                         "US eShop Game Price": "US_price"
                         }

            for game_name, game_key in info_name.items():
                if game_key == "description":
                    description += "{}: {}\n\n".format(_(game_name), game_info_json[tid]["{}".format(game_key)]\
                                                       .replace("\n\n", " ").replace("\n", "").strip())
                elif game_key == "Game_size":
                    try:
                        game_size_temp = bytes2human(float(game_info_json[tid]["{}".format(game_key)].replace("\n", "").strip()))
                        game_size_temp_size = float(game_size_temp[0:-3])
                        description += "{}: {:.2f} {}\n".format(_(game_name), game_size_temp_size, game_size_temp[-2:])
                    except:
                        description += "{}: {}\n".format(_(game_name), _("Unable to get game size"))
                elif game_key == "US_price":
                    description += "{}: ${}\n".format(_(game_name), game_info_json[tid]["{}".format(game_key)].replace("\n", "").strip())
                else:
                    description += "{}: {}\n".format(_(game_name), game_info_json[tid]["{}".format(game_key)].replace("\n", "").strip())
                                                                         
            self.game_text.delete("1.0", END)
            self.game_text.insert(INSERT, description)

            self.game_text.tag_add("All", "1.0", "end")
            self.game_text.tag_config("All", font=("Open Sans", 10))
            
            self.game_text.tag_add("Intro", "1.0", "1.end")
            self.game_text.tag_config("Intro", justify="center", font=("Open Sans", 10, "bold"))

            counter = 3
            for game_name, game_key in info_name.items():
                self.game_text.tag_add("{}".format(_(game_name)), "{}.0".format(counter), "{}.{}".format(counter, len(_(game_name))))
                self.game_text.tag_config("{}".format(_(game_name)), font=("Open Sans", 10, "bold"), spacing2="2", spacing3="3")
                if counter == 3:
                    counter += 2
                else:
                    counter += 1
        else:
            self.game_text.delete("1.0", END)
            self.game_text.insert(INSERT, _("\n\n\nDownloading game info..."))
            thread = threading.Thread(target = lambda: self.download_desc(tid))
            thread.start()
            
    def download_desc(self, tid, silent=False):
        # Coded by Panda
        global game_info_json
        done = False
        if tid in game_info_json:
            done = True
        if done == False:
##            try:
            titleinfo = {}
            titleinfo['titleid'] = tid
            titleinfo['date_added'] = time.strftime('%Y%m%d')
            titleinfo['last_updated'] = time.strftime('%Y%m%d')

            #initialize empty values
            titleinfo["release_date_string"] = ""
            titleinfo["release_date_iso"] = ""
            titleinfo["title"] = ""
            titleinfo["nsuid"] = ""
            titleinfo["slug"] = ""
            titleinfo["game_code"] = ""
            titleinfo["category"] = ""
            titleinfo["rating_content"] = ""
            titleinfo["number_of_players"] = ""
            titleinfo["rating"] = ""
            titleinfo["amiibo_compatibility"] = ""
            titleinfo["developer"] = ""
            titleinfo["publisher"] = ""
            titleinfo["front_box_art"] = ""
            titleinfo["intro"] = ""
            titleinfo["description"] = ""
            titleinfo["dlc"] = ""
            titleinfo["US_price"] = ""
            titleinfo["Game_size"] = ""

            result = requests.get("https://ec.nintendo.com/apps/%s/US" % tid)
            # result.status_code == 200
            if result.status_code == 200:
                if result.url != 'https://www.nintendo.com/games/':
                    soup = BeautifulSoup(result.text, "html.parser")
                    if soup.find("meta", {"property": "og:url"}) != None:
                        slug = soup.find("meta", {"property": "og:url"})["content"].split('/')[-1]
                        infoJson = json.loads(requests.get("https://www.nintendo.com/json/content/get/game/%s" % slug).text)["game"]
                        if "release_date" in infoJson:
                            titleinfo["release_date_string"] = infoJson["release_date"]
                            titleinfo["release_date_iso"] = datetime.datetime.strftime(datetime.datetime.strptime(infoJson["release_date"], "%b %d, %Y"),'%Y%m%d')

                        if "title" in infoJson:
                            titleinfo["title"] = infoJson["title"]

                        if "nsuid" in infoJson:
                            titleinfo["nsuid"] = infoJson["nsuid"]

                        if "slug" in infoJson:
                            titleinfo["slug"] = infoJson["slug"]

                        if "game_code" in infoJson:
                            titleinfo["game_code"] = infoJson["game_code"]

                        catagories = []
                        if "game_category_ref" in infoJson:
                            catindex = 0
                            if "title" in infoJson["game_category_ref"]:
                                catagories.append(infoJson["game_category_ref"]["title"])
                            else:
                                for game_category in infoJson["game_category_ref"]:
                                    catagories.append(infoJson["game_category_ref"][catindex]["title"])
                                    catindex += 1
                            if len(catagories) > 0:
                                titleinfo["category"] = ','.join(catagories)

                        esrbcontent = []
                        if "esrb_content_descriptor_ref" in infoJson:
                            esrbindex = 0
                            if "title" in infoJson["esrb_content_descriptor_ref"]:
                                esrbcontent.append(infoJson["esrb_content_descriptor_ref"]["title"])
                            else:
                                for descriptor in infoJson["esrb_content_descriptor_ref"]:
                                    esrbcontent.append(infoJson["esrb_content_descriptor_ref"][esrbindex]["title"])
                                    esrbindex += 1
                            if len(esrbcontent) > 0:
                                titleinfo["content"] = ','.join(esrbcontent)

                        if "number_of_players" in infoJson:
                            titleinfo["number_of_players"] = infoJson["number_of_players"]

                        if "eshop_price" in infoJson:
                            titleinfo["US_price"] = infoJson["eshop_price"]

                        if "esrb_rating_ref" in infoJson:
                            if "title" in infoJson["esrb_rating_ref"]:
                                titleinfo["rating"] = infoJson["esrb_rating_ref"]["esrb_rating"]["short_description"]

                        if "amiibo_compatibility" in infoJson:
                            titleinfo["amiibo_compatibility"] = infoJson["amiibo_compatibility"]
 
                        if "dlc" in infoJson:
                            titleinfo["dlc"] = infoJson["dlc"]

                        if "developer_ref" in infoJson:
                            if "title" in infoJson["developer_ref"]:
                                titleinfo["developer"] = infoJson["developer_ref"]["title"]


                        if "publisher_ref" in infoJson:
                            if "title" in infoJson["publisher_ref"]:
                                titleinfo["publisher"] = infoJson["publisher_ref"]["title"]

                        if "front_box_art" in infoJson:
                            if "image" in infoJson["front_box_art"]:
                                if "image" in infoJson["front_box_art"]["image"]:
                                    if "url" in infoJson["front_box_art"]["image"]["image"]:
                                        titleinfo["front_box_art"] = infoJson["front_box_art"]["image"]["image"]["url"]

                        if "intro" in infoJson:
                            try:
                                details = BeautifulSoup(infoJson["intro"][0],"html.parser")
                                try:
                                    details = details.decode(formatter=None)
                                except:
                                    details = details.decode()
                                details = re.sub('<[^<]+?>', '', details).strip()
                                details = re.sub(' +', ' ', details)
                                details = re.sub('\n ', '\n', details)
                                details = re.sub('\n\n+', '\n\n', details)
                                titleinfo["intro"] = details
                            except Exception as e:
                                pass

                        if "game_overview_description" in infoJson:
                            details = BeautifulSoup(infoJson["game_overview_description"][0],"html.parser")
                            try:
                                details = details.decode(formatter=None)
                            except:
                                details = details.decode()
                            details = re.sub('<[^<]+?>', '', details).strip()
                            details = re.sub(' +', ' ', details)
                            details = re.sub('\n ', '\n', details)
                            details = re.sub('\n\n+', '\n\n', details)
                            titleinfo["description"] = details

                        result = requests.get("https://ec.nintendo.com/apps/%s/AU" % tid)
                        _json = ''
                        if result.status_code == 200:
                            _json = json.loads(result.text.split('NXSTORE.titleDetail.jsonData = ')[1].split('NXSTORE.titleDetail')[0].replace(';',''))
                        else:
                            result = requests.get("https://ec.nintendo.com/apps/%s/JP" % tid)
                            
                            if result.status_code == 200:
                                _json = json.loads(result.text.split('NXSTORE.titleDetail.jsonData = ')[1].split('NXSTORE.titleDetail')[0].replace(';',''))
                        if _json != '':
        ##                    print(_json["total_rom_size"])
        ##                    sys.exit()

                            if "total_rom_size" in _json:
                                titleinfo["Game_size"] = str(_json["total_rom_size"])

                            game_info_json[tid] = titleinfo

            if tid not in game_info_json:
                result = requests.get("https://ec.nintendo.com/apps/%s/AU" % tid)
                _json = ''
                if result.status_code == 200:
                    _json = json.loads(result.text.split('NXSTORE.titleDetail.jsonData = ')[1].split('NXSTORE.titleDetail')[0].replace(';',''))
                else:
                    result = requests.get("https://ec.nintendo.com/apps/%s/JP" % tid)
                    
                    if result.status_code == 200:
                        _json = json.loads(result.text.split('NXSTORE.titleDetail.jsonData = ')[1].split('NXSTORE.titleDetail')[0].replace(';',''))
                if _json != '':
##                    print(_json["total_rom_size"])
##                    sys.exit()

                    if "total_rom_size" in _json:
                        titleinfo["Game_size"] = str(_json["total_rom_size"])

                    if "release_date_on_eshop" in _json:
                        titleinfo["release_date_iso"] = _json["release_date_on_eshop"].replace('-','')
                        titleinfo["release_date_string"] = datetime.datetime.strftime(datetime.datetime.strptime(_json["release_date_on_eshop"].replace('-',''),'%Y%m%d' ),"%b %d, %Y")
                    
                    if "formal_name" in _json:
                        titleinfo["title"] = _json["formal_name"]
                    
                    if "id" in _json:
                        titleinfo["nsuid"] = "%s" % _json["id"]
                        
                    titleinfo["slug"] = ""
                    titleinfo["game_code"] = ""

                    if "genre" in _json:
                        titleinfo["category"] = _json["genre"].replace(' / ',',')

                    if "rating_info" in _json:
                        if "rating" in _json["rating_info"]:
                            rating = ''
                            if "name" in _json["rating_info"]['rating']:
                                rating = "Rated %s" % _json["rating_info"]['rating']['name']

                            if "age" in _json["rating_info"]['rating']:
                                rating = rating + " for ages %s and up" % _json["rating_info"]['rating']['age']

                            titleinfo["rating"] = rating

                        if "content_descriptors" in _json["rating_info"]:
                            content = []
                            for descriptor in  _json["rating_info"]["content_descriptors"]:
                                content.append(descriptor['name'])
                            titleinfo["rating_content"] = ','.join(content)

                
                    if "player_number" in _json:
                        if 'offline_max' in _json["player_number"]:
                            titleinfo["number_of_players"] = "up to %s players" % _json["player_number"]["offline_max"]

                        if 'local_max' in _json["player_number"]:
                            titleinfo["number_of_players"] = "up to %s players" % _json["player_number"]["local_max"]

                    titleinfo["amiibo_compatibility"] = ""

                    titleinfo["developer"] = ""

                    if "publisher" in _json:
                        titleinfo["publisher"] = _json["publisher"]["name"]

                    if "applications" in _json:
                        if "image_url" in _json["applications"][0]:
                            titleinfo["front_box_art"] = _json["applications"][0]['image_url']
                    
                    if "hero_banner_url" in _json:
                        titleinfo["front_box_art_alt"] = _json["hero_banner_url"]

                    if "catch_copy" in _json:
                        titleinfo["intro"] = _json["catch_copy"]

                    if "description" in _json:
                        titleinfo["description"] = _json["description"]

                    titleinfo["dlc"] = ""
                    game_info_json[tid] = titleinfo
                
                else:
                    f = open("Config/missing.txt", 'a', encoding="utf8")
                    f.write(tid+"|title doesn't exist at ec.nintendo.com"+'\n')
                    f.close()
                    if not silent:
                        self.game_text.delete("1.0", END)
                        self.game_text.insert(INSERT, _("\n\n\nUnable to find game info"))
                    done = True

##            except Exception as e:
##                #print(repr(e))
##                f = open("Config/missing.txt", 'a', encoding="utf8")
##                f.write(tid+'|'+ repr(e) +'\n')
##                f.close()
##                self.game_text.delete("1.0", END)
##                self.game_text.insert(INSERT, _("\n\n\nUnable to find game info"))
##                done = True

        if not done:
            with open("Config/Game_info.json", "w", encoding="utf8") as jsonFile:
                json.dump(game_info_json, jsonFile, indent=4)
            jsonFile.close()
            if not silent:
                self.game_desc(tid)
            

    
    def threaded_download(self):
        option = self.updateOptions.get()
##        try:
        tid = self.game_titleID.get()
        updateTid = tid
        tkey = self.game_titleKey.get()
        ver = self.version_option.get()
        
        if len(tkey) != 32 and self.titlekey_check:
            self.messages(_('Error'), _('Titlekey {} is not a 32-digits hexadecimal number!').format(tkey))                
        elif len(tid) != 16:
            self.messages(_('Error'), _('TitleID {} is not a 16-digits hexadecimal number!').format(tid))
        else:
            if _("Latest") in ver:
                updateTid = tid
                if tid.endswith('000'):
                    updateTid = '%s800' % tid[:-3]
                elif tid.endswith('800'):
                    baseTid = '%s000' % tid[:-3]
                    updateTid = tid
                ver = get_versions(updateTid)[-1]
            elif "none" in ver:
                ver == "none"
                    
            if tid.endswith('000'):
                updateTid = '%s800' % tid[:-3]
            elif tid.endswith('800'):
                baseTid = '%s000' % tid[:-3]
                updateTid = tid
                
            if option == "U" or self.is_DLC == True:
                if ver != "none":
                    self.messages("", _("Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress."))
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                    self.messages("", _("Download finished!"))
                else:
                    self.messages("", _("No updates available for the game"))
                    
            elif option == "B+U+D":
                base_tid = "{}000".format(tid[0:13])
                self.messages("", _("Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress."))
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                if ver != 'none':
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, path_Dir=self.path)
                self.messages("", _("Download finished!"))

            elif option == "U+D":
                if ver != "none":
                    updateTid = "{}800".format(tid[0:13])
                    self.messages("", _("Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress."))
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, path_Dir=self.path)
                self.messages("", _("Download finished!"))


            elif option == "D":
                self.messages("", _("Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress."))
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, path_Dir=self.path)
                self.messages("", _("Download finished!"))

                
            elif option == "B":
                base_tid = "{}000".format(tid[0:13])
                self.messages("", _("Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress."))
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                self.messages("", _("Download finished!"))
                
            elif option == "B+U":
                base_tid = "{}000".format(tid[0:13])
                self.messages("", _("Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress."))
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                if ver != 'none':
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                    self.messages("", _("Download finished!"))
                else:
                    self.messages("", _("No updates available for the game, base game downloaded!"))
##        except:
##            print("Error downloading {}, note: if you're downloading a DLC then different versions of DLC may have different titlekeys".format(tid))
        return
    
    def download(self):
        thread = threading.Thread(target = self.threaded_download)
        thread.start()

    def export_persistent_queue(self):
        self.dump_persistent_queue(self.normalize_file_path(filedialog.asksaveasfilename(initialdir = self.path, title = "Select file", filetypes = (("JSON files","*.json"),("all files","*.*")))))

    def import_persistent_queue(self):
        self.load_persistent_queue(self.normalize_file_path(filedialog.askopenfilename(initialdir = self.path, title = "Select file", filetypes = (("JSON files","*.json"),("all files","*.*")))))

    def dump_persistent_queue(self, path = r'Config/CDNSP_queue.json'):
        if path == "":
            print(_("\nYou didn't choose a location to save the file!"))
            return
        elif not path.endswith(".json"):
            path += ".json"
            
        # if self.persist_queue # check for user option here
        f = open(path, 'w')
        json.dump(self.persistent_queue, f)
        f.close()

    def load_persistent_queue(self, path = r'Config/CDNSP_queue.json'):
        # if self.persist_queue # check for user option here
        try:
            f = open(path, 'r')
            try:
                self.remove_all()
            except:
                pass
            for c, tid, ver, key, option in json.load(f):
                self.add_item_to_queue((tid, ver, key, option), True)
            f.close()
        except:
            print(_("Persistent queue not found, skipping..."))

    def get_index_in_queue(self, item):
        try:
            return self.queue_list.index(item)
        except:
            print(_("Item not found in queue"), item)

    def add_selected_items_to_queue(self):
        self.add_items_to_queue(self.tree.selection())

    def add_items_to_queue(self, indices):
##        try:
        for index in indices:
            index = int(self.tree.item(index,"value")[0])-1
##            index = int(self.temp_list[index].split(",")[0])-1
            tid = self.titleID[index]
            key = self.titleKey[index]
            ver = self.version_option.get()
            option = self.updateOptions.get()
            if len(key) != 32 and self.titlekey_check:
                self.messages(_('Error'), _('Titlekey {} is not a 32-digits hexadecimal number!').format(key))
            elif len(tid) != 16:
                self.messages(_('Error'), _('TitleID {} is not a 16-digits hexadecimal number!').format(tid))
            else:
                self.add_item_to_queue((tid, ver, key, option))

        self.dump_persistent_queue()
##        except:
##            messagebox.showerror("Error", "No game selected/entered to add to queue")

    def process_item_versions(self, tid, ver):
        if _("Latest") or "Latest" in ver:
            if tid.endswith('000'):
                tid = '%s800' % tid[:-3]
            ver = get_versions(tid)[-1]
        elif "none" in ver:
            ver = "none"

        return (tid, ver)

    # takes an item with unformatted tid and ver
    def add_item_to_queue(self, item, dump_queue = False):
        tid, ver, key, option = item
        if len(tid) == 16:
            if not Toplevel.winfo_exists(self.queue_win):
                self.queue_menu_setup() #Fix for app crashing when close the queue menu and re-open
            self.queue_win.update()
            self.queue_win.deiconify()
            try:
                c = self.titleID.index(tid)
                c = self.title[c] # Name of the game
            except:
                print(_("Name for titleID not found in the list"), tid)
                c = "UNKNOWN NAME"

            formatted_tid, formatted_ver = self.process_item_versions(tid, ver)
            if "[DLC]" in c:
                option = "DLC"
            if c[-1] == "\n":
                c = c[:-1]
            if ver == _("Latest"):
                eng_ver = "Latest"
            else:
                eng_ver = ver
            self.queue_title_list.insert("end", "{}---{}---{}".format(c, _(ver), option))
            self.queue_list.append((formatted_tid, formatted_ver, key, option))
            self.persistent_queue.append((c, tid, eng_ver, key, option))
            if dump_queue: self.dump_persistent_queue()
        self.queue_title_list.yview(END) # Auto scroll the queue menu as requested

    def remove_selected_items(self):
        self.remove_items(self.queue_title_list.curselection())

    def remove_items(self, indices):
        counter = 0
        for index in indices:
            index = index - counter
            try:
                self.remove_item(index)
                counter += 1
            except:
                print(_("No game selected to remove!"))

        self.dump_persistent_queue()

    def remove_item(self, index, dump_queue = False):
        del self.queue_list[index]
        del self.persistent_queue[index]
        self.queue_title_list.delete(index)
        if dump_queue: self.dump_persistent_queue()
        
    def threaded_download_all(self):
        self.messages("", _("Download for all your queued games will now begin! You will be informed once all the download has completed, please wait and be patient!"))
        self.stateLabel.configure(text = _("Downloading games..."))
        download_list = self.queue_list.copy()
        for item in download_list:
            tid, ver, tkey, option = item
            ver = self.process_item_versions(tid, ver)[1]
##            try:
            if option == "U" or option == "DLC":
                if ver != "none":
                    if tid.endswith("00"):
                        tid = "{}800".format(tid[0:13])
                    download_game(tid, ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                else:
                    print(_("No updates available for titleID: {}").format(tid))
                    
            elif option == "B+U+D":
                base_tid = "{}000".format(tid[0:13])
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                if ver != 'none':
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, path_Dir=self.path)

            elif option == "U+D":
                if ver != "none":
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, path_Dir=self.path)


            elif option == "D":
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, path_Dir=self.path)

                
            elif option == "B":
                base_tid = "{}000".format(tid[0:13])
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                
            elif option == "B+U":
                base_tid = "{}000".format(tid[0:13])
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                if ver != 'none':
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, path_Dir=self.path)
                else:
                    print(_("No updates available for titleID: {}, base game downloaded!").format(tid))

            index = self.get_index_in_queue(item)
            self.remove_item(index, True)
##            except:
##                print("Error downloading {}, note: if you're downloading a DLC then different versions of DLC may have different titlekeys".format(tid))
        self.messages("", _("Download complete!"))
        self.stateLabel["text"] = _("Download Complete!")
        # self.remove_all(dump_queue = True)

    def download_all(self):
        thread = threading.Thread(target = self.threaded_download_all)
        thread.start()

##    def download_check(self, tid, ver):
##        if ver != "0" or ver != "1": # Is an update game
##            if any(tid_list in tid for tid_list in self.installed):
##                print(tid, self.installed.index(tid))
##        else:
##            if any(tid_list in tid for tid_list in self.installed):                      

    def normalize_file_path(self, file_path):
        if self.sys_name == "Win":
            return file_path.replace("/", "\\")
        else:
            return file_path

    def change_dl_path(self):
        self.path = self.normalize_file_path(filedialog.askdirectory())

        updateJsonFile("Download_location", self.path)
        print("\n{}".format(self.path))

    def nsp_repack_option(self):
        if self.repack == True:
            self.optionMenu.entryconfig(4, label= _("Enable NSP Repack"))
            self.repack = False
        elif self.repack == False:
            self.optionMenu.entryconfig(4, label= _("Disable NSP Repack"))
            self.repack = True
        updateJsonFile("NSP_repack", str(self.repack))

    def threaded_update_titlekeys(self):
        self.status_label.config(text=_("Status: Updating titlekeys"))
        print(self.db_URL)
##        try:
        r = requests.get(self.db_URL, allow_redirects=True, verify=False)
        if str(r.history) == "[<Response [302]>]" and str(r.status_code) == "200":
            r.encoding = "utf-8"
            newdb = r.text.split('\n')
            if newdb[-1] == "":
                newdb = newdb[:-1]
            if os.path.isfile('titlekeys.txt'):
                with open('titlekeys.txt',encoding="utf8") as f:
                    currdb = f.read().split('\n')
                    if currdb[-1] == "":
                        currdb = currdb[:-1]
                    currdb = [x.strip() for x in currdb]
                    counter = 0
                    info = ''
                    new_tid = []
                    for line in newdb:
                        if line.strip() not in currdb:
                            if line.strip() != newdb[0].strip():
                                new_tid.append(line.strip().split('|')[0])
                                info += (line.strip()).rsplit('|',1)[1] + '\n'
                                counter += 1
                    if len(new_tid) != 0:
                        file_path = open(r"Config/new.txt", "w")
                        text = ""
                        for new in new_tid:
                            text += "{}\n".format(new[:16])
                        file_path.write(text)
                        file_path.close()
                    if counter:
                        update_win = Toplevel(self.root) #https://stackoverflow.com/questions/13832720/how-to-attach-a-scrollbar-to-a-text-widget
                        self.update_window = update_win
                        global update_win_size
                        update_win.title(_("Finished update!"))
                        if update_win_size != "":
                            update_win.geometry(update_win_size)
                        else:
                            update_win.geometry("600x400+120+200")
                        # create a Frame for the Text and Scrollbar
                        txt_frm = Frame(update_win, width=600, height=400)
                        txt_frm.pack(fill="both", expand=True)
                        # ensure a consistent GUI size
                        txt_frm.grid_propagate(False)
                        # implement stretchability
                        txt_frm.grid_rowconfigure(0, weight=1)
                        txt_frm.grid_columnconfigure(0, weight=3)

                        # create a Text widget
                        txt = Text(txt_frm, borderwidth=3, relief="sunken")
                        txt.config(font=("Open Sans", 12), undo=True, wrap='word')
                        txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2, columnspan=2)
                        txt.insert("1.0", info)

                        # create a Scrollbar and associate it with txt
                        scrollb = Scrollbar(txt_frm, command=txt.yview, width=20)
                        scrollb.grid(row=0, column=3, sticky='nsew')
                        txt['yscrollcommand'] = scrollb.set


                        # info on total games added and an exit button
                        Label(txt_frm, text=_("Total of new games added: {}").format(counter)).grid(row=1, column=0)
                        Button(txt_frm, text=_("Close"), height=2, command=lambda: update_win.destroy()).grid(row=1, column=1)
    ##                    Label(txt_frm, text="   ").grid(row=1, column=3)
                        
                        try:
                            # print('\nSaving new database...')
                            f = open('titlekeys.txt','w',encoding="utf-8")
                            self.title = []
                            self.titleID = []
                            self.titleKey = []
                            for line in newdb:
                                if line.strip():
                                    self.title.append(line.strip().split("|")[2])
                                    self.titleID.append(line.strip().split("|")[0][:16])
                                    self.titleKey.append(line.strip().split("|")[1])
                                    f.write(line.strip() + '\n')
                            f.close()
                            self.current_status = []
                            self.update_list(rebuild=True, label=build_text)
                        except Exception as e:
                            print(e)
                    else:
                        self.status_label.config(text=_('Status: Finished update, There were no new games to update!'))
                        print(_('\nStatus: Finished update, There were no new games to update!'))
                        self.root.config(cursor="")
                        try:
                            self.imageLabel.config(cursor="hand2")
                        except:
                            pass
                        self.done_status()
            else:
                try:
                    # print('\nSaving new database...')
                    f = open('titlekeys.txt','w',encoding="utf-8")
                    self.title = []
                    self.titleID = []
                    self.titleKey = []
                    for line in newdb:
                        if line.strip():
                            self.title.append(line.strip().split("|")[2])
                            self.titleID.append(line.strip().split("|")[0][:16])
                            self.titleKey.append(line.strip().split("|")[1])
                            f.write(line.strip() + '\n')
                    f.close()
                    self.current_status = []
                    self.update_list(rebuild=True, label=_('Status: Finished update, Database rebuilt from scratch'))
                except Exception as e:
                    print(e)
        else:
            self.messages(_("Error"), _("The database server {} might be down or unavailable").format(self.db_URL))
        game_list = []
        self.title_list.delete(0, END)
        
        f = open("titlekeys.txt", "r", encoding="utf8")
        content = f.readlines()
        self.titleID = []
        self.titleKey = []
        self.title = []
        for i in range(len(content)):
            titleID = ""
            try:
                titleID, titleKey, title = content[i].split("|")
            except:
                print(_("Check if there's extra spaces at the bottom of your titlekeys.txt file! Delete if you do!"))
            if titleID != "":
                self.titleID.append(titleID[:16])
                self.titleKey.append(titleKey)
                self.title.append(title[:-1])
        global titleID_list
        global titleKey_list
        global title_list
        
        titleID_list = []
        titleKey_list = []
        title_list = []
        f.close()
        # self.messages("", "Updated!")
##        except:
##            self.messages("Error", "Too many people accessing the database, or then link is died, or the link is incorrect!")

    def update_titlekeys(self):
        self.root.config(cursor="watch")
        self.imageLabel.config(cursor="watch")
        thread = threading.Thread(target = self.threaded_update_titlekeys)
        thread.start()

    def mute_all(self):
        if self.mute == False:
            self.optionMenu.entryconfig(3, label= _("Unmute All Pop-ups"))
            self.mute = True
        elif self.mute == True:
            self.optionMenu.entryconfig(3, label= _("Mute All Pop-ups"))
            self.mute = False
        updateJsonFile("Mute", str(self.mute))

    def messages(self, title, text):
        if self.mute != True:
            messagebox.showinfo(title, text)
        else:
            print(_("\n{}\n").format(text))

    def titlekey_check_option(self):
        global titlekey_check
        if self.titlekey_check == True:
            self.titlekey_check = False
            titlekey_check = self.titlekey_check
            self.optionMenu.entryconfig(5, label= _("Enable Titlekey Check")) # Automatically disable repacking as well
            self.repack = False
            self.optionMenu.entryconfig(4, label= _("Enable NSP Repack"))
        elif self.titlekey_check == False:
            self.titlekey_check = True
            titlekey_check = self.titlekey_check
            self.optionMenu.entryconfig(5, label= _("Disable Titlekey Check"))
            self.repack = True
            self.optionMenu.entryconfig(4, label= _("Disable NSP Repack"))
        updateJsonFile("Titlekey_check", str(self.titlekey_check))
        
    def disable_aria2c(self):
        pass

    def disable_game_image(self):
        if self.game_image_disable == False:
            self.game_image_disable = True
            self.optionMenu.entryconfig(1, label= _("ENABLE GAME IMAGE"))
        elif self.game_image_disable == True:
            self.game_image_disable = False
            self.optionMenu.entryconfig(1, label= _("DISABLE GAME IMAGE"))
        updateJsonFile("Disable_game_image", str(self.game_image_disable))

    def threaded_preload_images(self):
##        try:
        for k in self.titleID:
            if k != "":
                start = time.time()
                tid = k
                isDLC = False
                if not tid.endswith("00"):
                    isDLC = True
                    tid = "{}".format(tid[0:12])
                    indices = [i for i, s in enumerate(self.titleID) if tid in s]
                    if len(indices) >= 2:
                        for t in indices:
                            if self.titleID[t].endswith("000"):
                                tid = self.titleID[t]
                                break
                        if tid.endswith("000"):
                            isDLC = False
                if not os.path.isfile("Images/{}.jpg".format(tid)):
                    if not isDLC:
                        global noaria
                        noaria = True
                        start = time.time()
                        base_ver = get_versions(tid)[-1]
                        result = game_image(tid, base_ver, self.titleKey[self.titleID.index(tid)])
                        noaria = False
                        if result[1] != "Exist":
                            if self.sys_name == "Win":
                                try:
                                    subprocess.check_output("{0} -k keys.txt {1}\\control.nca --section0dir={1}\\section0".format(hactoolPath, result[0].replace("/", "\\")), shell=True)
                                except subprocess.CalledProcessError as e:
                                    raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
                            else:
                                subprocess.check_output("{0} -k keys.txt '{1}/control.nca' --section0dir='{1}/section0'".format(hactoolPath, result[0]), shell=True)
                            icon_list = ["icon_AmericanEnglish.dat", "icon_BritishEnglish.dat", "icon_CanadianFrench.dat", "icon_German.dat", "icon_Italian.dat", "icon_Japanese.dat", "icon_LatinAmericanSpanish.dat", "icon_Spanish.dat"]
                            file_name = ""
                            dir_content = os.listdir(os.path.dirname(os.path.abspath(__file__))+'/Images/{}/section0/'.format(tid))
                            for i in icon_list:
                                if i in dir_content:
                                    file_name = i.split(".")[0]
                                    break
                            os.rename('{}/section0/{}.dat'.format(result[0], file_name), '{}/section0/{}.jpg'.format(result[0], file_name))
                            shutil.copyfile('{}/section0/{}.jpg'.format(result[0], file_name), 'Images/{}.jpg'.format(tid))
                            shutil.rmtree(os.path.dirname(os.path.abspath(__file__))+'/Images/{}'.format(tid))
        end = time.time()
        print(_("\nIt took {} seconds for you to get all images!\n").format(end - start))
        self.messages("", _("Done getting all game images!"))
##        except:
##            print("Error getting game images")

    def preload_images(self):
        thread = threading.Thread(target = self.threaded_preload_images)
        thread.start()
    
    def get_update_ver(self):
        tid = self.game_titleID.get()
        if tid != "" and len(tid) == 16:
            value = self.titleID.index(tid)
            print(tid)
            try:
                isDLC = False
                tid = self.titleID[value]
                updateTid = tid
                if tid.endswith('000'):
                    updateTid = '%s800' % tid[:-3]
                elif tid.endswith('800'):
                    baseTid = '%s000' % tid[:-3]
                    updateTid = tid
                elif not tid.endswith('00'):
                    isDLC = True
                update_list = []
                for i in get_versions(updateTid):
                    update_list.append(i)
                if isDLC:
                    if update_list[0] != "0":
                        update_list.insert(0, "0")
                if update_list[0] == 'none':
                    update_list[0] = "0"
                print(update_list)
                update_list.insert(0, _("Latest"))
                self.version_select["values"] = update_list
                self.version_select.set(_("Latest"))
            except:
                print(_("Failed to get version"))
        else:
            print(_("No TitleID or TitleID not 16 characters!"))

    def shorten(self):
        global truncateName
        if truncateName == False:
            truncateName = True
            self.optionMenu.entryconfig(7, label= _("Disable Shorten Name"))
        elif truncateName == True:
            truncateName = False
            self.optionMenu.entryconfig(7, label= _("Enable Shorten Name"))
        updateJsonFile("Shorten", str(truncateName))
            
    def tinfoil_change(self):
        global tinfoil
        if tinfoil == False:
            tinfoil = True
            self.optionMenu.entryconfig(8, label= _("Disable Tinfoil Download"))
        elif tinfoil == True:
            tinfoil = False
            self.optionMenu.entryconfig(8, label= _("Enable Tinfoil Download"))
        updateJsonFile("Tinfoil", str(tinfoil))

    def window_info(self, window):
        x = window.winfo_x()
        y = window.winfo_y()
        w = window.winfo_width()
        h = window.winfo_height()

        size_pos = "{}x{}+{}+{}".format(w, h, x, y)
        return size_pos

    def window_save(self):
        if Toplevel.winfo_exists(self.root):
            updateJsonFile("Main_win", self.window_info(self.root))
        try:
            if Toplevel.winfo_exists(self.queue_win):
                updateJsonFile("Queue_win", self.window_info(self.queue_win))
                global queue_win
                queue_win = self.window_info(self.queue_win)
        except:
            pass
        try:
            if Toplevel.winfo_exists(self.update_window):
                updateJsonFile("Update_win", self.window_info(self.update_window))
                global update_win
                update_win = self.window_info(self.update_window)
        except:
            pass
        try:
            if Toplevel.winfo_exists(self.my_game):
                updateJsonFile("Scan_win", self.window_info(self.my_game))
                global scan_win
                scan_win = self.window_info(self.my_game)
        except:
            pass
        try:
            if Toplevel.winfo_exists(self.base_64):
                updateJsonFile("Base64_win", self.window_info(self.base_64))
                global base64_win
                base64_win = self.window_info(self.base_64)
        except:
            pass
        self.messages("", _("Windows size and position saved!"))

    def my_game_GUI(self):
        global scan_win
        my_game = Toplevel(self.root)
        self.my_game = my_game
        my_game.title(_("Search for existing games"))
        my_game.geometry(scan_win)
        entry_w = 50
        if sys_name == "Mac":
            entry_w = 32
        dir_text = ""
        dir_entry = Entry(my_game, width=entry_w, text=dir_text)
        if self.game_location != "":
            dir_entry.delete(0, END)
            dir_entry.insert(0, self.game_location)
        self.dir_entry = dir_entry
        dir_entry.grid(row=0, column=0, padx=(10,0), pady=10)
        browse_btn = Button(my_game, text=_("Browse"), command=self.my_game_directory)
        browse_btn.grid(row=0, column=1, padx=10, pady=10)
        scan_btn = Button(my_game, text=_("Scan"), command=self.my_game_scan)
        scan_btn.grid(row=1, column=0, columnspan=2, sticky=N, padx=10)

    def my_game_directory(self):
        path = self.normalize_file_path(filedialog.askdirectory())
        if path != "":
            self.game_location = path
            updateJsonFile("Game_location", str(self.game_location))
        self.my_game.lift()
        self.my_game.update()
        self.dir_entry.delete(0, END)
        self.dir_entry.insert(0, path)

    def my_game_scan(self):
        import re

        a_dir = self.dir_entry.get()

        if a_dir == "":
            self.messages(_("Error"), _("You didn't choose a directory!"))
            self.my_game.lift()
        elif not os.path.isdir(a_dir):
            self.messages(_("Error"), _("The chosen directory doesn't exist!"))
            self.my_game.lift()
        else:
            game_list = []
            
    ##        print([name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))])
    ##        print(glob.glob(a_dir+"\*.nsp"))
            
    ##        for game in glob.iglob(r"{}\**\*.nsp".format(a_dir), recursive=True):
    ##            game_list.append(game)
    ##        print(os.scandir(a_dir))
            for root, dirs, files in os.walk(a_dir):
                for basename in files:
                    if basename.endswith(".nsp"):
                        game_list.append(basename)
    ##        game_list = os.listdir(self.dir_entry.get())
            if not os.path.isdir("Config"):
                os.mkdir("Config")
            tid_exist = [] # Tid that's already in the installed.txt
            ver_exist = []

            if os.path.isfile(r"Config/installed.txt"):
                file = open(r"Config/installed.txt", "r")
                for game in file.readlines():
                    tid_exist.append("{}".format(game.split(",")[0].strip()))
                    ver_exist.append("{}".format(game.split(",")[1].strip()))
                file.close()

            file = open(r"Config/installed.txt", "w")
            for game in game_list:
                title = re.search(r".*[0][0-9a-zA-Z]{15}.*[.nsp]", game)
                if title:
                    try:
                        tid_check = re.compile(r"[0][0-9a-zA-Z]{15}")
                        tid_result = tid_check.findall(game)[0]
                        tid_result = tid_result
                        if tid_result.endswith("800"):
                            tid_result = "{}000".format(tid_result[:13])
                    except:
                        tid_result = "0"
                    
                    try:
                        ver_check = re.compile(r"[v][0-9]+")
                        ver_result = ver_check.findall(game)[0]
                        ver_result = ver_result.split("v")[1]
                    except:
                        ver_result = "0"
                    if tid_result != "0":
                        if any(list_tid in tid_result for list_tid in tid_exist): # Check if the tid is already in installed.txt
                            if int(ver_result) > int(ver_exist[tid_exist.index(tid_result)]):
                                ver_exist[tid_exist.index(tid_result)] = ver_result
                        else:
                            tid_exist.append(tid_result)
                            ver_exist.append(ver_result)

            for i in range(len(tid_exist)):
                file.write("{}, {}\n".format(tid_exist[i], ver_exist[i]))

            file.close()

            self.update_list(rebuild=True, label=build_text)
            self.my_game.destroy()
            
    def base_64_GUI(self):
        global base64_win
        base_64 = Toplevel(self.root)
        self.base_64 = base_64
        base_64.title(_("Base64 Decoder"))
        base_64.geometry(base64_win)
        entry_w = 50
        if sys_name == "Mac":
            entry_w = 28
        base_64_label = Label(base_64, text=_("Base64 text:"))
        base_64_label.grid(row=0, column=0)
        base_64_entry = Entry(base_64, width=entry_w)
        self.base_64_entry = base_64_entry
        base_64_entry.grid(row=0, column=1, padx=(10,0), pady=10)
        browse_btn = Button(base_64, text=_("Decode"), command=self.decode_64)
        browse_btn.grid(row=0, column=2, padx=10, pady=10)

        decoded_label = Label(base_64, text=_("Decoded text:"))
        decoded_label.grid(row=1, column=0)
        decoded_entry = Entry(base_64, width=entry_w)
        self.decoded_entry = decoded_entry
        decoded_entry.grid(row=1, column=1, padx=(10,0), pady=10)
        scan_btn = Button(base_64, text=_("Open"), command=self.base64_open)
        scan_btn.grid(row=1, column=2, sticky=N, padx=10, pady=10)

    def decode_64(self):
        base64_text = self.base_64_entry.get()
        self.decoded_entry.delete(0, END)
        self.decoded_entry.insert(0, base64.b64decode(base64_text))

    def base64_open(self):
        url = self.decoded_entry.get()
        webbrowser.open(url, new=0, autoraise=True)

    def make_list(self):
        # Create list in advance
        self.full_list = self.current_status
        
        self.no_demo_list = [] # No demo list
        for game in self.full_list:
            if not "demo" in game[1].strip().lower() and not "体験版" in game[1].strip().lower():
                self.no_demo_list.append(game)
                
        self.no_jap_list = []
        for game in self.full_list:
            try:
                game[1].strip().lower().encode(encoding='utf-8').decode('ascii')
            except UnicodeDecodeError:
                pass
            else:
                self.no_jap_list.append(game)

        self.no_demo_jap_list = []
        for game in self.full_list:
            if not "demo" in game[1].strip().lower() and not "体験版" in game[1].strip().lower():
                try:
                    game[1].strip().lower().encode(encoding='utf-8').decode('ascii')
                except UnicodeDecodeError:
                    pass
                else:
                    self.no_demo_jap_list.append(game)
        
        
    def filter_game(self):        
        demo_off = self.demo.get()
        no_jap = self.jap.get()
        
        if demo_off and no_jap:
            self.current_status = self.no_demo_jap_list
        elif demo_off:
            self.current_status = self.no_demo_list
        elif no_jap:
            self.current_status = self.no_jap_list
        else:
            self.current_status = self.full_list
        try:
            search_term = self.search_var.get()
        except:
            search_term = ""
        self.tree.delete(*self.tree.get_children())
        for game_status in self.current_status:
            number = game_status[0].strip()
            tid = game_status[1].strip()
            game_name = game_status[2].strip()
            state = game_status[3].strip()
            
            tree_row = (number, tid, game_name, state)
            if search_term.lower().strip() in game_name.lower() or search_term.lower().strip() in tid.lower():
                self.tree.insert('', 'end', values=tree_row)
                    
    def sysver_zero(self):
        global sysver0
        if sysver0 == False:
            sysver0 = True
            self.optionMenu.entryconfig(9, label= _("Disable SysVer 0 Patch"))
        elif sysver0 == True:
            sysver0 = False
            self.optionMenu.entryconfig(9, label= _("Enable SysVer 0 Patch"))
        updateJsonFile("SysVerZero", str(sysver0))

##    def threaded_preload_desc(self):
##        self.status_label.config(text=_("Status: Downloading all game descriptions"))
##        
##        global game_info_json
##        for tid in self.titleID:
##            if not tid.endswith("00"):
##                tid = "{}".format(tid[0:12])
##                indices = [i for i, s in enumerate(self.titleID) if tid in s]
##                if len(indices) >= 2:
##                    for t in indices:
##                        if self.titleID[t].endswith("000"):
##                            tid = self.titleID[t]
##                            break
##            if tid not in game_info_json:
##                if len(tid) == 16:
##                    print(tid)
##                    self.download_desc(tid, silent=True)
##                
##        print(_("Done preloading all game descriptions!"))
##        thread = threading.Thread(target = lambda: self.done_status())
##        thread.start()
##
##    def preload_desc(self):
##        thread = threading.Thread(target = lambda: self.threaded_preload_desc())
##        thread.start()

    def credit_gui(self):
        credit_win = Toplevel(self.root)
##        credit_win.geometry("600x500+100+100")
        self.credit_win = credit_win
        credit_win.title(_("Credits"))

        credit_text = """This GUI was originally a project started by Bob, and eventually grew thanks to the overwhelming support from the community!

We now support 24 different languages!
I would like to thank the following users for translating:

German: Jojo#1234
Portuguese: KazumaKiryu#7300
Chinese Simplified: Dolur#7867
Chinese Traditional: Maruku#7128
Japanese: Jinoshi(ジノシ)#4416
Korean: RoutineFree#4012
Spanish: pordeciralgo#3603
French: cdndave#1833
Russian: JHI_UA#8876
Arabic: mk#6387
Turkish: arkham_knight#9797
Dutch: Soundwave#2606
Italian: Vinczenon#7788
Hebrew: dinoster#0218
Persian: SirArmazd#8283
Thai: Pacmasaurus#4158
Greek: ioann1s#3498
Indonesian: Damar#0799
Polish: szczuru#7105
Afrikaans: twitchRSA#5765
Vietnamese: gurucuku#4629
Hungarian: Quince#2831
Malaysian: fadzly#4390"""

        credit = Text(credit_win, wrap=WORD)
        credit.grid(row=0, column=0)
        credit.insert(INSERT, credit_text)
        scrollb = Scrollbar(credit_win, command=credit.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        credit['yscrollcommand'] = scrollb.set

    def threaded_update_ver_list(self):
        self.status_label.config(text=_("Status: Updating version list...")) 
        known_ver = {}

        if not os.path.isfile("Config/Version_info.json"):
            print(_("\nCan't find Version_info.json file!\n"))
            print(_("Attempting to download the Version_info.json file for you"))
            urllib.request.urlretrieve("https://raw.githubusercontent.com/Bob123a1/CDNSP-GUI-Files/master/Config/Version_info.json", "Config/Version_info.json")
                
        if os.path.isfile("Config/Version_info.json"):
            ver_file = open("Config/Version_info.json", "r", encoding="utf8")
            known_ver = json.load(ver_file)
            ver_file.close()

            installed = []
            file_path = r"Config/installed.txt"
            if os.path.exists(file_path):
                file = open(file_path, "r")
                for line in file.readlines():
                    if line[-1] == "\n":
                        line = line[:-1]
                    installed.append(line.split(",")[0].strip())
                file.close()
            print("\nUpdating version list...")
            for tid in installed:
                if tid.endswith("00"):
                    updateTid = "{}800".format(tid[:13])
                else:
                    updateTid = tid
                latest_ver = str(get_versions(updateTid)[-1])

                print("Tid: {}, latest version: {}".format(updateTid, latest_ver))
                known_ver[tid] = latest_ver
                
            ver_file = open("Config/Version_info.json", "w", encoding="utf8")
            json.dump(known_ver, ver_file, indent=4)
            ver_file.close()
        else:
            print(_("Unable to find Version_info.json file inside your Config folder"))
        self.update_list(rebuild=True)
        
    def update_ver_list(self):
        thread = threading.Thread(target=self.threaded_update_ver_list)
        thread.start()
# ------------------------
# Main Section

def main():
    urllib3.disable_warnings()       
    configPath = os.path.join(os.path.dirname(__file__), 'CDNSPconfig.json')
    global hactoolPath, keysPath, NXclientPath, ShopNPath, reg, fw, did, env, dbURL, nspout
    hactoolPath, keysPath, NXclientPath, ShopNPath, reg, fw, did, env, dbURL, nspout = load_config(configPath)
    
    spam_spec = util.find_spec("tqdm")
    found = spam_spec is not None
    global tqdmProgBar
    if found:
        tqdmProgBar = True
    else:
        tqdmProgBar = False
        print('Install the tqdm library for better-looking progress bars! (pip install tqdm)')
    global keysArg
    if keysPath != '':
        keysArg = ' -k "%s"' % keysPath
    else:
        keysArg = ''

    # Read titlekeys.txt file
    f = open("titlekeys.txt", "r", encoding="utf8")
    content = f.readlines()
    global titleID_list
    global titleKey_list
    global title_list

    titleID_list = []
    titleKey_list = []
    title_list = []
    for i in range(len(content)):
        titleID = ""
        try:
            titleID, titleKey, title = content[i].split("|")
        except:
            print(_("Check if there's extra spaces at the bottom of your titlekeys.txt file! Delete if you do!"))
        if titleID != "":
            titleID_list.append(titleID[:16])
            titleKey_list.append(titleKey)
            if title[:-1] == "\n":
                title_list.append(title[:-1])
            else:
                title_list.append(title)
    f.close()

    if os.path.isfile("titlekeys_overwrite.txt"):
        t_overwrite = open("titlekeys_overwrite.txt", "r", encoding="utf8")
        for line in t_overwrite.readlines():
            line = line.strip()
            if "#" not in line and line != "":
                if line[-1] == "\n":
                    line = line[:-1]
                _tid, _tkey = line.split("|")
                _tid = _tid[:16]
                _tkey = _tkey[:32]
                
                if len(_tid) == 16:
                    if len(_tkey) == 32:
                        if _tid in titleID_list:
                            titleKey_list[titleID_list.index(_tid)] = _tkey

    root = Tk()
    root.title("CDNSP GUI - Bobv4.1.1")
    Application(root, titleID_list, titleKey_list, title_list, dbURL)

    root.mainloop()

if __name__ == '__main__':
    main()
