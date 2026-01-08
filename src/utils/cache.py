from enum import StrEnum
from cachetools import LRUCache, TTLCache, LFUCache
from typing import Any, Optional

class CacheType(StrEnum):
    """缓存类型"""
    HOT = "hot"
    SESSION = "session"
    FOREVER = "forever"

    KEY_RESUME_GRAPH = "graph:" # 恢复/补全 graph 的关键标识
    KEY_EXTRACTED_PARAMS = "query:" # 提取的查询参数缓存
    KEY_FIELD_SCHEMAS = "fields:" # 字段 schema 缓存
    KEY_PAYLOAD_DATA = "payload:" # 数据缓存


class GlobalCache:
    """全局缓存管理器，封装多种缓存策略和操作方法"""

    def __init__(self):
        # 1. LRU 缓存（最近使用淘汰策略）
        # 适用于：热点数据缓存，优先保留最近访问的条目
        self.hot_cache = LRUCache(maxsize=100)  # 最大缓存 100 条

        # 2. TTL 缓存（超时自动淘汰策略）
        # 适用于：临时数据（如会话、短期有效的Token）
        self.session_cache = TTLCache(maxsize=5000, ttl=36000)  # 10小时后自动失效，最多 5000 条

        # 3. LFU 缓存（最不经常使用淘汰策略）
        # 适用于：长期运行的服务，优先保留访问频率高的条目
        self.forever_cache = LFUCache(maxsize=2000)  # 最大缓存 2000 条

    def set(self, key: Any, value: Any, cache_type: str = "hot") -> None:
        """设置缓存数据
        :param key: 缓存键
        :param value: 缓存值
        :param cache_type: 缓存类型，可选值为 "hot"（默认）、"session"、"forever"
        """
        if cache_type == "session":
            self.session_cache[key] = value
        elif cache_type == "forever":
            self.forever_cache[key] = value
        else:
            self.hot_cache[key] = value

    def get(self, key: Any, cache_type: str = "hot") -> Optional[Any]:
        """获取缓存数据
        :param key: 缓存键
        :param cache_type: 缓存类型，可选值为 "hot"（默认）、"session"、"forever"
        :return: 缓存值，如果键不存在则返回 None
        """
        if cache_type == "session":
            return self.session_cache.get(key, None)
        elif cache_type == "forever":
            return self.forever_cache.get(key, None)
        else:
            return self.hot_cache.get(key, None)

    # 清空所有缓存
    def clear_all(self) -> None:
        self.hot_cache.clear()
        self.session_cache.clear()
        self.forever_cache.clear()


# 全局唯一缓存实例（单例）
global_cache = GlobalCache()