# 抠图软件

```python
import os
import sys
if sys.version_info < (3, 0): 
  import Tkinter as tk # 导入 Tkinter 库
  from tkFileDialog import askopenfilename, asksaveasfilename
else :
  import tkinter as tk # 导入 Tkinter 库
  from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import Image, ImageTk, ImageDraw
from time import sleep
import numpy as np
import cv2 as cv
DEF_WIDTH = 1080
DEF_HEIGHT = 720
IMAGE_HEIGHT = 720
FRAME_LEFT_WIDTH = 360
# 太小的选定区域我们需要丢弃，防止误操作
MINI_RECT_AREA = 20
class RawImageEditor:
  def __init__(self, win, img, rects):
    #变量X和Y用来记录鼠标左键按下的位置
    self.X = tk.IntVar(value=0)
    self.Y = tk.IntVar(value=0)
    self.sel = False
    self.lastDraw = None
    self.lastDraws = []
    self.imageScale = 1.0
    self.dispWidth = DEF_WIDTH # 图片显示区域的最大高度，宽度
    self.dispHeight = DEF_HEIGHT
    self.rawImage = img
    self.calcImageScale(self.rawImage)
    self.dispWidth = int(self.imageScale * self.rawImage.width)
    self.dispHeight = int(self.imageScale * self.rawImage.height)
    # 图片缩放
    self.dispImage = self.rawImage.resize((self.dispWidth, self.dispHeight))
    # 选择区域
    self.selPositions = []
    for r in rects :
      self.selPositions.append((r[0] * self.imageScale, r[1] * self.imageScale, r[2] * self.imageScale, r[3] * self.imageScale))
    #创建顶级组件容器
    self.top = tk.Toplevel(win, width=self.dispWidth, height=self.dispHeight)
    #不显示最大化、最小化按钮
    self.top.overrideredirect(True)
    # Make topLevelWindow remain on top until destroyed, or attribute changes.
    self.top.attributes('-topmost', 'true')
    self.canvas = tk.Canvas(self.top, bg='white', width=self.dispWidth, height=self.dispHeight)
    self.tkImage = ImageTk.PhotoImage(self.dispImage)
    self.canvas.create_image(self.dispWidth//2, self.dispHeight//2, image=self.tkImage)
    for r in self.selPositions :
      draw = self.canvas.create_rectangle(r[0], r[1], r[2], r[3], outline='green')
      self.lastDraws.append(draw)
    #鼠标左键按下的位置
    def onLeftButtonDown(event):
      self.X.set(event.x)
      self.Y.set(event.y)
      #开始截图
      self.sel = True
      #重新绘制已经选择的区域
      for draw in self.lastDraws :
        self.canvas.delete(draw)
      self.lastDraws = []
      for r in self.selPositions :
        draw = self.canvas.create_rectangle(r[0], r[1], r[2], r[3], outline='green')
        self.lastDraws.append(draw)
    self.canvas.bind('<Button-1>', onLeftButtonDown)
    #鼠标左键移动，显示选取的区域
    def onLeftButtonMove(event):
      if not self.sel:
        return
      try:
        #删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
        self.canvas.delete(self.lastDraw)
      except Exception as e:
        pass
      self.lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='green')
    self.canvas.bind('<B1-Motion>', onLeftButtonMove)
    #获取鼠标左键抬起的位置，保存区域截图
    def onLeftButtonUp(event):
      self.sel = False
      sleep(0.1)
      #考虑鼠标左键从右下方按下而从左上方抬起的截图
      left, right = sorted([self.X.get(), event.x])
      top, bottom = sorted([self.Y.get(), event.y])
      if (right - left) * (bottom - top) > MINI_RECT_AREA :
        self.selPositions.append((left,top,right,bottom))
      #self.top.destroy()
    #鼠标右键按下
    def onRightButtonDown(event):
      self.sel = False
      self.top.destroy()
    self.canvas.bind('<Button-2>', onRightButtonDown)
    self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)
    self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
  def calcImageScale(self, image) :
    w = image.width
    h = image.height
    self.imageScale = 1.0
    # 计算最小的缩放比例，保证原始宽高比
    if w > self.dispWidth and h > self.dispHeight :
      ws = self.dispWidth * 1.0 / w
      hs = self.dispHeight * 1.0 / h
      if ws < hs :
        self.imageScale = ws
      else :
        self.imageScale = hs
    elif w > self.dispWidth and h < self.dispHeight :
      self.imageScale = self.dispWidth * 1.0 / w
    elif w < self.dispWidth and h > self.dispHeight :
      self.imageScale = self.dispHeight * 1.0 / h
  def waitForWindow(self, win) :      
    win.wait_window(self.top)
  def selectedPositions(self) : 
    # 转换为原始像素位置
    realPos = []
    for r in self.selPositions :
      realPos.append((r[0] / self.imageScale, r[1] / self.imageScale, r[2] / self.imageScale, r[3] / self.imageScale))
    return realPos   
class MainWin(tk.Tk):
  def __init__(self):
    if sys.version_info >= (3, 0):
      super().__init__()
    else : 
      tk.Tk.__init__(self)
    self.title('图像处理工具')
    self.geometry('{}x{}'.format(DEF_WIDTH, DEF_HEIGHT))
    self.rawImagePath = ''
    self.rawImage = None # self.rawImage 原始图像，未经过缩放处理
    self.transRawImage = None # self.transRawImage 经过转换处理之后的原始图像，没有经过缩放处理
    self.dispImage = None # self.dispImage 显示图像，可能经过缩放处理
    self.imageScale = 1.0 # 图片缩放比例，根据缩放比例进行显示的时候的缩放处理，后期选择区域的时候，需要进行缩放还原
    self.leftFrameWidth = FRAME_LEFT_WIDTH
    self.frameDispHeight = DEF_HEIGHT # 整个窗口的高度
    self.labelTextHeight = 20 # 文本标签的高度
    self.btnHeight = 40 # 按钮的高度
    self.imageDispWidth = IMAGE_HEIGHT # 图片显示区域的最大高度，宽度
    self.imageDispHeight = self.frameDispHeight / 2 - self.labelTextHeight * 2
    # 选择区域
    self.liRect = []
    self.rawImageEditor = None
    self.setupUI()
  def scaleDisplayImage(self, image) :
    w = image.width
    h = image.height
    self.imageScale = 1.0
    # 计算最小的缩放比例，保证原始宽高比
    if w > self.imageDispWidth and h > self.imageDispHeight :
      ws = self.imageDispWidth * 1.0 / w
      hs = self.imageDispHeight * 1.0 / h
      if ws < hs :
        self.imageScale = ws
      else :
        self.imageScale = hs
    elif w > self.imageDispWidth and h < self.imageDispHeight :
      self.imageScale = self.imageDispWidth * 1.0 / w
    elif w < self.imageDispWidth and h > self.imageDispHeight :
      self.imageScale = self.imageDispHeight * 1.0 / h
    # 图片缩放
    return image.resize((int(self.imageScale * w), int(self.imageScale * h)))
  
  # 打开图片时使用，传值（图）给展示函数
  def openAndDisplayImage(self):
    self.rawImagePath = self.selectImageFile()
    if '' != self.rawImagePath :
      self.rawImage = Image.open(self.rawImagePath)
      self.rawImage = self.rawImage.convert('RGBA')
      self.drawRawImageDisp()
  def drawListBox(self):
    self.l_box.delete(0,tk.END)
    for item in self.liRect:
      r = '{},{},{},{}'.format(round(item[0],1), round(item[1],1), round(item[2],1), round(item[3],1))
      self.l_box.insert(0, r)
  def drawRawImageDisp(self, selItems=[]):      
    self.dispImage = self.scaleDisplayImage(self.rawImage)
    self.dispImage = self.dispImage.convert('RGB')
    draw = ImageDraw.Draw(self.dispImage)
    for i in range(len(self.liRect)) :
      r = self.liRect[i]
      if i in selItems :
        draw.rectangle((r[0] * self.imageScale, r[1] * self.imageScale, r[2] * self.imageScale, r[3] * self.imageScale), outline = "red")
      else :
        draw.rectangle((r[0] * self.imageScale, r[1] * self.imageScale, r[2] * self.imageScale, r[3] * self.imageScale), outline = "green")
    img = ImageTk.PhotoImage(self.dispImage)
    self.image_l_raw.config(image=img)
    self.image_l_raw.image = img
  def deleteSelectedItemFromListBox(self):
    #print(self.l_box.get(self.l_box.curselection()))
    idx = self.l_box.curselection()
    if len(idx) > 0 :
      kp = []
      for v in range(len(self.liRect)) :
        if v not in idx :
          kp.append(self.liRect[v])
      self.liRect = kp
      self.drawListBox() 
      self.drawRawImageDisp() 
  # 打开图片时使用，获得地址
  def selectImageFile(self):
    path = tk.StringVar()
    file_entry = tk.Entry(self, state='readonly', text=path)
    path_ = askopenfilename()
    path.set(path_)
    return file_entry.get()
  def rawImageLabelClicked(self, event):
    if None != self.rawImage :
      if None == self.rawImageEditor :
        self.rawImageEditor = RawImageEditor(self, self.rawImage, self.liRect)
        self.rawImageEditor.waitForWindow(self.image_l_raw)
        self.liRect = self.rawImageEditor.selectedPositions()
        self.rawImageEditor = None
        self.drawListBox()
        self.drawRawImageDisp()
  def onRectListboxSelect(self, event):
    idx = self.l_box.curselection()
    if len(idx) > 0 :
      self.drawRawImageDisp(idx)
  def drawTransImageDisp(self):      
    transImage = self.scaleDisplayImage(self.transRawImage)
    transImage = transImage.convert('L')
    img = ImageTk.PhotoImage(transImage)
    self.image_l_trans.config(image=img)
    self.image_l_trans.image = img
  def doTransRawImage(self):
    self.transRawImage = Image.new('L', (self.rawImage.width, self.rawImage.height))
    for r in self.liRect :
      im = self.rawImage.crop(r)
      cv_im = cv.cvtColor(np.asarray(im), cv.COLOR_RGB2BGR)
      hsv = cv.cvtColor(cv_im, cv.COLOR_BGR2HSV)
      _, _, v = cv.split(hsv)
      avg = np.average(v.flatten())
      pixels = im.load()
      for j in range(im.height) :
        for i in range(im.width) :
          hv = v[j,i]
          if hv < avg * 1.2:
            #im.putpixel((i, j), 0) # slow
            pixels[i, j] = 0
          '''else :
            im.putpixel((i, j), (255, 255, 255, 255))'''
      self.transRawImage.paste(im, (int(r[0]),int(r[1])), mask = None) 
    self.drawTransImageDisp()
  def onTransRawImageBtnClicked(self):
    if None != self.rawImage :
      self.doTransRawImage()
  def onSaveTransRawImageBtnClicked(self):
    if None != self.transRawImage :
      ext = os.path.splitext(self.rawImagePath)[-1]
      (path,name) = os.path.split(self.rawImagePath)
      filename = asksaveasfilename(title = '保存图片', initialfile = name, filetypes = (("jpeg files","*{}".format(ext)), ("all files","*.*")))
      if '' != filename :
        self.transRawImage.save(filename)     
  def setupUI(self):
    # 左边菜单栏
    left_f = tk.Frame(self, height=self.frameDispHeight, width=self.leftFrameWidth)
    left_f.pack(side=tk.LEFT)
    # 各种功能按钮名称及位置
    btnOpen = tk.Button(left_f, text='打开图像', command=self.openAndDisplayImage)
    btnOpen.place(y=25, x=30, width=300, height=self.btnHeight)
    btnTrans = tk.Button(left_f, text='处理图像', command=self.onTransRawImageBtnClicked)
    btnTrans.place(y=85, x=30, width=300, height=self.btnHeight)
    l_selRect = tk.Label(left_f, text = '鼠标选定区域')
    l_selRect.place(x=0, y=165, width=self.leftFrameWidth, height=self.labelTextHeight)
    '''列表'''
    self.l_box = tk.Listbox(left_f) # 创建两个列表组件
    self.l_box.place(x=0, y=165+self.labelTextHeight, width=self.leftFrameWidth, height=270)
    self.l_box.bind('<<ListboxSelect>>', self.onRectListboxSelect)
    self.drawListBox()
    # 删除选定项
    btnDel = tk.Button(left_f, text='删除选定项', command=self.deleteSelectedItemFromListBox)
    btnDel.place(y=460, x=30, width=300, height=self.btnHeight)
    btnSave = tk.Button(left_f, text='保存结果', command=self.onSaveTransRawImageBtnClicked)
    btnSave.place(y=550, x=30, width=300, height=self.btnHeight)
    # 右侧图像显示栏
    right_f = tk.Frame(self, height=self.frameDispHeight, width=self.imageDispWidth)
    right_f.pack(side=tk.RIGHT)
    l_rawT = tk.Label(right_f, text = '原始图片')
    l_rawT.place(x=0, y=0, width=self.imageDispWidth, height=self.labelTextHeight)
    self.image_l_raw = tk.Label(right_f, relief='ridge')
    self.image_l_raw.place(x=0, y=self.labelTextHeight, width=self.imageDispWidth, height=self.imageDispHeight)
    self.image_l_raw.bind("<Button-1>",self.rawImageLabelClicked)
    l_transT = tk.Label(right_f, text = '处理后图片')
    l_transT.place(x=0, y=self.labelTextHeight + self.imageDispHeight, width=self.imageDispWidth, height=self.labelTextHeight)
    self.image_l_trans = tk.Label(right_f, relief='ridge')
    self.image_l_trans.place(x=0, y=self.labelTextHeight + self.imageDispHeight + self.labelTextHeight, width=self.imageDispWidth, height=self.imageDispHeight)
if __name__ == '__main__' :
  win = MainWin()
  # 进入消息循环
  win.mainloop()
```