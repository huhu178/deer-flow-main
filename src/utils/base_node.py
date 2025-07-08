"""
实现一个基础节点类，替代langgraph中的Node类
"""

import logging
from typing import Any, Dict, List, Optional, Type


class BaseNode:
    """
    自定义基础节点类，提供输入和输出的管理
    
    由于langgraph.graph.Node在当前版本中不可用，这个类提供了基本的节点功能
    """
    
    def __init__(self):
        """
        初始化基础节点
        """
        self._inputs = {}  # 存储输入定义
        self._outputs = {}  # 存储输出定义
        self._input_values = {}  # 存储输入值
        self._output_values = {}  # 存储输出值
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_input(self, name: str, type_: Type, default_value: Any = None):
        """
        添加输入定义
        
        @param {string} name - 输入名称
        @param {Type} type_ - 输入类型
        @param {Any} default_value - 默认值
        """
        self._inputs[name] = {
            "type": type_,
            "default": default_value
        }
        # 初始化输入值为默认值
        self._input_values[name] = default_value
    
    def add_output(self, name: str, type_: Type, default_value: Any = None):
        """
        添加输出定义
        
        @param {string} name - 输出名称
        @param {Type} type_ - 输出类型
        @param {Any} default_value - 默认值
        """
        self._outputs[name] = {
            "type": type_,
            "default": default_value
        }
        # 初始化输出值为默认值
        self._output_values[name] = default_value
    
    def set_input(self, name: str, value: Any):
        """
        设置输入值
        
        @param {string} name - 输入名称
        @param {Any} value - 输入值
        """
        if name not in self._inputs:
            self.logger.warning(f"设置未定义的输入: {name}")
            return
        
        # 简单类型检查
        expected_type = self._inputs[name]["type"]
        if value is not None and expected_type is not Any and not isinstance(value, expected_type):
            self.logger.warning(f"输入类型不匹配: {name}，期望 {expected_type}，实际 {type(value)}")
        
        self._input_values[name] = value
    
    def get_input(self, name: str) -> Any:
        """
        获取输入值
        
        @param {string} name - 输入名称
        @return {Any} 输入值
        """
        if name not in self._inputs:
            self.logger.warning(f"获取未定义的输入: {name}")
            return None
        
        return self._input_values.get(name, self._inputs[name]["default"])
    
    def set_output(self, name: str, value: Any):
        """
        设置输出值
        
        @param {string} name - 输出名称
        @param {Any} value - 输出值
        """
        if name not in self._outputs:
            self.logger.warning(f"设置未定义的输出: {name}")
            return
        
        # 简单类型检查
        expected_type = self._outputs[name]["type"]
        if value is not None and expected_type is not Any and not isinstance(value, expected_type):
            self.logger.warning(f"输出类型不匹配: {name}，期望 {expected_type}，实际 {type(value)}")
        
        self._output_values[name] = value
    
    def get_output(self, name: str) -> Any:
        """
        获取输出值
        
        @param {string} name - 输出名称
        @return {Any} 输出值
        """
        if name not in self._outputs:
            self.logger.warning(f"获取未定义的输出: {name}")
            return None
        
        return self._output_values.get(name, self._outputs[name]["default"])
    
    def process(self):
        """
        处理节点，由子类实现
        """
        raise NotImplementedError("子类必须实现process方法") 