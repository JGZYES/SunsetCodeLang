# SCL (SunsetCodeLang) 编程语言

## 什么是 SCL

SCL (SunsetCodeLang) 是一种简洁、高效、易于学习的编程语言，设计用于快速原型开发和脚本编写。它具有类似 Python 的语法，但更加轻量级，适合在资源有限的环境中运行。

## 主要特点

- **简洁的语法**：类似 Python 的语法，易于学习和使用
- **轻量级**：核心解释器体积小，运行内存占用低
- **高效执行**：经过优化的解释器，执行速度快
- **插件系统**：支持通过插件扩展功能
- **跨平台**：支持 Windows、Linux 和 macOS
- **易于嵌入**：可以轻松嵌入到其他应用程序中

## 系统要求

- **最低配置**：0.5GHz CPU, 512MB 内存
- **推荐配置**：1GHz CPU, 1GB 内存
- **Python 版本**：Python 3.6 或更高

## 安装方法

### 1. 从源代码安装

```bash
# 克隆仓库
git clone https://github.com/JGZYES/SunsetCodeLang.git
cd scl

# 直接运行
python scl.py your_script.scl
```

## 快速开始

### 第一个 SCL 程序

创建一个名为 `hello.scl` 的文件，内容如下：

```scl
# 导入基础插件
simp{basic}

# 打印 Hello World
sout : "Hello, World!"

# 变量赋值
set x | x : 10
set y | y : 20

# 计算并打印结果
sout : x + y
```

运行程序：

```bash
python scl.py hello.scl
```

### 基本语法

#### 变量赋值

```scl
set x | x : 10
set name | name : "SCL"
```

#### 条件语句

```scl
sif x > 5 |
    sout : "x 大于 5"
sel |
    sout : "x 小于等于 5"
end
```

#### 循环语句

```scl
set i | i : 0
swhi i < 5 |
    sout : i
    set i | i : i + 1
end
```

#### 函数定义

```scl
sdef <add(a, b)>
    sre : a + b
end

set result | result : add(1, 2)
sout : result
```

## 插件系统

SCL 支持通过插件扩展功能。内置插件包括：

- **basic**：基础功能，包括变量、条件、循环等
- **math**：数学运算功能
- **string**：字符串处理功能
- **request**：HTTP 请求功能
- **json**：JSON 处理功能
- **crypto**：加密功能
- **unit**：单位转换功能
- **color**：终端颜色输出功能

### 安装插件

使用 SCD (SCL Plugin Downloader) 工具安装插件：

```bash
# 安装单个插件
python scd.py install math

# 从文件安装多个插件
python scd.py install -t
```

## SCD (SCL Plugin Downloader)

SCD 是 SCL 的插件下载和管理工具，用于安装、更新和管理 SCL 插件。

### 主要功能

- **安装插件**：`scd install xxx` 下载并安装插件
- **更新插件**：`scd update xxx` 更新插件
- **更新 SCD**：`scd update scd` 更新 SCD 本身
- **批量安装**：`scd install plugins.txt -t` 从文件安装插件
- **管理镜像源**：`scd mirror https://xxxxx.xx` 添加镜像源
- **列出插件**：`scd list local` 列出本地插件，`scd list web` 列出远程插件

## 开发工具

### Nano 编辑器

SCL 内置了一个仿 Nano 的终端文本编辑器：

```bash
python scl.py --edit
```

### 打包工具

使用 `pack.py` 将 SCL 代码打包成 Python 代码：

```bash
python pack.py input.scl output.py
```

## 示例程序

### 1. 简单计算器

```scl
simp{basic}
simp{math}

sout : "简单计算器"
sout : "输入第一个数:"
set a | a : input()
sout : "输入运算符 (+, -, *, /):"
set op | op : input()
sout : "输入第二个数:"
set b | b : input()

sif op == "+" |
    set result | result : a + b
selif op == "-" |
    set result | result : a - b
selif op == "*" |
    set result | result : a * b
selif op == "/" |
    set result | result : a / b
sel |
    set result | result : "无效的运算符"
end

sout : "结果: " + result
```

### 2. HTTP 请求示例

```scl
simp{basic}
simp{request}

sout : "发送 HTTP 请求"
set response | response : request : GET<"https://api.github.com/users/octocat">
sout : response
```

## 性能优化

SCL 解释器经过了多方面的优化，包括：

- **缓存机制**：缓存表达式求值结果、tokenize 结果和代码块执行结果
- **内存管理**：限制缓存大小，防止内存过度使用
- **执行优化**：使用快速操作映射和递归下降解析器
- **算法优化**：优化字符串处理和数字转换

这些优化使得 SCL 在低配置设备上也能流畅运行。

## 贡献

欢迎贡献代码、报告 bug 或提出功能建议！请通过 GitHub Issues 或 Pull Requests 参与贡献。

## 许可证

SCL 采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

- **GitHub**：https://github.com/JGZYES/SunsetCodeLang
- **Email**：luoriguodu@qq.com

---

**享受编程的乐趣！** 🌅
