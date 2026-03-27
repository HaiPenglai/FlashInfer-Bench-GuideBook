# OpenClaw 配置 API 到启动避坑与复现指南

> **前置条件**: OpenClaw 已部署完成（版本 2026.3.24+），Node.js 环境已配置
> 
> **目标**: 从完全未启动状态 → 配置 API → 启动 Gateway → 使用 DeepSeek 成功对话

---

## 一、踩坑记录（血泪总结）

### 坑 1: 使用 anthropic 原生配置 ❌
**错误做法**:
```bash
openclaw config set providers.anthropic.apiKey "xxx"
```
**结果**: 403 Forbidden - Request not allowed

**原因**: 第三方 Claude API (api123.icu) 不支持 anthropic 原生格式，需要 Anthropic-compatible 格式，但配置复杂且容易出错

---

### 坑 2: 使用 openai 格式配置 Claude ❌
**错误做法**:
```bash
openclaw models set openai/claude-sonnet-4-6
```
**结果**: Unknown model: openai/claude-sonnet-4-6

**原因**: OpenClaw 没有内置这个模型别名

---

### 坑 3: Custom Provider 配置参数不全 ❌
**错误做法**:
```bash
openclaw onboard --custom-api-key "xxx" --custom-base-url "xxx"
# 缺少 --custom-compatibility anthropic
```
**结果**: 各种认证错误或 403

**原因**: 必须显式指定 `--custom-compatibility anthropic`，否则默认是 openai 格式

---

### 坑 4: 配置后不重启 Gateway ❌
**错误做法**:
```bash
openclaw onboard ...  # 配置完成
# 直接刷新 Dashboard
```
**结果**: 配置不生效，还是报错

**原因**: onboard 配置后必须重启 Gateway

---

### 坑 5: 使用 session 对话时 agent 认证失败 ❌
**错误做法**:
```bash
openclaw agent --message "test"  # 不指定 session
```
**结果**: Pass --to, --session-id, or --agent to choose a session

**原因**: 必须先创建 session 或通过 Dashboard 聊天

---

## 二、黄金路径：DeepSeek 方案 ✅

### 为什么选择 DeepSeek？

| 方案 | 复杂度 | 稳定性 | 推荐指数 |
|------|--------|--------|----------|
| Anthropic 原生 | ❌ 高 | ❌ 403错误 | ⭐ |
| Custom Provider | ❌ 中 | ❌ 403错误 | ⭐⭐ |
| **DeepSeek** | ✅ **低** | ✅ **稳定** | ⭐⭐⭐⭐⭐ |

DeepSeek 优势：
- OpenClaw 原生支持，无需 Custom Provider
- 国内 API，无网络问题
- 配置简单，一步到位

---

## 三、完整复现步骤（假设 OpenClaw 已部署）

### 步骤 1: 确保 Gateway 已停止

```bash
# 加载环境
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 停止当前 Gateway（如果正在运行）
pkill -f "openclaw-gateway"

# 确认已停止
ps aux | grep openclaw-gateway | grep -v grep || echo "✅ Gateway 已停止"
```

---

### 步骤 2: 配置 DeepSeek API（一键配置）

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 使用 onboard 配置 DeepSeek（推荐方式）
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --flow quickstart \
  --deepseek-api-key "sk-fc2ac9bed67b4c1c805b65b7428b78ac"
```

**预期输出**:
```
Config overwrite: /root/.openclaw/openclaw.json
Updated ~/.openclaw/openclaw.json
Workspace OK: ~/.openclaw/workspace
Sessions OK: ~/.openclaw/agents/main/sessions
```

---

### 步骤 3: 验证配置

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 查看模型配置
openclaw models status
```

**预期输出关键信息**:
```
Default       : deepseek/deepseek-chat
Aliases (1)   : DeepSeek -> deepseek/deepseek-chat
- deepseek effective=profiles:... | deepseek:default=sk-fc2ac...
```

确认看到 `deepseek/deepseek-chat` 和 API key 就对了。

---

### 步骤 4: 启动 Gateway

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 启用网络加速（可选）
source /etc/network_turbo 2>/dev/null || true

# 启动 Gateway
cd /root/openclaw
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &

echo "Gateway 启动中，PID: $!"
```

**验证启动**:
```bash
sleep 3
ps aux | grep openclaw-gateway | grep -v grep && echo "✅ Gateway 启动成功"
```

---

### 步骤 5: 验证 Gateway 状态

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

openclaw status
```

**关键检查点**:
- `Gateway`: reachable
- `Sessions`: 显示 deepseek/deepseek-chat

---

### 步骤 6: 获取 Dashboard 访问链接

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 获取带令牌的 URL
openclaw dashboard --no-open
```

**预期输出**:
```
Dashboard URL: http://127.0.0.1:18789/#token=xxxxx
```

---

### 步骤 7: 在浏览器中打开 Dashboard

复制上面的 URL，在浏览器中打开，格式类似：

```
http://127.0.0.1:18789/#token=openclaw-xxxxxxxx-xxxxxxxx
```

---

### 步骤 8: 开始对话

1. 在 Dashboard 界面点击 **"New Chat"** 或已有会话
2. 在底部输入框输入消息，例如：
   - `"你好，DeepSeek！"`
   - `"你是谁？"`
3. 按 **Enter** 发送

**预期结果**: DeepSeek 正常回复，无 403 错误

---

## 四、快捷命令脚本

创建一键启动脚本：

```bash
cat > /root/openclaw/start-deepseek.sh << 'EOF'
#!/bin/bash
# OpenClaw DeepSeek 一键启动脚本

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
source /etc/network_turbo 2>/dev/null || true

echo "========================================="
echo "OpenClaw + DeepSeek 启动脚本"
echo "========================================="

# 1. 停止旧进程
echo "[1/4] 停止旧 Gateway..."
pkill -f "openclaw-gateway" 2>/dev/null
sleep 2

# 2. 配置检查
echo "[2/4] 检查 DeepSeek 配置..."
MODEL=$(openclaw models status 2>/dev/null | grep "Default" | grep "deepseek" || echo "")
if [ -z "$MODEL" ]; then
    echo "⚠️  DeepSeek 未配置，正在配置..."
    openclaw onboard \
      --non-interactive \
      --accept-risk \
      --flow quickstart \
      --deepseek-api-key "sk-fc2ac9bed67b4c1c805b65b7428b78ac"
else
    echo "✅ DeepSeek 已配置"
fi

# 3. 启动 Gateway
echo "[3/4] 启动 Gateway..."
cd /root/openclaw
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &
sleep 3

# 4. 验证状态
echo "[4/4] 验证状态..."
if ps aux | grep openclaw-gateway | grep -v grep > /dev/null; then
    echo "✅ Gateway 启动成功"
    echo ""
    echo "访问地址:"
    openclaw dashboard --no-open 2>/dev/null || echo "http://127.0.0.1:18789/"
else
    echo "❌ Gateway 启动失败，查看日志:"
    tail -20 /root/openclaw/gateway.log
fi
EOF

chmod +x /root/openclaw/start-deepseek.sh
```

**使用方法**:
```bash
/root/openclaw/start-deepseek.sh
```

---

## 五、常见问题速查

### Q1: Gateway 启动后无法访问？
```bash
# 检查端口占用
netstat -tlnp 2>/dev/null | grep 18789 || ss -tlnp | grep 18789

# 检查日志
tail -50 /root/openclaw/gateway.log
```

### Q2: 模型配置错误如何重置？
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 重新运行 onboard 配置
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --flow quickstart \
  --deepseek-api-key "sk-fc2ac9bed67b4c1c805b65b7428b78ac"
```

### Q3: 如何切换回 Claude？
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 如果之前配置了 custom-api123-icu
openclaw models set custom-api123-icu/claude-sonnet-4-6

# 重启 Gateway
pkill -f "openclaw-gateway"
/root/openclaw/start-deepseek.sh
```

### Q4: 查看实时日志？
```bash
# 方法1: 使用 openclaw 命令
openclaw logs --follow

# 方法2: 直接查看日志文件
tail -f /tmp/openclaw/openclaw-2026-03-27.log
```

---

## 六、关键配置文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 主配置 | `~/.openclaw/openclaw.json` | Gateway 配置、模型设置 |
| 认证配置 | `~/.openclaw/agents/main/agent/auth-profiles.json` | API Key 存储 |
| 模型配置 | `~/.openclaw/agents/main/agent/models.json` | 自定义模型配置 |
| 运行日志 | `/tmp/openclaw/openclaw-*.log` | Gateway 运行日志 |
| 启动日志 | `/root/openclaw/gateway.log` | 当前会话日志 |

---

## 七、总结：成功路径 checklist

- [ ] OpenClaw 已部署（版本 2026.3.24+）
- [ ] Gateway 已停止（`pkill -f "openclaw-gateway"`）
- [ ] 使用 `openclaw onboard --deepseek-api-key "xxx"` 配置
- [ ] 验证模型显示 `deepseek/deepseek-chat`
- [ ] 启动 Gateway（`nohup openclaw gateway ...`）
- [ ] 获取 Dashboard URL（`openclaw dashboard --no-open`）
- [ ] 浏览器打开 URL 开始对话

**按照这个 checklist 操作，100% 成功！**

---

**最后更新时间**: 2026-03-27
**推荐模型**: DeepSeek (deepseek-chat)
**不推荐**: 第三方 Claude API (api123.icu) - 存在 403 问题
