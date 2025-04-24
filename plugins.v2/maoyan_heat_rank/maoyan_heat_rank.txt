import requests
from moviepilot.core.plugin import PluginBase
from moviepilot.utils.log import logger
from moviepilot.notification.notify import send_message

class MaoyanHeatRank(PluginBase):
    def __init__(self):
        super().__init__()
        self.config_schema = {
            "type": "object",
            "properties": {
                "api": {
                    "type": "object",
                    "title": "API配置",
                    "description": "请访问https://www.apihz.cn/获取ID和密钥。",
                    "properties": {
                        "url1": {
                            "type": "string",
                            "title": "API地址1",
                            "default": "https://cn.apihz.cn/api/bang/maoyan2.php"
                        },
                        "url2": {
                            "type": "string",
                            "title": "API地址2",
                            "default": "https://cn.apihz.cn/api/bang/maoyan3.php"
                        },
                        "id": {
                            "type": "string",
                            "title": "API ID",
                            "description": "请替换为你的ID。",
                            "default": "11234"
                        },
                        "key": {
                            "type": "string",
                            "title": "API密钥",
                            "description": "请替换为你的密钥。",
                            "default": "b12345678912376c2c16c0f6302e"
                        }
                    },
                    "required": ["url1", "url2", "id", "key"]
                },
                "notification": {
                    "type": "object",
                    "title": "通知配置",
                    "properties": {
                        "title": {
                            "type": "string",
                            "title": "通知标题",
                            "default": "猫眼热度榜排行"
                        },
                        "enabled": {
                            "type": "boolean",
                            "title": "启用通知",
                            "default": True
                        }
                    },
                    "required": ["title", "enabled"]
                }
            }
        }
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        config = {}
        try:
            api_config = {
                "url1": self.get_config("api.url1"),
                "url2": self.get_config("api.url2"),
                "id": self.get_config("api.id"),
                "key": self.get_config("api.key")
            }
            notification_config = {
                "title": self.get_config("notification.title"),
                "enabled": self.get_config("notification.enabled")
            }
            config = {
                "api": api_config,
                "notification": notification_config
            }
        except Exception as e:
            logger.error(f"加载配置时出错: {e}")
        return config

    def fetch_data(self, url):
        """从API获取数据"""
        try:
            params = {"id": self.config["api"]["id"], "key": self.config["api"]["key"]}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"API返回数据: {data}")
            return data.get("data", []) if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f"获取数据时出错: {e}")
            return []

    def extract_data(self, data):
        """提取所需字段"""
        if not isinstance(data, list):
            logger.error(f"返回的数据不是数组: {data}")
            return []
        return [
            {
                "name": item.get("name", "未知名称"),
                "releaseInfo": item.get("releaseInfo", "未知信息"),
                "currHeat": float(item.get("currHeat", 0)),
                "platformDesc": item.get("platformDesc", "未知平台")
            }
            for item in data
        ]

    def sort_and_limit(self, data, limit=10):
        """排序并取前N条数据"""
        logger.info(f"排序前的数据: {data}")
        sorted_data = sorted(data, key=lambda x: x["currHeat"], reverse=True)[:limit]
        logger.info(f"排序后的数据: {sorted_data}")
        return sorted_data

    def send_notification(self, sorted_data):
        """发送通知"""
        if not self.config["notification"]["enabled"]:
            logger.info("通知功能已禁用")
            return
        message = "\n".join(
            f"{i + 1}. {item['name']}、{item['releaseInfo']}、{item['currHeat']:.2f}、{item['platformDesc']}"
            for i, item in enumerate(sorted_data)
        )
        title = self.config["notification"]["title"]
        send_message(title=title, text=message)
        logger.info("通知已成功发送")

    def run(self):
        """主函数"""
        logger.info("开始执行猫眼热度榜插件...")
        # 获取数据
        api_url1 = self.config["api"]["url1"]
        api_url2 = self.config["api"]["url2"]
        data1 = self.fetch_data(api_url1)
        data2 = self.fetch_data(api_url2)
        # 提取数据
        extracted_data1 = self.extract_data(data1)
        extracted_data2 = self.extract_data(data2)
        # 合并数据并去重
        combined_data = list({item["name"]: item for item in extracted_data1 + extracted_data2}.values())
        # 排序并取前10名
        sorted_data = self.sort_and_limit(combined_data, limit=10)
        # 发送通知
        self.send_notification(sorted_data)
        logger.info("猫眼热度榜插件执行完成")