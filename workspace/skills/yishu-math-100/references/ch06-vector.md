# 第6章 平面向量

## 第1节：向量的基本运算

### 1.1 向量的加法

**核心方法：**
- **三角形法则**：$\vec{a} + \vec{b} = \vec{c}$，$\vec{c}$的起点为$\vec{a}$的终点，终点为$\vec{b}$的终点
- **平行四边形法则**：以$\vec{a}, \vec{b}$为邻边作平行四边形，对角线即为$\vec{a} + \vec{b}$
- **坐标运算**：$(x_1, y_1) + (x_2, y_2) = (x_1 + x_2, y_1 + y_2)$

**解题思路：**
1. 利用几何法则作图求解
2. 利用坐标法则进行代数运算
3. 利用加法的结合律和交换律简化计算

**典型题型：**
- 向量加法的几何意义
- 向量加法的坐标运算
- 向量加法的应用（如位移、力等）

**二级结论：**
- $\vec{a} + \vec{b} = \vec{b} + \vec{a}$（交换律）
- $(\vec{a} + \vec{b}) + \vec{c} = \vec{a} + (\vec{b} + \vec{c})$（结合律）
- $\vec{a} + \vec{0} = \vec{a}$，$\vec{a} + (-\vec{a}) = \vec{0}$
- $\vec{a} + \vec{b} = \vec{0} \iff \vec{a} = -\vec{b}$

### 1.2 向量的减法

**核心方法：**
- **三角形法则**：$\vec{a} - \vec{b} = \vec{a} + (-\vec{b})$，$\vec{c} = \vec{a} - \vec{b}$，$\vec{c}$的起点为$\vec{b}$的终点，终点为$\vec{a}$的终点
- **坐标运算**：$(x_1, y_1) - (x_2, y_2) = (x_1 - x_2, y_1 - y_2)$

**解题思路：**
1. 利用三角形法则作图求解
2. 利用坐标法则进行代数运算
3. 将减法转化为加法求解

**典型题型：**
- 向量减法的几何意义
- 向量减法的坐标运算
- 向量减法的应用

**二级结论：**
- $\vec{a} - \vec{b} = \vec{0} \iff \vec{a} = \vec{b}$
- $\vec{a} - \vec{b} = \vec{b} - \vec{a} \iff \vec{a} = \vec{b}$

### 1.3 向量的数乘

**核心方法：**
- **定义**：$\lambda\vec{a} = \vec{0} \iff \lambda = 0$或$\vec{a} = \vec{0}$
- **坐标运算**：$\lambda(x, y) = (\lambda x, \lambda y)$
- **共线条件**：$\vec{a} // \vec{b} \iff \exists \lambda \in \mathbb{R}, \vec{a} = \lambda\vec{b}$

**解题思路：**
1. 利用数乘的几何意义（方向和长度变化）
2. 利用坐标法则进行代数运算
3. 利用共线条件判断向量是否共线

**典型题型：**
- 向量数乘的几何意义
- 向量数乘的坐标运算
- 向量共线/共面的判断
- 利用数乘表示向量关系

**二级结论：**
- $\lambda\mu\vec{a} = \lambda(\mu\vec{a})$（结合律）
- $\lambda(\vec{a} + \vec{b}) = \lambda\vec{a} + \lambda\vec{b}$（分配律）
- $(\lambda + \mu)\vec{a} = \lambda\vec{a} + \mu\vec{a}$（分配律）
- $\vec{a} // \vec{b} \iff \vec{a} \times \vec{b} = \vec{0}$（向量积为零向量）

### 1.4 坐标运算

**核心方法：**
- **加法**：$(x_1, y_1) + (x_2, y_2) = (x_1 + x_2, y_1 + y_2)$
- **减法**：$(x_1, y_1) - (x_2, y_2) = (x_1 - x_2, y_1 - y_2)$
- **数乘**：$\lambda(x, y) = (\lambda x, \lambda y)$
- **数量积**：$(x_1, y_1) \cdot (x_2, y_2) = x_1x_2 + y_1y_2$
- **向量长度**：$|\vec{a}| = \sqrt{x^2 + y^2}$
- **向量夹角**：$\cos\theta = \frac{\vec{a} \cdot \vec{b}}{|\vec{a}| \cdot |\vec{b}|}$

**解题思路：**
1. 利用坐标运算进行代数求解
2. 利用向量长度和夹角公式解决几何问题
3. 利用数量积解决垂直、平行、距离等问题

**典型题型：**
- 向量的坐标运算
- 向量的长度和夹角
- 向量的垂直和平行
- 向量的距离和面积

**二级结论：**
- $|\vec{a} \cdot \vec{b}| = |\vec{a}| \cdot |\vec{b}| \cdot |\cos\theta| \leq |\vec{a}| \cdot |\vec{b}|$
- $|\vec{a} + \vec{b}|^2 = |\vec{a}|^2 + |\vec{b}|^2 + 2\vec{a} \cdot \vec{b}$
- $|\vec{a} - \vec{b}|^2 = |\vec{a}|^2 + |\vec{b}|^2 - 2\vec{a} \cdot \vec{b}$
- $|\vec{a} + \vec{b}| + |\vec{a} - \vec{b}| \geq 2|\vec{a}|$（等号当且仅当$\vec{a} // \vec{b}$时取到）

## 第2节：数量积的常见几何方法

### 2.1 定义法

**核心方法：**
- **定义**：$\vec{a} \cdot \vec{b} = |\vec{a}| \cdot |\vec{b}| \cdot \cos\theta$（$\theta$为$\vec{a}, \vec{b}$的夹角）
- **性质**：
  - $\vec{a} \cdot \vec{b} = \vec{b} \cdot \vec{a}$
  - $\lambda\vec{a} \cdot \vec{b} = \vec{a} \cdot (\lambda\vec{b})$
  - $(\vec{a} + \vec{b}) \cdot \vec{c} = \vec{a} \cdot \vec{c} + \vec{b} \cdot \vec{c}$
  - $\vec{a} \cdot \vec{b} = \vec{0} \iff \vec{a} \perp \vec{b}$

**解题思路：**
1. 利用数量积的定义直接计算
2. 利用数量积的性质进行化简
3. 利用数量积为零判断垂直

**典型题型：**
- 利用数量积的定义计算
- 利用数量积的性质化简
- 利用数量积判断垂直和平行

**二级结论：**
- $|\vec{a} \cdot \vec{b}| = |\vec{a}| \cdot |\vec{b}| \cdot |\cos\theta| \leq |\vec{a}| \cdot |\vec{b}|$
- $\vec{a} \cdot \vec{b} = |\vec{a}| \cdot |\vec{b}| \cdot \cos\theta = \frac{1}{2}(|\vec{a} + \vec{b}|^2 - |\vec{a}|^2 - |\vec{b}|^2)$
- $\vec{a} \cdot \vec{b} = \frac{1}{2}(|\vec{a} - \vec{b}|^2 - |\vec{a}|^2 - |\vec{b}|^2)$

### 2.2 基底法

**核心方法：**
- **基底**：若$\vec{e}_1, \vec{e}_2$不共线，则平面向量集合$\{\vec{a} \mid \vec{a} = x\vec{e}_1 + y\vec{e}_2, x, y \in \mathbb{R}\}$
- **基底表示**：$\vec{a} = x\vec{e}_1 + y\vec{e}_2$
- **基底运算**：
  - $\vec{e}_1 \cdot \vec{e}_1 = |\vec{e}_1|^2$
  - $\vec{e}_2 \cdot \vec{e}_2 = |\vec{e}_2|^2$
  - $\vec{e}_1 \cdot \vec{e}_2 = \vec{e}_2 \cdot \vec{e}_1 = |\vec{e}_1| \cdot |\vec{e}_2| \cdot \cos\theta$（$\theta$为$\vec{e}_1, \vec{e}_2$的夹角）

**解题思路：**
1. 选择合适的基底
2. 将向量表示为基底的线性组合
3. 利用基底运算求解

**典型题型：**
- 基底法求向量坐标
- 利用基底法证明向量等式
- 利用基底法求向量的数量积

**二级结论：**
- 若$\vec{e}_1 \perp \vec{e}_2$，则$\vec{a} \cdot \vec{b} = x_1x_2 + y_1y_2$
- 若$\vec{e}_1 // \vec{e}_2$，则$\vec{a} \cdot \vec{b} = (x_1y_2 - x_2y_1)^2$
- 若$\vec{e}_1 \perp \vec{e}_2$且$|\vec{e}_1| = |\vec{e}_2| = 1$，则$\vec{e}_1, \vec{e}_2$为单位正交基底

### 2.3 坐标法

**核心方法：**
- **坐标表示**：$\vec{a} = (x_1, y_1)$，$\vec{b} = (x_2, y_2)$
- **数量积坐标公式**：$\vec{a} \cdot \vec{b} = x_1x_2 + y_1y_2$
- **长度坐标公式**：$|\vec{a}| = \sqrt{x_1^2 + y_1^2}$
- **夹角坐标公式**：$\cos\theta = \frac{x_1x_2 + y_1y_2}{\sqrt{x_1^2 + y_1^2} \cdot \sqrt{x_2^2 + y_2^2}}$

**解题思路：**
1. 设向量的坐标
2. 利用坐标公式进行计算
3. 利用坐标公式解决几何问题

**典型题型：**
- 向量数量积的坐标运算
- 向量长度的坐标运算
- 向量夹角的坐标运算
- 向量垂直、平行的坐标判断

**二级结论：**
- $|\vec{a} \cdot \vec{b}| = |\vec{a}| \cdot |\vec{b}| \cdot |\cos\theta| \leq |\vec{a}| \cdot |\vec{b}|$
- $\vec{a} \perp \vec{b} \iff x_1x_2 + y_1y_2 = 0$
- $\vec{a} // \vec{b} \iff x_1y_2 - x_2y_1 = 0$
- $\cos\theta = \frac{x_1x_2 + y_1y_2}{\sqrt{x_1^2 + y_1^2} \cdot \sqrt{x_2^2 + y_2^2}}$

### 2.4 投影法

**核心方法：**
- **投影定义**：$\vec{a}$在$\vec{b}$方向上的投影为$|\vec{a}| \cos\theta$（$\theta$为$\vec{a}, \vec{b}$的夹角）
- **向量投影**：$\vec{a}$在$\vec{b}$方向上的投影向量为$(\vec{a} \cdot \frac{\vec{b}}{|\vec{b}|}) \cdot \frac{\vec{b}}{|\vec{b}|} = \frac{\vec{a} \cdot \vec{b}}{|\vec{b}|^2} \vec{b}$
- **投影公式**：$\vec{a} \cdot \vec{b} = |\vec{b}| \cdot (\vec{a} \text{在}\vec{b}\text{上的投影}) = |\vec{a}| \cdot (\vec{b} \text{在}\vec{a}\text{上的投影})$

**解题思路：**
1. 利用投影的几何意义
2. 利用投影公式进行计算
3. 利用投影解决几何问题

**典型题型：**
- 向量投影的计算
- 利用投影求距离
- 利用投影求角度

**二级结论：**
- $\vec{a}$在$\vec{b}$上的投影长度为$|\vec{a}| \cos\theta$
- $\vec{a}$在$\vec{b}$方向上的投影向量为$\frac{\vec{a} \cdot \vec{b}}{|\vec{b}|^2} \vec{b}$
- $|\vec{a} \cdot \vec{b}| = |\vec{a}| \cdot |\vec{b}| \cdot |\cos\theta| = |\vec{b}| \cdot |\vec{a}| \cdot |\cos\theta| = |\vec{b}| \cdot (\text{投影长度})$

## 第3节：向量的分解与共线性质

### 3.1 三点共线

**核心方法：**
- **条件**：$A, B, C$三点共线 $\iff \exists \lambda \in \mathbb{R}, \vec{AB} = \lambda \vec{AC}$
- **坐标条件**：$(x_1, y_1), (x_2, y_2), (x_3, y_3)$共线 $\iff x_1(y_2 - y_3) + x_2(y_3 - y_1) + x_3(y_1 - y_2) = 0$

**解题思路：**
1. 利用向量共线条件判断三点共线
2. 利用坐标条件判断三点共线
3. 利用共线条件解决几何问题

**典型题型：**
- 三点共线的判断
- 利用共线条件求参数
- 共线向量的表示

**二级结论：**
- $A, B, C$三点共线 $\iff \vec{AB} = \lambda \vec{AC}$（$\lambda \neq 0$）
- $A, B, C$三点共线 $\iff \vec{AB} // \vec{AC}$
- $A, B, C$三点共线 $\iff \vec{AB} + \vec{BC} = \vec{AC}$

### 3.2 等和线

**核心方法：**
- **定义**：若$A, B, C, D$四点共线，且$\vec{AB} + \vec{CD} = \vec{0}$，则$AB = CD$
- **条件**：$\vec{AB} = -\vec{CD} \iff \vec{AB} // \vec{CD}$且$|\vec{AB}| = |\vec{CD}|$

**解题思路：**
1. 利用向量相等的条件判断等和线
2. 利用向量共线和平行的条件判断等和线
3. 利用等和线解决几何问题

**典型题型：**
- 等和线的判断
- 利用等和线求长度
- 利用等和线证明等式

**二级结论：**
- $\vec{AB} = -\vec{CD} \iff \vec{AB} // \vec{CD}$且$|\vec{AB}| = |\vec{CD}|$
- 若$A, B, C, D$共线且$\vec{AB} = -\vec{CD}$，则$AB = CD$，且$AC = BD$
- 若$A, B, C, D, E$共线且$\vec{AB} + \vec{CD} = \vec{AE}$，则$BE = CE$

### 3.3 奔驰定理

**核心方法：**
- **内容**：若$P$是$\triangle ABC$内的一点，则$\frac{AP}{PD} = \frac{AB}{BD} + \frac{AC}{CD} = \frac{BC}{BD + CD}$
- **推广**：若$P$是$\triangle ABC$外的一点，则$\frac{AP}{PD} = \frac{AB}{BD} - \frac{AC}{CD} = \frac{BC}{BD - CD}$

**解题思路：**
1. 利用奔驰定理处理三角形内点问题
2. 利用奔驰定理处理三角形外点问题
3. 利用奔驰定理解决比例问题

**典型题型：**
- 奔驰定理的应用
- 三角形内点/外点的比例问题
- 利用奔驰定理求距离

**二级结论：**
- 若$P$是$\triangle ABC$的内心，则$\frac{AP}{PD} = \frac{AB + AC}{BC}$
- 若$P$是$\triangle ABC$的内心，则$AD = \frac{2bc}{b + c} \cos\frac{A}{2}$
- 若$P$是$\triangle ABC$的内心，则$PD = \frac{2bc}{b + c} \sin\frac{A}{2}$

## 第4节：向量的坐标运算与建系运用

### 4.1 建系技巧

**核心方法：**
- **斜坐标系**：$\vec{e}_1, \vec{e}_2$不共线，$\vec{a} = x\vec{e}_1 + y\vec{e}_2$
- **正交坐标系**：$\vec{e}_1 \perp \vec{e}_2$，$\vec{a} = x\vec{e}_1 + y\vec{e}_2$
- **单位正交基底**：$\vec{e}_1 \perp \vec{e}_2$，$|\vec{e}_1| = |\vec{e}_2| = 1$，$\vec{a} = x\vec{e}_1 + y\vec{e}_2$

**解题思路：**
1. 选择合适的坐标系
2. 建立向量与坐标的对应关系
3. 利用坐标运算解决几何问题

**典型题型：**
- 坐标系的建立
- 向量坐标的表示
- 向量坐标的运算

**二级结论：**
- 若$\vec{e}_1 \perp \vec{e}_2$，则$\vec{a} \cdot \vec{b} = x_1x_2 + y_1y_2$
- 若$\vec{e}_1 \perp \vec{e}_2$且$|\vec{e}_1| = |\vec{e}_2| = 1$，则$\vec{a} = (x, y)$
- 若$\vec{e}_1 // \vec{e}_2$，则$\vec{a} \cdot \vec{b} = (x_1y_2 - x_2y_1)^2$

### 4.2 极化恒等式

**核心方法：**
- **公式**：$\vec{a} \cdot \vec{b} = \frac{1}{4}\left(|\vec{a} + \vec{b}|^2 - |\vec{a} - \vec{b}|^2\right)$
- **证明**：$|\vec{a} + \vec{b}|^2 = |\vec{a}|^2 + |\vec{b}|^2 + 2\vec{a} \cdot \vec{b}$，$|\vec{a} - \vec{b}|^2 = |\vec{a}|^2 + |\vec{b}|^2 - 2\vec{a} \cdot \vec{b}$

**解题思路：**
1. 利用极化恒等式求数量积
2. 利用极化恒等式化简表达式
3. 利用极化恒等式证明等式

**典型题型：**
- 极化恒等式的应用
- 利用极化恒等式求数量积
- 利用极化恒等式证明等式

**二级结论：**
- $\vec{a} \cdot \vec{b} = \frac{1}{4}\left(|\vec{a} + \vec{b}|^2 - |\vec{a} - \vec{b}|^2\right)$
- $\vec{a} \cdot \vec{b} = \frac{1}{2}\left(|\vec{a}|^2 + |\vec{b}|^2 - |\vec{a} - \vec{b}|^2\right)$
- $\vec{a} \cdot \vec{b} = \frac{1}{2}\left(|\vec{a} + \vec{b}|^2 - |\vec{a}|^2 - |\vec{b}|^2\right)$

### 4.3 向量坐标运算

**核心方法：**
- **加法**：$(x_1, y_1) + (x_2, y_2) = (x_1 + x_2, y_1 + y_2)$
- **减法**：$(x_1, y_1) - (x_2, y_2) = (x_1 - x_2, y_1 - y_2)$
- **数乘**：$\lambda(x, y) = (\lambda x, \lambda y)$
- **数量积**：$(x_1, y_1) \cdot (x_2, y_2) = x_1x_2 + y_1y_2$
- **向量长度**：$|\vec{a}| = \sqrt{x^2 + y^2}$
- **向量夹角**：$\cos\theta = \frac{x_1x_2 + y_1y_2}{\sqrt{x_1^2 + y_1^2} \cdot \sqrt{x_2^2 + y_2^2}}$

**解题思路：**
1. 设向量的坐标
2. 利用坐标公式进行计算
3. 利用坐标公式解决几何问题

**典型题型：**
- 向量坐标的运算
- 向量长度的计算
- 向量夹角的计算
- 向量垂直、平行的判断

**二级结论：**
- $|\vec{a} \cdot \vec{b}| = |\vec{a}| \cdot |\vec{b}| \cdot |\cos\theta| \leq |\vec{a}| \cdot |\vec{b}|$
- $\vec{a} \perp \vec{b} \iff x_1x_2 + y_1y_2 = 0$
- $\vec{a} // \vec{b} \iff x_1y_2 - x_2y_1 = 0$
- $|\vec{a} + \vec{b}|^2 = |\vec{a}|^2 + |\vec{b}|^2 + 2\vec{a} \cdot \vec{b}$
- $|\vec{a} - \vec{b}|^2 = |\vec{a}|^2 + |\vec{b}|^2 - 2\vec{a} \cdot \vec{b}$

### 4.4 建系运用

**核心方法：**
- **几何问题坐标化**：将几何问题转化为代数问题
- **距离公式**：$|\vec{AB}| = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$
- **中点公式**：$M(x, y) = \left(\frac{x_1 + x_2}{2}, \frac{y_1 + y_2}{2}\right)$
- **斜率公式**：$k = \frac{y_2 - y_1}{x_2 - x_1}$

**解题思路：**
1. 建立坐标系
2. 将几何图形转化为坐标形式
3. 利用坐标公式进行计算
4. 利用坐标公式解决几何问题

**典型题型：**
- 建系解决几何问题
- 利用坐标公式求距离、中点、斜率
- 利用坐标公式解决直线、圆、向量问题

**二级结论：**
- 三点$(x_1, y_1), (x_2, y_2), (x_3, y_3)$共线 $\iff x_1(y_2 - y_3) + x_2(y_3 - y_1) + x_3(y_1 - y_2) = 0$
- $A(x_1, y_1), B(x_2, y_2), C(x_3, y_3)$，则$S_{\triangle ABC} = \frac{1}{2}|x_1(y_2 - y_3) + x_2(y_3 - y_1) + x_3(y_1 - y_2)|$
- $A(x_1, y_1), B(x_2, y_2)$，则$AB$的中点为$\left(\frac{x_1 + x_2}{2}, \frac{y_1 + y_2}{2}\right)$
