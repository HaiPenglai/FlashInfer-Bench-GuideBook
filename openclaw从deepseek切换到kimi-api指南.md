# OpenClaw 从 DeepSeek 切换到 Kimi API 完整指南

> **场景**: 已配置 DeepSeek，需要切换到 Kimi (Moonshot) API
> 
> **目标**: 零坑切换，一次性成功

---

## 一、踩坑记录（血泪总结）

### 坑 1: 旧会话不自动切换模型 ❌

**现象**: 
- 配置了 Kimi，但聊天还是显示 DeepSeek
- 模型标签显示 `kimi-k2.5`，但回复说"我是 DeepSeek"

**原因**: 
OpenClaw 的每个会话会记住创建时使用的模型。切换到新模型后，**旧会话不会自动更新**。

**解决**: 点击 **"New Chat"** 创建新会话，或刷新页面重新连接

---

### 坑 2: Kimi API baseUrl 错误 ❌

**现象**: 
```
HTTP 401: Invalid Authentication
```

**原因**: 
OpenClaw 配置的 moonshot baseUrl 默认为 `https://api.moonshot.ai/v1`，但**正确的应该是 `https://api.moonshot.cn/v1`**

**解决**: 修改配置文件或使用正确的 onboard 参数

---

### 坑 3: 配置后不重启 Gateway ❌

**现象**: 
- 配置了 Kimi，但状态还是显示 DeepSeek
- 模型列表没有更新

**原因**: 
配置更改后必须重启 Gateway 才能生效

**解决**: `pkill -f "openclaw-gateway"` 后重新启动

---

### 坑 4: 使用错误的 API key 参数名 ❌

**现象**: 
配置命令执行成功，但 API 调用失败

**原因**: 
OpenClaw 使用 `--moonshot-api-key` 而不是 `--kimi-api-key`

**解决**: 使用正确的参数名 `--moonshot-api-key`

---

## 二、黄金路径：无坑切换步骤 ✅

### 前置条件

- OpenClaw 已部署（版本 2026.3.24+）
- 当前使用 DeepSeek 或其他模型
- 已获取 Kimi API Key: `sk-qfS5c4bmVdNDIyr1FBRXhjFE0p6fTO9cbdTk8sWvkB6MnEli`

---

### 步骤 1: 停止当前 Gateway

```bash
# 加载环境
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 停止当前 Gateway
pkill -f "openclaw-gateway"

# 确认已停止
sleep 2
ps aux | grep openclaw-gateway | grep -v grep || echo "✅ Gateway 已停止"
```

---

### 步骤 2: 配置 Kimi API（关键步骤）

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 配置 Kimi（使用 --moonshot-api-key）
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --flow quickstart \
  --moonshot-api-key "sk-qfS5c4bmVdNDIyr1FBRXhjFE0p6fTO9cbdTk8sWvkB6MnEli"
```

**预期输出**:
```
Config overwrite: /root/.openclaw/openclaw.json
Updated ~/.openclaw/openclaw.json
Workspace OK: ~/.openclaw/workspace
Sessions OK: ~/.openclaw/agents/main/sessions
```

---

### 步骤 3: 修复 baseUrl（关键！避坑）

**⚠️ 这是最容易踩的坑！**

OpenClaw 默认配置的 baseUrl 可能是 `api.moonshot.ai`，需要改为 `api.moonshot.cn`：

```bash
# 修复 baseUrl
sed -i 's|api.moonshot.ai/v1|api.moonshot.cn/v1|g' ~/.openclaw/openclaw.json

# 验证修复
grep "moonshot.cn" ~/.openclaw/openclaw.json && echo "✅ baseUrl 已修复"
```

---

### 步骤 4: 验证配置

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 查看模型配置
openclaw models status
```

**关键检查点**:
- `Default: moonshot/kimi-k2.5`
- `moonshot:default=sk-qfS5c...` (API key 已配置)

---

### 步骤 5: 启动 Gateway

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 启用网络加速（可选）
source /etc/network_turbo 2>/dev/null || true

# 启动 Gateway
cd /root/openclaw
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &

echo "Gateway 启动中，PID: $!"
sleep 3

# 验证启动
ps aux | grep openclaw-gateway | grep -v grep && echo "✅ Gateway 启动成功"
```

**日志检查**:
```bash
cat /root/openclaw/gateway.log | grep "agent model"
# 预期输出: agent model: moonshot/kimi-k2.5
```

---

### 步骤 6: 获取 Dashboard 访问链接

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 获取带令牌的 URL
openclaw dashboard --no-open
```

---

### 步骤 7: 浏览器中新建会话（关键！避坑）

**⚠️ 重要：必须新建会话，不能用旧会话！**

1. 复制上面的 URL，在浏览器中打开
2. **点击 "New Chat" 或 "+" 创建新会话**
3. 在新会话中发送消息测试

**验证方法**: 问"你是谁"，应该回答"我是 Kimi"而不是 DeepSeek

---

## 三、一键切换脚本

创建自动化脚本：

```bash
cat > /root/openclaw/switch-to-kimi.sh << 'EOF'
#!/bin/bash
# OpenClaw 从 DeepSeek 切换到 Kimi 一键脚本

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
source /etc/network_turbo 2>/dev/null || true

echo "========================================="
echo "OpenClaw: DeepSeek → Kimi 切换脚本"
echo "========================================="

# 1. 停止旧 Gateway
echo "[1/5] 停止旧 Gateway..."
pkill -f "openclaw-gateway" 2>/dev/null
sleep 2

# 2. 配置 Kimi
echo "[2/5] 配置 Kimi API..."
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --flow quickstart \
  --moonshot-api-key "sk-qfS5c4bmVdNDIyr1FBRXhjFE0p6fTO9cbdTk8sWvkB6MnEli" 2>&1 | grep -E "Updated|Config|Error" || true

# 3. 修复 baseUrl（关键！）
echo "[3/5] 修复 baseUrl..."
sed -i 's|api.moonshot.ai/v1|api.moonshot.cn/v1|g' ~/.openclaw/openclaw.json
if grep -q "moonshot.cn" ~/.openclaw/openclaw.json; then
    echo "✅ baseUrl 已修复为 api.moonshot.cn"
else
    echo "⚠️  baseUrl 修复可能失败"
fi

# 4. 启动 Gateway
echo "[4/5] 启动 Gateway..."
cd /root/openclaw
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &
sleep 3

# 5. 验证状态
echo "[5/5] 验证状态..."
if ps aux | grep openclaw-gateway | grep -v grep > /dev/null; then
    echo "✅ Gateway 启动成功"
    echo ""
    echo "当前模型:"
    openclaw models status 2>/dev/null | grep "Default" || echo "未知"
    echo ""
    echo "访问地址:"
    openclaw dashboard --no-open 2>/dev/null || echo "请手动运行: openclaw dashboard --no-open"
    echo ""
    echo "⚠️  重要：请在浏览器中点击 'New Chat' 创建新会话！"
else
    echo "❌ Gateway 启动失败"
    tail -20 /root/openclaw/gateway.log
fi

echo ""
echo "========================================="
EOF

chmod +x /root/openclaw/switch-to-kimi.sh
```

**使用方法**:
```bash
/root/openclaw/switch-to-kimi.sh
```

---

## 四、验证切换成功

### 方法 1: 命令行验证

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 查看默认模型
openclaw models status | grep "Default"
# 预期: Default: moonshot/kimi-k2.5

# 查看 Gateway 状态
openclaw status | grep "model"
# 预期: agent model: moonshot/kimi-k2.5
```

### 方法 2: Dashboard 验证

1. 打开 Dashboard
2. **点击 "New Chat" 创建新会话**（重要！）
3. 发送消息："你是谁？"
4. 检查回复：
   - ✅ 如果回答"我是 Kimi" → 切换成功
   - ❌ 如果回答"我是 DeepSeek" → 还在用旧会话

### 方法 3: 查看模型标签

在 Dashboard 聊天界面，查看 Assistant 消息旁边的标签：
- ✅ `kimi-k2.5` → 正确
- ❌ `deepseek-chat` → 还在用 DeepSeek

---

## 五、常见问题速查

### Q1: 配置后还是显示 DeepSeek？

**原因**: 使用了旧会话

**解决**: 
- 点击 **"New Chat"** 创建新会话
- 或者刷新页面，重新输入令牌连接

### Q2: HTTP 401 Invalid Authentication？

**原因**: baseUrl 错误

**解决**: 
```bash
sed -i 's|api.moonshot.ai/v1|api.moonshot.cn/v1|g' ~/.openclaw/openclaw.json
# 然后重启 Gateway
pkill -f "openclaw-gateway"
/root/openclaw/switch-to-kimi.sh
```

### Q3: 如何切回 DeepSeek？

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 设置默认模型
openclaw models set deepseek/deepseek-chat

# 重启 Gateway
pkill -f "openclaw-gateway"
cd /root/openclaw && nohup openclaw gateway > gateway.log 2>&1 &
```

### Q4: 查看实时日志？

```bash
# 方法 1
openclaw logs --follow

# 方法 2
tail -f /tmp/openclaw/openclaw-2026-03-27.log

# 方法 3
tail -f /root/openclaw/gateway.log
```

---

## 六、关键配置文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 主配置 | `~/.openclaw/openclaw.json` | 包含 moonshot baseUrl 配置 |
| 认证配置 | `~/.openclaw/agents/main/agent/auth-profiles.json` | API Key 存储 |
| 运行日志 | `/tmp/openclaw/openclaw-*.log` | 详细调用日志 |

### 重要配置项检查

```bash
# 检查 baseUrl
grep "moonshot" ~/.openclaw/openclaw.json

# 应该显示:
# "baseUrl": "https://api.moonshot.cn/v1",
```

---

## 七、模型对比总结

| 特性 | DeepSeek | **Kimi K2.5** | Claude |
|------|----------|---------------|--------|
| 中文能力 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 代码能力 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 长文本 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (200K) | ⭐⭐⭐⭐⭐ |
| 接口稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 国内访问 | ✅ | ✅ | ❌ |
| OpenAI兼容 | ✅ | ✅ | ❌ |

**推荐**: Kimi K2.5 是 OpenClaw 的最佳选择！

---

## 八、Checklist（对照检查）

切换完成后检查：

- [ ] Gateway 已停止 (`pkill -f "openclaw-gateway"`)
- [ ] Kimi 已配置 (`openclaw onboard --moonshot-api-key ...`)
- [ ] baseUrl 已修复 (`api.moonshot.cn/v1`)
- [ ] Gateway 已启动 (`nohup openclaw gateway ...`)
- [ ] 默认模型显示 `moonshot/kimi-k2.5`
- [ ] Dashboard 中点击了 **"New Chat"**
- [ ] 新会话中模型标签显示 `kimi-k2.5`
- [ ] 回复内容显示"我是 Kimi"

**全部勾选 = 切换成功！** ✅

---

**最后更新时间**: 2026-03-27
**推荐模型**: moonshot/kimi-k2.5
**API 地址**: https://api.moonshot.cn/v1
