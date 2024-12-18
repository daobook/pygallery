.. py:currentmodule:: moderngl

OpenGL 简介
============

简化的故事
------------

`OpenGL`_ （开放图形库）有着悠久的历史，可以追溯到 1992 年，由 `Silicon Graphics`_ 创建。它部分基于其专有的 `IRIS GL`_（集成光栅成像系统图形库）库。

如今，OpenGL 由 `Khronos Group`_ 管理，这是一个由 150 多家领先的硬件和软件公司组成的开放行业联盟，致力于创建先进的、免版税的 3D 图形、增强现实和虚拟现实、视觉和机器学习加速标准。

`OpenGL`_ 的目的是提供一种标准的方式来与图形处理单元（GPU）交互，以在多个平台上实现硬件加速渲染。具体如何实现这一目标取决于供应商（AMD、Nvidia、Intel、ARM 等），只要遵循规范即可。

`OpenGL`_ 经历了许多版本，查找资源时可能会感到困惑。如今，我们将“旧版 OpenGL”和“现代 OpenGL”区分开来。从 2008 年到 2010 年，OpenGL 3.x 版本演进到 3.3 和 4.0 同时发布。

2010 年，发布了 3.3、4.0 和 4.1 版本，以现代化 API（简化解释），创建能够利用 Direct3D 11 级硬件的功能。**OpenGL 3.3 是第一个“现代 OpenGL”版本**（简化解释）。从此版本开始，所有内容都向前兼容，一直到最新的 4.x 版本。引入了一个可选的弃用机制，以禁用过时的功能。在 **核心模式** 下运行 OpenGL 会移除所有旧功能，而在 **兼容模式** 下运行则仍然允许混合旧版和新版 API。

.. 注意:: 当然，OpenGL 2.x、3.0、3.1 和 3.2 版本也可以直接访问一些现代 OpenGL 功能，但为了简单起见，我们专注于 3.3 版本，因为它创建了我们今天使用的最终标准。旧版 OpenGL 也是一个相当混乱的世界，有无数供应商特定的扩展。现代 OpenGL 在这方面进行了相当大的清理。

在 OpenGL 中，我们经常谈论 **固定管线** 和 **可编程管线**。

使用 **固定管线**（旧版 OpenGL）的 OpenGL 代码会使用诸如 ``glVertex``、``glColor``、``glMaterial``、``glMatrixMode``、``glLoadIdentity``、``glBegin``、``glEnd``、``glVertexPointer``、``glColorPointer``、``glPushMatrix`` 和 ``glPopMatrix`` 等函数。API 对您可以做什么有强烈的意见和限制，隐藏了底层实际发生的事情。

使用 **可编程管线**（现代 OpenGL）的 OpenGL 代码会使用诸如 ``glCreateProgram``、``UseProgram``、``glCreateShader``、``VertexAttrib*``、``glBindBuffer*`` 和 ``glUniform*`` 等函数。此 API 主要处理数据缓冲区，并使用在 GPU 上运行的小程序（称为“着色器”）来处理这些数据，使用 **OpenGL 着色语言（GLSL）**。这提供了巨大的灵活性，但要求我们理解 OpenGL 管线（实际上并不复杂）。

超越 OpenGL
-------------

OpenGL 在 25 年后有很多“包袱”，硬件在其诞生以来也发生了巨大的变化。“OpenGL 5”的计划作为 **下一代 OpenGL 计划（glNext）** 开始。这演变成了 `Vulkan`_ API，并进行了彻底的重新设计，以统一 OpenGL 和 OpenGL ES 为一个通用的 API，该 API 不会向后兼容现有的 OpenGL 版本。

这并不意味着今天学习 OpenGL 不值得。事实上，学习 3.3+ 着色器并理解渲染管线将极大地帮助您理解 `Vulkan`_。在大多数情况下，您几乎可以将着色器直接复制粘贴到 `Vulkan`_ 中。

ModernGL 在这些中扮演什么角色？
----------------------------------

ModernGL 库通过 OpenGL 3.3 核心或更高版本来公开 **可编程管线**。然而，并不直接公开 OpenGL 函数。相反，通过各种对象（如 :py:class:`Buffer` 和 :py:class:`Program`）以更“Pythonic”的方式公开功能。换句话说，它是更高层次的封装，使 OpenGL 更容易理解和使用。我们尝试隐藏大多数复杂的细节，以提高用户的工作效率。OpenGL 有很多陷阱，我们消除了其中的大部分。

学习 ModernGL 更多的是学习着色器和 OpenGL 管线。

.. _Vulkan: https://www.khronos.org/vulkan/
.. _IRIS GL: https://wikipedia.org/wiki/IRIS_GL
.. _OpenGL: https://en.wikipedia.org/wiki/OpenGL
.. _Silicon Graphics: https://wikipedia.org/wiki/Silicon_Graphics
.. _Khronos Group: https://www.khronos.org