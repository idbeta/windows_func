#!/usr/bin/env python
#coding=utf-8 

import os,sys,ctypes,win32con,winnt,win32api,struct,win32file,pywintypes
import traceback
import binascii
import re


##删除文件或文件夹
def delfileordir(filePath):
    '''delete files and folders'''
    if os.path.isfile(filePath):
        try:
            os.remove(filePath)
        except:
            pass
    elif os.path.isdir(filePath):
        for item in os.listdir(filePath):
            itemsrc=os.path.join(filePath,item)
            deletefilefolder(itemsrc) 
        try:
            os.rmdir(filePath)
        except:
            pass
##获取文件属性
def getFileAttributes(filePath): 
    iFileAttr = win32api.GetFileAttributes(filePath)
    _str = ''
    attr_map = {'FILE_ATTRIBUTE_READONLY':0x01,
                'FILE_ATTRIBUTE_HIDDEN':0x02,
                'FILE_ATTRIBUTE_COMPRESSED':0x800,
                'FILE_ATTRIBUTE_DIRECTORY':0x10,
                'FILE_ATTRIBUTE_ENCRYPTED':0x4000,
                'FILE_ATTRIBUTE_NORMAL':0x80,
                'FILE_ATTRIBUTE_ARCHIVE':0x20,
                'FILE_ATTRIBUTE_SYSTEM':0x4,
                'FILE_ATTRIBUTE_TEMPORARY':0x100,
                'FILE_ATTRIBUTE_DEVICE':0x40,
                'FILE_ATTRIBUTE_NOT_CONTENT_INDEXED':0x2000,
                'FILE_ATTRIBUTE_OFFLINE':0x1000,
                'FILE_ATTRIBUTE_REPARSE_POINT':0x400,
                'FILE_ATTRIBUTE_SPARSE_FILE':0x200,
                'FILE_ATTRIBUTE_VIRTUAL':0x10000}
    for key in attr_map.keys():
        if iFileAttr & attr_map[key]:
            if _str:
                _str += '|%s'%(key)
            else:
                _str += '%s'%(key)
    return _str

##设置文件属性
def setFileAttributes(filePath,Attributes):
    attr_map = {'FILE_ATTRIBUTE_READONLY':win32con.FILE_ATTRIBUTE_READONLY,
                'FILE_ATTRIBUTE_HIDDEN':win32con.FILE_ATTRIBUTE_HIDDEN,
                'FILE_ATTRIBUTE_COMPRESSED':win32con.FILE_ATTRIBUTE_COMPRESSED,
                'FILE_ATTRIBUTE_DIRECTORY':win32con.FILE_ATTRIBUTE_DIRECTORY,
                'FILE_ATTRIBUTE_ENCRYPTED':win32con.FILE_ATTRIBUTE_ENCRYPTED,
                'FILE_ATTRIBUTE_NORMAL':win32con.FILE_ATTRIBUTE_NORMAL,
                'FILE_ATTRIBUTE_ARCHIVE':win32con.FILE_ATTRIBUTE_ARCHIVE,
                'FILE_ATTRIBUTE_SYSTEM':win32con.FILE_ATTRIBUTE_SYSTEM,
                'FILE_ATTRIBUTE_TEMPORARY':win32con.FILE_ATTRIBUTE_TEMPORARY,
                'FILE_ATTRIBUTE_DEVICE':win32con.FILE_ATTRIBUTE_DEVICE,
                'FILE_ATTRIBUTE_NOT_CONTENT_INDEXED':win32con.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED,
                'FILE_ATTRIBUTE_OFFLINE':win32con.FILE_ATTRIBUTE_OFFLINE,
                'FILE_ATTRIBUTE_REPARSE_POINT':win32con.FILE_ATTRIBUTE_REPARSE_POINT,
                'FILE_ATTRIBUTE_SPARSE_FILE':win32con.FILE_ATTRIBUTE_SPARSE_FILE,
                'FILE_ATTRIBUTE_VIRTUAL':win32con.FILE_ATTRIBUTE_VIRTUAL}
    for key in attr_map.keys():
        if key==Attributes:
            win32api.SetFileAttributes(filePath,attr_map[Attributes])
    #to force deletion of a file set it to normal
    # win32api.SetFileAttributes(file, win32con.FILE_ATTRIBUTE_NORMAL)
    # os.remove(file) 
    
##锁文件、解锁文件用locket
    
# 3、遍历文件夹
# 4、搜索文件
# 5、获取文件信息
# 6、新建文件
# 7、写文件
# 8、锁定、解锁文件
# 9、创建任意大小PE文件
# 10、修改PE文件