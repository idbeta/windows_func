#!/usr/bin/env python
#coding=utf-8 
"""
建议用_winreg里面提供的方法
"""

import os,sys,ctypes,win32con,winnt,win32api,struct
import traceback
import binascii
import re
import _winreg

REG_SZ = win32con.REG_SZ
REG_DWORD = win32con.REG_DWORD
REG_MULTI_SZ = win32con.REG_MULTI_SZ
REG_EXPAND_SZ = win32con.REG_EXPAND_SZ

def getSamDesired(attr,reDirect=False):
    samDesired = attr
    if not reDirect:
        if struct.calcsize("P") == 8: # python  64 位
            samDesired = attr|win32con.KEY_WOW64_32KEY
        else:# python  32 位
            samDesired = attr|win32con.KEY_WOW64_64KEY
    return samDesired
        
def hasKey(keyFullName, reDirect= True):
    '''
    #Name:
    返回注册表键是否存在
    #Return:
    存在返回True，否则返回False
    #Args:
    keyFullName: 键全名
    reDirect:是否开启重定向
    '''
    hreg = None
    rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
    try:
        hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_READ,_reDirect))
    except Exception,e:
        return False
    finally:
        if hreg:
            win32api.RegCloseKey(hreg)
    return True

def __getRegSubKeysList__(keyFullName, subKeys, reDirect=False):
    '''
    #Name:
    递归的方法寻找注册表路径下所有子健
    '''
    rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
    subKeyTuple = []
    hreg = None
    try:
        hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_READ,_reDirect))
        subKeyTuple = win32api.RegEnumKeyEx(hreg)
    except:
        return False
    finally:
        if hreg:
            win32api.RegCloseKey(hreg)
    for subKey in subKeyTuple:
        subKeyPath = keyFullName + '\\' + subKey[0]
        subKeys.insert(0, subKeyPath)
        __getRegSubKeysList__(subKeyPath, subKeys)
            

def delKey(keyFullName, reDirect=True):
    '''
    #Name:
    删除注册表中的某键
    #Return:
    存在返回True，否则返回False
    #Args:
    keyFullName:键全名
    reDirect:是否开启重定向
    #Raises:
    此操作会删除键级键的所有子键
    '''
    if hasKey(keyFullName,reDirect):
        subKeysList = []
        __getRegSubKeysList__(keyFullName, subKeysList)
        subKeysList.append(keyFullName)
        for subKey in subKeysList:
            rootKeyName, subKeyName, _reDirect = _TransRootAndSub(subKey, reDirect)
            try:
                if g_qaOS64Bit:
                    win32api.RegDeleteKeyEx(rootKeyName, subKeyName,getSamDesired(win32con.KEY_WRITE,_reDirect),0)
                else:
                    win32api.RegDeleteKey(rootKeyName, subKeyName)
            except Exception,e:
                return False
        return True
    return True

def addKey(keyFullName, reDirect=True):
    '''
    #Name:
    向注册表中添加键
    #Return:
    存在返回True，否则返回False
    #Args:
    keyFullName:键全名
    reDirect:是否开启重定向
    '''
    bExist = False
    bExist = hasKey(keyFullName,reDirect)
    if not bExist:
        hreg = None
        flag = 0
        rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
        try:
            hreg, flag =  win32api.RegCreateKeyEx(rootKeyName, subKeyName, getSamDesired(win32con.KEY_WRITE,_reDirect), None, winnt.REG_OPTION_NON_VOLATILE, None, None)
        except:
            return False
        finally:
            if hreg:
                win32api.RegCloseKey(hreg)
    return True

def getKeyValue(keyFullName, valueName = None, reDirect=True):
    '''
    #Name:
    获取注册表键的值
    #Return:
    存在返回值，否则返回None
    #Args:
    keyFullName:键全名
    valueName: 值名（可选，为None时返回键的默认值）
    reDirect:是否开启重定向
    '''

    if hasKey(keyFullName,reDirect):
        hreg = None
        valueData = ''
        rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
        try:
            hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_READ,_reDirect))
            valueData, REG_type = win32api.RegQueryValueEx(hreg, valueName)
            if REG_type == win32con.REG_DWORD and valueData < 0:
                valueData = ctypes.c_uint(valueData).value
                if not valueData:
                    return None
                return valueData
            if REG_type == REG_MULTI_SZ:
                return getMultiKeyValue(keyFullName,valueName)
            elif REG_type == win32con.REG_QWORD:
                ret = 0
                k = 0
                for i in valueData:
                    ret += ord(i)*(16**k)
                    k+=2
                # 10进制
                return ret
            elif REG_type == win32con.REG_BINARY:
                return binascii.b2a_hex(valueData)
            return str(valueData)
        except Exception, e:
            return None
        finally:
            if hreg:
                win32api.RegCloseKey(hreg)
    return None

def getMultiKeyValue(keyFullName, valueName, reDirect=False):
    '''
    #Name:
    获取多字符串值
    #Return:
    存在返回值，否则返回None
    #Args:
    keyFullName:键全名
    valueName: 值名（可选，为None时返回键的默认值）
    reDirect:是否开启重定向
    '''
    
    c = wmi.WMI (namespace='DEFAULT').StdRegProv
    rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
    r1,value = c.GetMultiStringValue(rootKeyName, subKeyName, valueName)
    return value

def hasKeyValue(keyFullName, valueName, reDirect = False):
    '''
    #Name:
    判断是否有注册表值
    #Return:
    存在返回True，否则返回False
    #Args:
    keyFullName:键全名
    valueName: 值名（可选，为None时返回键的默认值）
    reDirect:是否开启重定向
    '''
    if getKeyValue(keyFullName, valueName, reDirect) == None:
        return False
    else:
        return True

def setKeyValue(keyFullName, valueName, type, value, reDirect = True):
    '''
    #Name:
    设置注册表键的值
    #Return:
    添加成功返回True，否则返回False
    #Args:
    keyFullName: 键全名
    valueName: 值名
    type: 值类型
    value: 值
    reDirect:是否开启重定向
    '''
    hreg = None
    addKey(keyFullName, reDirect)
    rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
    try:
        hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_WRITE,_reDirect))
        if type == win32con.REG_DWORD:
            value = int(value)
        win32api.RegSetValueEx(hreg, valueName, 0, type, value)
    except Exception,e:
        return False
    finally:
        if hreg:
            win32api.RegCloseKey(hreg)
    return True

def delKeyValue(keyFullName, valueName, reDirect = True):
    '''
    #Name:
    删除注册表键的值
    #Return:
    删除成功返回True，否则返回False
    #Args:
    keyFullName: 键全名
    valueName: 值名
    reDirect:是否开启重定向
    '''
    if hasKey(keyFullName,reDirect):
        hreg = None
        rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
        try:
            hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_WRITE,_reDirect))
            win32api.RegDeleteValue(hreg, valueName)
        except:
            return False
        finally:
            if hreg:
                win32api.RegCloseKey(hreg)
    return True

def backupKey(keyFullName, backupFileName):
    '''
    #Name:
    备份注册表键下所有内容
    #Args:
    keyFullName: 键全名
    backupFileName: 备份文件名
    '''
    cmd = r'REG SAVE %s "%s" /y 1> NUL 2> NUL' % (keyFullName, backupFileName)
    if os.system(cmd) != 0:
        raise Exception('备份注册表键失败！%s' % keyFullName)

def restoreKey(keyFullName, backupFileName):
    '''
    #Name:
    恢复注册表键下所有内容
    #Args:
    keyFullName: 键全名
    backupFileName: 恢复文件名
    '''
    addKey(keyFullName)
    cmd = r'REG RESTORE %s "%s" 1> NUL 2> NUL' % (keyFullName, backupFileName)
    if os.system(cmd) != 0:
        raise Exception('恢复注册表键失败！%s' % keyFullName)


def importRegFile(regFile):
    '''
    #Name:
    导入注册表文件
    #Args:
    regFile: 注册表文件路径
    '''
    cmd = r'REG IMPORT "%s" 1> NUL 2> NUL '%(regFile)
    os.system(cmd)
    if os.system(cmd) != 0:
        raise Exception('导入注册文件失败:"%s"' % regFile)

def exportKey(keyFullName, exportFileName):
    '''
    #Name:
    导出注册表文件
    #Args:
    keyFullName: 键全名
    regFile: 注册表文件路径
    '''
    if os.path.exists(exportFileName):
        return False
    cmd = r'REG export "%s" "%s" 1> NUL' % (keyFullName, exportFileName)    
    if os.system(cmd) != 0:
        return False
    return True

def transKeyName(keyName):
    '''
    #Name:
    注册表跟路径名称转换
    '''
    keyName = keyName.upper()
    if keyName in ['HKLM', 'HKEY_LOCAL_MACHINE']:
        keyName = win32con.HKEY_LOCAL_MACHINE
    elif keyName in ['HKCR', 'HKEY_CLASSES_ROOT']:
        keyName = win32con.HKEY_CLASSES_ROOT
    elif keyName in ['HKCU', 'HKEY_CURRENT_USER']:
        keyName = win32con.HKEY_CURRENT_USER
    elif keyName in ['HKU', 'HKEY_USERS']:
        keyName = win32con.HKEY_USERS
    elif keyName in ['HKCC', 'HKEY_CURRENT_CONFIG']:
        keyName = win32con.HKEY_CURRENT_CONFIG
    return keyName

def _TransRootAndSub(keyFullName, bRedirect):
    nameList = keyFullName.split('\\', 1)
    rootKeyName = transKeyName(nameList[0])
    subKeyName = None
    _bRedirect = bRedirect
    if len(nameList) == 2:
        subKeyName = nameList[1]
        pos = subKeyName.upper().find('WOW6432NODE\\')
        
        if struct.calcsize("P") == 8: # 64位python判断逻辑与32位python刚好相反
            if pos != -1:
                _bRedirect = False
        else:    
            if pos != -1 and not nameList[0] in ['HKCU', 'HKEY_CURRENT_USER']:
                subKeyName = '%s%s' %(subKeyName[0:pos],subKeyName[pos + len('WOW6432NODE\\'):])
                _bRedirect = True
                
    return rootKeyName, subKeyName, _bRedirect

def _openKey(keyName, subKeyName = None, _reDirect=False, key = win32con.KEY_ALL_ACCESS):
    try:
        return win32api.RegOpenKeyEx(keyName, subKeyName, 0, getSamDesired(key,_reDirect))
    except:
        return -1

def _getAllValue(key):
    res = {}
    index = 0
    while True:
        try:
            name, value, type = win32api.RegEnumValue(key, index)
            res[name] = (value, type)
            index += 1
        except:
            break
    return res

def getRegTreeInfo(keyFullName, open_key=win32con.KEY_ALL_ACCESS, reDirect=False):
    '''
    #Name:
    得到注册表键及其所有子键的值信息
    #Return:
    此操作返回一个dict，以注册表键全名为dict的键，以注册表键的值为了dict的值
    #Args:
    keyFullName: 键全名
    open_key: 打开权限
    #Raises:
    当键不存在时返回空dict
    '''
    stack = [keyFullName]
    res = {}
    while len(stack) != 0:
        keyFullName = stack.pop()
        rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
        key = _openKey(rootKeyName, subKeyName, _reDirect, open_key)
        if key == -1:
            continue
        if not key:
            break
        #枚举value
        valueMap = _getAllValue(key)
        res[keyFullName] = valueMap
        #枚举子项
        try:
            keyNameList = list(win32api.RegEnumKeyEx(key))
            for keyName in keyNameList:
                stack.append(os.path.join(keyFullName, keyName[0]))
        except:
            continue
            win32api.RegCloseKey(key)
    return res


def enumRegValues(keyFullName, reDirect= True):
    '''
    #Name:
    枚举注册表键下的所有值
    #Return:
    值列表
    #Args:
    keyFullName: 键全名
    reDirect: 是否重定向
    #Raises:
    当键不存在时返回空list
    '''
    hreg = None
    rootKeyName, subKeyName, _reDirect = _TransRootAndSub(keyFullName, reDirect)
    try:
        hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_READ,_reDirect))
        valueNum = win32api.RegQueryInfoKey(hreg)[1]
        ret = []
        for i in range(valueNum):
            ret.append(win32api.RegEnumValue(hreg,i)[0])
        return ret
    except Exception,e:
        import traceback
        print traceback.format_exc()
        return []
    finally:
        if hreg:
            win32api.RegCloseKey(hreg)

def reMatchRegKey(keyFullName, reDirect=False):
    '''
    #Name:
    支持路径中带通配符.*寻找匹配的注册表键
    #Return:
    真实注册表键
    #Args:
    keyFullName: 通配符.*的键
    reDirect: 是否重定向
    '''
    if not '.*' in keyFullName:
        return keyFullName
    key_items = keyFullName.split('\\')
    ret = []
    for item in key_items:
        if not '.*' in item:
            ret.append(item)
        else:
            __keyFullName = '\\'.join(ret)
            tree_info = getRegTreeInfo(__keyFullName, win32con.KEY_READ, reDirect=reDirect)
            if not tree_info:
                return
            findret = False
            for i in tree_info.keys():
                next_path = i.replace(__keyFullName+'\\', '').split('\\')[0]
                if re.match(item, next_path):
                    ret.append(next_path)
                    findret = True
                    break
            if not findret:
                return
    return '\\'.join(ret)

#判断注册表键是否存在    
def isRegKeyExit(regpath,ckey=None):
    category=regpath.split('\\')[0].upper()
    subject=regpath.replace((regpath.split('\\')[0]),'').lstrip('\\')
    category = {
    'HKEY_CLASSES_ROOT': lambda: _winreg.HKEY_CLASSES_ROOT,
    'HKEY_CURRENT_USER': lambda: _winreg.HKEY_CURRENT_USER,
    'HKEY_LOCAL_MACHINE': lambda: _winreg.HKEY_LOCAL_MACHINE,
    'HKEY_USERS': lambda: _winreg.HKEY_USERS,
    'HKEY_CURRENT_CONFIG': lambda: _winreg.HKEY_CURRENT_CONFIG,
    }[category]()
    if ckey:
        try:
            key = _winreg.OpenKey(category,subject)
            if _winreg.QueryValueEx(key,ckey):
                return True
            else:
                return False
        except Exception,info:
            return False
    else:
        try:
           key = _winreg.OpenKey(category,subject)
           return True
        except:
           return False
           
#判断注册表键是否存在
def isRegKeyExit_2(regpath):
    hreg = None    
    category=regpath.split('\\')[0].upper()
    subject=regpath.replace((regpath.split('\\')[0]),'').lstrip('\\')
    category = {
    'HKEY_CLASSES_ROOT': lambda: win32con.HKEY_CLASSES_ROOT,
    'HKEY_CURRENT_USER': lambda: win32con.HKEY_CURRENT_USER,
    'HKEY_LOCAL_MACHINE': lambda: win32con.HKEY_LOCAL_MACHINE,
    'HKEY_USERS': lambda: win32con.HKEY_USERS,
    'HKEY_CURRENT_CONFIG': lambda: win32con.HKEY_CURRENT_CONFIG,
    }[category]()
    try:
        hreg = win32api.RegOpenKeyEx(category, subject, 0, win32con.KEY_ALL_ACCESS)
        return hreg
    except:
        return False  
    
#获取注册表键值
def getRegKeyValue(regpath, key):
    hreg = None
    category=regpath.split('\\')[0].upper()
    subject=regpath.replace((regpath.split('\\')[0]),'').lstrip('\\')
    category = {
    'HKEY_CLASSES_ROOT': lambda: win32con.HKEY_CLASSES_ROOT,
    'HKEY_CURRENT_USER': lambda: win32con.HKEY_CURRENT_USER,
    'HKEY_LOCAL_MACHINE': lambda: win32con.HKEY_LOCAL_MACHINE,
    'HKEY_USERS': lambda: win32con.HKEY_USERS,
    'HKEY_CURRENT_CONFIG': lambda: win32con.HKEY_CURRENT_CONFIG,
    }[category]()
    try:
        hreg = win32api.RegOpenKeyEx(category, subject, 0, win32con.KEY_READ)
        return win32api.RegQueryValueEx(hreg, key)[0]
    except:
        # print traceback.format_exc()
        return None
    finally:
        if hreg:
            tryExcept(win32api.RegCloseKey, hreg)
    
#设置注册表键值
def setRegKeyValue(regpath, key, kind, value):#如果key为空则修改的是默认值
    category=regpath.split('\\')[0].upper()
    subject=regpath.replace((regpath.split('\\')[0]),'').lstrip('\\')
    hreg = None
    hreg = {
    'HKEY_CLASSES_ROOT': lambda: win32con.HKEY_CLASSES_ROOT,
    'HKEY_CURRENT_USER': lambda: win32con.HKEY_CURRENT_USER,
    'HKEY_LOCAL_MACHINE': lambda: win32con.HKEY_LOCAL_MACHINE,
    'HKEY_USERS': lambda: win32con.HKEY_USERS,
    'HKEY_CURRENT_CONFIG': lambda: win32con.HKEY_CURRENT_CONFIG,
    }[category]()
    kind=kind.upper()
    kind={
    'REG_SZ': lambda: win32con.REG_SZ,
    'REG_BINARY': lambda: win32con.REG_BINARY,
    'REG_DWORD': lambda: win32con.REG_DWORD,
    'REG_QWORD': lambda: win32con.REG_QWORD,
    'REG_MULTI_SZ': lambda: win32con.REG_MULTI_SZ,
    'REG_EXPAND_SZ': lambda: win32con.REG_EXPAND_SZ,
    }[kind]()    
    try:
        hreg = win32api.RegCreateKey(hreg, subject)
        win32api.RegSetValueEx(hreg, key, 0, kind, value)
    except Exception, e:
        print e
    finally:
        if hreg:
            try:
                win32api.RegCloseKey(hreg)
            except Exception, e:
                print e

def deleteRegKey(regpath):
    keyName=regpath.split('\\')[0].upper()
    subKeyName=regpath.replace((regpath.split('\\')[0]),'').lstrip('\\')
    try:
        return win32api.RegDeleteKey(keyName, subKeyName)
    except:
        pass

def deleteRegValue(regpath, key):
    hreg = None
    keyName=regpath.split('\\')[0].upper()
    subKeyName=regpath.replace((regpath.split('\\')[0]),'').lstrip('\\')
    if not getRegKeyValue(regpath, key):
        return
    keyName = {
    'HKEY_CLASSES_ROOT': lambda: win32con.HKEY_CLASSES_ROOT,
    'HKEY_CURRENT_USER': lambda: win32con.HKEY_CURRENT_USER,
    'HKEY_LOCAL_MACHINE': lambda: win32con.HKEY_LOCAL_MACHINE,
    'HKEY_USERS': lambda: win32con.HKEY_USERS,
    'HKEY_CURRENT_CONFIG': lambda: win32con.HKEY_CURRENT_CONFIG,
    }[keyName]()
    hreg = win32api.RegOpenKeyEx(keyName, subKeyName, 0, win32con.KEY_ALL_ACCESS)
    value = win32api.RegDeleteValue(hreg, key)
    if hreg:
        win32api.RegCloseKey(hreg)
    return value
if __name__ == '__main__':
    print reMatchRegKey(r'HKEY_USERS\360SandBox\Device\HarddiskVolume.*\test')
