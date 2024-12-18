Manim 的输出设置
================

本文档将重点介绍如何理解 manim 的输出文件以及一些主要的命令行标志。

.. note:: 本教程承接 :doc:`quickstart` 的内容，因此请在开始阅读本文档之前先阅读该文档。

Manim 输出文件夹
****************

此时，您刚刚执行了以下命令。

.. 代码块:: bash

   manim -pql scene.py SquareToCircle

让我们逐步分析刚刚发生的事情。首先，此命令在包含我们动画代码的文件 ``scene.py`` 上执行 manim。此外，此命令告诉 manim 要渲染哪个 ``Scene``，在本例中为 ``SquareToCircle``。这是必要的，因为单个场景文件可能包含多个场景。接下来，标志 `-p` 告诉 manim 在渲染完成后播放场景，而 `-ql` 标志告诉 manim 以低质量渲染场景。

视频渲染完成后，您会看到 manim 生成了一些新文件，项目文件夹将如下所示。

.. code-block:: bash

   project/
   ├─scene.py
   └─media
     ├─videos
     |  └─scene
     |     └─480p15
     |        ├─SquareToCircle.mp4
     |        └─partial_movie_files
     ├─text
     └─Tex


有很多新文件。主要输出在 ``media/videos/scene/480p15/SquareToCircle.mp4`` 中。默认情况下，``media`` 文件夹将包含所有 manim 的输出文件。``media/videos`` 子文件夹包含渲染后的视频。在其中，你会发现每个不同视频质量的文件夹。在我们的例子中，由于我们使用了 ``-l`` 标志，视频以 480 分辨率和每秒 15 帧的速度从 ``scene.py`` 文件生成。因此，输出可以在 ``media/videos/scene/480p15`` 中找到。额外的文件夹 ``media/videos/scene/480p15/partial_movie_files`` 以及 ``media/text`` 和 ``media/Tex`` 包含 manim 内部使用的文件。

你可以通过执行以下命令来查看 manim 如何利用生成的文件夹结构：

.. code-block:: bash

   manim -pqh scene.py SquareToCircle

``-ql`` 标志（用于低质量）已被 ``-qh`` 标志（用于高质量）取代。Manim 将花费相当长的时间来渲染这个文件，并且由于我们使用了 ``-p`` 标志，它会在完成后播放视频。输出应该如下所示：

.. manim:: SquareToCircle3
   :hide_source:
   :quality: high

   class SquareToCircle3(Scene):
       def construct(self):
           circle = Circle()                    # 创建一个圆
           circle.set_fill(PINK, opacity=0.5)   # 设置颜色和不透明度

           square = Square()                    # 创建一个正方形
           square.flip(RIGHT)                   # 水平翻转
           square.rotate(-3 * TAU / 8)          # 旋转一定角度

           self.play(Create(square))      # 动画创建正方形
           self.play(Transform(square, circle)) # 将正方形插值为圆
           self.play(FadeOut(square))           # 淡出动画

文件夹结构应该如下所示：

.. code-block:: bash

   project/
   ├─scene.py
   └─media
     ├─videos
     | └─scene
     |   ├─480p15
     |   | ├─SquareToCircle.mp4
     |   | └─partial_movie_files
     |   └─1080p60
     |     ├─SquareToCircle.mp4
     |     └─partial_movie_files
     ├─text
     └─Tex

Manim 创建了一个新的文件夹 ``media/videos/1080p60``，对应于高分辨率和每秒 60 帧。在其中，你可以找到新的 ``SquareToCircle.mp4``，以及相应的 ``partial_movie_files``。

当在一个包含多个场景的项目中工作，并尝试多种分辨率时，输出目录的结构将保持所有视频的组织性。

此外，manim 可以选择输出场景的最后一帧，通过添加 ``-s`` 标志。这是快速预览场景的最快选项。相应的文件夹结构如下所示：

.. code-block:: bash

   project/
   ├─scene.py
   └─media
     ├─images
     | └─scene
     |   ├─SquareToCircle.png
     ├─videos
     | └─scene
     |   ├─480p15
     |   | ├─SquareToCircle.mp4
     |   | └─partial_movie_files
     |   └─1080p60
     |     ├─SquareToCircle.mp4
     |     └─partial_movie_files
     ├─text
     └─Tex

使用 ``-s`` 保存最后一帧可以与不同分辨率的标志结合使用，例如 ``-s -ql``，``-s -qh``。

部分
********

除了电影输出文件外，还可以使用部分。每个部分都会生成自己的输出视频。两个部分之间的剪辑可以这样设置：

.. code-block:: python

    def construct(self):
        # 播放第一个动画...
        # 在最开始不需要部分，因为它会自动创建
        self.next_section()
        # 播放更多动画...
        self.next_section("这是一个可选的名称，不必唯一")
        # 播放更多动画...
        self.next_section("这是一个没有任何动画的部分，它将被删除")

所有在这两个剪辑之间的动画会被连接成一个单独的输出视频文件。
请注意，每个部分至少需要一个动画。例如，以下代码不会创建输出视频：

.. code-block:: python

   def construct(self):
       self.next_section()
       # 这个部分没有任何动画，将被删除
       # 但不会抛出错误
       # 如果你愿意，可以随意添加一堆空部分
       self.add(Circle())
       self.next_section()

解决这个问题的一种方法是等待一会儿：

.. code-block:: python

   def construct(self):
       self.next_section()
       self.add(Circle())
       # 现在我们等待1秒，这样就有了一个动画来满足部分的要求
       self.wait()
       self.next_section()

要为每个部分创建视频，你需要在Manim调用中添加 ``--save_sections`` 标志，如下所示：

.. code-block:: bash

   manim --save_sections scene.py

如果你这样做，``media`` 文件夹将如下所示：

.. code-block:: bash

    media
    ├── images
    │   └── simple_scenes
    └── videos
        └── simple_scenes
            └── 480p15
                ├── ElaborateSceneWithSections.mp4
                ├── partial_movie_files
                │   └── ElaborateSceneWithSections
                │       ├── 2201830969_104169243_1331664314.mp4
                │       ├── 2201830969_398514950_125983425.mp4
                │       ├── 2201830969_398514950_3447021159.mp4
                │       ├── 2201830969_398514950_4144009089.mp4
                │       ├── 2201830969_4218360830_1789939690.mp4
                │       ├── 3163782288_524160878_1793580042.mp4
                │       └── partial_movie_file_list.txt
                └── sections
                    ├── ElaborateSceneWithSections_0000.mp4
                    ├── ElaborateSceneWithSections_0001.mp4
                    ├── ElaborateSceneWithSections_0002.mp4
                    └── ElaborateSceneWithSections.json

如你所见，每个部分在 ``sections`` 目录中都会生成自己的输出视频。这里的 JSON 文件包含了一些对每个部分有用的信息：

.. code-block:: json

    [
        {
            "name": "create square",
            "type": "default.normal",
            "video": "ElaborateSceneWithSections_0000.mp4",
            "codec_name": "h264",
            "width": 854,
            "height": 480,
            "avg_frame_rate": "15/1",
            "duration": "2.000000",
            "nb_frames": "30"
        },
        {
            "name": "transform to circle",
            "type": "default.normal",
            "video": "ElaborateSceneWithSections_0001.mp4",
            "codec_name": "h264",
            "width": 854,
            "height": 480,
            "avg_frame_rate": "15/1",
            "duration": "2.000000",
            "nb_frames": "30"
        },
        {
            "name": "fade out",
            "type": "default.normal",
            "video": "ElaborateSceneWithSections_0002.mp4",
            "codec_name": "h264",
            "width": 854,
            "height": 480,
            "avg_frame_rate": "15/1",
            "duration": "2.000000",
            "nb_frames": "30"
        }
    ]

这些数据可以被第三方应用程序使用，例如演示系统或自动视频编辑工具。

你也可以跳过渲染属于某个部分的所有动画，如下所示：

.. code-block:: python

    def construct(self):
        self.next_section(skip_animations=True)
        # play some animations that shall be skipped...
        self.next_section()
        # play some animations that won't get skipped...


一些命令行标志
***********************

在执行命令时

.. code-block:: bash

   manim -pql scene.py SquareToCircle

它指定了要渲染的场景。现在这并不是必需的。当一个文件只包含一个 ``Scene`` 类时，它将直接渲染该 ``Scene`` 类。当一个文件包含多个 ``Scene`` 类时，Manim 会让你选择一个 ``Scene`` 类。如果你的文件包含多个 ``Scene`` 类，并且你想渲染它们全部，可以使用 ``-a`` 标志。

如前所述，``-ql`` 指定了低渲染质量（854x480 15FPS）。这看起来不是很好，但对于快速原型设计和测试非常有用。其他指定渲染质量的选项包括 ``-qm``、``-qh``、``-qp`` 和 ``-qk``，分别对应中等（1280x720 30FPS）、高（1920x1080 60FPS）、2k（2560x1440 60FPS）和 4k 质量（3840x2160 60FPS）。

``-p`` 标志会在渲染完成后播放动画。如果你想在文件浏览器中打开动画文件的位置而不是播放它，可以使用 ``-f`` 标志。你也可以省略这两个标志。

最后，默认情况下，Manim 会输出 .mp4 文件。如果你想将动画输出为 ``.gif`` 格式，可以使用 ``--format gif`` 标志。输出文件将与 .mp4 文件位于同一文件夹中，并且具有相同的名称，但文件扩展名不同。

这是对一些最常用的命令行标志的快速回顾。有关所有可用标志的详细回顾，请参阅 :doc:`关于 Manim 配置系统的主题指南 </guides/configuration>`。