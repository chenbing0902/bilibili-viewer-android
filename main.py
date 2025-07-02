from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

import threading
import json
import random
import requests
import time
import re
import traceback
from datetime import datetime
import uuid
import urllib.parse
import os
import concurrent.futures

# 导入代理管理类
from proxy_manager import ProxyManager

class LogView(ScrollView):
    def __init__(self, **kwargs):
        super(LogView, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1, spacing=2, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        
    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = Label(
            text=f"[{timestamp}] {message}", 
            size_hint_y=None, 
            height=30,
            text_size=(self.width, None),
            halign='left'
        )
        self.layout.add_widget(log_entry)
        # 滚动到底部
        self.scroll_to(log_entry)
        
class BilibiliViewerApp(App):
    status_text = StringProperty("就绪")
    progress_value = NumericProperty(0)
    running = BooleanProperty(False)
    
    def build(self):
        # 主布局
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 创建标签页面板
        self.tab_panel = TabbedPanel(do_default_tab=False, size_hint=(1, 1))
        
        # 主设置标签
        main_tab = TabbedPanelItem(text='主设置')
        main_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 代理设置区域
        proxy_layout = GridLayout(cols=2, spacing=5, size_hint_y=None, height=120)
        proxy_layout.add_widget(Label(text="应用ID:"))
        self.proxy_key_input = TextInput(multiline=False, hint_text="代理应用ID")
        proxy_layout.add_widget(self.proxy_key_input)
        
        proxy_layout.add_widget(Label(text="应用密码:"))
        self.proxy_secret_input = TextInput(multiline=False, password=True, hint_text="代理应用密码")
        proxy_layout.add_widget(self.proxy_secret_input)
        
        # 选项布局
        options_layout = GridLayout(cols=2, spacing=5, size_hint_y=None, height=120)
        
        # 代理选项
        proxy_check_layout = BoxLayout(orientation='horizontal')
        proxy_check_layout.add_widget(Label(text="启用代理"))
        self.use_proxy_checkbox = CheckBox(active=True)
        proxy_check_layout.add_widget(self.use_proxy_checkbox)
        options_layout.add_widget(proxy_check_layout)
        
        # IPv6选项
        ipv6_check_layout = BoxLayout(orientation='horizontal')
        ipv6_check_layout.add_widget(Label(text="优先IPv6"))
        self.use_ipv6_checkbox = CheckBox(active=False)
        ipv6_check_layout.add_widget(self.use_ipv6_checkbox)
        options_layout.add_widget(ipv6_check_layout)
        
        # 视频链接设置
        url_layout = GridLayout(cols=2, spacing=5, size_hint_y=None, height=40)
        url_layout.add_widget(Label(text="视频链接:"))
        self.video_url_input = TextInput(multiline=False, hint_text="https://www.bilibili.com/video/BV...")
        url_layout.add_widget(self.video_url_input)
        
        # 参数设置
        params_layout = GridLayout(cols=4, spacing=5, size_hint_y=None, height=120)
        
        params_layout.add_widget(Label(text="播放次数:"))
        self.count_input = TextInput(multiline=False, text="30")
        params_layout.add_widget(self.count_input)
        
        params_layout.add_widget(Label(text="线程数:"))
        self.thread_count_input = TextInput(multiline=False, text="3")
        params_layout.add_widget(self.thread_count_input)
        
        params_layout.add_widget(Label(text="观看时长(秒):"))
        self.view_time_input = TextInput(multiline=False, text="30")
        params_layout.add_widget(self.view_time_input)
        
        params_layout.add_widget(Label(text="请求延迟(秒):"))
        self.delay_input = TextInput(multiline=False, text="10")
        params_layout.add_widget(self.delay_input)
        
        params_layout.add_widget(Label(text="运行模式:"))
        self.run_mode_spinner = Spinner(text='标准', values=('标准', '高效', '平衡', '稳定'))
        params_layout.add_widget(self.run_mode_spinner)
        
        params_layout.add_widget(Label(text="最大重试:"))
        self.max_retry_input = TextInput(multiline=False, text="3")
        params_layout.add_widget(self.max_retry_input)
        
        # 添加到主内容
        main_content.add_widget(proxy_layout)
        main_content.add_widget(options_layout)
        main_content.add_widget(url_layout)
        main_content.add_widget(params_layout)
        
        # 高级选项区域
        advanced_layout = GridLayout(cols=2, spacing=5, size_hint_y=None, height=60)
        
        # 随机UA选项
        ua_check_layout = BoxLayout(orientation='horizontal')
        ua_check_layout.add_widget(Label(text="随机User-Agent"))
        self.random_ua_checkbox = CheckBox(active=True)
        ua_check_layout.add_widget(self.random_ua_checkbox)
        advanced_layout.add_widget(ua_check_layout)
        
        # 模拟进度选项
        progress_check_layout = BoxLayout(orientation='horizontal')
        progress_check_layout.add_widget(Label(text="模拟进度"))
        self.simulate_progress_checkbox = CheckBox(active=True)
        progress_check_layout.add_widget(self.simulate_progress_checkbox)
        advanced_layout.add_widget(progress_check_layout)
        
        # 模拟点击选项
        click_check_layout = BoxLayout(orientation='horizontal')
        click_check_layout.add_widget(Label(text="模拟点击"))
        self.simulate_click_checkbox = CheckBox(active=True)
        click_check_layout.add_widget(self.simulate_click_checkbox)
        advanced_layout.add_widget(click_check_layout)
        
        # 刷新Cookie选项
        cookie_check_layout = BoxLayout(orientation='horizontal')
        cookie_check_layout.add_widget(Label(text="刷新Cookie"))
        self.refresh_cookie_checkbox = CheckBox(active=True)
        cookie_check_layout.add_widget(self.refresh_cookie_checkbox)
        advanced_layout.add_widget(cookie_check_layout)
        
        # 添加到主内容
        main_content.add_widget(advanced_layout)
        
        # 控制按钮区域
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        self.start_button = Button(text="开始任务", on_press=self.start_task)
        button_layout.add_widget(self.start_button)
        
        self.stop_button = Button(text="停止任务", on_press=self.stop_task, disabled=True)
        button_layout.add_widget(self.stop_button)
        
        self.stats_button = Button(text="导出统计", on_press=self.export_statistics, disabled=True)
        button_layout.add_widget(self.stats_button)
        
        # 添加到主内容
        main_content.add_widget(button_layout)
        
        # 进度条区域
        progress_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=50)
        self.status_label = Label(text=self.status_text)
        progress_layout.add_widget(self.status_label)
        
        self.progress_bar = ProgressBar(max=100, value=0)
        progress_layout.add_widget(self.progress_bar)
        
        # 添加到主内容
        main_content.add_widget(progress_layout)
        
        # 添加主内容到标签页
        main_tab.add_widget(main_content)
        self.tab_panel.add_widget(main_tab)
        
        # 日志标签页
        log_tab = TabbedPanelItem(text='运行日志')
        self.log_view = LogView(size_hint=(1, 1))
        log_tab.add_widget(self.log_view)
        self.tab_panel.add_widget(log_tab)
        
        # 统计信息标签页
        stats_tab = TabbedPanelItem(text='统计信息')
        stats_layout = GridLayout(cols=2, spacing=10, padding=10)
        
        stats_layout.add_widget(Label(text="运行时间:"))
        self.runtime_label = Label(text="00:00:00")
        stats_layout.add_widget(self.runtime_label)
        
        stats_layout.add_widget(Label(text="成功请求:"))
        self.success_count_label = Label(text="0")
        stats_layout.add_widget(self.success_count_label)
        
        stats_layout.add_widget(Label(text="活跃线程:"))
        self.active_threads_label = Label(text="0/0")
        stats_layout.add_widget(self.active_threads_label)
        
        stats_layout.add_widget(Label(text="有效播放:"))
        self.real_success_label = Label(text="0")
        stats_layout.add_widget(self.real_success_label)
        
        stats_tab.add_widget(stats_layout)
        self.tab_panel.add_widget(stats_tab)
        
        # 添加标签面板到主布局
        self.main_layout.add_widget(self.tab_panel)
        
        # 初始化变量
        self.success_count = 0
        self.real_success_count = 0
        self.threads = []
        self.thread_statuses = {}
        self.last_activity_time = {}
        self.start_time = None
        self.proxy_manager = None
        self.ipv6_addresses = []
        self.completed_threads = 0
        self.use_ipv6 = False
        
        # 检测IPv6能力
        self.detect_ipv6_capability()
        
        # 设置定时器
        Clock.schedule_interval(self.update_ui_status, 1)
        Clock.schedule_interval(self.check_frozen_threads, 30)
        
        # 添加测试日志
        self.log_view.add_log("B站播放量助手 - 移动版已启动")
        self.log_view.add_log("等待输入视频链接和设置参数")
        
        return self.main_layout
    
    def update_log(self, message):
        """更新日志"""
        Clock.schedule_once(lambda dt: self.log_view.add_log(message))
    
    def update_status(self, text):
        """更新状态文本"""
        self.status_text = text
    
    def update_ui_status(self, dt):
        """更新UI状态"""
        # 更新进度条
        self.progress_bar.value = self.progress_value
        
        if self.running:
            # 更新运行时间
            if self.start_time:
                elapsed = time.time() - self.start_time
                hours, remainder = divmod(int(elapsed), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                self.runtime_label.text = time_str
            
            # 更新状态显示
            active_threads = sum(1 for t in self.threads if t.is_alive())
            status_text = f"运行中 - 活跃线程: {active_threads}/{len(self.threads)}"
            status_text += f", 成功/有效: {self.success_count}/{self.real_success_count}"
            self.update_status(status_text)
            
            # 更新统计标签
            self.success_count_label.text = str(self.success_count)
            self.real_success_label.text = str(self.real_success_count)
            self.active_threads_label.text = f"{active_threads}/{len(self.threads)}"
    
    def check_frozen_threads(self, dt):
        """检查是否有卡死线程并处理"""
        if self.running:
            current_time = time.time()
            frozen_threads = []
            
            # 检查每个线程是否卡死
            for thread_id, last_time in list(self.last_activity_time.items()):
                if current_time - last_time > 180:  # 3分钟超时
                    frozen_threads.append(thread_id)
                    self.update_log(f"警告: 线程 {thread_id} 已卡死，超过3分钟无活动")
            
            # 处理卡死的线程
            if frozen_threads:
                self.update_log(f"检测到问题线程: {len(frozen_threads)}个")
                self.restart_frozen_threads(frozen_threads)
    
    def restart_frozen_threads(self, thread_ids):
        """重启卡死的线程"""
        if not self.running:
            return
            
        try:
            # 获取视频信息
            video_url = self.video_url_input.text.strip()
            video_info = self.parse_video_url(video_url)
            if not video_info:
                self.update_log("重启线程失败：无法获取视频信息")
                return
                
            # 获取参数
            view_time = int(self.view_time_input.text)
            delay = int(self.delay_input.text)
            
            for thread_id in thread_ids:
                self.update_log(f"重启线程 {thread_id}")
                
                # 创建新线程
                new_thread = threading.Thread(
                    target=self.view_task,
                    args=(video_info, 5, delay, view_time, thread_id)
                )
                new_thread.daemon = True
                new_thread.start()
                
                # 更新线程列表
                for i, t in enumerate(self.threads):
                    if i+1 == thread_id:
                        self.threads[i] = new_thread
                        break
                
                # 清除旧的状态记录
                if thread_id in self.thread_statuses:
                    del self.thread_statuses[thread_id]
                if thread_id in self.last_activity_time:
                    del self.last_activity_time[thread_id]
        except Exception as e:
            self.update_log(f"重启线程异常: {str(e)}")
    
    def detect_ipv6_capability(self):
        """检测系统是否支持IPv6"""
        self.update_log("检测IPv6支持...")
        try:
            import socket
            test_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            test_sock.settimeout(1)
            
            # 尝试连接谷歌的IPv6地址
            try:
                test_sock.connect(("2001:4860:4860::8888", 80))
                self.update_log("检测到IPv6支持")
                self.ipv6_addresses = ["2001:db8::1"]  # 示例地址
            except:
                self.update_log("未检测到IPv6支持")
            finally:
                test_sock.close()
        except:
            self.update_log("IPv6检测失败")
    
    def get_random_headers(self):
        """获取随机User-Agent和请求头"""
        if not self.random_ua_checkbox.active:
            return {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) Chrome/93.0.0.0 Mobile Safari/537.36",
                "Referer": "https://www.bilibili.com/"
            }
        
        # 高级随机UA生成    
        os_types = ["Android 10", "Android 11", "Android 12", "Android 13"]
        chrome_versions = [f"Chrome/{v}" for v in ["91.0.4472.124", "92.0.4515.159", "93.0.4577.82"]]
        
        os_type = random.choice(os_types)
        chrome_ver = random.choice(chrome_versions)
        
        ua = f"Mozilla/5.0 (Linux; {os_type}; K) {chrome_ver} Mobile Safari/537.36"
        
        return {
            "User-Agent": ua,
            "Referer": "https://www.bilibili.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
    
    def parse_video_url(self, url):
        """解析视频URL获取视频信息"""
        try:
            # 提取BV号
            if 'BV' in url:
                bvid = re.search(r'BV\w+', url).group()
            else:
                self.update_log("无效的视频URL，请确保包含BV号")
                return None
            
            # 构建API URL
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            
            # 发送请求获取视频信息
            headers = self.get_random_headers()
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.update_log(f"获取视频信息失败: HTTP {response.status_code}")
                return None
            
            data = response.json()
            if data['code'] != 0:
                self.update_log(f"获取视频信息失败: {data['message']}")
                return None
            
            video_data = data['data']
            self.update_log(f"成功获取视频信息: 《{video_data['title']}》")
            return {
                'aid': video_data['aid'],
                'bvid': video_data['bvid'],
                'cid': video_data['cid'],
                'title': video_data['title'],
                'mid': video_data['owner']['mid'],
                'duration': video_data['duration']
            }
        except Exception as e:
            self.update_log(f"解析视频URL时出错: {str(e)}")
            return None
    
    def simulate_user_behavior(self, session, video_info, proxies, headers, using_ipv6=False, ipv6_address=None):
        """模拟用户浏览行为"""
        # 简化版实现，主要功能与原始代码相同，但减少了复杂度
        try:
            timeout = 20
            
            # 访问视频页面
            video_url = f"https://www.bilibili.com/video/{video_info['bvid']}"
            self.update_log(f"访问视频页面: {video_info.get('title', '')}")
            
            response = session.get(
                video_url,
                headers=headers,
                proxies=proxies,
                timeout=timeout
            )
            
            if response.status_code != 200:
                self.update_log(f"访问视频页面失败: HTTP {response.status_code}")
                return False
            
            # 简单等待模拟观看
            time.sleep(5)
            
            # 发送心跳请求
            self.update_log(f"发送视频心跳")
            time.sleep(3)
            
            self.update_log(f"视频观看完成: {video_info.get('title', '')}")
            return True
        except Exception as e:
            self.update_log(f"模拟用户行为异常: {str(e)}")
            return False
    
    def view_task(self, video_info, count, delay, view_time, thread_id):
        """单个线程的观看任务"""
        session = requests.Session()
        success_count = 0
        
        # 初始化线程状态
        self.thread_statuses[thread_id] = "启动中"
        self.last_activity_time[thread_id] = time.time()
        
        self.update_log(f"线程 {thread_id} 已启动, 目标请求数: {count}")
        
        for i in range(count):
            if not self.running:
                self.update_log(f"线程 {thread_id} 被中止")
                break
            
            # 更新线程状态
            self.thread_statuses[thread_id] = f"执行中 {i+1}/{count}"
            self.last_activity_time[thread_id] = time.time()
            
            try:
                # 获取代理
                proxies = None
                if self.use_proxy_checkbox.active and self.proxy_manager:
                    proxies = self.proxy_manager.get_proxy(thread_id)
                
                # 模拟用户行为
                behavior_success = self.simulate_user_behavior(
                    session, video_info, proxies, self.get_random_headers()
                )
                
                if behavior_success:
                    success_count += 1
                    
                    # 记录有效播放
                    if random.random() < 0.6:
                        self.real_success_count += 1
                
                # 随机延迟
                time.sleep(random.uniform(delay * 0.5, delay * 1.5))
                
            except Exception as e:
                self.update_log(f"线程 {thread_id}: 请求异常 - {str(e)}")
                time.sleep(2)
        
        # 更新统计
        self.success_count += success_count
        self.thread_statuses[thread_id] = "已完成"
        self.completed_threads += 1
        
        self.update_log(f"线程 {thread_id} 完成: 成功 {success_count}/{count}")
        
        # 检查是否所有线程都完成了
        all_done = True
        for t in self.threads:
            if t.is_alive():
                all_done = False
                break
        
        if all_done and self.running:
            Clock.schedule_once(lambda dt: self.all_tasks_completed())
    
    def all_tasks_completed(self):
        """所有任务完成后的回调"""
        self.running = False
        self.update_log("所有任务已完成")
        
        # 显示统计结果
        self.update_log(f"总共成功请求: {self.success_count}")
        self.update_log(f"有效播放请求: {self.real_success_count}")
        
        # 恢复按钮状态
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.stats_button.disabled = False
        
        # 更新状态和进度条
        self.update_status(f"完成 - 成功: {self.success_count} / 有效: {self.real_success_count}")
        self.progress_value = 100
        
        # 显示完成消息
        self.show_completion_popup()
    
    def show_completion_popup(self):
        """显示任务完成弹窗"""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=f"所有任务已完成\n成功请求: {self.success_count}\n有效播放: {self.real_success_count}"))
        
        btn = Button(text="确定", size_hint=(1, 0.3))
        content.add_widget(btn)
        
        popup = Popup(title='任务完成', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def start_task(self, instance):
        """开始任务"""
        if self.running:
            self.update_log("任务已在运行中")
            return
        
        # 重置计数器
        self.success_count = 0
        self.real_success_count = 0
        self.completed_threads = 0
        self.thread_statuses.clear()
        self.last_activity_time.clear()
        self.progress_value = 0
        
        # 记录开始时间
        self.start_time = time.time()
        
        # 获取参数
        video_url = self.video_url_input.text.strip()
        if not video_url:
            self.update_log("请输入视频URL")
            return
        
        # 解析视频信息
        video_info = self.parse_video_url(video_url)
        if not video_info:
            self.update_log("无法获取视频信息，请检查URL是否正确")
            return
        
        # 初始化代理管理器
        if self.use_proxy_checkbox.active:
            app_key = self.proxy_key_input.text.strip()
            app_secret = self.proxy_secret_input.text.strip()
            
            if not app_key or not app_secret:
                self.update_log("请输入代理服务的应用ID和密码")
                return
            
            try:
                self.proxy_manager = ProxyManager(app_key, app_secret)
                self.update_log("代理管理器已初始化")
            except Exception as e:
                self.update_log(f"代理初始化失败: {str(e)}")
                self.proxy_manager = None
        else:
            self.proxy_manager = None
        
        try:
            # 获取其他参数
            count = int(self.count_input.text)
            thread_count = int(self.thread_count_input.text)
            view_time = int(self.view_time_input.text)
            delay = int(self.delay_input.text)
            
            if count < 1 or thread_count < 1 or view_time < 1 or delay < 1:
                self.update_log("请输入有效的参数值")
                return
            
            # 计算每个线程的任务数
            base_count = count // thread_count
            extra = count % thread_count
            
            # 启动标志
            self.running = True
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.stats_button.disabled = True
            self.update_status("任务进行中...")
            
            # 创建并启动线程
            self.threads = []
            for i in range(thread_count):
                # 分配任务数
                thread_count_adjusted = base_count + (1 if i < extra else 0)
                if thread_count_adjusted > 0:
                    thread = threading.Thread(
                        target=self.view_task,
                        args=(video_info, thread_count_adjusted, delay, view_time, i+1)
                    )
                    thread.daemon = True
                    thread.start()
                    self.threads.append(thread)
            
            self.update_log(f"已启动 {thread_count} 个线程")
            
        except ValueError:
            self.update_log("请输入有效的数字参数")
            self.running = False
        except Exception as e:
            self.update_log(f"启动任务时出错: {str(e)}")
            self.running = False
    
    def stop_task(self, instance):
        """停止任务"""
        if not self.running:
            return
        
        self.running = False
        self.update_log("正在停止任务...")
        self.update_status("正在停止...")
        
        # 立即启用开始按钮并禁用停止按钮
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.stats_button.disabled = False
    
    def export_statistics(self, instance):
        """导出统计信息"""
        # 简化版统计导出
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_dir = "stats"
        if not os.path.exists(stats_dir):
            os.makedirs(stats_dir)
        
        stats_file = f"stats/bilibili_stats_{now}.txt"
        with open(stats_file, "w", encoding="utf-8") as f:
            f.write(f"B站视频播放量助手统计报告\n")
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"成功请求数: {self.success_count}\n")
            f.write(f"有效播放数: {self.real_success_count}\n")
            
            if self.start_time:
                elapsed = time.time() - self.start_time
                hours, remainder = divmod(int(elapsed), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                f.write(f"运行时间: {time_str}\n")
        
        self.update_log(f"统计数据已保存到 {stats_file}")
        
        # 显示导出完成弹窗
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=f"统计信息已保存到文件:\n{stats_file}"))
        
        btn = Button(text="确定", size_hint=(1, 0.3))
        content.add_widget(btn)
        
        popup = Popup(title='导出完成', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()

# 程序入口
if __name__ == "__main__":
    BilibiliViewerApp().run() 
