从 PyPI（pip）获取
-----------------

ModernGL 在 PyPI 上提供了适用于 Windows、OS X 和 Linux 的预构建 wheel 包。除非你正在设置开发环境，否则无需进行复杂的配置。

.. code-block:: sh

    $ pip install moderngl

验证包是否正常工作：

.. code:: sh

    $ python -m moderngl
    moderngl 5.6.0
    --------------
    vendor: NVIDIA Corporation
    renderer: GeForce RTX 2080 SUPER/PCIe/SSE2
    version: 3.3.0 NVIDIA 441.87
    python: 3.7.6 (tags/v3.7.6:43364a7ae0, Dec 19 2019, 00:42:30) [MSC v.1916 64 bit (AMD64)]
    platform: win32
    code: 330

.. 注意:: 如果你遇到问题，可能与上下文创建有关。在某些情况下，可能需要更多的配置才能运行 moderngl。尤其是在没有 X 的 Linux 系统上运行时。请参阅上下文部分。

开发环境
-----------------------

理想情况下，你首先需要 fork 仓库。

.. code-block:: sh

    # .. 或者克隆你的 fork
    git clone https://github.com/moderngl/moderngl.git
    cd moderngl

在不同平台上构建：

* 在 Windows 上，你需要安装 Visual C++ 构建工具：
  https://visualstudio.microsoft.com/visual-cpp-build-tools/
* 在 OS X 上，你需要安装 X Code 和命令行工具（``xcode-select --install``）
* 在 Linux 上构建应该可以直接运行
* 要编译 moderngl：``python setup.py build_ext --inplace``

包和开发依赖项：

* 安装 ``requirements.txt``、``tests/requirements.txt`` 和 ``docs/requirements.txt``
* 以可编辑模式安装包：``pip install -e .``

在 Windows 上与 Mesa 3D 一起使用
-----------------------------

如果你的旧显卡在运行 moderngl 时出现错误，可以尝试使用此方法使其正常工作。

基本上有两种方法：

* 自行编译 Mesa，请参阅 https://docs.mesa3d.org/install.html。
* 使用 msys2，它提供了预编译的 Mesa 二进制文件。

使用 MSYS2
___________

* 下载并安装 https://www.msys2.org/#installation
* 检查你使用的是 32 位还是 64 位 Python。

32 位 Python
+++++++++++++

如果你使用的是 32 位 Python，请打开 ``C:\msys64\mingw32.exe`` 并输入以下命令

.. code-block:: sh

    pacman -S mingw-w64-i686-mesa

它将安装 Mesa 及其依赖项。然后你可以将 ``C:\msys64\mingw32\bin`` 添加到 PATH 中，并在 ``C:\Windows`` 之前设置，moderngl 应该可以正常工作。此外，你应该设置一个名为 ``GLCONTEXT_WIN_LIBGL`` 的环境变量，其中包含 Mesa 中 opengl32 dll 的路径。在这种情况下，它应该是 ``GLCONTEXT_WIN_LIBGL=C:\msys64\mingw32\bin\opengl32.dll``。

64 位 Python
+++++++++++++

如果你使用的是 64 位 Python，请打开 ``C:\msys64\mingw64.exe`` 并输入以下命令

.. code-block:: sh

    pacman -S mingw-w64-x86_64-mesa

它将安装 Mesa 及其依赖项。然后你可以将 ``C:\msys64\mingw64\bin`` 添加到 PATH 中，并在 ``C:\Windows`` 之前设置，moderngl 应该可以正常工作。此外，你应该设置名为 ``GLCONTEXT_WIN_LIBGL`` 的环境变量，其中包含 Mesa 中 opengl32 dll 的路径。在这种情况下，它应该是 ``GLCONTEXT_WIN_LIBGL=C:\msys64\mingw64\bin\opengl32.dll``。