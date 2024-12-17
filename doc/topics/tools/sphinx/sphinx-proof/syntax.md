# 语法指南

```{note}
本文档采用了[Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/index.html)语法。
```

此包使用了名为 `prf` 的[Sphinx域](https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html)，用于描述和链接认为应该归为一类的排版标记对象（定理、证明、推论等）。所有指令遵循`{<域名>:<类型设置>}`的模式，而所有角色遵循`{<域名>:ref}`的模式。要使用“proof”域中的任何指令，请遵循`{prf:<类型设置>}`的模式。要引用任何指令，请遵循`{prf:ref}`的模式。

## 指令集合

(syntax:proof)=
### 证明

可以通过 `prf:proof` 模式包含证明指令。与通过此扩展提供的其他指令不同，证明指令不包含任何参数，也不需要任何参数。证明指令可以通过[目标](https://myst-parser.readthedocs.io/en/latest/using/syntax.html#targets-and-cross-referencing)轻松引用。

支持以下选项：

* `class`: text

	证明类属性的值，可用于添加自定义 CSS 或 JavaScript。

**示例**

````{prf:proof}
:label: my-proof

我们将省略完整的证明。

但我们将证明所断言条件的充分性。

为此，令$y \in \mathbb{R}^n$，并设 $S$ 是 $\mathbb{R}^n$ 的线性子空间。

令 $\hat{y}$ 为 $\mathbb{R}^n$ 中的向量，使得 $\hat{y} \in S$ 且 $y - \hat{y} \perp S$。

让 $z$ 是 $S$ 中的任意其他点，并利用 $S$ 是线性子空间的事实来推导出：

```{math}
\| y - z \|^2
= \| (y - \hat y) + (\hat y - z) \|^2
= \| y - \hat y \|^2  + \| \hat y - z  \|^2
```

因此，$\| y - z \| \geq \| y - \hat{y} \|$，这完成了证明。
````

MyST 语法

`````
````{prf:proof}
:label: my-proof

我们将省略完整的证明。

但我们将证明所断言条件的充分性。

为此，令$y \in \mathbb{R}^n$，并设 $S$ 是 $\mathbb{R}^n$ 的线性子空间。

令 $\hat{y}$ 为 $\mathbb{R}^n$ 中的向量，使得 $\hat{y} \in S$ 且 $y - \hat{y} \perp S$。

让 $z$ 是 $S$ 中的任意其他点，并利用 $S$ 是线性子空间的事实来推导出：

```{math}
\| y - z \|^2
= \| (y - \hat y) + (\hat y - z) \|^2
= \| y - \hat y \|^2  + \| \hat y - z  \|^2
```

因此，$\| y - z \| \geq \| y - \hat{y} \|$，这完成了证明。
````
`````

_来源:_ [QuantEcon](https://python-advanced.quantecon.org/orth_proj.html#The-Orthogonal-Projection-Theorem)

(syntax:theorem)=
### 定理

定理指令可以使用 `prf:theorem` 模式包含。默认情况下，该指令是枚举的，并且可以接受一个可选的标题参数。还支持以下选项：

* `label` : 文本

	您可以用来引用定理的唯一标识符，不能包含空格或特殊字符。
* `class` : 文本

	定理的类属性的值，可用于添加自定义 CSS 或 JavaScript。
* `nonumber` : 标志（空）

	关闭定理自动编号。

	```{math}
	\DeclareMathOperator*{\argmax}{arg\,max}
	\DeclareMathOperator*{\argmin}{arg\,min}
	```

示例：

````{prf:theorem} 正交投影定理
:label: my-theorem

设 $y \in \mathbb R^n$ 和线性子空间 $S \subset \mathbb R^n$，存在唯一的解使得最小化问题

```{math}
\hat y := \argmin_{z \in S} \|y - z\|
```

最小化者 $\hat y$ 是 $\mathbb R^n$ 中满足以下条件的唯一向量：

* $\hat y \in S$
* $y - \hat y \perp S$

向量 $\hat y$ 被称为 $y$ 到 $S$ 上的**正交投影**。
````

MyST 语法
`````
````{prf:theorem} 正交投影定理
:label: my-theorem

设 $y \in \mathbb R^n$ 和线性子空间 $S \subset \mathbb R^n$，存在唯一的解使得最小化问题

```{math}
\hat y := \argmin_{z \in S} \|y - z\|
```

最小化者 $\hat y$ 是 $\mathbb R^n$ 中满足以下条件的唯一向量：

* $\hat y \in S$
* $y - \hat y \perp S$

向量 $\hat y$ 被称为 $y$ 到 $S$ 上的**正交投影**。
````
`````

_来源_： [QuantEcon](https://python-advanced.quantecon.org/orth_proj.html#The-Orthogonal-Projection-Theorem)

#### 引用定理

你可以通过使用 `{prf:ref}` 标签来引用一个定理，例如：```{prf:ref}`my-theorem` ```。这将把引用替换成定理的编号，例如：{prf:ref}`my-theorem`。当提供明确的文本时，这个标题将作为引用的标题。例如，```{prf:ref}`Orthogonal-Projection-Theorem <my-theorem>` ``` 将生成：{prf:ref}`Orthogonal-Projection-Theorem <my-theorem>`。

(syntax:axiom)=
### 公理

可以使用 `prf:axiom` 模式来包含公理指令。该指令默认情况下会被枚举，并且可以接受一个可选的标题参数。还支持以下选项：

* `label` : 文本

	这是您的公理的唯一标识符，您可以用它通过 `{prf:ref}` 引用它。不能包含空格或特殊字符。
* `class` : 文本

	公理的类属性的值，可以用来添加自定义 CSS 或 JavaScript。
* `nonumber` : 标志（空）

	关闭公理的自动编号。

示例
```{prf:axiom} $\mathbb{R}$ 的完备性
:label: my-axiom

每一个实数域上的柯西序列都是收敛的。
```

MyST 语法
````
```{prf:axiom} $\mathbb{R}$ 的完备性
:label: my-axiom

每一个实数域上的柯西序列都是收敛的。
```
````


_来源:_ {cite}`economic-dynamics-book`

#### 引用公理

你可以通过使用 `{prf:ref}` 角色来引用公理，例如：```{prf:ref}`my-axiom````，这将用公理编号替换引用，如：{prf:ref}`my-axiom`。当提供显式文本时，此标题将作为引用的标题。

(syntax:lemma)=
### 引理

可以通过使用 `prf:lemma` 模式来包含引理指令。默认情况下，该指令会被枚举，并且可以接受可选的标题参数。此外，还支持以下选项：

为您的引理提供唯一的标识符，您可以用它来通过 `{prf:ref}` 进行引用。不能包含空格或特殊字符。
* `class` : text
	词条的类属性的值，可以用来添加自定义的 CSS 或 JavaScript。

* `nonumber` : flag (empty)
	关闭词条自动编号功能。

示例

````{prf:lemma}
如果$\hat P$是映射$\mathcal B \circ \mathcal D$的不动点，且$\hat F$是在[(7)](https://python-advanced.quantecon.org/robustness.html#equation-rb-oc-ih)中给出的鲁棒策略，那么

```{math}
:label: rb_kft

K(\hat F, \theta) = (\theta I - C'\hat P C)^{-1} C' \hat P  (A - B \hat F)
```
````

**MyST语法**

`````
````{prf:lemma}
:label: my-lemma

如果$\hat P$是映射$\mathcal B \circ \mathcal D$的不动点，且$\hat F$是在[(7)](https://python-advanced.quantecon.org/robustness.html#equation-rb-oc-ih)中给出的鲁棒策略，那么

```{math}
:label: rb_kft

K(\hat F, \theta) = (\theta I - C'\hat P C)^{-1} C' \hat P  (A - B \hat F)
```
````
`````

_来源：_ [QuantEcon](https://python-advanced.quantecon.org/robustness.html#Appendix)

#### 引用引理

您可以使用 `{prf:ref}` 角色来引用引理，例如：```{prf:ref}`my-lemma` ```，这将把引用替换为引理编号，如下所示：{prf:ref}`my-lemma`。当提供显式文本时，此标题将作为引用的标题。

(syntax:definition)=
### 定义

可以通过使用 `prf:definition` 模式包含一个定义指令。默认情况下，该指令是编号的，并且可以接受可选的标题参数。还支持以下选项：

* `label` : 文本
	一个唯一的标识符，用于通过 `{prf:ref}` 引用您的定义。不能包含空格或特殊字符。
* `class` : 文本
	定义的类属性的值，可以用来添加自定义 CSS 或 JavaScript。
* `nonumber` : 标志（空）
	关闭定义自动编号。

示例

````{prf:definition}
:label: my-definition

The *economical expansion problem* (EEP) for
$(A,B)$ is to find a semi-positive $n$-vector $p>0$
and a number $\beta\in\mathbb{R}$, such that

$$
&\min_{\beta} \hspace{2mm} \beta \\
&\text{s.t. }\hspace{2mm}Bp \leq \beta Ap
$$

````

MyST 语法

``````
````{prf:definition}
:label: my-definition

The *economical expansion problem* (EEP) for
$(A,B)$ is to find a semi-positive $n$-vector $p>0$
and a number $\beta\in\mathbb{R}$, such that

$$
&\min_{\beta} \hspace{2mm} \beta \\
&\text{s.t. }\hspace{2mm}Bp \leq \beta Ap
$$
````
``````

_来源:_ [QuantEcon](https://python-advanced.quantecon.org/von_neumann_model.html#Duality)

#### 引用定义

您可以使用 `{prf:ref}` 角色来引用一个定义，例如：```{prf:ref}`my-definition` ```，这将用定义编号替换引用，像这样：{prf:ref}`my-definition`。当提供明确的文本时，该标题将作为引用的标题。

(syntax:criterion)=
### 准则

可以使用 `prf:criterion` 模式包含准则指令。默认情况下，该指令会被枚举出来，并且可以接受可选的标题参数。还支持以下选项：

* `label`: 文本

	这是你的标准的唯一标识符，你可以使用它与`{prf:ref}`进行引用。不能包含空格或特殊字符。
* `class`: 文本

	标准的类属性值，可以用来添加自定义CSS或JavaScript。
* `nonumber`: 标志（空）

	关闭标准的自动编号。

示例

**Example**

````{prf:criterion} Weyl 准则
:label: weyls-criterion

韦伊准则表明，数列 $a_n$ 在模 $1$ 下是等分布的，当且仅当对于所有非零整数 $m$，

```{math}
\lim_{n \rightarrow \infty} \frac{1}{n} \sum_{j=1}^{n} \exp^{2 \pi i m a_j} = 0
```
````

MyST 语法

`````
````{prf:criterion} Weyl 准则
:label: weyls-criterion

韦伊准则表明，数列 $a_n$ 在模 $1$ 下是等分布的，当且仅当对于所有非零整数 $m$，

```{math}
\lim_{n \rightarrow \infty} \frac{1}{n} \sum_{j=1}^{n} \exp^{2 \pi i m a_j} = 0
```
````
`````

_来源:_ [Wikipedia](https://en.wikipedia.org/wiki/Equidistributed_sequence#Weyl's_criterion)

#### 引用准则

你可以使用 `{prf:ref}` 角色来引用准则，例如：```{prf:ref}`weyls-criterion` ```，这将用准则的编号替换该引用，如下所示：{prf:ref}`weyls-criterion`。当提供明确的文本时，这个标题将作为引用的标题。

(syntax:remark)=
### 备注

可以使用 `prf:remark` 模式包含备注指令。该指令默认是枚举的，并且可以接受可选的标题参数。还支持以下选项：

* `label` : 文本

	您可以用来引用备注的唯一标识符，不能包含空格或特殊字符。
* `class` : 文本

	备注的 class 属性的值，可以用来添加自定义 CSS 或 JavaScript。
* `nonumber` : 标志（空）

	关闭备注自动编号功能。


```{prf:remark}
:label: my-remark

More generally there is a class of density functions
that possesses this feature, i.e.

$$
\exists g: \mathbb{R}_+ \mapsto \mathbb{R}_+ \ \ \text{ and } \ \ c \geq 0,
\ \ \text{s.t.  the density } \ \ f \ \ \text{of} \ \ Z  \ \
\text{ has the form } \quad f(z) = c g(z\cdot z)
$$

This property is called **spherical symmetry** (see p 81. in Leamer
(1978))
```

MyST 语法

````
```{prf:remark}
:label: my-remark

More generally there is a class of density functions
that possesses this feature, i.e.

$$
\exists g: \mathbb{R}_+ \mapsto \mathbb{R}_+ \ \ \text{ and } \ \ c \geq 0,
\ \ \text{s.t.  the density } \ \ f \ \ \text{of} \ \ Z  \ \
\text{ has the form } \quad f(z) = c g(z\cdot z)
$$

This property is called **spherical symmetry** (see p 81. in Leamer
(1978))
```
````

_来源:_ [QuantEcon](https://python-advanced.quantecon.org/black_litterman.html)

#### 引用说明

你可以通过使用`{prf:ref}`角色来引用一个说明，例如：```{prf:ref}`my-remark````, 这将会把引用替换为说明编号，如下所示：{prf:ref}`my-remark`。当提供了明确的文本时，这个标题将作为参考的标题。

(syntax:conjecture)=
### 猜想

**示例**

```{prf:conjecture} 虚假的 $\gamma$ 猜想
:label: my-conjecture

这是虚拟的猜想，用以说明标题中可以使用数学表达。
```

MyST 语法
````
```{prf:conjecture} 虚假的 $\gamma$ 猜想
:label: my-conjecture

这是虚拟的猜想，用以说明标题中可以使用数学表达。
```
````

#### 引用猜想

您可以使用 `{prf:ref}` 角色来引用猜想，例如：```{prf:ref}`my-conjecture` ```，这将会将引用替换为猜想编号，如下所示：{prf:ref}`my-conjecture`。当提供了明确的文本时，此标题将作为引用的标题。

(syntax:corollary)=
### 推论

推论指令可以通过使用 `prf:corollary` 模式来包含。默认情况下，该指令会被编号，并且可以接受一个可选的标题参数。以下选项也被支持：

* `label` : text

	为您的推论提供一个唯一的标识符，您可以使用 `{prf:ref}` 来引用它。不能包含空格或特殊字符。
* `class` : text

	推论的类属性的值，可以用来添加自定义的CSS或JavaScript。
* `nonumber` : flag (empty)

	关闭推论自动编号。

示例

```{prf:corollary}
:label: my-corollary

If $A$ is a convergent matrix, then there exists a matrix norm such
that $\vert \vert A \vert \vert < 1$.
```

````
```{prf:corollary}
:label: my-corollary

If $A$ is a convergent matrix, then there exists a matrix norm such
that $\vert \vert A \vert \vert < 1$.
```
````

_来源:_ [QuantEcon](https://python-intro.quantecon.org/_static/lecture_specific/linear_models/iteration_notes.pdf)

#### 引用推论

您可以使用 `{prf:ref}` 角色来引用推论，例如：```{prf:ref}`my-corollary````，这将用推论编号替换引用，如：{prf:ref}`my-corollary`。当提供明确的文本时，此标题将作为参考的标题。

(syntax:algorithm)=
### 算法

可以使用 `prf:algorithm` 模式包含算法指令。该指令默认是枚举的，并且可以接受一个可选的标题参数。还支持以下选项：

* `label` : 文本

	您可以用来引用算法的唯一标识符，不能包含空格或特殊字符。
* `class` : 文本

	算法的 class 属性的值，可以用来添加自定义的 CSS 或 JavaScript。
* `nonumber` : 标志（空）

	关闭算法自动编号。

```{prf:algorithm} Ford–Fulkerson
:label: my-algorithm

**Inputs** Given a Network $G=(V,E)$ with flow capacity $c$, a source node $s$, and a sink node $t$

**Output** Compute a flow $f$ from $s$ to $t$ of maximum value

1. $f(u, v) \leftarrow 0$ for all edges $(u,v)$
2. While there is a path $p$ from $s$ to $t$ in $G_{f}$ such that $c_{f}(u,v)>0$ for all edges $(u,v) \in p$:

	1. Find $c_{f}(p)= \min \{c_{f}(u,v):(u,v)\in p\}$
	2. For each edge $(u,v) \in p$

		1. $f(u,v) \leftarrow f(u,v) + c_{f}(p)$ *(Send flow along the path)*
		2. $f(u,v) \leftarrow f(u,v) - c_{f}(p)$ *(The flow might be "returned" later)*
```

MyST 语法

````
```{prf:algorithm} Ford–Fulkerson
:label: my-algorithm

**Inputs** Given a Network $G=(V,E)$ with flow capacity $c$, a source node $s$, and a sink node $t$

**Output** Compute a flow $f$ from $s$ to $t$ of maximum value

1. $f(u, v) \leftarrow 0$ for all edges $(u,v)$
2. While there is a path $p$ from $s$ to $t$ in $G_{f}$ such that $c_{f}(u,v)>0$ for all edges $(u,v) \in p$:

	1. Find $c_{f}(p)= \min \{c_{f}(u,v):(u,v)\in p\}$
	2. For each edge $(u,v) \in p$

		1. $f(u,v) \leftarrow f(u,v) + c_{f}(p)$ *(Send flow along the path)*
		2. $f(u,v) \leftarrow f(u,v) - c_{f}(p)$ *(The flow might be "returned" later)*
```
````

_Source:_ [Wikipedia](https://en.wikipedia.org/wiki/Ford%E2%80%93Fulkerson_algorithm)

#### 引用算法

您可以使用 `{prf:ref}` 角色来引用算法，例如：```{prf:ref}`my-algorithm` ```，这将把引用替换为算法编号，例如： {prf:ref}`my-algorithm`。当提供明确的文本时，该标题将作为引用的标题。

(syntax:example)=
### 示例

可以使用 `prf:example` 模式包含示例指令。默认情况下，该指令会被枚举，并且可以接受可选的标题参数。还支持以下选项：

* `label` : 文本

	您可以使用它来引用您的示例，格式为 `{prf:ref}`。不能包含空格或特殊字符。
* `class` : 文本

	示例的 class 属性的值，可以用来添加自定义的 CSS 或 JavaScript。
* `nonumber` : 标记（空）

	关闭示例自动编号功能。


````{prf:example}
:label: my-example

Next, we shut down randomness in demand and assume that the demand shock
$\nu_t$ follows a deterministic path:


```{math}
\nu_t = \alpha + \rho \nu_{t-1}
```
Again, we’ll compute and display outcomes in some figures

```python
ex2 = SmoothingExample(C2=[[0], [0]])

x0 = [0, 1, 0]
ex2.simulate(x0)
```
````

MyST 语法

`````
````{prf:example}
:label: my-example

Next, we shut down randomness in demand and assume that the demand shock
$\nu_t$ follows a deterministic path:


```{math}
\nu_t = \alpha + \rho \nu_{t-1}
```
Again, we’ll compute and display outcomes in some figures

```python
ex2 = SmoothingExample(C2=[[0], [0]])

x0 = [0, 1, 0]
ex2.simulate(x0)
```
````
`````

_来源:_ [QuantEcon](https://python.quantecon.org/lq_inventories.html#Example-2)

#### 引用示例

您可以通过使用 `{prf:ref}` 角色来引用示例，例如：```{prf:ref}`my-example` ```，这将用示例编号替换引用，如下所示：{prf:ref}`my-example`。当提供显式文本时，此标题将作为引用的标题。

好的，我会翻译你提供的段落。以下是中文翻译：

(syntax:property)=
### 属性

可以使用 `prf:property` 模式来包含一个属性指令。默认情况下，此指令会进行枚举，并且可以接受一个可选的标题参数。还支持以下选项：

* `label` : 文本

	这是您的属性的唯一标识符，您可以使用 `{prf:ref}` 来引用它。不能包含空格或特殊字符。
* `class` : 文本

	这是属性的类属性值，可用于添加自定义 CSS 或 JavaScript。
* `nonumber` : 标志（空）

	关闭属性自动编号功能。

示例


```{prf:property}
:label: my-property

This is a dummy property to illustrate the directive.
```

MyST 语法

````

```{prf:property}
:label: my-property

This is a dummy property to illustrate the directive.
```
````

#### 引用属性

您可以使用 `{prf:ref}` 角色来引用一个属性，例如：```{prf:ref}`my-property````，这将会把引用替换为属性编号，如下所示：{prf:ref}`my-property`。当提供明确的文本时，此标题将作为引用的标题。

(syntax:observation)=
### 观测

可以通过`prf:observation`模式包含一个观测指令。该指令默认情况下会被枚举，并可以接受一个可选的标题参数。还支持以下选项：

* `label` : 文本

	用于您的观测的唯一标识符，您可以使用它与`{prf:ref}`进行引用。不能包含空格或特殊字符。
* `class` : 文本

	观测的类属性的值，可用于添加自定义CSS或JavaScript。
* `nonumber` : 标志（空）

	关闭观测自动编号功能。

示例


```{prf:observation}
:label: my-observation

This is a dummy observation directive.
```

MyST 语法

````

```{prf:observation}
:label: my-observation

This is a dummy observation directive.
```
````

#### 引用观测

您可以使用 `{prf:ref}` 角色来引用一个观察，例如：```{prf:ref}`my-observation` ```，这将用观察编号替换引用，如下所示：{prf:ref}`my-observation`。当提供明确文本时，此标题将作为引用的标题。

(syntax:proposition)=
### 命题

可以使用 `prf:proposition` 模式包含一个命题指令。默认情况下，该指令是枚举的，并且可以接受一个可选的标题参数。还支持以下选项：

* `label` : 文本

	您可以用来引用命题的唯一标识符，不能包含空格或特殊字符。
* `class` : 文本

	命题的 class 属性的值，可用于添加自定义 CSS 或 JavaScript。
* `nonumber` : 标志（空）

	关闭命题自动编号。

示例

```{prf:proposition}
:label: my-proposition

This is a dummy proposition directive.
```

MyST 语法

````
```{prf:proposition}
:label: my-proposition

This is a dummy proposition directive.
```
````

#### 引用命题

您可以使用 `{prf:ref}` 角色来引用一个命题，例如：```{prf:ref}`my-proposition` ```，这将用命题编号替换该引用，如下所示：{prf:ref}`my-proposition`。当提供明确的文本时，此标题将作为引用的标题。

(syntax:assumption)=
### 假设

可以通过使用 `prf:assumption` 模式包含假设指令。默认情况下，该指令会被枚举，并且可以接受一个可选的标题参数。还支持以下选项：

* `label` : 文本

	一个用于假设的唯一标识符，您可以使用它与`{prf:ref}`进行引用。不能包含空格或特殊字符。
* `class` : 文本

	假设类属性的值，可用于添加自定义CSS或JavaScript。
* `nonumber` : 标志（空）

	关闭假设自动编号。

示例

```{prf:assumption}
:label: my-assumption

This is a dummy assumption directive.
```

MyST

````
```{prf:assumption}
:label: my-assumption

This is a dummy assumption directive.
```
````

### 引用假设

你可以通过使用 `{prf:ref}` 角色来引用一个假设，例如：```{prf:ref}`my-assumption` ```，这将把引用替换为假设编号，如下所示：{prf:ref}`my-assumption`。当提供了明确的文本时，这个标题将作为引用的标题。

## 如何隐藏内容

指令内容可以通过`dropdown`类进行隐藏，该类通过[sphinx-togglebutton](https://sphinx-togglebutton.readthedocs.io/en/latest/)提供。如果您的项目使用了[MyST-NB](https://myst-nb.readthedocs.io/en/latest/)扩展，则无需激活`sphinx-togglebutton`，因为它已与`MyST-NB`捆绑在一起。

对于Sphinx项目，请在`conf.py`中的`extensions`列表添加`"sphinx_togglebutton"`以激活该扩展。

在Jupyter Book项目中，将`sphinx_togglebutton`添加到`extra_extensions`下。

```yaml
sphinx:
  extra_extensions:
    - sphinx_togglebutton
```

要隐藏指令，只需在指令选项中添加`:class: dropdown`。

**示例**

```{prf:theorem}
:class: dropdown

这是一个如何隐藏指令内容的示例。
```

**MyST语法**：

````
```{prf:theorem}
:class: dropdown

这是一个如何隐藏指令内容的示例。
```
````