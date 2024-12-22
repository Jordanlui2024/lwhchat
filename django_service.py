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
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'django_service.log')

# 配置日誌處理器，使用系統編碼
file_handler = logging.FileHandler(log_path, encoding=system_encoding)
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
CHECK_INTERVAL = 30     # 檢查間隔（秒）
MAX_RESTART_ATTEMPTS = 3 # 最大重啟嘗試次數
RESTART_COOLDOWN = 300  # 重啟冷卻時間（秒）
DJANGO_SCRIPT = "manage.py"  # Django 啟動腳本
PYTHON_PATH = r"C:\HOMEPAGE\django_chat\venv-djangochat\Scripts\python.exe"  # 修改為虛擬環境的 Python 路徑
DJANGO_HOST = "0.0.0.0"     # 監聽地址
DJANGO_PORT = "8880"        # 監聽端口

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
        """判斷是否需要重啟"""
        current_time = time.time()
        
        if current_time - self.last_restart_time < RESTART_COOLDOWN:
            return False
            
        if self.restart_attempts >= MAX_RESTART_ATTEMPTS:
            logger.warning("已達到最大重啟次數限制")
            self.restart_attempts = 0
            self.last_restart_time = current_time
            return False
            
        return cpu_percent >= CPU_THRESHOLD or memory_percent >= MEMORY_THRESHOLD

    def restart_django(self):
        """重啟 Django 進程"""
        django_proc = self.get_django_process()
        if django_proc:
            old_pid = django_proc.pid
            logger.info(f"正在關閉 Django 進程 (PID: {old_pid})")
            
            try:
                django_proc.terminate()
                django_proc.wait(timeout=10)
            except psutil.TimeoutExpired:
                django_proc.kill()
            
            logger.info(f"成功關閉舊進程 (PID: {old_pid})")

        try:
            # 指定完整的工作目錄路徑
            working_dir = r"C:\HOMEPAGE\django_chat\djangochat"
            new_process = subprocess.Popen(
                [PYTHON_PATH, DJANGO_SCRIPT, "runserver", f"{DJANGO_HOST}:{DJANGO_PORT}"],
                cwd=working_dir
            )
            logger.info(f"已啟動新的 Django 進程 (PID: {new_process.pid}) 在 {DJANGO_HOST}:{DJANGO_PORT}")
            return True
        except Exception as e:
            logger.error(f"啟動新進程時出錯: {str(e)}")
            return False

    def main(self):
        """主要監控邏輯"""
        while self.running:
            django_proc = self.get_django_process()
            
            if django_proc:
                try:
                    cpu_percent = django_proc.cpu_percent(interval=1)
                    memory_percent = self.check_memory_usage(django_proc)
                    logger.info(f"系統狀態 - CPU: {cpu_percent}%, 記憶體: {memory_percent:.1f}%")
                    
                    if self.should_restart(cpu_percent, memory_percent):
                        logger.warning(f"資源使用超過閾值 (CPU: {cpu_percent}%, 記憶體: {memory_percent:.1f}%)")
                        self.restart_attempts += 1
                        self.last_restart_time = time.time()
                        
                        if self.restart_django():
                            logger.info(f"Django 進程已成功重啟 (嘗試次數: {self.restart_attempts})")
                        else:
                            logger.error("重啟 Django 進程失敗")
                except Exception as e:
                    logger.error(f"監控進程時出錯: {str(e)}", exc_info=True)
            else:
                logger.warning("未找到 Django 進程，嘗試啟動新進程")
                self.restart_django()
            
            rc = win32event.WaitForSingleObject(self.stop_event, CHECK_INTERVAL * 1000)
            if rc == win32event.WAIT_OBJECT_0:
                break

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DjangoService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DjangoService)