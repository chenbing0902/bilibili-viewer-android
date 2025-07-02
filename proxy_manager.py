import requests
import random
import time
import json

class ProxyManager:
    """代理管理器类，负责获取和管理代理"""
    
    def __init__(self, app_key, app_secret):
        """
        初始化代理管理器
        app_key: 代理服务的应用ID
        app_secret: 代理服务的应用密码
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.used_proxies = set()  # 已使用代理集合
        self.bad_proxies = set()   # 失效代理集合
        self.proxy_cache = []      # 代理缓存
        
        # 测试连接，确认API密钥正确
        self.test_connection()
    
    def test_connection(self):
        """测试代理API连接"""
        # 在实际应用中，这里应该调用代理API进行测试
        # 但为了移动端应用简洁，我们这里简化处理
        return True
    
    def get_proxy(self, thread_id=0):
        """
        获取一个代理地址
        thread_id: 线程ID，用于日志记录
        """
        # 如果缓存中有代理，直接使用
        if self.proxy_cache:
            proxy = self.proxy_cache.pop(0)
            self.used_proxies.add(proxy['http'])
            return proxy
        
        # 实际项目中，这里应该调用代理API获取代理
        # 在这个示例中，我们生成一个模拟代理
        proxy_addr = f"http://proxy{random.randint(1000, 9999)}.example.com:8080"
        proxy = {"http": proxy_addr, "https": proxy_addr}
        
        self.used_proxies.add(proxy_addr)
        return proxy
    
    def report_bad_proxy(self, proxy):
        """
        报告无效代理
        proxy: 无效的代理地址
        """
        if isinstance(proxy, dict):
            addr = proxy.get('http') or proxy.get('https')
            if addr:
                self.bad_proxies.add(addr)
        elif isinstance(proxy, str):
            self.bad_proxies.add(proxy)
    
    def pre_fetch_proxies(self, count=10):
        """
        预先获取多个代理
        count: 预取代理数量
        """
        self.proxy_cache = []
        for _ in range(count):
            proxy_addr = f"http://proxy{random.randint(1000, 9999)}.example.com:8080"
            self.proxy_cache.append({"http": proxy_addr, "https": proxy_addr})
        
        return len(self.proxy_cache) > 0

# 示例使用方法
if __name__ == "__main__":
    # 创建代理管理器
    proxy_manager = ProxyManager("test_key", "test_secret")
    
    # 获取一个代理
    proxy = proxy_manager.get_proxy()
    print(f"获取代理: {proxy}")
    
    # 预取多个代理
    proxy_manager.pre_fetch_proxies(5)
    print(f"预取代理数: {len(proxy_manager.proxy_cache)}") 