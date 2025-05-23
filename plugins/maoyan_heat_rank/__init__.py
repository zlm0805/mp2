from moviepilot.core.plugin import PluginBase
import traceback

class MaoyanHeatRank(PluginBase):
    plugin_info = {
        "name": "猫眼热度榜排行",
        "description": "获取猫眼热度榜数据并发送通知。",
        "version": "0.1",
        "author": "zlm0805",
        "url": "https://github.com/zlm0805/MoviePilot-Plugins/",
        "icon": "1.png"  # 添加图标路径
    }
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
                            "default": "10003779"
                        },
                        "key": {
                            "type": "string",
                            "title": "API密钥",
                            "description": "请替换为你的密钥。",
                            "default": "b37d7cb7e9d70760576c2c16c0f6302e"
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

# 全局变量
plugin = None
def init_plugin():
    """初始化插件"""
    global plugin
    try:
        plugin = MaoyanHeatRank()  # 实例化插件
        plugin.register_config_page(
            title="猫眼热度榜排行插件",
            description="获取猫眼热度榜数据并发送通知。",
            schema=plugin.config_schema
        )
        from moviepilot.core.scheduler import Scheduler
        plugin.scheduler = Scheduler()
        plugin.scheduler.add_job(plugin.run, "interval", hours=1, name="猫眼热度榜排行")
    except Exception as e:
        print(f"插件初始化失败: {e}")
        print(traceback.format_exc())

def destroy_plugin():
    """销毁插件"""
    global plugin
    if plugin:
        try:
            plugin.scheduler.remove_job("猫眼热度榜排行")
        except Exception as e:
            print(f"移除任务失败: {e}")
            print(traceback.format_exc())
        plugin = None
