import threading
import time

# 创建一个 Event 对象
stop_event = threading.Event()

def worker():
    while not stop_event.is_set():
        print("Working...")
        time.sleep(1)
    print("Worker stopped.")

# 创建并启动工作线程
worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()

# 主线程等待一段时间
time.sleep(5)

# 设置 Event，通知工作线程停止
stop_event.set()

# 等待工作线程结束
worker_thread.join()
print("Main thread exits.")
