from dataclasses import dataclass, field


@dataclass
class Item:
    source: str            # telegram / youtube / vk / reddit / bluesky / web
    url: str
    title: str = ""
    text: str = ""
    author: str = ""
    published: str = ""    # ISO-дата, если известна
    audience: int = 0      # подписчики/просмотры, если известны (0 = неизвестно)
    extra: dict = field(default_factory=dict)
