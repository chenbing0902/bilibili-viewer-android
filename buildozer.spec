[app]

# App名称
title = B站播放量助手

# 包名
package.name = bilibiliviewer
package.domain = org.bilibili

# 源文件
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
source.include_patterns = assets/*,images/*,data/*
source.exclude_dirs = tests, bin, .git, .github

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
android.accept_sdk_license = True

# 应用图标和启动屏幕
#icon.filename = %(source.dir)s/data/icon.png
#presplash.filename = %(source.dir)s/data/presplash.png

# 控制台输出（开发时设为1，发布时设为0）
android.logcat_filters = *:S python:D

# Python-for-android 配置
p4a.bootstrap = sdl2
p4a.branch = master
p4a.setup_py = false

# Android 组件配置
android.enable_androidx = True

# 架构选择
android.archs = arm64-v8a

# 版本文件
version.filename = %(source.dir)s/main.py

[buildozer]
# 日志级别 (0 = error only, 1 = info, 2 = debug)
log_level = 2

# 警告：不要使用自定义镜像源，让buildozer使用默认源
# warning.txt = 使用默认源可以避免很多下载问题 
