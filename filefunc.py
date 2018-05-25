#!/usr/bin/env python
#coding=utf-8 

import os,sys,ctypes,win32con,winnt,win32api,struct,win32file,pywintypes
import traceback
import binascii
import re
from win32com.shell import shell
from win32com.shell import shellcon

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
            
#得到正常路径
#参数:
#   path: 路径，其中可以包含系统环境变量，如%appdata%等
def getNormalPath(path): 
    '''
    替换路径中的环境变量为正常路径
    '''
    tmpPath = os.path.expandvars(path)
    if os.path.exists(tmpPath):
        tmpPath = win32api.GetLongPathName(tmpPath)
    return tmpPath
    
##获取文件属性
def getFileAttributes(filePath): 
    iFileAttr = win32api.GetFileAttributes(filePath)
    print iFileAttr 
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
        # print iFileAttr & attr_map[key] # & 按位与运算符：按位运算符是把数字看作二进制来进行计算的。参与运算的两个值,如果两个相应位都为1,则该位的结果为1,否则为0
        if iFileAttr & attr_map[key]:
            if _str:
                _str += '|%s'%(key)
            else:
                _str += '%s'%(key)
    return _str
# print getFileAttributes(r"E:\Dropbox\360\code\python\case\file_test\file_time.py")
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
    
def isFileHidden(path): 
    #name:
    path = getNormalPath(path)
    return win32api.GetFileAttributes(path) & 2 == 2

def hideFile(path, hidden = True): 
    #name:
    if hidden:
        setFileAttribute(path, '+h')
    else:
        setFileAttribute(path, '-h')
##锁文件、解锁文件用locket
    
# 3、遍历文件夹
# 4、搜索文件
# 5、获取文件信息
# 6、新建文件
# 7、写文件
# 8、锁定、解锁文件
# 9、创建任意大小PE文件
# 10、修改PE文件
def __get_special_path(ptype):        
    idList = shell.SHGetSpecialFolderLocation(0, ptype)
    return shell.SHGetPathFromIDList(idList)

def __getPath__(path, fileName = None):    
    if fileName:        
        fileName = os.path.basename(fileName)
        return os.path.join(path, fileName)
    return path

def GetCookiesPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COOKIES), fileName)

def GetLocalApp(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_LOCAL_APPDATA), fileName)

def GetTempPath(fileName=None):
    if fileName:
        return os.path.join(win32api.GetLongPathName(os.environ['TMP']), fileName)
    else:
        return win32api.GetLongPathName(os.environ['TMP'])

def GetWindowsTempPath(fileName=None):
    if fileName:return os.path.join(win32api.GetLongPathName(os.environ['SYSTEMROOT']), 'Temp', fileName)
    else:return os.path.join(win32api.GetLongPathName(os.environ['SYSTEMROOT']), 'Temp')

def GetPublicPath(fileName = None):
    publicPath = os.path.join(os.environ['HOMEDRIVE'], r'\Users\Public')
    if fileName:
        return os.path.join(publicPath, fileName)
    else:
        return publicPath

def GetCommonApp(fileName=None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COMMON_APPDATA), fileName)

def GetCommonPrograms(fileName=None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COMMON_PROGRAMS), fileName)

def GetDesktopPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_DESKTOP), fileName)

def GetStartMenuPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_STARTMENU), fileName)

def GetCommonStartMenuPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COMMON_STARTMENU), fileName)

def GetFavoritePath(fileName = None):    
    return __getPath__(__get_special_path(shellcon.CSIDL_FAVORITES), fileName)

def GetPersonalPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_PERSONAL), fileName)

def GetProfilePath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_PROFILE), fileName)

def GetLocalLowPath(fileName = None):
    if fileName:
        return os.path.join(GetProfilePath(), 'AppData\LocalLow', fileName)
    else:
        return os.path.join(GetProfilePath(), 'AppData\LocalLow')

def GetDesktopDirectoryPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_DESKTOPDIRECTORY), fileName)

def GetCommonDesktopDirectoryPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COMMON_DESKTOPDIRECTORY), fileName)

def GetFontsPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_FONTS), fileName)

def GetProGramsPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_PROGRAMS), fileName)

def GetAppData(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_APPDATA), fileName)
    
def GetInternetCachePath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_INTERNET_CACHE), fileName)
    
def GetQuickLaunchPath(fileName = None):
    path = os.path.join(GetAppData(),'Microsoft\Internet Explorer\Quick Launch')    
    if fileName:
        fileName = os.path.basename(fileName)
        return os.path.join(path, fileName)
    return path
       
def createFolder(path):
    path = getNormalPath(path)
    try:
        if os.path.exists(path):
            return False
        os.makedirs(path)        
        return path
    except:
        return False
    return True
    
def createDesktopFolder(folderName):
    return createFolder(os.path.join(GetDesktopPath(), folderName))

def createStartMenuFolder(folderName):
    return createFolder(os.path.join(GetStartMenuPath(), folderName))

def createFavoritesFolder(folderName):
    return createFolder(os.path.join(GetFavoritePath(), folderName))

def createProgramsFolder(folderName):
    return createFolder(os.path.join(GetProGramsPath(), folderName))

def createQuickLaunchFolder(folderName):
    return createFolder(os.path.join(GetQuickLaunchPath(), folderName))

extEnviron = os.environ
# print extEnviron
if not extEnviron.has_key('PUBLIC'):
    extEnviron['PUBLIC'] = GetPublicPath()
if not extEnviron.has_key('DESKTOPDIRECTORY'):
    extEnviron['DESKTOPDIRECTORY'] = GetDesktopDirectoryPath()
if not extEnviron.has_key('COMMON_DESKTOPDIRECTORY'):
    extEnviron['COMMON_DESKTOPDIRECTORY'] = GetCommonDesktopDirectoryPath()
if not extEnviron.has_key('INTERNET_CACHE'):
    extEnviron['INTERNET_CACHE'] = GetInternetCachePath()
if not extEnviron.has_key('WINDOWS'):
    extEnviron['WINDOWS'] = extEnviron['SYSTEMROOT']
if not extEnviron.has_key('SYSTEM'):
    extEnviron['SYSTEM'] = os.path.join(extEnviron['SYSTEMROOT'], 'system32')
if not extEnviron.has_key('DESKTOP'):
    extEnviron['DESKTOP'] = GetDesktopPath()
if not extEnviron.has_key('STARTMENU'):
    extEnviron['STARTMENU'] = GetStartMenuPath()
if not extEnviron.has_key('COMMON_STARTMENU'):
    extEnviron['COMMON_STARTMENU'] = GetCommonStartMenuPath()
if not extEnviron.has_key('FAVORITES'):
    extEnviron['FAVORITES'] = GetFavoritePath()
if not extEnviron.has_key('PERSONAL'):
    extEnviron['PERSONAL']  = GetPersonalPath()
if not extEnviron.has_key('FONTS'):
    extEnviron['FONTS']     = GetFontsPath()
if not extEnviron.has_key('PROGRAMS'):
    extEnviron['PROGRAMS']  = GetProGramsPath()
if not extEnviron.has_key('QUICKLAUNCH'):
    extEnviron['QUICKLAUNCH']  = GetQuickLaunchPath()
if not extEnviron.has_key('REPAIRBAK'):
    extEnviron['REPAIRBAK'] = r'%appdata%\repairbak'
if not extEnviron.has_key('COMMON_APPDATA'):
    extEnviron['COMMON_APPDATA'] = GetCommonApp()
if not extEnviron.has_key('LOCAL_APPDATA'):
    extEnviron['LOCAL_APPDATA'] = GetLocalApp()
if not extEnviron.has_key('TEMP'):
    extEnviron['TEMP'] = GetTempPath()
if not extEnviron.has_key('WINDOWSTEMP'):
    extEnviron['WINDOWSTEMP'] = GetWindowsTempPath()
if not extEnviron.has_key('COOKIES'):
    extEnviron['COOKIES'] = GetCookiesPath()
if not extEnviron.has_key('PROFILE'):
    extEnviron['PROFILE'] = GetProfilePath()
if not extEnviron.has_key('LOCALLOWAPPDATA'):
    extEnviron['LOCALLOWAPPDATA'] = GetLocalLowPath()
if not extEnviron.has_key('COMMON_PROGRAMS'):
    extEnviron['COMMON_PROGRAMS'] = GetCommonPrograms()

#创建正常格式的url快捷方式
import pythoncom
def createUrl(url, path, name): 
    #name:
    shortcut = pythoncom.CoCreateInstance(shell.CLSID_InternetShortcut,
                                          None,
                                          pythoncom.CLSCTX_INPROC_SERVER,
                                          shell.IID_IUniformResourceLocator)
    shortcut.SetURL(url)
    if os.path.splitext(name)[-1] != '.url':
        name += '.url'

    path = getNormalPath(path)
    name = getNormalPath(name)
    path = os.path.join(path, name)
    try:
        if not os.path.exists(os.path.dirname(path)):
            createFolder(os.path.dirname(path))
        shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(path, 0)        
        return path
    except:
        return False
    return True

def createDesktopUrl(url, name): 
    #name:
    return createUrl(url, '%desktop%', name)

def createRootUrl(url, rootPath, subPath, name): 
    #name:
    return createUrl(url, os.path.join(rootPath, subPath), name)

def createStartMenuUrl(url, subPath, name): 
    #name:
    return createRootUrl(url, '%startmenu%', subPath, name)

def createFavoritesUrl(url, subPath, name): 
    #name:
    return createRootUrl(url, '%favorites%', subPath, name)

def createProgramsUrl(url, subPath, name): 
    #name:
    return createRootUrl(url, '%programs%', subPath, name)

def createQuickLanuchUrl(target, subPath, name): 
    #name:
    return createRootUrl(target, '%quicklaunch%', subPath, name)
    
#从正常格式的快捷方式中得到目标指向
def getTargetFromLink(lnkPath): 
    #name:
    lnkPath = getNormalPath(lnkPath)
    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink,
                                          None,
                                          pythoncom.CLSCTX_INPROC_SERVER,
                                          shell.IID_IShellLink)
    shortcut.QueryInterface(pythoncom.IID_IPersistFile).Load(lnkPath)
    path = None
    try:
        path = shortcut.GetPath(shell.SLGP_UNCPRIORITY)
    except Exception,e:
        return None
    return path[0].lower()
    
# print getTargetFromLink(r"C:\Users\hujin.ESG\Desktop\WinSCP.lnk")
