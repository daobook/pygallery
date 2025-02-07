from tkinter import Tk, ttk
from contextlib import ContextDecorator
from dataclasses import dataclass
from typing import Coroutine
import asyncio
from asyncio.events import AbstractEventLoop
import threading
import time

@dataclass
class Scheduler(ContextDecorator):
    coro: Coroutine
    loop: AbstractEventLoop

    def __post_init__(self):
        # 初始化
        self.thread = None
        self.future = None

    def __call__(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(
                target=self.start_loop, 
                daemon=True, # 保证设置子线程为守护线程，当主线程结束时，守护线程会自动结束
            )   #通过当前线程开启新的线程去启动事件循环
            self.thread.start()
            # 在新线程中事件循环不断“游走”执行
            self.future = asyncio.run_coroutine_threadsafe(self.coro, self.loop)

    def start_loop(self):
        """定义专门创建事件循环 loop 的函数，在另一个线程中启动它"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def __enter__(self):
        print(f'启动：{self.coro}@{self.loop}')
        return self

    def __exit__(self, *exc):
        print(f'离开：{self.coro}@{self.loop}')
        return False


class Window(Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.geometry('500x300')
        self.button = ttk.Button(self, text="开始计算", command=self.change_form_state)
        self.label = ttk.Label(master=self, text="等待计算结果")
        self.button.pack()
        self.label.pack()

    async def calculate(self):
        await asyncio.sleep(3)
        self.label["text"] = 300
 
    def get_loop(self,loop):
        self.loop = loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def change_form_state(self):
        self.label["text"] = "等待计算结果"
        coroutine1 = self.calculate()
        new_loop = asyncio.new_event_loop()                        #在当前线程下创建时间循环，（未启用），在start_loop里面启动它
        t = threading.Thread(target=self.get_loop,args=(new_loop,))   #通过当前线程开启新的线程去启动事件循环
        t.start()
        asyncio.run_coroutine_threadsafe(coroutine1, new_loop)  #这几个是关键，代表在新线程中事件循环不断“游走”执行



async def async_task(num):
    print(f'准备调用, {time.asctime()}')
    res = await asyncio.sleep(1, result=num*2)
    print(f'函数运行结束 {time.asctime()}')
    return res

async def async_tasks():
    for num in range(5):
        await async_task(num)

if __name__ == "__main__":
    new_loop = asyncio.new_event_loop()
    scheduler = Scheduler(async_tasks(), new_loop)
    scheduler()
    print(scheduler.future.result())
    print(scheduler.thread.is_alive())
    # root = Window()
    # root.mainloop()
