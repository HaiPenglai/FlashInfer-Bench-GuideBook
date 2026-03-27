# OpenClaw 在 AutoDL 部署避坑与复现指南

## 一、部署环境信息

- **平台**: AutoDL 云服务器
- **系统**: Ubuntu 22.04
- **OpenClaw 版本**: 2026.3.24
- **Node.js 版本**: v22.22.2
- **部署目录**: `/root/openclaw`

---

## 二、踩坑记录（按遇到顺序）

### 坑 1: npm 证书错误
**现象**: 
```
npm error code SELF_SIGNED_CERT_IN_CHAIN
npm error errno SELF_SIGNED_CERT_IN_CHAIN
npm error request to https://registry.npmjs.org/openclaw failed
```

**原因**: AutoDL 网络环境下的证书问题

**解决**:
```bash
# 切换到国内镜像并关闭严格 SSL 检查
npm config set strict-ssl false
npm config set registry https://registry.npmmirror.com
```

---

### 坑 2: 缺少系统依赖（sharp 编译失败）
**现象**:
```
npm error code ENOENT
npm error syscall spawn sh
npm error path /root/.nvm/versions/node/v22.22.2/lib/node_modules/openclaw/node_modules/sharp
```

**原因**: sharp 图片处理库需要 libvips 系统库

**解决**:
```bash
apt-get update && apt-get install -y build-essential libvips-dev
```

---

### 坑 3: 安装过程超时
**现象**: npm install 过程非常慢，容易超时中断

**原因**: OpenClaw 依赖包很多，网络下载慢

**解决**: 使用后台进程安装并持续监控
```bash
# 后台安装
nohup npm install -g openclaw@latest > /root/openclaw/install.log 2>&1 &

# 监控进度
tail -f /root/openclaw/install.log
```

---

### 坑 4: Gateway 启动失败 - 未配置 mode
**现象**:
```
Gateway start blocked: set gateway.mode=local (current: unset) or pass --allow-unconfigured
```

**原因**: 首次安装后 gateway.mode 未设置

**解决**:
```bash
openclaw config set gateway.mode local
```

---

### 坑 5: Gateway 启动失败 - 无法使用 systemd
**现象**:
```
Gateway service disabled.
Start with: openclaw gateway install
systemd user services are unavailable
```

**原因**: AutoDL 容器环境没有 systemd

**解决**: 直接使用前台模式启动（配合 nohup）
```bash
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &
```

---

### 坑 6: 安全审计警告
**现象**: 启动后状态显示安全警告
```
CRITICAL Gateway auth missing on loopback
CRITICAL Browser control has no auth
```

**原因**: 未配置身份验证

**解决**:
```bash
# 配置安全令牌
openclaw config set gateway.auth.token "your-secure-token-$(date +%s)"
openclaw config set gateway.bind loopback
```

---

## 三、完整复现步骤

### 步骤 1: 启用网络加速
```bash
source /etc/network_turbo
echo "网络加速已启用"
```

### 步骤 2: 安装 NVM 和 Node.js 22
```bash
# 安装 NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# 加载 NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 安装 Node.js 22
nvm install 22
nvm use 22
nvm alias default 22

# 验证
node --version  # 应显示 v22.x.x
npm --version   # 应显示 10.x.x
```

### 步骤 3: 配置 npm 镜像（避坑关键）
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 使用国内镜像，避免证书问题
npm config set strict-ssl false
npm config set registry https://registry.npmmirror.com
```

### 步骤 4: 安装系统依赖（避坑关键）
```bash
apt-get update && apt-get install -y build-essential libvips-dev
```

### 步骤 5: 创建安装目录并安装 OpenClaw
```bash
mkdir -p /root/openclaw
cd /root/openclaw

# 加载环境
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
source /etc/network_turbo

# 后台安装（避免超时）
nohup npm install -g openclaw@latest > /root/openclaw/install.log 2>&1 &
echo "安装 PID: $!"

# 查看安装进度（可能需要等待 3-5 分钟）
tail -f /root/openclaw/install.log
```

等待看到 `changed XXX packages` 表示安装成功。

### 步骤 6: 验证安装
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

openclaw --version
openclaw status
```

### 步骤 7: 配置 Gateway（避坑关键）
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 设置 local 模式（必须）
openclaw config set gateway.mode local

# 配置安全令牌（必须）
openclaw config set gateway.auth.token "openclaw-$(date +%s)-$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 16)"

# 绑定本地回环
openclaw config set gateway.bind loopback

echo "配置完成"
```

### 步骤 8: 启动 Gateway
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 前台模式后台运行（容器环境无 systemd）
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &

# 等待启动
sleep 5

# 检查进程
ps aux | grep openclaw-gateway | grep -v grep
```

### 步骤 9: 验证运行状态
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

openclaw status
```

看到 `reachable` 和 `auth token` 表示启动成功。

---

## 四、快捷命令脚本

### 创建启动脚本
```bash
cat > /root/openclaw/start-openclaw.sh << 'EOF'
#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
source /etc/network_turbo 2>/dev/null || true
echo "启动 OpenClaw Gateway..."
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &
echo "Gateway 启动中，PID: $!"
EOF
chmod +x /root/openclaw/start-openclaw.sh
```

### 创建停止脚本
```bash
cat > /root/openclaw/stop-openclaw.sh << 'EOF'
#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
echo "停止 OpenClaw Gateway..."
openclaw gateway stop
EOF
chmod +x /root/openclaw/stop-openclaw.sh
```

---

## 五、常见问题排查

### Q1: 如何查看 Gateway 是否运行？
```bash
ps aux | grep openclaw-gateway | grep -v grep
```

### Q2: 如何查看 Gateway 日志？
```bash
cat /root/openclaw/gateway.log
# 或实时查看
tail -f /root/openclaw/gateway.log
```

### Q3: 如何访问 Dashboard？
Gateway 绑定在 `127.0.0.1:18789`，需要通过 SSH 隧道访问：

```bash
# 在本地电脑执行
ssh -N -L 18789:127.0.0.1:18789 root@<你的服务器IP>

# 然后在浏览器打开
http://localhost:18789/
```

### Q4: 如何更换 AI 模型？
```bash
openclaw models list
openclaw models set <模型名称>
openclaw gateway restart
```

### Q5: 安装过程被中断怎么办？
```bash
# 清理残留进程
pkill -f "npm install openclaw"

# 重新执行安装
rm -f /root/openclaw/install.log
nohup npm install -g openclaw@latest > /root/openclaw/install.log 2>&1 &
```

---

## 六、关键配置说明

### 重要配置文件
- **主配置**: `~/.openclaw/openclaw.json`
- **会话数据**: `~/.openclaw/agents/main/sessions/`
- **日志文件**: `/tmp/openclaw/openclaw-*.log`

### 默认端口
| 服务 | 端口 | 说明 |
|------|------|------|
| Gateway | 18789 | WebSocket + Dashboard |
| Browser | 18791 | 浏览器控制接口 |

### 安全建议
1. 保持 `gateway.bind=loopback`（仅本机访问）
2. 设置强密码的 `gateway.auth.token`
3. 配置文件权限：`chmod 600 ~/.openclaw/openclaw.json`

---

## 七、参考资源

- 官方文档: https://docs.openclaw.ai/
- GitHub: https://github.com/openclaw/openclaw
- 中文社区: https://moltcn.com

---

**最后更新时间**: 2026-03-27
