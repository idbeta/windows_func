#!/usr/bin/env python
#coding=utf-8 

import os,sys
import socket,uuid
import binascii
import netifaces
import re
from psutil import net_if_addrs
import ctypes
def cur_file_dir():
    return os.path.split(os.path.realpath(__file__))[0]
    
def getlocalIP():
    return socket.gethostbyname_ex(socket.gethostname())[2]

def getlocalMAC():
    #方法一不支持多网卡
    # mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    # return ":".join([mac[i:i+2] for i in range(0,11,2)])
    #方法二支持多网卡
    macs=[]
    for k, v in net_if_addrs().items():
        for item in v:
            address = item[1]
            if '-' in address and len(address)==17:
                macs.append(address)
    return macs
    
def getlocalNAME():
    return socket.gethostbyname_ex(socket.gethostname())[0]
    
def getlocalGateway():
    #方法一
    # return netifaces.gateways()['default'][netifaces.AF_INET][0] 
    #方法二
    getways=[]
    for i in netifaces.gateways()[2]:
        getways.append(i[0])
    return getways
    
def getlocalDNS():
    getdns=ctypes.WinDLL(cur_file_dir()+r'\getlocaldns.dll')
    getlocaldns2=getdns.getlocaldns2
    buff_size = 256
    out = ctypes.create_string_buffer(buff_size)
    size = ctypes.c_int(buff_size)
    getlocaldns2(out, size)
    return out.value
# print getlocalDNS()
