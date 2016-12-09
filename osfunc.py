#!/usr/bin/env python
#coding=utf-8 
import os,sys,win32api,time,win32file,socket,uuid
import ctypes
from ctypes import wintypes
import pywintypes
import win32con
import win32process
import win32security
import platform
import winnt,struct
import traceback
import binascii
import re
import regfunc
from win32com.shell import shell, shellcon
class OSVERSIONINFOW(ctypes.Structure):
    _fields_ = [
        ('dwOSVersionInfoSize', wintypes.c_long),
        ('dwMajorVersion', wintypes.c_long),
        ('dwMinorVersion', wintypes.c_long),
        ('dwBuildNumber', wintypes.c_long),
        ('dwPlatformId', wintypes.c_long),
        ('szCSDVersion', ctypes.c_char_p*128),
    ]
class OSVERSIONINFOEXW(ctypes.Structure):
    _fields_ = [
        ('dwOSVersionInfoSize', wintypes.c_long),
        ('dwMajorVersion', wintypes.c_long),
        ('dwMinorVersion', wintypes.c_long),
        ('dwBuildNumber', wintypes.c_long),
        ('dwPlatformId', wintypes.c_long),
        ('szCSDVersion', ctypes.c_char_p*128),
        ('wServicePackMajor', wintypes.c_ulong),
        ('wServicePackMinor', wintypes.c_ulong),
        ('wSuiteMask', wintypes.c_ulong),
        ('wProductType', wintypes.c_ulong),
        ('wReserved', wintypes.c_byte),
    ]
def isWin64():        
    myhandle = pywintypes.HANDLE(win32api.GetCurrentProcess())
    ret = win32process.IsWow64Process(myhandle)
    if ret:
        return True
    else:
        sysInfo = win32api.GetNativeSystemInfo()
    if sysInfo and (sysInfo[0] == 9 or sysInfo[0] == 6):
        return True
    return False
def isWin64_2():
    return 'PROGRAMFILES(X86)' in os.environ

def getOSName():
    return platform.system()
    
def getOSVersion():
    return platform.version()      

def getOSbit():
    return platform.architecture()

def getWindowsVersion():
    return platform.uname()[0]+" "+platform.uname()[2]+" "+platform.uname()[3]+" "+platform.uname()[4]
    
def getIEVersion():
    version = regfunc.getKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer','svcVersion')
    if version:
        return version
    version = regfunc.getKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer','Version')
    if not version:
        # print u"获取IE版本失败"
        # sys.exit(0)
        # raise Exception在py2.7中不支持中文，除非用ansi保存代码，其实换成print+sys.exit(0)也差不多。
        raise Exception('getIEVersion fail')  
    return version

def getAllLogicalDrivers():
    '''
    返回盘符列表，如['C:\\', 'D:\\', 'F:\\']
    '''
    s = win32api.GetLogicalDriveStrings()
    return s.strip('\x00').split('\x00')
    
def getLogicDrivers():
     return win32api.GetLogicalDriveStrings().replace(':\\\x00', '')
     
def isFixed(driver):
    '''
    返回driver是否为固定磁盘，driver为磁盘根目录，如C:\
    '''
    return win32file.GetDriveType(driver) == win32con.DRIVE_FIXED

def isRemovable(driver):
    '''
    返回driver是否为可移动磁盘，driver为磁盘根目录
    '''
    return win32file.GetDriveType(driver) == win32con.DRIVE_REMOVABLE

def isCDROM(driver):
    '''
    返回driver是否为CDROM
    '''
    return win32file.GetDriveType(driver) == win32con.DRIVE_CDROM

def getRemovableDrivers():
    res = []
    drivers = getAllLogicalDrivers()
    for driver in drivers:
        if isRemovable(driver) and 'a' not in driver.lower(): #不包括A盘
            res.append(driver)
    return res 
    
def __get_special_path(type):
    idList = shell.SHGetSpecialFolderLocation(0, type)
    return shell.SHGetPathFromIDList(idList)

def __getPath__(path, fileName = None):
    if fileName:
        fileName = os.path.basename(fileName)
        return os.path.join(path, fileName)
    return path

def GetDesktopPath(fileName = None):
    '''返回桌面路径'''
    return __getPath__(__get_special_path(shellcon.CSIDL_DESKTOP), fileName)

def GetStartMenuPath(fileName = None):
    '''返回开始菜单路径'''
    return __getPath__(__get_special_path(shellcon.CSIDL_STARTMENU), fileName)

def GetFavoritePath(fileName = None):
    '''返回收藏夹路径'''
    return __getPath__(__get_special_path(shellcon.CSIDL_FAVORITES), fileName)

def GetPersonalPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_PERSONAL), fileName)

def GetFontsPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_FONTS), fileName)

def GetProGramsPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_PROGRAMS), fileName)

def GetQuickLaunchPath(fileName = None):
    path = getNormalPath(r'%appdata%\Microsoft\Internet Explorer\Quick Launch')
    if fileName:
        fileName = os.path.basename(fileName)
        return os.path.join(path, fileName)
    return path    
def DisableUAC():
    cmd = r'reg ADD HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0 /f >NUL 2>NUL'
    os.system(cmd)

#创建快捷方式
def createLink(target, arguments, path):
    return tryExcept(winshell.CreateShortcut, Target = target, Arguments = arguments, Path = path)[0]
    
#获取时间戳
def getCurrentTime(style = '%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime())

#日期的格式为：2011-09-09
#时间的格式为：05:05:05
def setCurrentTime(sDate=None,sTime=None):
    if ctypes.windll.kernel32.GetUserDefaultUILanguage() !=2052:   # os.system 方法在中文之外的系统会失效
        return setCurrentTimeEx(sDate,sTime)
    if sDate:
        os.system('date %s '%sDate)
    if sTime:
        os.system('time %s '%sTime)

def setCurrentTimeEx(sDate=None,sTime=None):
    try:
        tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(time.time())
        if sDate:
            tm_year, tm_mon, tm_day = sDate.split('-')
        if sTime:
            tm_hour, tm_min, tm_sec = sTime.split(':')
        win32api.SetSystemTime(int(tm_year), int(tm_mon), 1, int(tm_day), int(tm_hour), int(tm_min), int(tm_sec), 0)   
    except:
        if sDate:
            os.system('date %s '%sDate)
        if sTime:
            os.system('time %s '%sTime)

#在当前的时间基础上加上秒数，然后再设置时间
def addTime(secAdded):
    timeString = time.strftime('%Y-%m-%d%H:%M:%S',time.localtime(time.time()+secAdded))
    sDate = timeString[0:10]
    sTime = timeString[10:]
    setCurrentTime(sDate,sTime)

def GetPhysMemorySize():
    return win32api.GlobalMemoryStatus()['TotalPhys']

def getCurrentUserInfo():
    listRet = []        
    userName = win32api.GetUserName()
    userInfo = win32security.LookupAccountName(None,userName)
    listRet.append(userInfo[0])
    listRet.append(userInfo[1])
    listRet.append(userInfo[2])
    listRet.append(userName)
    return listRet#获取当前用户信息：0---SID,    1---doman,    2---SID type,    3---username

#判断当前用户是否属于Domain
def isDomainUser():
    listUserInfo = getCurrentUserInfo()
    if listUserInfo[1] and len(listUserInfo[1]) > 0:
        return True
    return False
    
def getSysVersionByNtdll():
    dll = ctypes.windll.LoadLibrary('ntdll')
    RtlGetVersion = dll.RtlGetVersion
    osversion = OSVERSIONINFOW()
    osversion.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOW)
    RtlGetVersion(ctypes.byref(osversion))
    major_version = osversion.dwMajorVersion
    minor_version = osversion.dwMinorVersion
    dwBuildNumber = osversion.dwBuildNumber
    dwPlatformId = osversion.dwPlatformId  ##define VER_PLATFORM_WIN32_NT   2
    szCSDVersion = osversion.szCSDVersion
    return (major_version, minor_version, dwBuildNumber, dwPlatformId, szCSDVersion)
        
def getCmdOutput(cmd):
    pf = None
    try:
        pf = os.popen(cmd)
        output = pf.read()
        return output
    except Exception, e:
        return e
    finally:
        if pf: pf.close()
        
def getlocalIP():
    myname = socket.getfqdn(socket.gethostname())
    return socket.gethostbyname(myname)
    
def gelocalMAC(): 
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    return ":".join([mac[e:e+2] for e in range(0,11,2)])
    
def ping(ip):
    '''
    检查本机与指定ip的机器是否能通信，返回0表示可以，返回1表示不行。
    '''
    print 'ping %s' % ip
    return os.system('ping %s -n 2 -w 100 1>NUL 2>NUL' % ip)
        