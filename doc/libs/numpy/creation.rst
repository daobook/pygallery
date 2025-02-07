.. _arrays.creation:


**************
数组创建
**************

.. seealso:: :ref:`数组创建例程 <routines.array-creation>`

介绍
============

有 6 种通用机制来创建数组：

1. 从其他 Python 结构（即列表和元组）转换
2. 内置的 NumPy 数组创建函数（例如 arange、ones、zeros等）
3. 复制、连接或修改现有数组
4. 从磁盘读取数组，无论是标准格式还是自定义格式
5. 通过使用字符串或缓冲区从原始字节创建数组
6. 使用特殊库函数（例如，random）

您可以使用这些方法来创建 ndarrays 或 :ref:`结构化数组 <structured_arrays>`。
本文档将介绍ndarray创建的一般方法。

1) 将 Python 序列转换为 NumPy 数组
==============================================

NumPy 数组可以使用 Python 序列（如列表和元组）来定义。列表和元组分别使用 ``[...]`` 和 ``(...)`` 来定义。列表和元组可以用于定义 ndarray 的创建：

* 一个数字列表将创建一个一维数组，
* 一个列表的列表将创建一个二维数组，
* 进一步嵌套的列表将创建更高维度的数组。通常，NumPy 中的任何数组对象都称为 **ndarray**。

::

  >>> import numpy as np
  >>> a1D = np.array([1, 2, 3, 4])
  >>> a2D = np.array([[1, 2], [3, 4]])
  >>> a3D = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

当你使用 :func:`numpy.array` 定义一个新数组时，你应该考虑数组元素的 :doc:`dtype <basics.types>`，它可以显式指定。这个特性让你可以更好地控制底层数据结构以及元素在 C/C++ 函数中的处理方式。

当值不匹配且你使用了 ``dtype`` 时，NumPy 可能会抛出错误::

  >>> import numpy as np
  >>> np.array([127, 128, 129], dtype=np.int8)
  Traceback (most recent call last):
  ...
  OverflowError: Python integer 128 out of bounds for int8

一个 8 位有符号整数表示从 -128 到 127 的整数。将 ``int8`` 数组分配给超出此范围的整数会导致溢出。这个特性经常被误解。如果你使用不匹配的 ``dtype`` 进行计算，你可能会得到不想要的结果，例如::

    >>> import numpy as np
    >>> a = np.array([2, 3, 4], dtype=np.uint32)
    >>> b = np.array([5, 6, 7], dtype=np.uint32)
    >>> c_unsigned32 = a - b
    >>> print('unsigned c:', c_unsigned32, c_unsigned32.dtype)
    unsigned c: [4294967293 4294967293 4294967293] uint32
    >>> c_signed32 = a - b.astype(np.int32)
    >>> print('signed c:', c_signed32, c_signed32.dtype)
    signed c: [-3 -3 -3] int64

注意当你使用两个具有相同 ``dtype`` 的数组进行操作时：``uint32``，结果数组是相同类型。当你使用不同 ``dtype`` 的数组进行操作时，NumPy 会分配一个新类型，该类型可以满足计算中涉及的所有数组元素，这里 ``uint32`` 和 ``int32`` 都可以表示为 ``int64``。

NumPy 的默认行为是创建 32 位或 64 位有符号整数（平台相关，并与 C 的 ``long`` 大小匹配）或双精度浮点数数组。如果你希望你的整数数组是特定类型，那么你需要在创建数组时指定 dtype。

2) 内置的 NumPy 数组创建函数
===========================================

..
  40 个函数看起来数量不多，但 `routines.array-creation` 中大约有 47 个。我相信还有更多。

NumPy 提供了超过 40 个内置函数用于创建数组，这些函数在 :ref:`数组创建例程 <routines.array-creation>` 中有详细介绍。这些函数大致可以分为三类，基于它们创建的数组维度：

1) 一维数组
2) 二维数组
3) 多维数组（ndarrays）

1 - 一维数组创建函数
-------------------------------

一维数组创建函数，例如 :func:`numpy.linspace` 和 :func:`numpy.arange`，通常需要至少两个输入参数，``start`` 和 ``stop``。

:func:`numpy.arange` 创建一个包含规则递增值的数组。请查阅文档以获取完整信息和示例。以下是一些示例::

 >>> import numpy as np
 >>> np.arange(10)
 array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
 >>> np.arange(2, 10, dtype=float)
 array([2., 3., 4., 5., 6., 7., 8., 9.])
 >>> np.arange(2, 3, 0.1)
 array([2. , 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9])

注意：使用 :func:`numpy.arange` 的最佳实践是使用整数作为 ``start``、``end`` 和 ``step`` 值。关于 ``dtype`` 有一些细微差别。在第二个示例中，``dtype`` 被定义。在第三个示例中，数组的 ``dtype=float`` 以适应 ``0.1`` 的步长。由于舍入误差，有时会包含 ``stop`` 值。

:func:`numpy.linspace` 将创建一个包含指定数量元素的数组，这些元素在指定的起始值和结束值之间均匀分布。例如：::

 >>> import numpy as np
 >>> np.linspace(1., 4., 6)
 array([1. ,  1.6,  2.2,  2.8,  3.4,  4. ])

这种创建函数的优点是你可以保证元素的数量以及起始点和结束点。之前的 ``arange(start, stop, step)`` 不会包含 ``stop`` 值。

2 - 二维数组创建函数
-------------------------------

二维数组创建函数，例如 :func:`numpy.eye`、:func:`numpy.diag` 和 :func:`numpy.vander`，定义了以二维数组表示的特殊矩阵的属性。

``np.eye(n, m)`` 定义了一个二维单位矩阵。其中 i=j（行索引和列索引相等）的元素为 1，其余为 0，如下所示::

 >>> import numpy as np
 >>> np.eye(3)
 array([[1., 0., 0.],
        [0., 1., 0.],
        [0., 0., 1.]])
 >>> np.eye(3, 5)
 array([[1., 0., 0., 0., 0.],
        [0., 1., 0., 0., 0.],
        [0., 0., 1., 0., 0.]])

:func:`numpy.diag` 可以定义一个对角线上有给定值的方形二维数组，或者如果给定一个二维数组，则返回一个仅包含对角线元素的一维数组。这两种数组创建函数在做线性代数时非常有用，例如::
 
 >>> import numpy as np
 >>> np.diag([1, 2, 3])
 array([[1, 0, 0],
        [0, 2, 0],
        [0, 0, 3]])
 >>> np.diag([1, 2, 3], 1)
 array([[0, 1, 0, 0],
        [0, 0, 2, 0],
        [0, 0, 0, 3],
        [0, 0, 0, 0]])
 >>> a = np.array([[1, 2], [3, 4]])
 >>> np.diag(a)
 array([1, 4])

``vander(x, n)`` 定义了一个范德蒙矩阵（Vandermonde matrix），作为二维 NumPy 数组。范德蒙矩阵的每一列是输入的一维数组或列表或元组 ``x`` 的递减幂，其中最高多项式阶数为 ``n-1``。这种数组创建例程在生成线性最小二乘模型时非常有用，例如::

 >>> import numpy as np
 >>> np.vander(np.linspace(0, 2, 5), 2)
 array([[0. , 1. ],
       [0.5, 1. ],
       [1. , 1. ],
       [1.5, 1. ],
       [2. , 1. ]])
 >>> np.vander([1, 2, 3, 4], 2)
 array([[1, 1],
        [2, 1],
        [3, 1],
        [4, 1]])
 >>> np.vander((1, 2, 3, 4), 4)
 array([[ 1,  1,  1,  1],
        [ 8,  4,  2,  1],
        [27,  9,  3,  1],
        [64, 16,  4,  1]])
 
3 - 通用多维数组创建函数
--------------------------------------

多维数组创建函数，例如 :func:`numpy.ones`、:func:`numpy.zeros` 和 :meth:`~numpy.random.Generator.random`，基于所需的形状定义数组。这些多维数组创建函数可以通过指定元组或列表中的维度和每个维度的长度来创建任意维度的数组。

:func:`numpy.zeros` 将创建一个填充了 0 值的数组，形状由指定的形状决定。默认的 ``dtype`` 是 ``float64``::

 >>> import numpy as np
 >>> np.zeros((2, 3))
 array([[0., 0., 0.], 
        [0., 0., 0.]])
 >>> np.zeros((2, 3, 2))
 array([[[0., 0.],
         [0., 0.],
         [0., 0.]],
 <BLANKLINE>        
        [[0., 0.],
         [0., 0.],
         [0., 0.]]])

:func:`numpy.ones` 将创建一个填充了 1 值的数组。它在所有其他方面与 ``zeros`` 相同，例如::

 >>> import numpy as np
 >>> np.ones((2, 3))
 array([[1., 1., 1.], 
        [1., 1., 1.]])
 >>> np.ones((2, 3, 2))
 array([[[1., 1.],
         [1., 1.],
         [1., 1.]],
 <BLANKLINE>
        [[1., 1.],
         [1., 1.],
         [1., 1.]]])

:meth:`~numpy.random.Generator.random` 方法是 ``default_rng`` 的结果，将创建一个填充了 0 到 1 之间随机值的数组。它包含在 :func:`numpy.random` 库中。下面创建了两个形状分别为 (2,3) 和 (2,3,2) 的数组。种子设置为 42，以便你可以重现这些伪随机数::

 >>> import numpy as np
 >>> from numpy.random import default_rng
 >>> default_rng(42).random((2,3))
 array([[0.77395605, 0.43887844, 0.85859792],
        [0.69736803, 0.09417735, 0.97562235]])
 >>> default_rng(42).random((2,3,2))
 array([[[0.77395605, 0.43887844],
         [0.85859792, 0.69736803],
         [0.09417735, 0.97562235]],
        [[0.7611397 , 0.78606431],
         [0.12811363, 0.45038594],
         [0.37079802, 0.92676499]]])

:func:`numpy.indices` 将创建一组数组（堆叠为一个更高维度的数组），每个维度一个，每个数组表示该维度上的变化::

 >>> import numpy as np
 >>> np.indices((3,3))
 array([[[0, 0, 0], 
         [1, 1, 1], 
         [2, 2, 2]], 
        [[0, 1, 2], 
         [0, 1, 2], 
         [0, 1, 2]]])

这在多维函数的规则网格上求值时特别有用。

3) 复制、连接或修改现有数组
====================================================

一旦你创建了数组，你可以复制、连接或修改这些现有数组来创建新的数组。当你将一个数组或其元素赋值给一个新变量时，你必须显式地使用 :func:`numpy.copy` 来复制数组，否则该变量只是原始数组的视图。考虑以下示例：

```python
>>> import numpy as np
>>> a = np.array([1, 2, 3, 4, 5, 6])
>>> b = a[:2]
>>> b += 1
>>> print('a =', a, '; b =', b)
a = [2 3 3 4 5 6] ; b = [2 3]
```

在这个例子中，你没有创建一个新的数组。你创建了一个变量 ``b``，它只是 ``a`` 的前两个元素的视图。当你将 1 加到 ``b`` 上时，相当于将 1 加到 ``a[:2]`` 上。如果你想创建一个**新**的数组，使用 :func:`numpy.copy` 数组创建例程，如下所示：

```python
>>> import numpy as np
>>> a = np.array([1, 2, 3, 4])
>>> b = a[:2].copy()
>>> b += 1
>>> print('a = ', a, 'b = ', b)
a =  [1 2 3 4] b =  [2 3]
```

更多信息和示例请参见 :ref:`Copies and Views <quickstart.copies-and-views>`。

有许多例程可以连接现有数组，例如 :func:`numpy.vstack`、:func:`numpy.hstack` 和 :func:`numpy.block`。以下是一个使用 ``block`` 将四个 2x2 数组连接成一个 4x4 数组的示例：

```python
>>> import numpy as np
>>> A = np.ones((2, 2))
>>> B = np.eye(2, 2)
>>> C = np.zeros((2, 2))
>>> D = np.diag((-3, -4))
>>> np.block([[A, B], [C, D]])
array([[ 1.,  1.,  1.,  0.],
       [ 1.,  1.,  0.,  1.],
       [ 0.,  0., -3.,  0.],
       [ 0.,  0.,  0., -4.]])
```

其他例程使用类似的语法来连接 ndarray。查看例程的文档以获取更多示例和语法。

4) 从磁盘读取数组，无论是标准格式还是自定义格式
===================================================================

这是创建大型数组的最常见情况。细节很大程度上取决于磁盘上数据的格式。本节提供了处理各种格式的一般指导。有关更详细的 IO 示例，请参见 :ref:`How to Read and Write files <how-to-io>`。

标准二进制格式
-----------------------

各个领域都有标准的数组数据格式。以下列出了已知有 Python 库可以读取并返回 NumPy 数组的格式（可能还有其他格式可以读取并转换为 NumPy 数组，因此请查看最后一节）：

```
HDF5: h5py
FITS: Astropy
```

无法直接读取但可以通过库（如 PIL）轻松转换的格式示例包括那些支持读取和写入许多图像格式（如 jpg、png 等）的格式。

常见的 ASCII 格式
--------------------

分隔符文件，如逗号分隔值（csv）和制表符分隔值（tsv）文件，用于 Excel 和 LabView 等程序。Python 函数可以逐行读取和解析这些文件。NumPy 有两个标准例程用于导入分隔符数据文件：:func:`numpy.loadtxt` 和 :func:`numpy.genfromtxt`。这些函数在 :doc:`how-to-io` 中有更复杂的用例。给定一个 ``simple.csv`` 文件：

```bash
$ cat simple.csv
x, y
0, 0
1, 1
2, 4
3, 9
```

使用 :func:`numpy.loadtxt` 导入 ``simple.csv``：

```python
>>> import numpy as np
>>> np.loadtxt('simple.csv', delimiter = ',', skiprows = 1) # doctest: +SKIP
array([[0., 0.],
       [1., 1.],
       [2., 4.],
       [3., 9.]])
```

更通用的 ASCII 文件可以使用 `scipy.io` 和 `Pandas <https://pandas.pydata.org/>`_ 读取。

5) 通过使用字符串或缓冲区从原始字节创建数组
=======================================================================

有多种方法可以使用。如果文件格式相对简单，可以编写一个简单的 I/O 库，并使用 NumPy 的 ``fromfile()`` 函数和 ``.tofile()`` 方法直接读取和写入 NumPy 数组（注意字节顺序！）。如果有一个好的 C 或 C++ 库可以读取数据，可以使用多种技术来包装该库，尽管这需要更多的工作，并且需要更高级的知识来与 C 或 C++ 接口。

6) 使用特殊库函数（例如，SciPy、pandas 和 OpenCV）
=====================================================================

NumPy 是 Python 科学计算堆栈中用于数组容器的核心库。许多 Python 库，包括 SciPy、Pandas 和 OpenCV，都使用 NumPy ndarray 作为数据交换的通用格式。这些库可以创建、操作和使用 NumPy 数组。