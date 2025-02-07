
.. _basics.interoperability:

***************************
与 NumPy 的互操作性
***************************

NumPy 的 `ndarray` 对象提供了用于操作数组结构化数据的高级 API，以及基于 :ref:`分步内存存储 <arrays>` 的具体实现。虽然这个 API 功能强大且相当通用，但其具体实现存在一些限制。随着数据集的增长以及 NumPy 在各种新环境和架构中的使用，某些情况下分步内存存储策略并不适用，这导致不同的库为了自身需求重新实现了这个 API。这包括 GPU 数组（CuPy_）、稀疏数组（`scipy.sparse`、 `PyData/Sparse <Sparse_>`_ ）、并行数组（Dask_ 数组），以及深度学习框架中的各种类 NumPy 实现，如 TensorFlow_ 和 PyTorch_。同样，有许多项目基于 NumPy API 构建，用于标记和索引数组（XArray_）、自动微分（JAX_）、掩码数组（`numpy.ma`）、物理单位（astropy.units_、pint_、unyt_）等，这些项目在 NumPy API 的基础上增加了额外的功能。

然而，用户仍然希望使用熟悉的 NumPy API 来处理这些数组，并尽量减少（理想情况下为零）移植现有代码的开销。基于这一目标，定义了各种协议，用于实现与 NumPy 高级 API 匹配的多维数组。

大致来说，有三组功能用于与 NumPy 的互操作性：

1. 将外部对象转换为 `ndarray` 的方法；
2. 将执行延迟从 NumPy 函数转移到其他数组库的方法；
3. 使用 NumPy 函数并返回外部对象实例的方法。

我们在下面描述这些功能。

1. 在 NumPy 中使用任意对象
-----------------------------------

NumPy API 中的第一组互操作性功能允许在可能的情况下将外部对象视为 NumPy 数组。当 NumPy 函数遇到外部对象时，它们将按顺序尝试以下方法：

1. 缓冲区协议，描述在 :py:doc:`Python C-API 文档 <python:c-api/buffer>` 中。
2. ``__array_interface__`` 协议，描述在 :ref:`本页 <arrays.interface>` 中。这是 Python 缓冲区协议的前身，它定义了一种从其他 C 扩展访问 NumPy 数组内容的方式。
3. ``__array__()`` 方法，该方法要求任意对象将其自身转换为数组。

对于缓冲区协议和 ``__array_interface__`` 协议，对象描述其内存布局，NumPy 负责其余所有工作（如果可能，则零拷贝）。如果无法实现零拷贝，对象本身负责从 ``__array__()`` 返回一个 ``ndarray``。

:doc:`DLPack <dlpack:index>` 是另一种以语言和设备无关的方式将外部对象转换为 NumPy 数组的协议。NumPy 不会隐式地使用 DLPack 将对象转换为 `ndarray`。它提供了 `numpy.from_dlpack` 函数，该函数接受任何实现了 ``__dlpack__`` 方法的对象，并输出一个 NumPy  `ndarray` （通常是输入对象数据缓冲区的视图）。 :ref:`dlpack:python-spec` 页面详细解释了 ``__dlpack__`` 协议。

数组接口协议
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`数组接口协议 <arrays.interface>` 定义了一种方式，使得类似数组的对象可以重用彼此的数据缓冲区。其实现依赖于以下属性或方法的存在：

-  ``__array_interface__``：一个包含数组形状、元素类型，以及可选的数据缓冲区地址和步长的 Python 字典；
-  ``__array__()``：一个返回 NumPy ndarray 副本或类似数组对象视图的方法；

可以直接检查 ``__array_interface__`` 属性：

 >>> import numpy as np
 >>> x = np.array([1, 2, 5.0, 8])
 >>> x.__array_interface__
 {'data': (94708397920832, False), 'strides': None, 'descr': [('', '<f8')], 'typestr': '<f8', 'shape': (4,), 'version': 3}

``__array_interface__`` 属性也可以用于就地操作对象数据：

 >>> class wrapper():
 ...     pass
 ...
 >>> arr = np.array([1, 2, 3, 4])
 >>> buf = arr.__array_interface__
 >>> buf
 {'data': (140497590272032, False), 'strides': None, 'descr': [('', '<i8')], 'typestr': '<i8', 'shape': (4,), 'version': 3}
 >>> buf['shape'] = (2, 2)
 >>> w = wrapper()
 >>> w.__array_interface__ = buf
 >>> new_arr = np.array(w, copy=False)
 >>> new_arr
 array([[1, 2],
        [3, 4]])

我们可以检查 ``arr`` 和 ``new_arr`` 是否共享相同的数据缓冲区：

 >>> new_arr[0, 0] = 1000
 >>> new_arr
 array([[1000,    2],
        [   3,    4]])
 >>> arr
 array([1000, 2, 3, 4])


.. _dunder_array.interface:

``__array__()`` 方法
~~~~~~~~~~~~~~~~~~~~

``__array__()`` 方法确保任何实现它的类都可以被用作 NumPy 数组。这些类包括：数组、任何暴露数组接口的对象、一个 ``__array__()`` 方法返回数组的对象，或者任何嵌套的序列。如果可能，这将意味着使用 ``__array__()`` 来创建一个数组类对象的 NumPy ndarray 视图。否则，这将把数据复制到一个新的 ndarray 对象中。这不是最优的，因为将数组强制转换为 ndarray 可能会导致性能问题，或者需要复制数据并丢失元数据，因为原始对象及其任何属性和行为都会丢失。

该方法的签名应为 ``__array__(self, dtype=None, copy=None)``。如果传递的 ``dtype`` 不是 ``None`` 并且与对象的数据类型不同，则应进行类型转换。如果 ``copy`` 是 ``None``，则仅在 ``dtype`` 参数强制要求时才应进行复制。对于 ``copy=True``，应始终进行复制，而对于 ``copy=False``，如果需要复制，则应引发异常。

如果一个类实现了旧的签名 ``__array__(self)``，对于 ``np.array(a)``，将发出警告，提示缺少 ``dtype`` 和 ``copy`` 参数。

要查看包含 ``__array__()`` 使用的自定义数组实现的示例，请参阅 :ref:`basics.dispatch`。

DLPack 协议
~~~~~~~~~~~~

:doc:`DLPack <dlpack:index>` 协议定义了一种跨步的 n 维数组对象的内存布局。它提供了以下数据交换语法：

1. 一个 `numpy.from_dlpack` 函数，该函数接受具有 ``__dlpack__`` 方法的（数组）对象，并使用该方法构造一个包含来自 ``x`` 数据的新数组。
2. 数组对象上的 ``__dlpack__(self, stream=None)`` 和 ``__dlpack_device__`` 方法，这些方法将在 ``from_dlpack`` 内部调用，以查询数组所在的设备（可能需要传入正确的流，例如在多 GPU 的情况下）并访问数据。

与缓冲区协议不同，DLPack 允许交换包含非 CPU 设备（例如 Vulkan 或 GPU）上数据的数组。由于 NumPy 仅支持 CPU，它只能转换数据存在于 CPU 上的对象。但其他库，如 PyTorch_ 和 CuPy_，可能使用此协议在 GPU 上交换数据。


2. 在不转换的情况下操作外部对象
----------------------------------

NumPy API 定义的第二组方法允许我们将 NumPy 函数的执行推迟到另一个数组库。

考虑以下函数：

 >>> import numpy as np
 >>> def f(x):
 ...     return np.mean(np.exp(x))


注意 `np.exp <numpy.exp>` 是 :ref:`ufunc <ufuncs-basics>`，这意味着它以逐元素的方式对 ndarray 进行操作。另一方面，`np.mean <numpy.mean>` 沿数组的一个轴进行操作。

可以直接将 ``f`` 应用于 NumPy ndarray 对象：

 >>> x = np.array([1, 2, 3, 4])
 >>> f(x)
 21.1977562209304

我们希望这个函数同样适用于任何类似 NumPy 的数组对象。

NumPy 允许类通过以下接口指示它希望以自定义方式处理计算：

-  ``__array_ufunc__``：允许第三方对象支持并覆盖 :ref:`ufuncs <ufuncs-basics>`。
-  ``__array_function__``：一个用于捕获 NumPy 功能的全能接口，这些功能不在通用函数的 ``__array_ufunc__`` 协议范围内。

只要外部对象实现了 ``__array_ufunc__`` 或 ``__array_function__`` 协议，就可以在不进行显式转换的情况下对它们进行操作。

``__array_ufunc__`` 协议
~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`通用函数（或简称 ufunc）<ufuncs-basics>` 是一个“矢量化”的函数包装器，它接受固定数量的特定输入并生成固定数量的特定输出。ufunc（及其方法）的输出不一定是 ndarray，如果并非所有输入参数都是 ndarray。实际上，如果任何输入定义了 ``__array_ufunc__`` 方法，控制权将完全传递给该函数，即 ufunc 被覆盖。在该（非 ndarray）对象上定义的 ``__array_ufunc__`` 方法可以访问 NumPy 的 ufunc。由于 ufunc 具有定义良好的结构，外部 ``__array_ufunc__`` 方法可以依赖于 ufunc 属性，如 ``.at()``、``.reduce()`` 等。

子类可以通过重写默认的 ``ndarray.__array_ufunc__`` 方法来覆盖在其上执行 NumPy ufunc 时的行为。该方法将代替 ufunc 执行，并应返回操作的结果，或者如果请求的操作未实现，则返回 ``NotImplemented``。

``__array_function__`` 协议
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

为了覆盖 NumPy API 的足够部分以支持下游项目，需要超越 ``__array_ufunc__`` 并实现一个协议，该协议允许 NumPy 函数的参数接管控制权并将执行重定向到另一个函数（例如，GPU 或并行实现），以一种在项目之间安全且一致的方式。

``__array_function__`` 的语义与 ``__array_ufunc__`` 非常相似，只是操作由任意可调用对象指定，而不是 ufunc 实例和方法。有关更多详细信息，请参阅 :ref:`NEP18`。

3. 返回外部对象
------------------

第三种类型的功能集旨在使用NumPy函数的实现，然后将返回值转换回外部对象的实例。`__array_finalize__` 和 `__array_wrap__` 方法在幕后起作用，以确保可以根据需要指定NumPy函数的返回类型。

`__array_finalize__` 方法是NumPy提供的一种机制，允许子类处理创建新实例的各种方式。每当系统从`ndarray`的子类（子类型）对象内部分配新数组时，都会调用此方法。它可用于在构造后更改属性，或者从“父类”更新元信息。

`__array_wrap__` 方法在某种意义上“包装了操作”，允许任何对象（例如用户定义的函数）设置其返回值的类型并更新属性和元数据。这可以看作是 `__array__` 方法的相反操作。在实现 `__array_wrap__` 的每个对象的末尾，此方法会在具有最高 `array priority` 的输入对象上调用，或者如果指定了输出对象，则在输出对象上调用。`__array_priority__` 属性用于确定在有多种可能的返回对象类型时，应返回哪种类型的对象。例如，子类可以选择使用此方法将输出数组转换为子类的实例，并在将数组返回给用户之前更新元数据。

有关这些方法的更多信息，请参阅 :ref:`basics.subclassing` 和 :ref:`specific-array-subtyping`。


互操作性示例
--------------

示例：Pandas 的 `Series` 对象
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

考虑以下示例：


>>> import pandas as pd
>>> ser = pd.Series([1, 2, 3, 4])
>>> type(ser)
pandas.core.series.Series


现在，`ser` **不是** `ndarray`，但由于它 `实现了 __array_ufunc__ 协议 <https://pandas.pydata.org/docs/user_guide/dsintro.html#dataframe-interoperability-with-numpy-functions>`__，我们可以像对待`ndarray`一样对其应用ufunc：


>>> np.exp(ser)
0     2.718282
1     7.389056
2    20.085537
3    54.598150
dtype: float64
>>> np.sin(ser)
0    0.841471
1    0.909297
2    0.141120
3   -0.756802
dtype: float64

我们甚至可以与其他`ndarray`进行操作：

>>> np.add(ser, np.array([5, 6, 7, 8]))
0     6
1     8
2    10
3    12
dtype: int64
>>> f(ser)
21.1977562209304
>>> result = ser.__array__()
>>> type(result)
numpy.ndarray

示例：PyTorch 张量
~~~~~~~~~~~~~~~~~~~~

`PyTorch <https://pytorch.org/>`__ 是一个针对使用 GPU 和 CPU 进行深度学习优化的张量库。PyTorch 数组通常被称为 *张量*。张量类似于 NumPy 的 ndarray，不同之处在于张量可以在 GPU 或其他硬件加速器上运行。事实上，张量和 NumPy 数组通常可以共享相同的底层内存，从而无需复制数据。


>>> import torch
>>> data = [[1, 2],[3, 4]]
>>> x_np = np.array(data)
>>> x_tensor = torch.tensor(data)


请注意，``x_np`` 和 ``x_tensor`` 是不同类型的对象：


>>> x_np
array([[1, 2],
       [3, 4]])
>>> x_tensor
tensor([[1, 2],
        [3, 4]])


然而，我们可以将 PyTorch 张量视为 NumPy 数组，而无需显式转换：


>>> np.exp(x_tensor)
tensor([[ 2.7183,  7.3891],
        [20.0855, 54.5982]], dtype=torch.float64)


此外，请注意此函数的返回类型与初始数据类型兼容。

.. 警告::

   尽管这种混合 ndarray 和张量的方式可能很方便，但不推荐使用。它不适用于非 CPU 张量，并且在某些情况下可能会产生意外行为。用户应优先显式地将 ndarray 转换为张量。

.. 注意::

   PyTorch 没有实现 ``__array_function__`` 或 ``__array_ufunc__``。在底层，``Tensor.__array__()`` 方法返回一个 NumPy ndarray，作为张量数据缓冲区的视图。有关详细信息，请参阅 `此问题 <https://github.com/pytorch/pytorch/issues/24015>`__ 和 `__torch_function__ 实现 <https://github.com/pytorch/pytorch/blob/master/torch/overrides.py>`__。

还要注意，即使 ``torch.Tensor`` 不是 ndarray 的子类，我们也可以在这里看到 ``__array_wrap__`` 的作用：


>>> import torch
>>> t = torch.arange(4)
>>> np.abs(t)
tensor([0, 1, 2, 3])


PyTorch 实现了 ``__array_wrap__``，以便能够从 NumPy 函数中获取张量，并且我们可以直接修改它，以控制这些函数返回的对象类型。

示例：CuPy 数组
~~~~~~~~~~~~~~~~~~~~

CuPy 是与 NumPy/SciPy 兼容的数组库，用于使用 Python 进行 GPU 加速计算。CuPy 通过实现 ``cupy.ndarray`` （这是 NumPy ndarray 的对应物）来实现 NumPy 接口的子集。


>>> import cupy as cp
>>> x_gpu = cp.array([1, 2, 3, 4])


``cupy.ndarray`` 对象实现了 ``__array_ufunc__`` 接口。这使得 NumPy 的 ufunc 可以应用于 CuPy 数组（这将把操作委托给 CuPy 的 CUDA/ROCm 实现的相应 ufunc）：


>>> np.mean(np.exp(x_gpu))
array(21.19775622)


请注意，这些操作的返回类型仍然与初始类型一致：

>>> arr = cp.random.randn(1, 2, 3, 4).astype(cp.float32)
>>> result = np.sum(arr)
>>> print(type(result))
<class 'cupy._core.core.ndarray'>


有关详细信息，请参阅 `CuPy 文档中的此页面 <https://docs.cupy.dev/en/stable/reference/ufunc.html>`__。

``cupy.ndarray`` 还实现了 ``__array_function__`` 接口，这意味着可以执行如下操作：


>>> a = np.random.randn(100, 100)
>>> a_gpu = cp.asarray(a)
>>> qr_gpu = np.linalg.qr(a_gpu)


CuPy 在 ``cupy.ndarray`` 对象上实现了许多 NumPy 函数，但并非全部。有关详细信息，请参阅 `CuPy 文档 <https://docs.cupy.dev/en/stable/user_guide/difference.html>`__。

示例：Dask 数组
~~~~~~~~~~~~~~~~~~~~

Dask 是一个灵活的 Python 并行计算库。Dask Array 使用分块算法实现了一个 NumPy ndarray 接口的子集，将大数组切割成许多小数组。这使得可以在使用多个核心的情况下对大于内存的数组进行计算。

Dask 支持 ``__array__()`` 和 ``__array_ufunc__``。


>>> import dask.array as da
>>> x = da.random.normal(1, 0.1, size=(20, 20), chunks=(10, 10))
>>> np.mean(np.exp(x))
dask.array<mean_agg-aggregate, shape=(), dtype=float64, chunksize=(), chunktype=numpy.ndarray>
>>> np.mean(np.exp(x)).compute()
5.090097550553843


.. 注意::

   Dask 是惰性求值的，计算结果不会在计算后立即生成，直到你通过调用 ``compute()`` 来请求它。

有关详细信息，请参阅 `Dask 数组文档 <https://docs.dask.org/en/stable/array.html>`__ 和 `Dask 数组与 NumPy 数组的互操作性范围 <https://docs.dask.org/en/stable/array.html#scope>`__。

DLPack 示例
~~~~~~~~~~~~~~~~~~~~

一些 Python 数据科学库实现了 ``__dlpack__`` 协议，其中包括 PyTorch_ 和 CuPy_。完整支持该协议的库列表可以在 `DLPack 文档 <https://docs.dlpack.org/en/latest/index.html>`__ 找到。

将 PyTorch CPU 张量转换为 NumPy 数组：

>>> import torch
>>> x_torch = torch.arange(5)
>>> x_torch
tensor([0, 1, 2, 3, 4])
>>> x_np = np.from_dlpack(x_torch)
>>> x_np
array([0, 1, 2, 3, 4])
>>> # 注意 x_np 是 x_torch 的视图
>>> x_torch[1] = 100
>>> x_torch
tensor([  0, 100,   2,   3,   4])
>>> x_np
array([  0, 100,   2,   3,   4])

导入的数组是只读的，因此写入或原地操作会失败：

>>> x.flags.writeable
False
>>> x_np[1] = 1
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: assignment destination is read-only


为了在导入的数组上进行原地操作，必须创建副本，但这意味着复制内存。对于非常大的数组，不要这样做：

>>> x_np_copy = x_np.copy()
>>> x_np_copy.sort()  # 可以工作

**注意**：

GPU 张量不能转换为 NumPy 数组，因为 NumPy 不支持 GPU 设备：

>>> x_torch = torch.arange(5, device='cuda')
>>> np.from_dlpack(x_torch)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
RuntimeError: Unsupported device in DLTensor.

但是，如果两个库都支持数据缓冲区所在的设备，可以使用 ``__dlpack__`` 协议（例如 PyTorch_ 和 CuPy_）：

>>> x_torch = torch.arange(5, device='cuda')
>>> x_cupy = cupy.from_dlpack(x_torch)


类似地，NumPy 数组可以转换为 PyTorch 张量：


>>> x_np = np.arange(5)
>>> x_torch = torch.from_dlpack(x_np)


不可写的数组不能导出：


>>> x_np = np.arange(5)
>>> x_np.flags.writeable = False
>>> torch.from_dlpack(x_np)  # doctest: +ELLIPSIS
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File ".../site-packages/torch/utils/dlpack.py", line 63, in from_dlpack
    dlpack = ext_tensor.__dlpack__()
TypeError: NumPy currently only supports dlpack for writeable arrays


.. _CuPy: https://cupy.dev/
.. _Sparse: https://sparse.pydata.org/
.. _Dask: https://docs.dask.org/
.. _TensorFlow: https://www.tensorflow.org/
.. _PyTorch: https://pytorch.org/
.. _XArray: https://xarray.dev/
.. _JAX: https://jax.readthedocs.io/
.. _astropy.units: https://docs.astropy.org/en/stable/units/
.. _pint: https://pint.readthedocs.io/
.. _unyt: https://unyt.readthedocs.io/