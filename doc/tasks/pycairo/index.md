#  Pycairo

[Pycairo](https://pycairo.readthedocs.io/en/latest/index.html) 是 Python 模块，为 [cairo 图形库](https://cairographics.org/)提供绑定。它依赖于 `cairo >= 1.15.10`，并且支持 Python 3.9+ 和 PyPy3。Pycairo 及其文档均采用 [LGPL-2.1-only 或 MPL-1.1 许可证](https://spdx.dev/ids)。

Pycairo 绑定旨在尽可能紧密地匹配 cairo 的 C API，仅在明显更适合以更“Pythonic”方式实现的情况下才有所不同。

使用 pip 安装 pycairo：
```bash
pip install pycairo
```

安装 Pycairo 需要 `pkg-config` 和 `cairo`（包括其头文件）。以下是一些平台上的安装示例：
- Ubuntu/Debian: `sudo apt install libcairo2-dev pkg-config python3-dev`
- macOS/Homebrew: `brew install cairo pkg-config`
- Arch Linux: `sudo pacman -S cairo pkgconf`
- Fedora: `sudo dnf install cairo-devel pkg-config python3-devel`
- openSUSE: `sudo zypper install cairo-devel pkg-config python3-devel`

Pycairo 绑定的特性：

- 提供了面向对象的接口来访问 cairo。
- 查询对象的错误状态并将其转换为异常。
- 提供了 C API，可供其他 Python 扩展使用。
- 具有完全类型化和文档化的 API。

```{toctree}
:hidden:

intro
pillow
pygame
numpy
examples
gtk/index
cairo-snippets/index
```
