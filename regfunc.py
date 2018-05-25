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
    ##'REG_QWORD'、'REG_QWORD_LITTLE_ENDIAN'这两个不支持py2.7_winreg
    
    '1': 'REG_SZ',
    '2': 'REG_EXPAND_SZ',
    '3': 'REG_BINARY',
    '4': 'REG_DWORD',
    '7': 'REG_MULTI_SZ',
    '11': 'REG_QWORD',
    }

#获取注册表所有子项
def enumregkeys(regpath):
    root=regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.OpenKey(regDict[root],path)
    subkeys=[]
    try:
        i = 0
        while 1:
    #EnumValue方法用来枚举键值，EnumKey用来枚举子键
            subkeys.append(_winreg.EnumKey(keyHandle, i))
            i +=1
    except WindowsError:
        pass
    return root,path,subkeys
# print enumregkeys("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem")

#删除注册表项
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

#删除注册表值
def delregvalue(regpath,keyname):
    root=regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.CreateKey(regDict[root],path)
    _winreg.DeleteValue(keyHandle, keyname)
# delregvalue("HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem\Mynewsubitem","MyNewkey")
    
#向注册表中添加项
def addregitem(regpath,keyname):
    root=regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.OpenKey(regDict[root],path)
    _winreg.CreateKey(keyHandle,keyname)
# addregitem("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer","MyNewitem")

#向注册表中增加键和值，无需预先创建项
def addregvalue(regpath,key_name,key_type,value,reserved='1'):
    keytype=key_type.upper()
    root=regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.CreateKey(regDict[root],path)    
    ret = _winreg.SetValueEx(keyHandle,key_name,reserved,regDict[keytype],value)##_winreg.SetValueEx(key, value_name, reserved, type, value),reserved是一个保留字段，值随意
# addregvalue("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem",'testkey',"REG_SZ",'dasdadadadasdadasds')

#设置注册表项的默认值，无需预先创建项
def setitemdefaultvalue(regpath,key_type,value):
    key = regpath.split('\\')[len(regpath.split('\\'))-1]
    keytype = key_type.upper()
    root = regpath.split('\\')[0].upper()
    path = '\\'.join(regpath.split('\\')[1:len(regpath.split('\\'))-1]) 
    keyHandle = _winreg.CreateKey(regDict[root],path)    
    ret = _winreg.SetValue(keyHandle,key,regDict[keytype],value)##_winreg.SetValue(key, sub_key, type, value),type可以用数字的
# setItemdefaultvalue("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem","REG_SZ",'11111111111')

#获取注册表键的值和值类型
def getkeyvalue(regpath, key):
    root = regpath.split('\\')[0].upper()
    path= '\\'.join(regpath.split('\\')[1:]) 
    keyHandle = _winreg.OpenKey(regDict[root],path)
    value, type = _winreg.QueryValueEx(keyHandle, key)
    return value,regDict[str(type)]
    
#判断注册表键是否存在
# try:
    # getKeyValue("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem",'test6')
# except WindowsError,info:
    # if info[0]==2:
        # print 'key not exit'
        
#判断注册表项是否存在
# try:
    # enumregkeys("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem2")
# except WindowsError,info:
    # if info[0]==2:
        # print 'item not exit'

#获取注册表项的默认值
def getitemdefaultvalue(regpath):
    key = regpath.split('\\')[len(regpath.split('\\'))-1]
    root = regpath.split('\\')[0].upper()
    path = '\\'.join(regpath.split('\\')[1:len(regpath.split('\\'))-1])
    keyHandle = _winreg.OpenKey(regDict[root],path)
    return _winreg.QueryValue(keyHandle, key)
# getItemDefaultValue("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem")

#导入注册表文件
def importregfile(regFile):    
    cmd = r'REG IMPORT "%s" 1> NUL 2> NUL '%(regFile)
    os.system(cmd)
    if os.system(cmd) != 0:
        raise Exception('导入注册文件失败:"%s"' % regFile)
# importRegFile("c:\\2.reg")

#导出注册表二进制文件
def backupregbinfile(regpath, backupFileName):
    cmd = r'REG SAVE %s "%s" /y 1> NUL 2> NUL' % (regpath, backupFileName)
    if os.system(cmd) != 0:
        raise Exception('备份注册表键失败！%s' % regpath)
# backupKey("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem","c:\\1.reg")

#导入注册表二进制文件
def restoreregbinfile(regpath, backupFileName):
    selfName = regpath.split('\\')[len(regpath.split('\\'))-1]
    selfPath = '\\'.join(regpath.split('\\')[0:len(regpath.split('\\'))-1])
    addregitem(selfPath,selfName)
    cmd = r'REG RESTORE %s "%s" 1> NUL 2> NUL' % (regpath, backupFileName)
    if os.system(cmd) != 0:
        raise Exception('恢复注册表键失败！%s' % regpath)
# restoreKey("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MyNewitem","c:\\1.reg")