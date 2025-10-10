"""
Региональные очереди для обработки запросов
"""
from typing import Dict, List
from .storage import Region

class RegionalQueue:
    """Очередь запросов для региона"""
    
    def __init__(self, region: Region, queue_url: str):
        self.region = region
        self.queue_url = queue_url
        self._queue: List[Dict] = []
    
    async def enqueue(self, request: Dict):
        """Добавление запроса в очередь"""
        request["region"] = self.region.value
        self._queue.append(request)
    
    async def dequeue(self) -> Dict:
        """Извлечение запроса из очереди"""
        if self._queue:
            return self._queue.pop(0)
        return None
    
    def size(self) -> int:
        """Размер очереди"""
        return len(self._queue)

class RegionalQueueManager:
    """Менеджер региональных очередей"""
    
    def __init__(self, storage_manager):
        self.queues = {
            region: RegionalQueue(region, config.queue_url)
            for region, config in storage_manager.storages.items()
        }
    
    async def route_to_queue(self, request: Dict, region: Region):
        """Маршрутизация запроса в региональную очередь"""
        queue = self.queues.get(region)
        if queue:
            await queue.enqueue(request)
        else:
            raise ValueError(f"No queue for region: {region}")
