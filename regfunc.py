#!/usr/bin/env python
#coding=utf-8 

import os,sys,ctypes,win32con,winnt,win32api,struct,win32file,pywintypes
import _winreg
import binascii
import re

regDict = {
    'HKEY_CLASSES_ROOT': _winreg.HKEY_CLASSES_ROOT,
    'HKEY_CURRENT_USER': _winreg.HKEY_CURRENT_USER,
    'HKEY_LOCAL_MACHINE': _winreg.HKEY_LOCAL_MACHINE,
    'HKEY_USERS': _winreg.HKEY_USERS,
    'HKEY_CURRENT_CONFIG': _winreg.HKEY_CURRENT_CONFIG,
    'HKCR': _winreg.HKEY_CLASSES_ROOT,
    'HKCU': _winreg.HKEY_CURRENT_USER,
    'HKLM': _winreg.HKEY_LOCAL_MACHINE,
    
    'REG_BINARY': _winreg.REG_BINARY,
    'REG_DWORD': _winreg.REG_DWORD,
    'REG_DWORD_LITTLE_ENDIAN': _winreg.REG_DWORD_LITTLE_ENDIAN,
    'REG_DWORD_BIG_ENDIAN': _winreg.REG_DWORD_BIG_ENDIAN,
    'REG_EXPAND_SZ': _winreg.REG_EXPAND_SZ,
    'REG_LINK': _winreg.REG_LINK,
    'REG_MULTI_SZ': _winreg.REG_MULTI_SZ,
    'REG_NONE': _winreg.REG_NONE,
    'REG_SZ': _winreg.REG_SZ,
    'REG_RESOURCE_LIST': _winreg.REG_RESOURCE_LIST,
    'REG_FULL_RESOURCE_DESCRIPTOR': _winreg.REG_FULL_RESOURCE_DESCRIPTOR,
    'REG_RESOURCE_REQUIREMENTS_LIST': _winreg.REG_RESOURCE_REQUIREMENTS_LIST,
    ##'REG_QWORD'��'REG_QWORD_LITTLE_ENDIAN'��������֧��py2.7_winreg
    
    '1': 'REG_SZ',
    '2': 'REG_EXPAND_SZ',
    '3': 'REG_BINARY',
    '4': 'REG_DWORD',
    '7': 'REG_MULTI_SZ',
    '11': 'REG_QWORD',
    }

#��ȡע�����������
def enumregkeys(regpath):
    root=regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.OpenKey(regDict[root],path)
    subkeys=[]
    try:
        i = 0
        while 1:
    #EnumValue��������ö�ټ�ֵ��EnumKey����ö���Ӽ�
            subkeys.append(_winreg.EnumKey(keyHandle, i))
            i +=1
    except WindowsError:
        pass
    return root,path,subkeys
# print enumregkeys("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem")

#ɾ��ע�����
def delregkey(regpath):
    root,path,subkeys=enumregkeys(regpath)
    keyHandle = _winreg.CreateKey(regDict[root],path)
    for i in subkeys:
        _winreg.DeleteKey(keyHandle, i)
        
    selfName = regpath.split('\\')[len(regpath.split('\\'))-1]
    selfPath = '\\'.join(regpath.split('\\')[1:len(regpath.split('\\'))-1]) 
    selfHandle = _winreg.CreateKey(regDict[root],selfPath)
    _winreg.DeleteKey(selfHandle, selfName)
# delregkey("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem\Mynewsubitem")

#ɾ��ע���ֵ
def delregvalue(regpath,keyname):
    root=regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.CreateKey(regDict[root],path)
    _winreg.DeleteValue(keyHandle, keyname)
# delregvalue("HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem\Mynewsubitem","MyNewkey")
    
#��ע����������
def addregitem(regpath,keyname):
    root=regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.OpenKey(regDict[root],path)
    _winreg.CreateKey(keyHandle,keyname)
# addregitem("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer","MyNewitem")

#��ע��������Ӽ���ֵ������Ԥ�ȴ�����
def addregvalue(regpath,key_name,key_type,value,reserved='1'):
    keytype=key_type.upper()
    root=regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.CreateKey(regDict[root],path)    
    ret = _winreg.SetValueEx(keyHandle,key_name,reserved,regDict[keytype],value)##_winreg.SetValueEx(key, value_name, reserved, type, value),reserved��һ�������ֶΣ�ֵ����
# addregvalue("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem",'testkey',"REG_SZ",'dasdadadadasdadasds')

#����ע������Ĭ��ֵ������Ԥ�ȴ�����
def setitemdefaultvalue(regpath,key_type,value):
    key = regpath.split('\\')[len(regpath.split('\\'))-1]
    keytype = key_type.upper()
    root = regpath.split('\\')[0].upper()
    path = '\\'.join(regpath.split('\\')[1:len(regpath.split('\\'))-1]) 
    keyHandle = _winreg.CreateKey(regDict[root],path)    
    ret = _winreg.SetValue(keyHandle,key,regDict[keytype],value)##_winreg.SetValue(key, sub_key, type, value),type���������ֵ�
# setItemdefaultvalue("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem","REG_SZ",'11111111111')

#��ȡע������ֵ��ֵ����
def getkeyvalue(regpath, key):
    root = regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.OpenKey(regDict[root],path)
    value, type = _winreg.QueryValueEx(keyHandle, key)
    return value,regDict[str(type)]
    
#�ж�ע�����Ƿ����
# try:
    # getKeyValue("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem",'test6')
# except WindowsError,info:
    # if info[0]==2:
        # print 'key not exit'
        
#�ж�ע������Ƿ����
# try:
    # enumregkeys("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem2")
# except WindowsError,info:
    # if info[0]==2:
        # print 'item not exit'

#��ȡע������Ĭ��ֵ
def getitemdefaultvalue(regpath):
    key = regpath.split('\\')[len(regpath.split('\\'))-1]
    root = regpath.split('\\')[0].upper()
    path = '\\'.join(regpath.split('\\')[1:len(regpath.split('\\'))-1])
    keyHandle = _winreg.OpenKey(regDict[root],path)
    return _winreg.QueryValue(keyHandle, key)
# getItemDefaultValue("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem")

#����ע����ļ�
def importregfile(regFile):    
    cmd = r'REG IMPORT "%s" 1> NUL 2> NUL '%(regFile)
    os.system(cmd)
    if os.system(cmd) != 0:
        raise Exception('����ע���ļ�ʧ��:"%s"' % regFile)
# importRegFile("c:\\2.reg")

#����ע���������ļ�
def backupregbinfile(regpath, backupFileName):
    cmd = r'REG SAVE %s "%s" /y 1> NUL 2> NUL' % (regpath, backupFileName)
    if os.system(cmd) != 0:
        raise Exception('����ע����ʧ�ܣ�%s' % regpath)
# backupKey("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem","c:\\1.reg")

#����ע���������ļ�
def restoreregbinfile(regpath, backupFileName):
    selfName = regpath.split('\\')[len(regpath.split('\\'))-1]
    selfPath = '\\'.join(regpath.split('\\')[0:len(regpath.split('\\'))-1])
    addregitem(selfPath,selfName)
    cmd = r'REG RESTORE %s "%s" 1> NUL 2> NUL' % (regpath, backupFileName)
    if os.system(cmd) != 0:
        raise Exception('�ָ�ע����ʧ�ܣ�%s' % regpath)
# restoreKey("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem","c:\\1.reg")