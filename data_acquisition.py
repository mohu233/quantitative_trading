import psutil
import win32api
import ctypes.wintypes
import uiautomation as auto
import win32gui
import win32process
from datetime import datetime, timezone
import pytz
from collections import Counter
import traceback



# 获取当前时间并提取秒数

# =============== 工具函数 ===============

def get_pid_by_name(process_name):
    for p in psutil.process_iter(['pid', 'name']):
        if p.info['name'] and p.info['name'].lower() == process_name.lower():
            return p.info['pid']
    return None

def get_windows_by_pid(pid):
    titles = []
    def callback(hwnd, extra):
        try:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                title = win32gui.GetWindowText(hwnd)
                if title:
                    titles.append(title)
        except Exception:
            pass
    win32gui.EnumWindows(callback, None)
    return titles

def find_control_by_automationid_and_name(root_control, automation_id, name=""):
    for child in root_control.GetChildren():
        if child.AutomationId == automation_id and child.Name == name:
            return child
        result = find_control_by_automationid_and_name(child, automation_id, name)
        if result:
            return result
    return None


# 添加列表
def add_json(key, result,result2,result3,result4,data):
    if result2 == 0:
        result2 = result
    if result3 == 0:
        result3 = result
    if result4 == 0:
        result4 = result
    if data[-1][0] == key:
        data[-1][1]['c'] = result  # 收盘价
        if data[-1][1]['h'] < result:
            data[-1][1]['h'] = result
        if data[-1][1]['l'] > result:
            data[-1][1]['l'] = result

        if data[-1][1]['h'] < result2:
            data[-1][1]['h'] = result2
        if data[-1][1]['l'] > result2:
            data[-1][1]['l'] = result2

        if data[-1][1]['h'] < result3:
            data[-1][1]['h'] = result3
        if data[-1][1]['l'] > result3:
            data[-1][1]['l'] = result3

        if data[-1][1]['h'] < result4:
            data[-1][1]['h'] = result4
        if data[-1][1]['l'] > result4:
            data[-1][1]['l'] = result4
    else:
        if data[-1][1]['o'] == data[-1][1]['c'] ==data[-1][1]['h'] ==data[-1][1]['l']:
            pass
        else:
            print('保存数据', str(data[-1]))
            with open('数据.txt', 'a+', encoding='utf-8') as f:
                f.write(str(data[-1]) + '\n')
                f.close()
        # 添加数据
        del data[0]
        data.append([key,{'c': result, 'o': result, 'l': result, 'h': result}])
        # 保存数据

    return data


def add_list_S(key,key_s,result,data_s,data):
    if data_s[0] == key_s:
        data_s[1].append(result)
        return data_s,data
    else:
        # print('data_s',data_s)
        count = Counter(data_s[1])
        sorted_items = sorted(count.items(), key=lambda x: (-x[1], x[0]))
        list_r = [item for item, freq in sorted_items]
        val = 0
        val2 = 0
        val3 = 0
        val4 = 0
        if list_r:
            val = list_r[0]
        if len(list_r)>1:
            val2 = list_r[1]
        if len(list_r)>2:
            val3 = list_r[1]
        if len(list_r)>3:
            val4 = list_r[1]
        print(data_s)
        print('添加数据',val, val2,val3,val4)
        if val == 0:
            pass
        else:
            data = add_json(key, val, val2,val3,val4,data)  # 添加
        data_s = [key_s,[]]
        return data_s,data



# =============== 主流程 ===============

# 1. 获取 isky.exe 进程PID
target_pid = get_pid_by_name('isky.exe')
if not target_pid:
    print("未找到 isky.exe 进程。")
    # exit(1)
print(f'isky.exe 的 PID 是: {hex(target_pid)}')

# 2. 获取主窗口标题（找带'OkF'关键词的第一个窗口标题）
window_title = ''
for t in get_windows_by_pid(target_pid):
    if 'OkF' in t:
        window_title = t
        break
if not window_title:
    print("未找到目标窗口标题")
    exit(1)
print(f'窗口标题: {window_title}')

# 3. 用 uiautomation 定位目标窗口（可模糊匹配窗口名）
window = auto.WindowControl(searchDepth=1, Name=window_title)
if not window.Exists(0, 0):
    print("未找到窗口")
    # exit(1)

# 4. 寻找唯一 Name为空且 AutomationId=59648 的控件
pane = find_control_by_automationid_and_name(window, "59648", "")
if not pane or not pane.Exists(0, 0):
    print("未找到目标窗格控件")
    exit(1)



# 6. 读取指定内存地址数据（循环输出double值）
address = 0x0019F39C
PROCESS_ALL_ACCESS = 0x1F0FFF
handle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, target_pid)
data =  [['00:00',{'c': 0, 'o': 0, 'l': 0, 'h': 0,}]]
data_s = ['0',[]]
try:
    ord_val = 0
    val = 0
    while True:
        utc_now = datetime.now(timezone.utc)
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = utc_now.astimezone(beijing_tz)

        # 格式化为标准字符串
        key = beijing_time.strftime('%H:%M')
        key_s = beijing_time.strftime('%S')

        buffer = ctypes.create_string_buffer(8)
        bytesRead = ctypes.c_size_t(0)
        result = ctypes.windll.kernel32.ReadProcessMemory(
            int(handle),
            ctypes.c_void_p(address),
            buffer,
            8,
            ctypes.byref(bytesRead)
        )
        if result == 0:
            print("读取内存失败，检查权限、位宽、地址是否有效")
        else:
            dbl_val = ctypes.c_double.from_buffer(buffer).value
            # print(f"地址0x{address:X}处的double类型值为：{dbl_val}")
            try:

                if 100 < dbl_val < 10000:
                    val = int(dbl_val)
                    if val != ord_val:
                        ord_val = val

                        data_s,data = add_list_S(key,key_s, val, data_s,data)
                        print('数据变化，当前值是', val, dbl_val, data)
                        # print(data)
                        # if data[-1][1]['o'] == data[-1][1]['c']:
                        #     print('平点')
                        #     continue
                        # if data[-1][1]['o'] > data[-1][1]['c'] and data[-1][1]['h'] - data[-1][1]['l'] == 3:
                        #     print('阴K')
                        #     continue
                        # elif data[-1][1]['o'] > data[-1][1]['c'] :
                        #     print('阴K平头')
                        #     continue
                        # if data[-1][1]['o'] < data[-1][1]['c'] and data[-1][1]['h'] - data[-1][1]['l'] == 3:
                        #     print('阳K')
                        #     continue
                        # elif data[-1][1]['o'] < data[-1][1]['c'] :
                        #     print('阳K平头')
                        #     continue
                        # input()

            except:
                traceback.print_exc()
                pass
                print(val)
                print('数据错误')
                # input()


        # 5. 截图目标窗格区域
        # rect = pane.BoundingRectangle
        # left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
        # print(f"BoundingRectangle: l={left}, t={top}, r={right}, b={bottom}")
        # im = ImageGrab.grab(bbox=(left, top, right, bottom))
        # im.save('isky_dynamic_screenshot.png')
        # im.show()

        # time.sleep(1)  # 每秒读取一次

except KeyboardInterrupt:
    print("\n手动停止循环。")
finally:
    win32api.CloseHandle(handle)