# `sphinx-proof`

[`sphinx-proof` 文档](https://sphinx-proof.readthedocs.io/en/latest/index.html)

```{admonition} Sphinx 证明扩展包
该软件包包含了用于[Sphinx](http://www.sphinx-doc.org/)的扩展，旨在生成包括[证明](syntax:proof)、[定理](syntax:theorem)、[公理](syntax:axiom)、[引理](syntax:lemma)、[定义](syntax:definition)、[标准](syntax:criterion)、[备注](syntax:remark)、[猜想](syntax:conjecture)、[推论](syntax:corollary)、[算法](syntax:algorithm)、[示例](syntax:example)、[性质](syntax:property)、[观察](syntax:observation)、[命题](syntax:proposition)和[假设](syntax:assumption)指令的文档内容。
```

**特性**：

1. 指令会自动编号。
2. 支持诸如 `class`、`label` 和 `nonumber` 等指令选项。
3. 可以通过 `prf:ref` 角色进行引用。

安装

```bash
pip install sphinx-proof
```

```{toctree}
syntax
options
```
