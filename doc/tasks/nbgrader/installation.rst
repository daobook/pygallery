安装
============

nbgrader系统和命令行工具
------------------------------------------
您可以安装包含评分系统和命令行工具的当前版本的nbgrader::

    pip install nbgrader

或者，如果您使用 `Anaconda <https://www.anaconda.com/download>`__ ::

    conda install jupyter
    conda install -c conda-forge nbgrader


Jupyter Lab中的nbgrader扩展
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在安装nbgrader后，扩展将自动安装。

安装将激活4个服务器扩展（formgrader、assignment_list、course_list和validate_assignment）
和5个lab扩展（formgrader、assignment-list、course-list、validate-assignment和create-assignment）。

可以通过运行以下命令单独禁用服务器扩展::

    jupyter server extension disable nbgrader.server_extensions.formgrader
    jupyter server extension disable nbgrader.server_extensions.assignment_list
    jupyter server extension disable nbgrader.server_extensions.course_list
    jupyter server extension disable nbgrader.server_extensions.validate_assignment

默认情况下，所有lab扩展都是启用的，但可以通过运行以下命令单独禁用::

    jupyter labextension disable @jupyter/nbgrader:formgrader
    jupyter labextension disable @jupyter/nbgrader:assignment-list
    jupyter labextension disable @jupyter/nbgrader:course-list
    jupyter labextension disable @jupyter/nbgrader:create-assignment
    jupyter labextension disable @jupyter/nbgrader:validate-assignment

或者启用::

    jupyter labextension enable @jupyter/nbgrader:formgrader
    jupyter labextension enable @jupyter/nbgrader:assignment-list
    jupyter labextension enable @jupyter/nbgrader:course-list
    jupyter labextension enable @jupyter/nbgrader:create-assignment
    jupyter labextension enable @jupyter/nbgrader:validate-assignment

为了正常工作，**作业列表**、**评分器**、**课程列表**和**验证作业**扩展需要同时启用lab扩展和服务器扩展。**创建作业**扩展只有lab扩展部分。

安装选项
~~~~~~~~~~~~~~~~~~~~

当使用``--sys-prefix``选项安装/启用时，服务器扩展将安装并启用给使用特定Python安装或conda环境的所有用户。如果该Python安装是系统范围的，所有用户将立即能够使用nbgrader扩展。

您可能需要自定义安装的几种方式：

- 要仅为当前用户安装或启用lab扩展/服务器扩展，请使用 ``--user`` 而不是 ``--sys-prefix`` 运行上述命令::

    jupyter labextension enable --level=user @jupyter/nbgrader
    jupyter server extension enable --user --py nbgrader

- 要为系统上的所有Python安装安装或启用lab扩展/服务器扩展，请使用 ``--system`` 而不是 ``--sys-prefix`` 运行上述命令::

    jupyter labextension enable --level=system @jupyter/nbgrader
    jupyter server extension enable --system --py nbgrader

禁用扩展
~~~~~~~~~~~~~~~~~~~~

您可能只想安装其中 nbgrader 扩展。为此，请按照上述步骤安装所有内容，然后禁用您不需要的扩展。例如，要禁用作业列表扩展::

    jupyter labextension disable --level=sys_prefix @jupyter/nbgrader:assignment-list
    jupyter server extension disable --sys-prefix nbgrader.server_extensions.assignment_list

或者禁用创建作业扩展::

    jupyter labextension disable --level=sys_prefix @jupyter/nbgrader:create-assignment

或者禁用评分器扩展::

    jupyter labextension disable --level=sys_prefix @jupyter/nbgrader:formgrader
    jupyter server extension disable --sys-prefix nbgrader.server_extensions.formgrader

或者禁用课程列表扩展::

    jupyter labextension disable --level=sys_prefix @jupyter/nbgrader:course-list
    jupyter server extension disable --sys-prefix nbgrader.server_extensions.course_list

例如，假设您通过 `Anaconda <https://www.anaconda.com/download>`__ 安装了nbgrader（这意味着所有服务器扩展都已安装并使用 ``--sys-prefix`` 标志启用，即使用特定Python安装或conda环境的所有用户）。但是您只想让**创建作业**扩展对特定用户可用，而不是对其他所有人。首先，您需要为其他所有人禁用**创建作业**扩展::

    jupyter labextension disable @jupyter/nbgrader:create-assignment

然后使用特定用户登录，并仅为该用户启用**创建作业**扩展::

    jupyter labextension enable --level=user @jupyter/nbgrader:create-assignment

最后，要查看所有已安装的lab扩展/服务器扩展，请运行::

    jupyter labextension list
    jupyter server extension list

有关这些命令的进一步文档，请运行::

    jupyter labextension --help-all
    jupyter server extension --help-all

有关安装**作业列表**扩展的高级说明，请参阅 :ref:`高级安装说明 <assignment-list-installation>`。

快速开始
-----------

要快速开始使用nbgrader，您可以通过运行``nbgrader quickstart``命令创建一个包含示例课程文件的示例目录::

    nbgrader quickstart course_id

您应该将``course_id``替换为您的课程名称。有关quickstart命令如何工作的进一步详细信息，请运行::

    nbgrader quickstart --help

有关此目录的结构以及其中不同文件的解释，请继续阅读 :doc:`philosophy`。