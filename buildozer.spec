[app]

# 应用名称
title = B站播放量助手

# 包名
package.name = bilibiliviewer
package.domain = org.bilibili

# 源文件
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# 版本信息
version = 0.1

# 依赖项
requirements = python3,kivy==2.2.1,plyer,android,requests,urllib3

# Android权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 屏幕方向
orientation = portrait

# Android特定设置
fullscreen = 0
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.arch = arm64-v8a

# Android 组件配置
android.enable_androidx = True

# 架构选择
android.archs = arm64-v8a

# 版本文件
version.filename = %(source.dir)s/main.py
