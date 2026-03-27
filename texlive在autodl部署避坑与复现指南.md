# TeX Live 在 AutoDL 部署避坑与复现指南

## 📋 说明

本指南记录 TeX Live 在 AutoDL 服务器上部署的过程，包含踩坑记录和一键复现方案。

- **安装位置**: `/root/texlive`
- **适用平台**: AutoDL (Ubuntu 20.04/22.04)
- **网络加速**: 使用 `source /etc/network_turbo` (仅限 AutoDL)

---

## 🚫 避坑记录

### ❌ 坑 1: 直接安装完整版 (scheme-full)

**问题**: 
- 完整版有 **5000+ 个包**，需要下载约 4-5GB
- AutoDL 后台任务有 **1 小时超时限制**
- 尝试了多次，每次都是超时失败，浪费大量时间

**表现**:
```
Installing [2508/5014, time/total: 59:03/06:20:15]: levy [59k]
# 然后任务超时退出
```

**结论**: 完整版无法在 AutoDL 单任务时间内完成，需要分多次或使用其他方案。

---

### ❌ 坑 2: 安装中型版本 (scheme-medium)

**问题**:
- 中型版有 **1521 个包**，预计需要 2-3 小时
- 同样超出 1 小时限制，安装到约 30-40% 就超时了

**表现**:
```
Installing [0574/1521, time/total: 59:36/02:14:41]: hausarbeit-jura [353k]
# 任务超时
```

**结论**: 中型版也不行，必须选择能在 1 小时内完成的方案。

---

### ❌ 坑 3: 使用阿里云镜像

**问题**:
- 阿里云镜像 (`mirrors.aliyun.com`) 在高峰期连接不稳定
- 大量包下载失败，安装器不断重试，拖慢速度

**表现**:
```
TLPDB::_install_data: downloading did not succeed for https://mirrors.aliyun.com/CTAN/...
Failed to install xxx, will be retried later.
```

**结论**: 使用清华镜像更稳定。

---

### ❌ 坑 4: 安装文档和源码

**问题**:
- 默认配置会安装文档 (`docfiles`) 和源码 (`srcfiles`)
- 这部分占用大量空间且非必需

**结论**: 基础版本安装时建议关闭，如需可后续单独安装。

---

## ✅ 复现指南（一次性成功版）

### 步骤 1: 准备安装配置文件

创建 `/tmp/texlive.profile`:

```bash
cat > /tmp/texlive.profile << 'EOF'
# Tex Live installation profile - Basic scheme (一次成功版)
selected_scheme scheme-basic
TEXDIR /root/texlive
TEXMFCONFIG ~/.texlive/texmf-config
TEXMFHOME ~/texmf
TEXMFLOCAL /root/texlive/texmf-local
TEXMFSYSCONFIG /root/texlive/texmf-config
TEXMFSYSVAR /root/texlive/texmf-var
TEXMFVAR ~/.texlive/texmf-var
binary_x86_64-linux 1
instopt_adjustpath 0
instopt_adjustrepo 1
instopt_letter 0
instopt_portable 0
instopt_write18_restricted 1
tlpdbopt_autobackup 1
tlpdbopt_backupdir tlpkg/backups
tlpdbopt_create_formats 1
tlpdbopt_desktop_integration 1
tlpdbopt_file_assocs 1
tlpdbopt_generate_updmap 0
tlpdbopt_install_docfiles 0      # 不装文档，节省空间和时间
tlpdbopt_install_srcfiles 0      # 不装源码，节省空间和时间
tlpdbopt_post_code 1
tlpdbopt_sys_bin /usr/local/bin
tlpdbopt_sys_info /usr/local/share/info
tlpdbopt_sys_man /usr/local/share/man
tlpdbopt_w32_multi_user 1
EOF
```

**关键配置**:
- `selected_scheme scheme-basic` - 选择基础版（132个包，约139MB）
- `tlpdbopt_install_docfiles 0` - 不安装文档
- `tlpdbopt_install_srcfiles 0` - 不安装源码

---

### 步骤 2: 下载并解压安装器

```bash
# 进入临时目录
cd /tmp

# 下载安装器（使用清华镜像）
wget -O install-tl-unx.tar.gz "https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet/install-tl-unx.tar.gz"

# 解压
tar -xzf install-tl-unx.tar.gz

# 查看解压后的目录名
ls -d install-tl-*
```

---

### 步骤 3: 执行安装

```bash
# 使用 AutoDL 网络加速（关键！）
source /etc/network_turbo

# 进入安装器目录
cd /tmp/install-tl-20260326  # 注意：日期可能会变，按实际目录名调整

# 执行安装（指定清华镜像）
./install-tl --profile=/tmp/texlive.profile --repository="https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet"
```

**安装时间**: 约 2-3 分钟

**成功标志**:
```
Welcome to TeX Live!
Add /root/texlive/bin/x86_64-linux to your PATH for current and future sessions.
```

---

### 步骤 4: 配置环境变量

```bash
# 添加到 ~/.bashrc
echo 'export PATH="/root/texlive/bin/x86_64-linux:$PATH"' >> ~/.bashrc
echo 'export MANPATH="/root/texlive/texmf-dist/doc/man:$MANPATH"' >> ~/.bashrc
echo 'export INFOPATH="/root/texlive/texmf-dist/doc/info:$INFOPATH"' >> ~/.bashrc

# 立即生效
source ~/.bashrc
```

---

### 步骤 5: 验证安装

```bash
# 检查版本
pdflatex --version

# 测试编译
cat > /tmp/test.tex << 'EOF'
\documentclass{article}
\usepackage{amsmath}
\begin{document}
Hello, TeX Live!
\[
    E = mc^2
\]
\end{document}
EOF

cd /tmp && pdflatex test.tex

# 查看生成的 PDF
ls -la test.pdf
```

---

## 📦 基础版包含的工具

| 工具 | 版本 | 说明 |
|------|------|------|
| pdflatex | pdfTeX 3.141592653-2.6-1.40.29 | 标准 PDF 编译 |
| lualatex | LuaHBTeX 1.24.0 | LuaTeX 编译 |
| bibtex | BibTeX 0.99e | 参考文献 |
| dvips |  | DVI 转 PS |
| dvipdfmx |  | DVI 转 PDF |
| makeindex |  | 索引生成 |
| metafont |  | 字体设计 |

---

## 🔧 后续扩展（按需安装）

基础版只包含最常用的宏包，如需更多可以单独安装：

```bash
# 示例：安装中文支持
tlmgr install collection-langchinese

# 安装额外字体
tlmgr install collection-fontsrecommended

# 安装 Beamer
tlmgr install beamer

# 查看已安装的包
tlmgr list --only-installed

# 搜索包
tlmgr search <keyword>
```

---

## 📝 总结

| 方案 | 包数量 | 大小 | 安装时间 | 是否可行 |
|------|--------|------|----------|----------|
| scheme-full | 5000+ | ~5GB | 5-6小时 | ❌ 超时 |
| scheme-medium | 1521 | ~2GB | 2-3小时 | ❌ 超时 |
| **scheme-basic** | **132** | **~139MB** | **~2分钟** | ✅ **推荐** |

**核心经验**: 在 AutoDL 上部署 TeX Live，选择 **scheme-basic** + **清华镜像** + **网络加速** 是一击必杀的组合。

---

## 📚 参考

- [TeX Live 官方文档](https://tug.org/texlive/)
- [清华镜像站](https://mirrors.tuna.tsinghua.edu.cn/CTAN/)
- [AutoDL 网络加速](https://www.autodl.com/docs/network/)
