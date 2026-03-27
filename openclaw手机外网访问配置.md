# OpenClaw 手机外网访问配置指南

## ✅ 配置完成

### 当前状态

| 配置项 | 值 |
|--------|-----|
| **监听地址** | 0.0.0.0:6006 (所有网络接口) |
| **本地地址** | http://127.0.0.1:6006/ |
| **内网地址** | http://172.17.0.8:6006/ |
| **外网映射** | https://u882079-9fb9-97768833.bjb2.seetacloud.com:8443 |
| **模型** | moonshot/kimi-k2.5 |
| **Gateway 状态** | 运行中 ✅ |

---

## 📱 手机访问地址

### 完整链接（含令牌）

```
https://u882079-9fb9-97768833.bjb2.seetacloud.com:8443/#token=5cf19ad1ef02a742bd5a9589124d56b4cbdac0daa2dc4d99
```

**直接在手机浏览器中打开上面的链接即可！**

---

## 🔧 配置步骤（已执行）

### 1. 停止 Gateway
```bash
openclaw gateway stop
# 或
pkill -f "openclaw-gateway"
```

### 2. 修改端口和绑定地址
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 修改端口为 6006
openclaw config set gateway.port 6006

# 修改绑定地址为 lan（允许外部访问）
openclaw config set gateway.bind lan
```

### 3. 启动 Gateway
```bash
cd /root/openclaw
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &
```

---

## ⚠️ 安全提醒

**当前配置允许外部网络访问，请确保：**

1. ✅ 已配置 gateway.auth.token（已配置）
2. ✅ 不要泄露 token 链接
3. ✅ AutoDL 端口映射有访问控制

**风险提示**: `bind=lan` 会监听所有网络接口，任何人知道地址和 token 都可以访问。

---

## 🔍 故障排查

### 无法访问？

1. **检查 Gateway 是否运行**
   ```bash
   ps aux | grep openclaw-gateway
   ```

2. **检查端口监听**
   ```bash
   netstat -tlnp | grep 6006
   # 或
   ss -tlnp | grep 6006
   ```

3. **检查 AutoDL 端口映射**
   - 登录 AutoDL 控制台
   - 确认 6006 端口已映射

4. **查看日志**
   ```bash
   tail -50 /root/openclaw/gateway.log
   ```

---

## 📝 常用命令

### 重启 Gateway
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

pkill -f "openclaw-gateway"
sleep 2
cd /root/openclaw
nohup openclaw gateway > /root/openclaw/gateway.log 2>&1 &
```

### 查看状态
```bash
openclaw gateway status
```

### 获取 Dashboard 链接
```bash
openclaw dashboard --no-open
```

### 恢复本地访问（关闭外网）
```bash
openclaw config set gateway.bind loopback
openclaw config set gateway.port 18789
pkill -f "openclaw-gateway"
```

---

## 🎯 快速检查清单

- [x] Gateway 监听在 0.0.0.0:6006
- [x] AutoDL 端口映射 6006 → 外网
- [x] Token 认证已配置
- [x] 手机可以通过外网地址访问

**全部完成！可以用手机访问 OpenClaw 了！** 🎉
