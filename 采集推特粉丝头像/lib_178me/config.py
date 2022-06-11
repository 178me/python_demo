""" 配置文件模块
"""
import os
import configparser

class Config():
    """ 配置文件模块 """

    def __init__(self,config_name="mainwindow"):
        self.config = configparser.ConfigParser()
        if not os.path.exists("./config"):
            os.mkdir("./config")
        self.config_path = os.path.join("./","config",f"{config_name}.ini")
        if not os.path.exists(self.config_path):
            with open(self.config_path,"w",encoding="utf-8") as f:
                f.write("")
        self.config.read(self.config_path, encoding="utf-8")

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)

    def get(self, section=None, key=None):
        if key:
            if not self.config.has_option(section, key):
                return None
            return self.config.get(section, key)
        if section:
            if not self.config.has_section(section):
                return []
            return self.config.items(section)
        return self.config.sections()

    def remove(self, section, key=None):
        if not self.config.has_section(section):
            return None
        if key:
            return self.config.remove_option(section, key)
        return self.config.remove_section(section)

    def write(self):
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            self.config.write(config_file)

