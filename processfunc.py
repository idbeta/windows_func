#!/usr/bin/env python
#coding=utf-8 

import os,sys,ctypes,win32con,winnt,win32api,struct,win32process
import traceback
import binascii
import re,copy
import psutil
import subprocess
from ctypes.wintypes import *
from ctypes import  *
import collections

class PROCESSENTRY32(Structure):
    _fields_ = [
        ('dwSize',              c_uint), 
        ('cntUsage',            c_uint),
        ('th32ProcessID',       c_uint),
        ('th32DefaultHeapID',   c_uint),
        ('th32ModuleID',        c_uint),
        ('cntThreads',          c_uint),
        ('th32ParentProcessID', c_uint),
        ('pcPriClassBase',      c_long),
        ('dwFlags',             c_uint),
        ('szExeFile',           c_char * 260), 
        ('th32MemoryBase',      c_long),
        ('th32AccessKey',       c_long)
    ] 
kernel32 = windll.kernel32
CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.argtypes = [c_int, c_int]
CreateToolhelp32Snapshot.rettype = c_long
TH32CS_SNAPPROCESS = 2
STANDARD_RIGHTS_REQUIRED = 0x000F0000
SYNCHRONIZE = 0x00100000
PROCESS_ALL_ACCESS = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFF)
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPTHREAD = 0x00000004
MAX_MODULE_NAME32 = 255
MAX_PATH = 260
INVALID_HANDLE_VALUE = c_void_p(-1).value
Module32First = windll.kernel32.Module32First
Module32Next = windll.kernel32.Module32Next
Process32First = windll.kernel32.Process32First
Process32First.argtypes = [c_void_p , POINTER(PROCESSENTRY32)]
Process32First.rettype  = c_int
Process32Next = windll.kernel32.Process32Next
Process32Next.argtypes = [c_void_p , POINTER(PROCESSENTRY32)]
Process32Next.rettype  = c_int
CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = [c_void_p]
CloseHandle.rettype  = c_int 
class MODULEENTRY32(Structure):
    _fields_ = [
        ('dwSize', c_uint), 
        ('th32ModuleID', c_uint),
        ('th32ProcessID', c_uint),
        ('GlblcntUsage', c_uint),
        ('ProccntUsage', c_uint),
        ('modBaseAddr', c_uint),
        ('modBaseSize', c_uint),
        ('hModule', c_uint),
        ('szModule', c_char * (MAX_MODULE_NAME32 + 1)),
        ('szExePath', c_char * MAX_PATH),
    ]
##获取进程id、优先级、用户、父进程、命令行、启动时间
def getprocessdetail(pid):
    import time
    p = psutil.Process(pid)
    # return p.as_dict()
    return p.as_dict()['pid'],p.as_dict()['nice'],p.as_dict()['username'],p.as_dict()['ppid'],p.as_dict()['cmdline'],time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(p.as_dict()['create_time']))
    
##判断进程是否存在
def processExists(name):
    return getPidByName_1(name) != []
    
##枚举进程
def enumProcess():
    hSnapshot = kernel32.CreateToolhelp32Snapshot(15, 0)
    fProcessEntry32 = PROCESSENTRY32()
    processClass = collections.namedtuple("processInfo","processName processID")
    processSet = []
    #if hSnapshot:
    fProcessEntry32.dwSize = sizeof(fProcessEntry32)
    listloop = kernel32.Process32First(hSnapshot, byref(fProcessEntry32))
    while listloop:
        processName = (fProcessEntry32.szExeFile)
        processID = fProcessEntry32.th32ProcessID
        processSet.append(processClass(processName, processID))
        listloop = kernel32.Process32Next(hSnapshot, byref(fProcessEntry32))
    return processSet
# for i in enumProcess():
    # print(i.processName,i.processID)

def getProcList():
    CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
    Process32First = ctypes.windll.kernel32.Process32First
    Process32Next = ctypes.windll.kernel32.Process32Next
    CloseHandle = ctypes.windll.kernel32.CloseHandle
    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
    if Process32First(hProcessSnap,ctypes.byref(pe32)) == False:
        print >> sys.stderr, "Failed getting first process."
        return
    while True:
        yield pe32      
        # print pe32.szExeFile
        # print pe32.th32ProcessID
        if Process32Next(hProcessSnap,ctypes.byref(pe32)) == False:
            break
    CloseHandle(hProcessSnap)
# for proc in processfunc.getProcList():
    # print proc.szExeFile,proc.th32ParentProcessID

##创建进程
si = win32process.STARTUPINFO()
def createProcess(szPath, user='admin'):#非阻塞
    create_flags = win32process.CREATE_NEW_CONSOLE
    return win32process.CreateProcess(None, szPath, None, None, True,create_flags, None, None, si)

def createProcessbysubprocess(szPath,command=None):#阻塞
    if command:
        returnCode = subprocess.call(szPath+" "+command)
    else:
        returnCode = subprocess.call(szPath)
    return 'returncode:', returnCode

def createProcessbyossystem(szPath,command=None):#阻塞
    if command:
        returnCode = os.system(szPath+" "+command)
    else:
        returnCode = os.system(szPath)
    return 'returncode:', returnCode 

def createProcessbyosstartfile(szPath):#非阻塞，这个是非正常用法，不能传命令行参数 os.startfile("c:\\", "explore")
    returnCode = os.startfile(szPath)
    return 'returncode:', returnCode

def createProcessbyShellExecute(szPath,command=None):#非阻塞
    if command:
        returnCode = win32api.ShellExecute(0,'open',szPath,command,'',1)
    else:
        returnCode = win32api.ShellExecute(0,'open',szPath, '','',1)
    return 'returncode:', returnCode
    
def createProcessbyospopen(szPath,command=None):#阻塞,2.6版开始被subprocess替换
    if command:
        returnCode = os.popen(szPath+" "+command)
    else:
        returnCode = os.popen(szPath)
    return 'returncode:', returnCode
    
##根据进程名获取PID
def getPidByName_1(x):
    num=[]
    for r in psutil.process_iter():
        aa = str(r)
        f = re.compile(x,re.I)
        if f.search(aa):
            num.append( aa.split('pid=')[1].split(',')[0] )
    return num
# print getPidByName('chrome')

def getProcessEntry32ByIdOrName(name,pid=None):  #only32
    hSnapshot = None
    pe32List = []
    try:
        hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if INVALID_HANDLE_VALUE == hSnapshot:
            return

        pe32 = PROCESSENTRY32()
        pe32.dwSize = sizeof(PROCESSENTRY32)
        ret = Process32First(hSnapshot, pointer(pe32))
        while ret:
            if pid and pid == pe32.th32ProcessID:
                return pe32
            if name and name.lower() == pe32.szExeFile.lower():
                pe32List.append(copy.copy(pe32))
            ret = Process32Next(hSnapshot, pointer(pe32))
        if name:
            return pe32List
    except:
        print traceback.format_exc()
    finally:
        if hSnapshot: CloseHandle(hSnapshot)

def getPidByName_2(name):  #only32
    pidList = []
    pe32List = getProcessEntry32ByIdOrName(name,None)
    for pe32 in pe32List:
        pidList.append(pe32.th32ProcessID)
    return pidList 
    
##根据进程名获取进程全路径
def nametopath(x):
    num=[]
    for i in nametopid(x):
        num.append(psutil.Process(int(i)).exe())
    return num
# print nametopath('notepad')
        
##根据PID获取进程名
def getNameByPid_1(x):
    return psutil.Process(int(x)).name()
# print pidtoname('sasa')

def getNameByPid_2(pid):  #only32
    pe32 = getProcessEntry32ByIdOrName(None,pid)
    if not pe32:
        return
    return pe32.szExeFile 
    
##根据PID获取进程全路径
def pidtopath(x):
    return psutil.Process(int(x)).exe()
# print pidtopath('1280')

##枚举进程模块
def getModuleByPid(pid):
    res = {}
    res[pid] = []
    me32 = MODULEENTRY32()
    snapMod = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid);
    me32.dwSize = sizeof(MODULEENTRY32);
    if Module32First(snapMod, pointer(me32)):
        while Module32Next(snapMod, pointer(me32)):
            res[pid].append(me32.szExePath.lower())
    CloseHandle(snapMod);
    return res
    
def getModuleByName(name):
    pidList = getPidByName_2(name)
    if not pidList:
        return
    res = {}
    for pid in pidList:
        res[pid] = []
        me32 = MODULEENTRY32()
        snapMod = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid);
        me32.dwSize = sizeof(MODULEENTRY32);
        if Module32First(snapMod, pointer(me32)):
            while Module32Next(snapMod, pointer(me32)):
                res[pid].append(me32.szExePath.lower())
        CloseHandle(snapMod);
    return res 

def listProcessModules(pid):
    '''
    32位进程不能枚举64位进程
    '''
    hprocess = None
    modules = []
    try:
        hprocess = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ | win32con.PROCESS_ALL_ACCESS, False, pid)
        moduleinfo = win32process.EnumProcessModules(hprocess)
        for module in moduleinfo:
            modulefile = win32process.GetModuleFileNameEx(hprocess, module)
            modules.append(modulefile)
        return modules
    except:
        return modules
    finally:
        if hprocess:
            win32api.CloseHandle(hprocess)
    
##获取进程的GDI数量
def getProcessGDI(pid):
    proc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ | win32con.PROCESS_ALL_ACCESS, False, pid)
    gdi = win32process.GetGuiResources( proc.handle, win32con.GR_GDIOBJECTS)
    proc.close
    return gdi
        
##杀进程
def killprocess(x):
    if x.isdigit():
        psutil.Process(int(x)).terminate()
    else:
        for i in nametopid(x):
            psutil.Process(int(i)).terminate()

def getChildPid(pid):
    procList = getProcList()
    for proc in procList:
        if proc.th32ParentProcessID == pid:
            yield proc.th32ProcessID#等于返回一个list
            
OpenProcess = windll.kernel32.OpenProcess
OpenProcess.argtypes = [c_void_p, c_int, c_long]
OpenProcess.rettype  = c_long
def killPid(pid):
    childList = getChildPid(pid)
    for childPid in childList:
        killPid(childPid)
    # handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)    
    # ctypes.windll.kernel32.TerminateProcess(handle,0)
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)
    win32api.TerminateProcess(handle,0)
    
def killProcessbycmd(imgName, killChild = False, force = True):
    flag = '/T'
    if not killChild:
        flag = ''
    if force:
        force = '/F'
    else:
        force = ''
    cmd = 'taskkill %s %s /IM %s 1> NUL 2> NUL' % (force, flag, imgName)
    os.system(cmd)
    
##杀进程树
def killprocesstree(x):
    if x.isdigit():#根据pid杀
        for pid in psutil.pids():
            if psutil.Process(int(pid)).ppid()==int(x):                
                psutil.Process(int(pid)).terminate()
        psutil.Process(int(x)).terminate()
    else:#根据进程名杀
        try:
            for pid in psutil.pids():#杀子进程
                if str(psutil.Process(int(pid)).ppid()) in nametopid(x): #if 'a' in theList:
                    psutil.Process(int(pid)).terminate()
            for i in nametopid(x):#杀父进程
                psutil.Process(int(i)).terminate()
        except Exception,info:
            return "input the right pname!"
 
##获取进程内存占用 , psutil does not expose the private working set
def getprocessmem(x):
    if x.isdigit():
        return psutil.Process(int(x)).memory_info()
    else:
        for i in nametopid(x):
            return psutil.Process(int(i)).memory_info()
# print getprocessmem('236')
 
##获取进程CPU占用
def getprocesscpu(x):
    if x.isdigit():
        return psutil.Process(int(x)).cpu_percent(interval=1.0) / psutil.cpu_count()
    else:
        num=[]
        for i in nametopid(x):
            num.append(psutil.Process(int(i)).cpu_percent(interval=1.0) / psutil.cpu_count() )
        return num
        
##注入dll
def injectDll(pid, path, buf = ctypes.create_unicode_buffer(256)):
    proc = None
    try:
        proc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)
        vaddr = ctypes.windll.kernel32.VirtualAllocEx(proc.handle, 0, len(path) * 2 + 1, win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
        if not vaddr:
            return False
        buf.value = path
        if not ctypes.windll.kernel32.WriteProcessMemory(proc.handle, vaddr, buf, len(path) * 2, 0):
            return False
        faddr = win32api.GetProcAddress(win32api.GetModuleHandle('kernel32'), 'LoadLibraryW')
        if not ctypes.windll.kernel32.CreateRemoteThread(proc.handle, 0, 0, faddr, vaddr, 0, 0):
            return False
        return True
    except Exception,e:
        print str(e)
        
        return False
    finally:
        if proc:
            proc.close()
            
##释放进程注入的DLL
def unloadDll(pid,libName):
    proc = None
    hModuleSnap = c_void_p(0)  
    me32 = MODULEENTRY32()  
    me32.dwSize = sizeof( MODULEENTRY32 )  
    try:
        mod = None
        CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
        hModuleSnap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)
        ret = ctypes.windll.kernel32.Module32First( hModuleSnap, pointer(me32) )  
        if ret == 0 :
            print  " Module32First Error"
            ctypes.windll.kernel32.CloseHandle( hModuleSnap )  
            return False   
                
        while ret :  
            if me32.szModule  == libName or me32.szExePath  == libName:
                mod = me32
                break
            ret = ctypes.windll.kernel32.Module32Next( hModuleSnap , pointer(me32) )  
        if not mod:
            print '没有在进程中找到DLL模块'
            return False
        proc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)
        faddr = win32api.GetProcAddress(win32api.GetModuleHandle('kernel32'), 'FreeLibrary')
        if not ctypes.windll.kernel32.CreateRemoteThread(proc.handle, 0, 0, faddr, mod.modBaseAddr, 0, 0):
            return False
        return True
    except Exception,e:
        print str(e)
        return False
    finally:
        if hModuleSnap:
            windll.kernel32.CloseHandle( hModuleSnap )         
        if proc:
            proc.close()         