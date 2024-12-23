import psutil
import time
import os
import sys
import subprocess
import signal
import logging
import win32serviceutil
import win32service
import win32event
import servicemanager
from datetime import datetime
import locale

# 設置系統默認編碼
system_encoding = locale.getpreferredencoding()

# 修改日誌配置
LOG_PATH = r"C:\HOMEPAGE\django_chat\django_service.log"

# 確保日誌目錄存在
log_dir = os.path.dirname(LOG_PATH)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日誌處理器，使用系統編碼
file_handler = logging.FileHandler(LOG_PATH, encoding=system_encoding)
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 設置格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 配置根日誌記錄器
logger = logging.getLogger('')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 配置參數
CPU_THRESHOLD = 22.0    # CPU 使用率閾值
MEMORY_THRESHOLD = 80.0 # 記憶體使用率閾值
CHECK_INTERVAL = 15     # 縮短檢查間隔（秒）
MAX_RESTART_ATTEMPTS = 3 # 最大重啟嘗試次數
RESTART_COOLDOWN = 180  # 縮短冷卻時間（秒）
DJANGO_SCRIPT = "manage.py"  # Django 啟動腳本
PYTHON_PATH = r"C:\HOMEPAGE\django_chat\venv-djangochat\Scripts\python.exe"  # 修改為虛擬環境的 Python 路徑
DJANGO_HOST = "127.0.0.1"     # 監聽地址
DJANGO_PORT = "8000"        # 修改為 8000 端口

class DjangoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DjangoService"
    _svc_display_name_ = "Django Web Service"
    _svc_description_ = "監控並管理 Django Web 服務器"
    _exe_name_ = r"C:\HOMEPAGE\django_chat\venv-djangochat\Scripts\python.exe"
    _exe_args_ = r'"C:\HOMEPAGE\django_chat\djangochat\django_service.py"'

    def __init__(self, args):
        try:
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)
            self.running = True
            self.last_restart_time = 0
            self.restart_attempts = 0
            logging.info(f"服務初始化完成，使用Python路徑: {self._exe_name_}")
        except Exception as e:
            logging.error(f"初始化錯誤: {str(e)}", exc_info=True)
            raise

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False
        logger.info("服務停止命令已接收")

    def SvcDoRun(self):
        try:
            logger.info("=== 服務開始運行 ===")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            self.main()
        except Exception as e:
            logger.error(f"服務運行時發生錯誤: {str(e)}", exc_info=True)
            servicemanager.LogErrorMsg(str(e))

    def get_django_process(self):
        """獲取 Django 進程"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and DJANGO_SCRIPT in ' '.join(proc.info['cmdline'] or []):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return None

    def check_memory_usage(self, process):
        """檢查進程記憶體使用率"""
        try:
            memory_percent = process.memory_percent()
            logger.info(f"當前記憶體使用率: {memory_percent:.1f}%")
            return memory_percent
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"檢查記憶體使用率時出錯: {str(e)}")
            return 0

    def should_restart(self, cpu_percent, memory_percent):
        """改進的重啟判斷邏輯"""
        current_time = time.time()
        
        # 查冷卻時間
        if current_time - self.last_restart_time < RESTART_COOLDOWN:
            return False
        
        if self.restart_attempts >= MAX_RESTART_ATTEMPTS:
            logger.warning("已達到最大重啟次數限制")
            if current_time - self.last_restart_time > RESTART_COOLDOWN * 2:
                self.restart_attempts = 0  # 重置計數器
            return False
        
        # 主要關注 CPU 使用率
        if cpu_percent >= CPU_THRESHOLD:
            # 二次確認高 CPU 使用率
            time.sleep(2)
            try:
                process = self.get_django_process()
                if process:
                    second_cpu = process.cpu_percent(interval=1)
                    if second_cpu >= CPU_THRESHOLD:
                        logger.warning(f"CPU 使用率持續超過閾值: {second_cpu}%")
                        return True
            except Exception as e:
                logger.error(f"CPU 二次確認時出錯: {str(e)}")
        
        return False

    def restart_django(self):
        """重啟 Django 進程"""
        try:
            django_proc = self.get_django_process()
            if django_proc:
                old_pid = django_proc.pid
                logger.info(f"正在關閉 Django 進程 (PID: {old_pid})")
                
                try:
                    django_proc.terminate()
                    django_proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    django_proc.kill()
                
                time.sleep(1)
            
            working_dir = os.path.abspath(r"C:\HOMEPAGE\django_chat\djangochat")
            logger.info(f"工作目錄: {working_dir}")
            
            cmd = [
                PYTHON_PATH,
                "-u",  # 無緩衝輸出
                DJANGO_SCRIPT,
                "runserver",
                f"{DJANGO_HOST}:{DJANGO_PORT}"
            ]
            logger.info(f"執行命令: {' '.join(cmd)}")
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            new_process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                startupinfo=startupinfo,
                env=os.environ.copy()  # 使用當前環境變量
            )
            
            # 等待進程啟動
            time.sleep(3)
            if new_process.poll() is None:
                logger.info(f"Django 進程成功啟動 (PID: {new_process.pid})")
                
                # 檢查端口是否被監聽
                for _ in range(5):  # 最多等待 5 秒
                    try:
                        import socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex((DJANGO_HOST, int(DJANGO_PORT)))
                        sock.close()
                        if result == 0:
                            logger.info(f"端口 {DJANGO_PORT} 已成功監聽")
                            return True
                    except:
                        pass
                    time.sleep(1)
                
                logger.error(f"端口 {DJANGO_PORT} 未被監聽")
                return False
            else:
                stdout, stderr = new_process.communicate()
                logger.error(f"Django 進程啟動失敗。錯誤信息：{stderr}")
                return False
                
        except Exception as e:
            logger.error(f"重啟過程中出錯: {str(e)}", exc_info=True)
            return False

    def main(self):
        """主要監控邏輯"""
        logger.info("=== 服務開始運行 ===")
        
        # 首次啟動時立即啟動 Django
        logger.info("正在啟動 Django 服務器...")
        if not self.restart_django():
            logger.error("首次啟動 Django 失敗")
        
        while self.running:
            try:
                django_proc = self.get_django_process()
                
                if django_proc:
                    cpu_percent = django_proc.cpu_percent(interval=1)
                    memory_percent = self.check_memory_usage(django_proc)
                    logger.info(f"系統狀態 - CPU: {cpu_percent}%, 記憶體: {memory_percent:.1f}%")
                    
                    if self.should_restart(cpu_percent, memory_percent):
                        logger.warning(f"資源使用超過閾值 (CPU: {cpu_percent}%, 記憶體: {memory_percent:.1f}%)")
                        if not self.restart_django():
                            logger.error("重啟 Django 進程失敗")
                else:
                    logger.warning("未找到 Django 進程，嘗試啟動新進程")
                    if not self.restart_django():
                        logger.error("啟動 Django 進程失敗")
                        time.sleep(10)  # 等待後重試
                
                # 檢查服務停止信號
                rc = win32event.WaitForSingleObject(self.stop_event, CHECK_INTERVAL * 1000)
                if rc == win32event.WAIT_OBJECT_0:
                    break
                
            except Exception as e:
                logger.error(f"監控過程中出錯: {str(e)}", exc_info=True)
                time.sleep(5)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DjangoService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DjangoService)