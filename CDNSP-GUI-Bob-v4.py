#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Credit:
# Thanks to Zotan (DB and script), Big Poppa Panda, AnalogMan, F!rsT-S0uL
# Design inspiration: Lucas Rey's GUI (https://darkumbra.net/forums/topic/174470-app-cdnsp-gui-v105-download-nsp-gamez-using-a-gui/)
# Thanks to the developer(s) that worked on CDNSP_Next for the cert fix!
# Thanks to the help of devloper NighTime, kvn1351, gizmomelb, theLorknessMonster
# CDNSP - GUI - Bob - v4
import sys
import time
import random

# Check that user is using Python 3
if (sys.version_info > (3, 0)):
    # Python 3 code in this block
    pass
else:
    # Python 2 code in this block
    print("\n\nError - Application launched with Python 2, please install Python 3 and delete Python 2\n")
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
        url = 'https://raw.githubusercontent.com/bob7689/CDNSP-GUI/master/{}'.format(file)  
        urllib.request.urlretrieve(url, file)

def install_module(module):
    try:
       subprocess.check_output("pip3 install {}".format(module), shell=True)
    except:
        print("Error installing {0}, close the application and you can install the module manually by typing in CMD: pip3 install {0}".format(module))

print("\nChecking if all required modules are installed!\n\n")
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
    import pyopenssl
except:
    pass

req_file = ["CDNSPconfig.json", "keys.txt", "nx_tls_client_cert.pem", "titlekeys.txt"]
try:
    for file in req_file:
        check_req_file(file)
    print("Everything looks good!")
except:
    print("Unable to get required files! Check your internet connection")
    
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
import operator
import platform
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

import locale

global sys_locale

if platform.system() != 'Darwin':
    sys_locale = locale.getdefaultlocale() # Detect system locale to fix Window size on Chinese Windows Computer
    sys_locale = sys_locale[0]
else:
    sys_locale = "Mac"

#Global Vars
truncateName = False
tinfoil = False
enxhop = False
    
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
    return 0x10000 * s[1] + s[0]


def read_u64(f, off):
    return upk('<Q', read_at(f, off, 8))[0]

def calc_sha256(fPath):
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
        raise ValueError("n < 0")
    symbols = ('B', 'KB', 'MB', 'GB', 'TB')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return f % locals()
    return f % dict(symbol=symbols[0], value=n)


def load_config(fPath):
    dir = os.path.dirname(__file__)

    config = {'Paths': {
        'hactoolPath': 'hactool',
        'keysPath': 'keys.txt',
        'NXclientPath': 'nx_tls_client_cert.pem',
        'ShopNPath': 'ShopN.pem'},
        'Values': {
            'Region': 'US',
            'Firmware': '5.1.0-0',
            'DeviceID': '0000000000000000',
            'Environment': 'lp1',
            'TitleKeysURL': '',
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


def make_request(method, url, certificate='', hdArgs={}):
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


def get_info(tid, silent=False):
    info = ''
    name = get_name(tid)
    if tid.endswith('000'):
        baseTid = tid
        updateTid = '%s800' % tid[:-3]
    elif tid.endswith('800'):
        baseTid = '%s000' % tid[:-3]
        updateTid = tid
    elif not tid.endswith('00'):
        baseTid = '%016x' % (int(tid, 16) - 0x1000 & 0xFFFFFFFFFFFFF000)
        updateTid = '%s800' % baseTid[:-3]
    else:
        info = 'Not a valid title'
        return info

    info = '\nName: ' + name + '\n' + 'Titleid: ' + tid + '\n' + 'Versions: ' + ' '.join(
        get_versions(tid)) + '\n' + 'Update Titleid: ' + updateTid + '\n' + 'Versions: ' + ' '.join(
        get_versions(updateTid)) + '\n'

    if not silent:
        print(info)
    return info


def get_versions(tid):
    #url = 'https://tagaya.hac.%s.eshop.nintendo.net/tagaya/hac_versionlist' % env
    url = 'https://superfly.hac.%s.d4c.nintendo.net/v1/t/%s/dv' % (env,tid)
    r = make_request('GET', url)
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

def download_file(url, fPath):
    fName = os.path.basename(fPath).split()[0]

    if os.path.exists(fPath):
        dlded = os.path.getsize(fPath)
        r = make_request('GET', url, hdArgs={'Range': 'bytes=%s-' % dlded})
        
        if r.headers.get('Server') != 'openresty/1.9.7.4':
            print('\t\tDownload is already complete, skipping!')
            return fPath
        elif r.headers.get('Content-Range') == None: # CDN doesn't return a range if request >= filesize
            fSize = int(r.headers.get('Content-Length'))
        else:
            fSize = dlded + int(r.headers.get('Content-Length'))
            
        if dlded == fSize:
            print('\t\tDownload is already complete, skipping!')
            return fPath
        elif dlded < fSize:
            print('\t\tResuming download...')
            f = open(fPath, 'ab')
        else:
            print('\t\tExisting file is bigger than expected (%s/%s), restarting download...' % (dlded, fSize))
            dlded = 0
            f = open(fPath, "wb")
    else:
        dlded = 0
        r = make_request('GET', url)
        fSize = int(r.headers.get('Content-Length'))
        f = open(fPath, 'wb')
        
    chunkSize = 1000
    if tqdmProgBar == True and fSize >= 10000:
        for chunk in tqdm(r.iter_content(chunk_size=chunkSize), initial=dlded//chunkSize, total=fSize//chunkSize,
                          desc=fName, unit='kb', smoothing=1, leave=False):
            f.write(chunk)
            dlded += len(chunk)
    elif fSize >= 10000:
        for chunk in r.iter_content(chunkSize): # https://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
            f.write(chunk)
            dlded += len(chunk)
            done = int(50 * dlded / fSize)
            sys.stdout.write('\r%s:  [%s%s] %d/%d b' % (fName, '=' * done, ' ' * (50-done), dlded, fSize) )    
            sys.stdout.flush()
        sys.stdout.write('\033[F')
    else:
        f.write(r.content)
        dlded += len(r.content)
    
    if fSize != 0 and dlded != fSize:
        raise ValueError('Downloaded data is not as big as expected (%s/%s)!' % (dlded, fSize))
        
    f.close()    
    print('\r\t\tSaved to %s!' % f.name)
    return fPath

def decrypt_NCA(fPath, outDir=''):
    fName = os.path.basename(fPath).split()[0]

    if outDir == '':
        outDir = os.path.splitext(fPath)[0]
    os.makedirs(outDir, exist_ok=True)

    commandLine = hactoolPath + ' "' + fPath + '"' + keysArg \
                  + ' --exefsdir="' + outDir + os.sep + 'exefs"' \
                  + ' --romfsdir="' + outDir + os.sep + 'romfs"' \
                  + ' --section0dir="' + outDir + os.sep + 'section0"' \
                  + ' --section1dir="' + outDir + os.sep + 'section1"' \
                  + ' --section2dir="' + outDir + os.sep + 'section2"' \
                  + ' --section3dir="' + outDir + os.sep + 'section3"' \
                  + ' --header="' + outDir + os.sep + 'Header.bin"'

    try:
        subprocess.check_output(commandLine, shell=True)
        if os.listdir(outDir) == []:
            raise subprocess.CalledProcessError('\nDecryption failed, output folder %s is empty!' % outDir)
    except subprocess.CalledProcessError:
        print('\nDecryption failed!')
        raise

    return outDir


def verify_NCA(ncaFile, titleKey):
    commandLine = hactoolPath + ' "' + ncaFile + '"' + keysArg + ' --titlekey="' + titleKey + '"'

    try:
        output = str(subprocess.check_output(commandLine, stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        return False
    else:
        if "Error: section 0 is corrupted!" in output or "Error: section 1 is corrupted!" in output:
            print("\nNCA Verification failed. Probably a bad titlekey.")
            return False
    print("\nTitlekey verification successful.")
    return True


def get_biggest_file(path):
    try:
        objects = os.listdir(path)
        sofar = 0
        name = ""
        for item in objects:
            size = os.path.getsize(os.path.join(path, item))
            if size > sofar:
                sofar = size
                name = item
        return os.path.join(path, name)
    except Exception as e:
        print(e)


def download_cetk(rightsID, fPath):
    url = 'https://atum.hac.%s.d4c.nintendo.net/r/t/%s?device_id=%s' % (env, rightsID, did)
    r = make_request('HEAD', url)
    id = r.headers.get('X-Nintendo-Content-ID')

    url = 'https://atum.hac.%s.d4c.nintendo.net/c/t/%s?device_id=%s' % (env, id, did)
    cetk = download_file(url, fPath)

    return cetk


def download_title(gameDir, tid, ver, tkey='', nspRepack=False, n='', verify=False):
    print('\n%s v%s:' % (tid, ver))
    tid = tid.lower();
    tkey = tkey.lower();
    if len(tid) != 16:
        tid = (16 - len(tid)) * '0' + tid

    url = 'https://atum%s.hac.%s.d4c.nintendo.net/t/a/%s/%s?device_id=%s' % (n, env, tid, ver, did)
    print(url)
    try:
        r = make_request('HEAD', url)
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
    print(cnmtNCA)
    cnmtDir = decrypt_NCA(cnmtNCA)
    CNMT = cnmt(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]),
                os.path.join(cnmtDir, 'Header.bin'))

    if nspRepack == True:
        outf = os.path.join(gameDir, '%s.xml' % os.path.basename(cnmtNCA.strip('.nca')))
        cnmtXML = CNMT.gen_xml(cnmtNCA, outf)

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
    for type in [0, 3, 4, 5, 1, 2, 6]:  # Download smaller files first
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
        for key in [1, 5, 2, 4, 6]:
            try:
                files.append(NCAs[key])
            except KeyError:
                pass
        files.append(cnmtNCA)
        files.append(cnmtXML)
        try:
            files.append(NCAs[3])
        except KeyError:
            pass

        return files

def download_title_tinfoil(gameDir, tid, ver, tkey='', nspRepack=False, n='', verify=False):
    print('\n%s v%s:' % (tid, ver))
    tid = tid.lower();
    tkey = tkey.lower();
    if len(tid) != 16:
        tid = (16 - len(tid)) * '0' + tid

    url = 'https://atum%s.hac.%s.d4c.nintendo.net/t/a/%s/%s?device_id=%s' % (n, env, tid, ver, did)
    print(url)
    try:
        r = make_request('HEAD', url)
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


def get_tik(tid, ver, tkey='', nspRepack=True, n='n'):
    print('\n%s v%s:' % (tid, ver))
    gameDir = os.path.join(os.path.dirname(__file__), tid)
    tikDir = os.path.join(os.path.dirname(__file__), '_TIKOUT')
    os.makedirs(gameDir, exist_ok=True)
    os.makedirs(tikDir, exist_ok=True)
    tid = tid.lower()
    tkey = tkey.lower()
    if len(tid) != 16:
        tid = (16 - len(tid)) * '0' + tid

    url = 'https://atum%s.hac.%s.d4c.nintendo.net/t/a/%s/%s?device_id=%s' % (n, env, tid, ver, did)
    print(url)
    try:
        r = make_request('HEAD', url)
    except Exception as e:
        print("Error downloading title. Check for incorrect titleid or version.")
        return
    CNMTid = r.headers.get('X-Nintendo-Content-ID')

    print('\nDownloading CNMT (%s.cnmt.nca)...' % CNMTid)
    url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/a/%s?device_id=%s' % (n, env, CNMTid, did)
    fPath = os.path.join(gameDir, CNMTid + '.cnmt.nca')
    cnmtNCA = download_file(url, fPath)
    cnmtDir = decrypt_NCA(cnmtNCA)
    CNMT = cnmt(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]),
                os.path.join(cnmtDir, 'Header.bin'))

    rightsID = '%s%s%s' % (tid, (16 - len(CNMT.mkeyrev)) * '0', CNMT.mkeyrev)
    name = get_name(tid)
    if name != 'Unknown Title':
        tikPath = os.path.join(gameDir, '%s [%s][v%s].tik' % (name, tid, ver))
    else:
        tikPath = os.path.join(gameDir, '%s[v%s].tik' % (tid, ver))

    if CNMT.type == 'Application' or CNMT.type == 'AddOnContent':
        if tkey != '':
            with open(os.path.join(os.path.dirname(__file__), 'Ticket.tik'), 'rb') as intik:
                data = bytearray(intik.read())
                data[0x180:0x190] = uhx(tkey)
                data[0x286] = int(CNMT.mkeyrev)
                data[0x2A0:0x2B0] = uhx(rightsID)

                with open(tikPath, 'wb') as outtik:
                    outtik.write(data)
            print('\nGenerated %s!' % (os.path.basename(tikPath)))
            shutil.copy(tikPath, tikDir)
            shutil.rmtree(gameDir)
            print('cleaned up downloaded content')
        else:
            print("Can't get tik without titlekey")

def get_control_nca(tid, ver, tkey='', n='n'):
    tempDir = '_TEMP'
    os.makedirs(tempDir, exist_ok=True)
    controlDir = '_CONTROLOUT'
    os.makedirs(controlDir, exist_ok=True)
    tid = tid.lower();
    if tkey != '' and tkey != None:
        tkey = tkey.lower();
    if len(tid) != 16:
        tid = (16 - len(tid)) * '0' + tid

    url = 'https://atum%s.hac.%s.d4c.nintendo.net/t/a/%s/%s?device_id=%s' % (n, env, tid, ver, did)
    print(url)
    try:
        r = make_request('HEAD', url)
    except Exception as e:
        print("Error downloading title. Check for incorrect titleid or version.")
        return ''
    CNMTid = r.headers.get('X-Nintendo-Content-ID')

    print('\nDownloading CNMT (%s.cnmt.nca)...' % CNMTid)
    url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/a/%s?device_id=%s' % (n, env, CNMTid, did)
    if CNMTid == None:
        return ''
    fPath = os.path.join(tempDir, CNMTid + '.cnmt.nca')
    cnmtNCA = download_file(url, fPath)
    cnmtDir = decrypt_NCA(cnmtNCA)
    CNMT = cnmt(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]),
                os.path.join(cnmtDir, 'Header.bin'))

    for ncaID in CNMT.parse(CNMT.ncaTypes[3]):
        print('\nDownloading %s entry (%s.nca)...' % (CNMT.ncaTypes[3], ncaID))
        url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/c/%s?device_id=%s' % (n, env, ncaID, did)
        fPath = os.path.join(controlDir, ncaID + '.nca')
        ncaPath = download_file(url, fPath)
        shutil.rmtree(tempDir)
        return ncaPath

def extract_control_nca(ncaFile):
    extractDir = '_NCAEXTRACT'
    command = '%s %s %s --section0dir="%s"' % (hactoolPath,keysArg,ncaFile,extractDir)
    try:
        output = str(subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        return False
    print("\nNCA extraction successful.")
    return extractDir




def get_name_control(tid):
    global quiet
    quiet = True
    basetid = tid
    if tid.endswith('000'):  # Base game
        pass
    elif tid.endswith('800'):  # Update
        basetid = '%s000' % tid[:-3]
    else:  # DLC
        basetid = '%016x' % (int(tid, 16) - 0x1000 & 0xFFFFFFFFFFFFF000)
    name = ''
    tkey = get_titlekey(basetid)
    ver = get_versions(basetid)[-1]
    ncaFile = get_control_nca(basetid,ver,tkey)
    if ncaFile == '':
        return ''
    extractDir = extract_control_nca(ncaFile)
    nacpFile = os.path.join(extractDir,'control.nacp')
    pos = 0
    with open(nacpFile, 'rb') as f:
        wf = TextIOWrapper(f, 'utf-8')
        wf._CHUNK_SIZE = 1  
        while wf.read(1) == '':
            pos = pos + 1
        wf.seek(pos)
        name  = wf.read(100).rstrip(' \t\r\n\0')

    shutil.rmtree(extractDir)
    os.remove(ncaFile)
    quiet = False
    return name.strip()
    
    

def get_titlekey(tid):
    for line in titlekey_list:
        if tid in line:
            return line.split('|')[1].strip()
    return ''

    
def download_game(tid, ver, tkey='', nspRepack=False, name='', verify=False, path_Dir=""):
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

    if tinfoil:
        files = download_title_tinfoil(gameDir, tid, ver, tkey, nspRepack, verify=verify)
    else:
        files = download_title(gameDir, tid, ver, tkey, nspRepack, verify=verify)

    if gameType != 'UPD':
        verified = verify_NCA(get_biggest_file(gameDir), tkey)

        if not verified:
            shutil.rmtree(gameDir)            
            print("Not verifed", gameDir)
            return

    if nspRepack == True:
        if files == None:
            return
        NSP = nsp(outf, files)
        print('\nstarting repack, This may take a while')
        NSP.repack()
        shutil.rmtree(gameDir)
        print('\ncleaned up downloaded content')

        if enxhop:
            enxhopDir = os.path.join(outputDir,'switch')
            os.makedirs(enxhopDir, exist_ok=True)
            with open(os.path.join(enxhopDir,'eNXhop.txt'), 'a+') as f:
                f.write(tid + '\n')

        return outf

    return gameDir

class cnmt:
    def __init__(self, fPath, hdPath):
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

        f = open(fPath, 'rb')

        self.path = fPath
        self.type = self.packTypes[read_u8(f, 0xC)]
        self.id = '0%s' % format(read_u64(f, 0x0), 'x')
        self.ver = str(read_u32(f, 0x8))
        self.sysver = str(read_u64(f, 0x28))
        self.dlsysver = str(read_u64(f, 0x18))
        self.digest = hx(read_at(f, f.seek(0, 2) - 0x20, f.seek(0, 2))).decode()

        with open(hdPath, 'rb') as ncaHd:
            self.mkeyrev = str(read_u8(ncaHd, 0x220))

        f.close()

    def parse(self, ncaType=''):
        f = open(self.path, 'rb')

        data = {}
        if self.type == 'SystemUpdate':
            EntriesNB = read_u16(f, 0x12)
            for n in range(0x20, 0x10 * EntriesNB, 0x10):
                tid = hex(read_u64(f, n))[2:]
                if len(tid) != 16:
                    tid = '%s%s' % ((16 - len(tid)) * '0', tid)
                ver = str(read_u32(f, n + 0x8))
                packType = self.packTypes[read_u8(f, n + 0xC)]

                data[tid] = ver, packType
        else:
            tableOffset = read_u16(f, 0xE)
            contentEntriesNB = read_u16(f, 0x10)
            cmetadata = {}
            for n in range(contentEntriesNB):
                offset = 0x20 + tableOffset + 0x38 * n
                hash = hx(read_at(f, offset, 0x20)).decode()
                tid = hx(read_at(f, offset + 0x20, 0x10)).decode()
                size = str(read_u48(f, offset + 0x30))
                type = self.ncaTypes[read_u16(f, offset + 0x36)]

                if type == ncaType or ncaType == '':
                    data[tid] = type, size, hash

        f.close()
        return data

    def gen_xml(self, ncaPath, outf):
        data = self.parse()
        hdPath = os.path.join(os.path.dirname(ncaPath),
                              '%s.cnmt' % os.path.basename(ncaPath).split('.')[0], 'Header.bin')
        with open(hdPath, 'rb') as ncaHd:
            mKeyRev = str(read_u8(ncaHd, 0x220))

        ContentMeta = ET.Element('ContentMeta')

        ET.SubElement(ContentMeta, 'Type').text = self.type
        ET.SubElement(ContentMeta, 'Id').text = '0x%s' % self.id
        ET.SubElement(ContentMeta, 'Version').text = self.ver
        ET.SubElement(ContentMeta, 'RequiredDownloadSystemVersion').text = self.dlsysver

        n = 1
        for tid in data:
            locals()["Content" + str(n)] = ET.SubElement(ContentMeta, 'Content')
            ET.SubElement(locals()["Content" + str(n)], 'Type').text = data[tid][0]
            ET.SubElement(locals()["Content" + str(n)], 'Id').text = tid
            ET.SubElement(locals()["Content" + str(n)], 'Size').text = data[tid][1]
            ET.SubElement(locals()["Content" + str(n)], 'Hash').text = data[tid][2]
            ET.SubElement(locals()["Content" + str(n)], 'KeyGeneration').text = mKeyRev
            n += 1

        # cnmt.nca itself
        cnmt = ET.SubElement(ContentMeta, 'Content')
        ET.SubElement(cnmt, 'Type').text = 'Meta'
        ET.SubElement(cnmt, 'Id').text = os.path.basename(ncaPath).split('.')[0]
        ET.SubElement(cnmt, 'Size').text = str(os.path.getsize(ncaPath))
        hash = sha256()
        with open(ncaPath, 'rb') as nca:
            hash.update(nca.read())  # Buffer not needed
        ET.SubElement(cnmt, 'Hash').text = hash.hexdigest()
        ET.SubElement(cnmt, 'KeyGeneration').text = mKeyRev

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

    def gen_xml_tinfoil(self, ncaPath, outf):
        data = self.parse()
        hdPath = os.path.join(os.path.dirname(ncaPath),
                              '%s.cnmt' % os.path.basename(ncaPath).split('.')[0], 'Header.bin')
        with open(hdPath, 'rb') as ncaHd:
            mKeyRev = str(read_u8(ncaHd, 0x220))

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
                ET.SubElement(locals()["Content" + str(n)], 'Size').text = data[tid][1]
                ET.SubElement(locals()["Content" + str(n)], 'Hash').text = data[tid][2]
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
        
        hd = self.gen_header()
        
        totSize = len(hd) + sum(os.path.getsize(file) for file in self.files)
        if os.path.exists(self.path) and os.path.getsize(self.path) == totSize:
            print('\t\tRepack %s is already complete!' % self.path)
            return
            
        t = tqdm(total=totSize, unit='B', unit_scale=True, desc=os.path.basename(self.path), leave=False)
        
        t.write('\t\tWriting header...')
        outf = open(self.path, 'wb')
        outf.write(hd)
        t.update(len(hd))
        
        done = 0
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
        
        print('\t\tRepacked to %s!' % outf.name)
        outf.close()

    def gen_header(self):
        filesNb = len(self.files)
        stringTable = '\x00'.join(os.path.basename(file) for file in self.files)
        headerSize = 0x10 + (filesNb)*0x18 + len(stringTable)
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

def load_titlekeys():
    global titlekey_list
    try:
        print('\nloading titlekeys...')
        with open('titlekeys.txt', encoding="utf8") as f:
            lines = f.readlines()
    except Exception as e:
        print("Error:", e)
        print('the -title command will NOT WORK to download games without it')
        return
    try:
        for line in lines:
            titlekey_list.append(line)
        print('\ntitlekeys loaded')
    except Exception as e:
        print('Error: ', e)
        return

def load_titlekeysout():
    global titlekey_list
    try:
        titlekeysOut = os.path.join('titlekeysout','titlekeys.txt')
        if not os.path.isfile(titlekeysOut):
            return
        print('\nloading titlekeys from titlekeysout...')
        with open(titlekeysOut, encoding="utf8") as f:
            lines = f.readlines()
    except Exception as e:
        print("Error:", e)
        return
    try:
        for line in lines:
            split = line.split('|')
            for title in titlekey_list:      
                if title.find(split[0]) != -1:
                    continue
            titlekey_list.append(line)
        print('\ntitlekeys loaded')
    except Exception as e:
        print('Error: ', e)
        return  

def title_in_keylist(tid):
    global titlekey_list
    # temporarily add any new titlekeys to current list
    newKeysFile = os.path.join('titlekeysout','titlekeys.txt')
    if os.path.isfile(newKeysFile):
        with open(newKeysFile, encoding="utf8") as f:
                lines = f.readlines()
                for line in lines:
                    titlekey_list.append(line)
                    # remove any duplicates from the addition
                    titlekey_list = list(set(titlekey_list))
    for title in titlekey_list:
        if title.find(tid) != -1:
            return True
    return False

def read_keys_dump(keysFile):
    print('parsing titlekeys file',keysFile)
    with open(keysFile, encoding="utf8") as f:
        lines = f.readlines()
        pos = 0
        tid = ''
        tkey = ''
        titleList = []
        for line in lines:
            if 'Ticket' in line:
                pos = 1

            elif 'Rights ID' in line:
                pos = 2

            elif pos == 2:
                tid = line.split(': ')[1].strip()
                pos = 3

            elif pos == 3:
                tkey = line.split(': ')[1].strip()
                pos = 0
                name = 'unknown'
                if not tid.endswith('800') and not title_in_keylist(tid):
                    titleList.append(tid + '|' + tkey + '|' + '\n')
        return titleList

def read_keys_list(keysFile):
    titleList = []

    with open(keysFile, encoding="utf8") as f:
        print('parsing titlekeys file',keysFile)
        lines = f.readlines()
        for line in lines:
            split = line.split("|")
            if not split[0].endswith('800') and not title_in_keylist(split[0]):
                tid = split[0]
                tkey = split[1]
                name = split[2]
                titleList.append(tid + '|' + tkey + "|" + name + '\n')
    return titleList

def get_list_type(keysFile):
    with open(keysFile, encoding="utf8") as f:
        lines = f.readlines()
        if lines[0].find('Ticket ') != -1:
            return 'consoledump'
        else:
            return 'titlekeylist'

def process_keys():
    keyList = []
    if os.path.exists('titlekeysin'):
        files = os.listdir('titlekeysin')
        if files == []:
            print("no key fles in input forlder")
            return
        else:
            for keyFile in files:
                keyFile = os.path.join('titlekeysin',keyFile)
                keyType = get_list_type(keyFile)
                if keyType == 'consoledump':
                    keyList = keyList + read_keys_dump(keyFile)
                else:
                    keyList = keyList + read_keys_list(keyFile)
                os.remove(keyFile)
        keyList = list(set(keyList))
        os.makedirs('titlekeysout', exist_ok=True)
        titlekeysout = os.path.join('titlekeysout','titlekeys.txt')
        f = open(titlekeysout, 'a', encoding="utf8")
        print('\ngetting title names...')
        for line in keyList:
            split = line.split('|')
            if split[2].strip() == '':
                name = get_name(split[0])
                if not split[0].endswith('000'):
                    name = '[DLC] ' + name
                line = split[0] + '|' + split[1] + '|' + name + '\n'
            f.write(line)
        f.close()

    else:
        print('No titletitlekeysin folder exists')
        print('Create titletitlekeysin folder and add the correct files')


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
    CNMT = cnmt(os.path.join(cnmtDir, 'section0', os.listdir(os.path.join(cnmtDir, 'section0'))[0]), 
                os.path.join(cnmtDir, 'Header.bin'))
    
    NCAs = {}
    for type in [3]: # Download smaller files first
        for ncaID in CNMT.parse(CNMT.ncaTypes[type]):
            url = 'https://atum%s.hac.%s.d4c.nintendo.net/c/c/%s?device_id=%s' % (n, env, ncaID, did)
            fPath = os.path.join(gameDir, "control" + '.nca')
            NCAs.update({type: download_file(url, fPath)})
            if verify:
                if calc_sha256(fPath) != CNMT.parse(CNMT.ncaTypes[type])[ncaID][2]:
                    pass
                else:
                    pass
    return (gameDir, "N")
  
# End of CDNSP script
# --------------------------
# GUI code begins
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
        print("Check if there's extra spaces at the bottom of your titlekeys.txt file! Delete if you do!")
    if titleID != "":
        titleID_list.append(titleID[:16])
        titleKey_list.append(titleKey)
        if title[:-1] == "\n":
            title_list.append(title[:-1])
        else:
            title_list.append(title)
f.close()


def updateJsonFile(key, value):
    if os.path.isfile("CDNSP-GUI-config.json"):
        with open("CDNSP-GUI-config.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["Options"]["{}".format(key)] = value

        with open("CDNSP-GUI-config.json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
    else:
        print("Error!, Missing CDNSP-GUI-config.json file")

def GUI_config(fPath):
    if sys_locale != "zh_CN":
        main_win = "650x530+100+100"
        queue_win = "620x300+770+100"
    else:
        main_win = "750x550+100+100"
        queue_win = "720x300+770+100"
            
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
                "Update_win": "600x400+120+200"}}

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

    if not os.path.exists(download_location): # If the custom download directory doesn't exist then use default path
        download_location = ""
        updateJsonFile("Download_location", download_location)
    return download_location, game_location, repack, mute, titlekey_check, noaria, \
           disable_game_image, shorten, tinfoil, sysver0, main_win, queue_win, update_win

class Application():

    def __init__(self, root, titleID, titleKey, title, dbURL):

        global main_win
        global queue_win
        global update_win_size
        
        configGUIPath = os.path.join(os.path.dirname(__file__), 'CDNSP-GUI-config.json') # Load config file
        self.path, self.game_location, self.repack, self.mute, self.titlekey_check, noaria_temp, \
                   self.game_image_disable, shorten_temp, tinfoil_temp, sysver0_temp, main_win, \
                   queue_win, update_win = GUI_config(configGUIPath) # Get config values

        
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
        self.downloadMenu.add_command(label="Select Download Location", command=self.change_dl_path)
        self.downloadMenu.add_command(label="Preload Game Images", command=self.preload_images)
        self.downloadMenu.add_separator() # Add separator to the menu dropdown
        self.downloadMenu.add_command(label="Load Saved Queue", command=self.import_persistent_queue)
        self.downloadMenu.add_command(label="Save Queue", command=self.export_persistent_queue)

        # Options Menu Tab
        self.optionMenu = Menu(self.menubar, tearoff=0)
        self.optionMenu.add_command(label="Aria2c will be missed", command=self.disable_aria2c)
        self.optionMenu.add_command(label="DISABLE GAME IMAGE", command=self.disable_game_image)
        
        self.optionMenu.add_separator() # Add separator to the menu dropdown
        
        self.optionMenu.add_command(label="Mute All Pop-ups", command=self.mute_all)
        self.optionMenu.add_command(label="Disable NSP Repack", command=self.nsp_repack_option)
        self.optionMenu.add_command(label="Disable Titlekey check", command=self.titlekey_check_option)
        
        self.optionMenu.add_separator() # Add separator to the menu dropdown
        
        self.optionMenu.add_command(label="Enable Shorten Name", command=self.shorten)
        self.optionMenu.add_command(label="Enable Tinfoil Download", command=self.tinfoil_change)
        self.optionMenu.add_command(label="Enable SysVer 0 Patch", command=self.sysver_zero)
        
        self.optionMenu.add_separator() # Add separator to the menu dropdown
        
        self.optionMenu.add_command(label="Save Windows Location and Size", command=self.window_save)

        
        # Tool Menu Tab
        self.toolMenu = Menu(self.menubar, tearoff=0)
        self.toolMenu.add_command(label="Scan for existing games", command=self.my_game_GUI)
        self.toolMenu.add_command(label="Base64 Decoder", command=self.base_64_GUI)

        # Menubar config
        self.menubar.add_cascade(label="Download", menu=self.downloadMenu)
        self.menubar.add_cascade(label="Options", menu=self.optionMenu)
        self.menubar.add_cascade(label="Tools", menu=self.toolMenu)
        self.root.config(menu=self.menubar)

        # Change Menu Label Based on loaded values
        if self.repack == True:
            self.optionMenu.entryconfig(4, label= "Disable NSP Repack")
        else:
            self.optionMenu.entryconfig(4, label= "Enable NSP Repack")
        if self.mute == True:
            self.optionMenu.entryconfig(3, label= "Unmute All Pop-ups")
        else:
            self.optionMenu.entryconfig(3, label= "Mute All Pop-ups")
        if self.titlekey_check == True:
            self.optionMenu.entryconfig(5, label= "Disable Titlekey check")
        else:
            self.optionMenu.entryconfig(5, label= "Enable Titlekey check")
        if self.game_image_disable == True:
            self.optionMenu.entryconfig(1, label= "ENABLE GAME IMAGE")
        else:
            self.optionMenu.entryconfig(1, label= "DISABLE GAME IMAGE")
        if truncateName == True:
            self.optionMenu.entryconfig(7, label= "Disable Shorten Name")
        else:
            self.optionMenu.entryconfig(7, label= "Enable Shorten Name")
        if tinfoil == True:
            self.optionMenu.entryconfig(8, label= "Disable Tinfoil Download")
        else:
            self.optionMenu.entryconfig(8, label= "Enable Tinfoil Download")
        if sysver0 == True:
            self.optionMenu.entryconfig(9, label= "Disable SysVer 0 Patch")
        else:
            self.optionMenu.entryconfig(9, label= "Enable SysVer 0 Patch")

        # Status Label
        self.status_label = Label(self.root, text="Status:")
        self.status_label.grid(row=0, column=0, columnspan=2, sticky=NS)
        
        # Game selection section
        self.search_var = StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_list(True))

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
        self.tree = ttk.Treeview(columns=("num", "G", "S"), show="headings", selectmode=EXTENDED)
        self.tree.bind('<<TreeviewSelect>>', self.game_info)
        self.tree.heading("num", text="#", command=lambda c="num": self.sortby(self.tree, c, 0))
        self.tree.column("num", width=40)
        self.tree.heading("G", text="Game", command=lambda c="G": self.sortby(self.tree, c, 0))
        self.tree.column("G", width=590)
        self.tree.heading("S", text="State", command=lambda c="S": self.sortby(self.tree, c, 0))
        self.tree.column("S", width=60)
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Info labels
        self.sizeLabel = Label(game_selection_frame, text="Game Image:")
        self.sizeLabel.grid(row=2, column=0, pady=(20, 0), columnspan=2)

        self.update_list()

        self.image = Image.open("blank.jpg")
        self.photo = ImageTk.PhotoImage(self.image)
        self.imageLabel = Label(game_selection_frame, image=self.photo, borderwidth=0, highlightthickness=0, cursor="hand2")
        self.imageLabel.bind("<Button-1>", self.eShop_link)
        self.imageLabel.image = self.photo # keep a reference!
        self.imageLabel.grid(row=3, column=0, sticky=N, pady=0, columnspan=2)

        Label(game_selection_frame, text="Click the game image above \nto open the game in the eShop!").grid(row=4, column=0, pady=10, columnspan=2)

        #-------------------------------------------

        # Game title info section

        game_info_frame = Frame(self.root)
        game_info_frame.grid(row=1, column=1, sticky=N)

        # Demo filter
        self.demo = IntVar()
        Checkbutton(game_info_frame, text="No Demo", \
                    variable=self.demo, command=self.filter_demo)\
                    .grid(row=0, column=0, columnspan=2, pady=(20,0), sticky=NS)
        
        # Title ID info
        self.titleID_label = Label(game_info_frame, text="Title ID:")
        self.titleID_label.grid(row=1, column=0, pady=(20,0), columnspan=2)

        self.game_titleID = StringVar()
        self.gameID_entry = Entry(game_info_frame, textvariable=self.game_titleID)
        self.gameID_entry.grid(row=2, column=0, columnspan=2)

        # Title Key info
        self.titleID_label = Label(game_info_frame, text="Title Key:")
        self.titleID_label.grid(row=3, column=0, pady=(20,0), columnspan=2)

        self.game_titleKey = StringVar()
        self.gameKey_entry = Entry(game_info_frame, textvariable=self.game_titleKey)
        self.gameKey_entry.grid(row=4, column=0, columnspan=2)

        # Select update versions
        self.version_label = Label(game_info_frame, text="Select update version:")
        self.version_label.grid(row=5, column=0, pady=(20,0), columnspan=2)

        self.version_option = StringVar()
        self.version_select = ttk.Combobox(game_info_frame, textvariable=self.version_option, state="readonly", postcommand=self.get_update_ver)
        self.version_select["values"] = ("Latest")
        self.version_select.set("Latest")
        self.version_select.grid(row=6, column=0, columnspan=2)
        
        # Download options
        self.download_label = Label(game_info_frame, text="Download options:")
        self.download_label.grid(row=7, column=0, pady=(20,0), columnspan=2)

        MODES = [
            ("Base game + Update + DLC", "B+U+D"),
            ("Base game + Update", "B+U"),
            ("Update + DLC", "U+D"),
            ("Base game only", "B"),
            ("Update only", "U"),
            ("All DLC", "D")
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
        queue_btn = Button(game_info_frame, text="Add to queue", command=self.add_selected_items_to_queue)
        queue_btn.grid(row=50, column=0, pady=(20,0))
        dl_btn = Button(game_info_frame, text="Download", command=self.download)
        dl_btn.grid(row=50, column=1, pady=(20,0), padx=(5,0))

        update_btn = Button(game_info_frame, text="Update Titlekeys", command=self.update_titlekeys)
        update_btn.grid(row=51, column=0, pady=(20, 0), columnspan=2)

        #-----------------------------------------
        self.queue_menu_setup()
        #-----------------------------------------

        self.load_persistent_queue() # only load the queue once the UI is initialized

    def queue_menu_setup(self):
        # Queue Menu
        global queue_win
        self.queue_win = Toplevel(self.root)
        self.queue_win.title("Queue Menu")
        self.queue_win.geometry(queue_win)
        self.queue_win.withdraw() # Hide queue window, will show later

        # Top Menu bar
        menubar = Menu(self.queue_win)

        # Download Menu Tab
        downloadMenu = Menu(menubar, tearoff=0)
        downloadMenu.add_command(label="Load Saved Queue", command=self.import_persistent_queue)
        downloadMenu.add_command(label="Save Queue", command=self.export_persistent_queue)
        
        # Menubar config
        menubar.add_cascade(label="Download", menu=downloadMenu)
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

        Button(self.queue_win, text="Remove selected game", command=self.remove_selected_items).grid(row=1, column=0, pady=(30,0))
        Button(self.queue_win, text="Remove all", command=self.remove_all_and_dump).grid(row=1, column=1, pady=(30,0))
        Button(self.queue_win, text="Download all", command=self.download_all).grid(row=1, column=2, pady=(30,0))
        self.stateLabel = Label(self.queue_win, text="Click download all to download all games in queue!")
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
            region = ["US", "EU", "GB", "FR", "JP"]
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
            self.root.config(cursor="wait")
            self.imageLabel.config(cursor="wait")
            thread.start()

    def update_list(self, search=False, rebuild=False):
        self.root.config(cursor="wait")
        self.status_label.config(text="Status: Getting game status... Please wait")

        if not os.path.isdir("Config"):
            os.mkdir("Config")
        if not os.path.isfile(r"Config/Current_status.txt"):
            rebuild = True

        if rebuild: # Rebuild current_status.txt file
            print("\nBuilding the current state file... Please wait, this may take some time \
depending on how many games you have.")
            try:
                self.status_label.config(text="Status: Building the current state file... Please wait, this may take some time \
depending on how many games you have.")
            except:
                pass
            updates_tid = []
            installed = []
            new_tid = []
            
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
                    if any(tid_text in tid for tid_text in self.titleID):
                        if tid.endswith("00"):
                            tid = "{}800".format(tid[0:13])
                        latest_ver = get_versions(tid)[-1]
                        if latest_ver == "none":
                            latest_ver = 0
                        else:
                            latest_ver = int(latest_ver)
                        if  latest_ver > int(ver):
                            if tid.endswith("00"):
                                tid = "{}000".format(tid[0:13])
                            updates_tid.append(tid)
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

                if any(list_tid in tid for list_tid in new_tid):
                    state = "New"
                
                if any(list_tid in tid for list_tid in installed):
                    state = "Own"
                
                if any(list_tid in tid for list_tid in updates_tid):
                    state = "Update"
                tree_row = (str(number), game_name, state)
                status_file.write(str(tree_row)+"\n")
                
            status_file.close()
            self.update_list()
            
        elif search:
            search_term = self.search_var.get()
            self.tree.delete(*self.tree.get_children())
            for game_status in self.current_status:
                number = game_status[0].strip()
                game_name = game_status[1].strip()
                state = game_status[2].strip()
                
                tree_row = (number, game_name, state)
                if search_term.lower() in game_name.lower():
                    self.tree.insert('', 'end', values=tree_row)
                    
        else:
            if os.path.isfile(r"Config/Current_status.txt"):
                self.current_status = []
                file = open(r"Config/Current_status.txt", "r", encoding="utf-8")
                for line in file.readlines():
                    if line[-1] == "\n":
                        line = line[:-1]
                    status_list = eval(line)
                    self.current_status.append(status_list)
                self.update_list(search=True)
                file.close()
            else:
                print("Error, Current_status.txt doesn't exist")
                    
        self.tree.yview_moveto(0)
        # Reset the sorting back to default (descending)
        self.tree.heading("num", text="#", command=lambda c="num": self.sortby(self.tree, c, 1))
        self.tree.heading("G", text="Game", command=lambda c="G": self.sortby(self.tree, c, 1))
        self.tree.heading("S", text="State", command=lambda c="S": self.sortby(self.tree, c, 1))

        # Reset cursor status
        self.root.config(cursor="")
        try:
            self.imageLabel.config(cursor="hand2")
        except:
            pass
        self.status_label.config(text="Status: Done!")

##    def update_list(self, search=False):
##        # Set cursor status to waiting 
##        thread = threading.Thread(target = lambda: self.threaded_update_list(search))
##        thread.start()
        
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
##            except:
##                pass
    def game_info(self, evt):
        self.imageLabel.config(image="", text="\n\n\nDownloading game image...")
        thread = threading.Thread(target = lambda: self.threaded_game_info(evt))
        thread.start()

    def threaded_download(self):
        option = self.updateOptions.get()
##        try:
        tid = self.game_titleID.get()
        updateTid = tid
        tkey = self.game_titleKey.get()
        ver = self.version_option.get()
        
        if len(tkey) != 32 and self.titlekey_check:
            self.messages('Error', 'Titlekey %s is not a 32-digits hexadecimal number!' % tkey)                
        elif len(tid) != 16:
            self.messages('Error', 'TitleID %s is not a 16-digits hexadecimal number!' % tid)
        else:
            if self.titlekey_check == False:
                tkey = ""
            if "Latest" in ver:
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
                    self.messages("", "Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress.")
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                    self.messages("", "Download finished!")
                else:
                    self.messages("", "No updates available for the game")
                    
            elif option == "B+U+D":
                base_tid = "{}000".format(tid[0:13])
                self.messages("", "Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress.")
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                if ver != 'none':
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, name="", path_Dir=self.path)
                self.messages("", "Download finished!")

            elif option == "U+D":
                if ver != "none":
                    updateTid = "{}800".format(tid[0:13])
                    self.messages("", "Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress.")
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, name="", path_Dir=self.path)
                self.messages("", "Download finished!")


            elif option == "D":
                self.messages("", "Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress.")
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, name="", path_Dir=self.path)
                self.messages("", "Download finished!")

                
            elif option == "B":
                base_tid = "{}000".format(tid[0:13])
                self.messages("", "Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress.")
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                self.messages("", "Download finished!")
                
            elif option == "B+U":
                base_tid = "{}000".format(tid[0:13])
                self.messages("", "Starting to download! It will take some time, please be patient. You can check the CMD (command prompt) at the back to see your download progress.")
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                if ver != 'none':
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                    self.messages("", "Download finished!")
                else:
                    self.messages("", "No updates available for the game, base game downloaded!")
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
            print("\nYou didn't choose a location to save the file!")
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
            self.remove_all()
            for c, tid, ver, key, option in json.load(f):
                self.add_item_to_queue((tid, ver, key, option), True)
            f.close()
        except:
            print("Persistent queue not found, skipping...")

    def get_index_in_queue(self, item):
        try:
            return self.queue_list.index(item)
        except:
            print("Item not found in queue", item)

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
                self.messages('Error', 'Titlekey %s is not a 32-digits hexadecimal number!' % key)
            elif len(tid) != 16:
                self.messages('Error', 'TitleID %s is not a 16-digits hexadecimal number!' % tid)
            else:
                self.add_item_to_queue((tid, ver, key, option))

        self.dump_persistent_queue()
##        except:
##            messagebox.showerror("Error", "No game selected/entered to add to queue")

    def process_item_versions(self, tid, ver):
        if "Latest" in ver:
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
            if self.first_queue:
                if not Toplevel.winfo_exists(self.queue_win):
                    self.queue_menu_setup() #Fix for app crashing when close the queue menu and re-open
                self.queue_win.update()
                self.queue_win.deiconify()
            try:
                c = self.titleID.index(tid)
                c = self.title[c] # Name of the game
            except:
                print("Name for titleID not found in the list", tid)
                c = "UNKNOWN NAME"

            formatted_tid, formatted_ver = self.process_item_versions(tid, ver)

            if "[DLC]" in c:
                option = "DLC"

            self.queue_title_list.insert("end", "{}---{}---{}".format(c, ver, option))
            self.queue_list.append((formatted_tid, formatted_ver, key, option))
            self.persistent_queue.append((c, tid, ver, key, option))
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
                print("No game selected to remove!")

        self.dump_persistent_queue()

    def remove_item(self, index, dump_queue = False):
        del self.queue_list[index]
        del self.persistent_queue[index]
        self.queue_title_list.delete(index)
        if dump_queue: self.dump_persistent_queue()
        
    def threaded_download_all(self):
        self.messages("", "Download for all your queued games will now begin! You will be informed once all the download has completed, please wait and be patient!")
        self.stateLabel.configure(text = "Downloading games...")
        download_list = self.queue_list.copy()
        for item in download_list:
            tid, ver, tkey, option = item
##            try:
            if option == "U" or option == "DLC":
                if ver != "none":
                    if tid.endswith("00"):
                        tid = "{}800".format(tid[0:13])
                    download_game(tid, ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                else:
                    print("No updates available for titleID: {}".format(tid))
                    
            elif option == "B+U+D":
                base_tid = "{}000".format(tid[0:13])
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                if ver != 'none':
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, name="", path_Dir=self.path)

            elif option == "U+D":
                if ver != "none":
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, name="", path_Dir=self.path)


            elif option == "D":
                DLC_titleID = []
                tid = "{}".format(tid[0:12])
                indices = [i for i, s in enumerate(self.titleID) if tid in s]
                for index in indices:
                    if not self.titleID[index].endswith("00"):
                        DLC_titleID.append(self.titleID[index])
                for DLC_ID in DLC_titleID:
                    DLC_ver = get_versions(DLC_ID)[-1]
                    download_game(DLC_ID, DLC_ver, self.titleKey[self.titleID.index(DLC_ID)], nspRepack=self.repack, name="", path_Dir=self.path)

                
            elif option == "B":
                base_tid = "{}000".format(tid[0:13])
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                
            elif option == "B+U":
                base_tid = "{}000".format(tid[0:13])
                base_ver = get_versions(base_tid)[-1]
                download_game(base_tid, base_ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                if ver != 'none':
                    updateTid = "{}800".format(tid[0:13])
                    download_game(updateTid, ver, tkey, nspRepack=self.repack, name="", path_Dir=self.path)
                else:
                    print("No updates available for titleID: {}, base game downloaded!".format(tid))

            index = self.get_index_in_queue(item)
            self.remove_item(index, True)
##            except:
##                print("Error downloading {}, note: if you're downloading a DLC then different versions of DLC may have different titlekeys".format(tid))
        self.messages("", "Download complete!")
        self.stateLabel["text"] = "Download Complete!"
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
            self.optionMenu.entryconfig(4, label= "Enable NSP Repack")
            self.repack = False
        elif self.repack == False:
            self.optionMenu.entryconfig(4, label= "Disable NSP Repack")
            self.repack = True
        updateJsonFile("NSP_repack", str(self.repack))

    def threaded_update_titlekeys(self):
        self.status_label.config(text="Status: Updating titlekeys")
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
                    # print('There are currently %d titles in titlekeys.txt.\n' % len(currdb))
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
                        update_win.title("Finished update!")
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
                        Label(txt_frm, text="Total of new games added: {}".format(counter)).grid(row=1, column=0)
                        Button(txt_frm, text="Close", width=5, height=2, command=lambda: update_win.destroy()).grid(row=1, column=1)
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
                            self.update_list(rebuild=True)
                        except Exception as e:
                            print(e)
                    else:
                        self.status_label.config(text='Status: Finished update, There were no new games to update!')
                        print('\nStatus: Finished update, There were no new games to update!')
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
                    self.status_label.config(text='Status: Finished update, Database rebuilt from scratch')
                    self.current_status = []
                    self.update_list(rebuild=True)
                except Exception as e:
                    print(e)
        else:
            self.messages("Error", "The database server {} might be down or unavailable".format(self.db_URL))
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
                print("Check if there's extra spaces at the bottom of your titlekeys.txt file! Delete if you do!")
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
        self.update_list(True)
        # self.messages("", "Updated!")
##        except:
##            self.messages("Error", "Too many people accessing the database, or then link is died, or the link is incorrect!")

    def update_titlekeys(self):
        self.root.config(cursor="wait")
        self.imageLabel.config(cursor="wait")
        thread = threading.Thread(target = self.threaded_update_titlekeys)
        thread.start()

    def mute_all(self):
        if self.mute == False:
            self.optionMenu.entryconfig(3, label= "Unmute All Pop-ups")
            self.mute = True
        elif self.mute == True:
            self.optionMenu.entryconfig(3, label= "Mute All Pop-ups")
            self.mute = False
        updateJsonFile("Mute", str(self.mute))

    def messages(self, title, text):
        if self.mute != True:
            messagebox.showinfo(title, text)
        else:
            print("\n{}\n".format(text))

    def titlekey_check_option(self):
        global titlekey_check
        if self.titlekey_check == True:
            self.titlekey_check = False
            titlekey_check = self.titlekey_check
            self.optionMenu.entryconfig(5, label= "Enable Titlekey Check") # Automatically disable repacking as well
            self.repack = False
            self.optionMenu.entryconfig(4, label= "Enable NSP Repack")
        elif self.titlekey_check == False:
            self.titlekey_check = True
            titlekey_check = self.titlekey_check
            self.optionMenu.entryconfig(5, label= "Disable Titlekey Check")
            self.repack = True
            self.optionMenu.entryconfig(4, label= "Disable NSP Repack")
        updateJsonFile("Titlekey_check", str(self.titlekey_check))

    def save_game_in_folder(self):
##        global save_game_folder
##        if save_game_folder == False:
##            save_game_folder = True
##            self.fileMenuItem.entryconfig(5, label= "Disable Saving in Game Name Folder")
##        elif save_game_folder == True:
##            save_game_folder = False
##            self.fileMenuItem.entryconfig(5, label= "Enable Saving in Game Name Folder")
        pass
        
    def disable_aria2c(self):
        pass

    def disable_game_image(self):
        if self.game_image_disable == False:
            self.game_image_disable = True
            self.optionMenu.entryconfig(1, label= "ENABLE GAME IMAGE")
        elif self.game_image_disable == True:
            self.game_image_disable = False
            self.optionMenu.entryconfig(1, label= "DISABLE GAME IMAGE")
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
                        print(result)
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
        print("\nIt took {} seconds for you to get all images!\n".format(end - start))
        self.messages("", "Done getting all game images!")
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
                update_list.insert(0, "Latest")
                self.version_select["values"] = update_list
                self.version_select.set("Latest")
            except:
                print("Failed to get version")
        else:
            print("No TitleID or TitleID not 16 characters!")

    def shorten(self):
        global truncateName
        if truncateName == False:
            truncateName = True
            self.optionMenu.entryconfig(7, label= "Disable Shorten Name")
        elif truncateName == True:
            truncateName = False
            self.optionMenu.entryconfig(7, label= "Enable Shorten Name")
        updateJsonFile("Shorten", str(truncateName))
            
    def tinfoil_change(self):
        global tinfoil
        if tinfoil == False:
            tinfoil = True
            self.optionMenu.entryconfig(8, label= "Disable Tinfoil Download")
        elif tinfoil == True:
            tinfoil = False
            self.optionMenu.entryconfig(8, label= "Enable Tinfoil Download")
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
        except:
            pass
        try:
            if Toplevel.winfo_exists(self.update_window):
                updateJsonFile("Update_win", self.window_info(self.update_window))
        except:
            pass
        self.messages("", "Windows size and position saved!")

    def my_game_GUI(self):
        my_game = Toplevel(self.root)
        self.my_game = my_game
        my_game.title("Search for existing games")
        my_game.geometry("400x100+100+100")
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
        browse_btn = Button(my_game, text="Browse", command=self.my_game_directory)
        browse_btn.grid(row=0, column=1, padx=10, pady=10)
        scan_btn = Button(my_game, text="Scan", command=self.my_game_scan)
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
            self.messages("Error", "You didn't choose a directory!")
            self.my_game.lift()
        elif not os.path.isdir(a_dir):
            self.messages("Error", "The chosen directory doesn't exist!")
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
                title = re.search(r".*[0-9a-zA-Z]{16}.*[.nsp]", game)
                if title:
                    try:
                        tid_check = re.compile(r"[\[][0-9a-zA-Z]{16}[\]]")
                        tid_result = tid_check.findall(game)[0]
                        tid_result = tid_result[1:-1]
                        if tid_result.endswith("800"):
                            tid_result = "{}000".format(tid_result[:13])
                    except:
                        tid_result = "0"
                    
                    try:
                        ver_check = re.compile(r"[\[][v][0-9]+[\]]")
                        ver_result = ver_check.findall(game)[0]
                        ver_result = ver_result[1:-1].split("v")[1]
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
            self.messages("", "Finished scanning your games!")
            self.status_label.config(text="Status: Building the current state file... Please wait, this may take some time depending on how many games you have.")
            self.my_game.lift()
            self.my_game.destroy()
            self.update_list(rebuild=True)
            
    def base_64_GUI(self):
        base_64 = Toplevel(self.root)
        self.base_64 = base_64
        base_64.title("Base64 Decoder")
        base_64.geometry("470x100+100+100")
        entry_w = 50
        if sys_name == "Mac":
            entry_w = 28
        base_64_label = Label(base_64, text="Base64 text:")
        base_64_label.grid(row=0, column=0)
        base_64_entry = Entry(base_64, width=entry_w)
        self.base_64_entry = base_64_entry
        base_64_entry.grid(row=0, column=1, padx=(10,0), pady=10)
        browse_btn = Button(base_64, text="Decode", command=self.decode_64)
        browse_btn.grid(row=0, column=2, padx=10, pady=10)

        decoded_label = Label(base_64, text="Decoded text:")
        decoded_label.grid(row=1, column=0)
        decoded_entry = Entry(base_64, width=entry_w)
        self.decoded_entry = decoded_entry
        decoded_entry.grid(row=1, column=1, padx=(10,0), pady=10)
        scan_btn = Button(base_64, text="Open", command=self.base64_open)
        scan_btn.grid(row=1, column=2, sticky=N, padx=10, pady=10)

    def decode_64(self):
        base64_text = self.base_64_entry.get()
        self.decoded_entry.delete(0, END)
        self.decoded_entry.insert(0, base64.b64decode(base64_text))

    def base64_open(self):
        url = self.decoded_entry.get()
        webbrowser.open(url, new=0, autoraise=True)

    def filter_demo(self):
        demo_off = self.demo.get()
        if demo_off:
            self.full_list = self.current_status
            no_demo_list = []
            for game in self.current_status:
                if not "demo" in game[1].strip().lower():
                    no_demo_list.append(game)
            self.current_status = no_demo_list
            search_term = ""
            self.tree.delete(*self.tree.get_children())
            for game_status in self.current_status:
                number = game_status[0].strip()
                game_name = game_status[1].strip()
                state = game_status[2].strip()
                
                tree_row = (number, game_name, state)
                if search_term.lower() in game_name.lower():
                    self.tree.insert('', 'end', values=tree_row)
        else:
            self.current_status = self.full_list
            search_term = ""
            self.tree.delete(*self.tree.get_children())
            for game_status in self.current_status:
                number = game_status[0].strip()
                game_name = game_status[1].strip()
                state = game_status[2].strip()
                
                tree_row = (number, game_name, state)
                if search_term.lower() in game_name.lower():
                    self.tree.insert('', 'end', values=tree_row)
                    
    def sysver_zero(self):
        global sysver0
        if sysver0 == False:
            sysver0 = True
            self.optionMenu.entryconfig(9, label= "Disable SysVer 0 Patch")
        elif sysver0 == True:
            sysver0 = False
            self.optionMenu.entryconfig(9, label= "Enable SysVer 0 Patch")
        updateJsonFile("SysVerZero", str(sysver0))

# ------------------------
# Main Section

if __name__ == '__main__':
    urllib3.disable_warnings()       
    configPath = os.path.join(os.path.dirname(__file__), 'CDNSPconfig.json')
    hactoolPath, keysPath, NXclientPath, ShopNPath, reg, fw, did, env, dbURL, nspout = load_config(configPath)
    
    spam_spec = util.find_spec("tqdm")
    found = spam_spec is not None
    if found:
        tqdmProgBar = True
    else:
        tqdmProgBar = False
        print('Install the tqdm library for better-looking progress bars! (pip install tqdm)')
    if keysPath != '':
        keysArg = ' -k "%s"' % keysPath
    else:
        keysArg = ''
    root = Tk()
    root.title("CDNSP GUI - Bobv4")
    Application(root, titleID_list, titleKey_list, title_list, dbURL)

    root.mainloop()
