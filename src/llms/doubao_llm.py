# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
豆包（字节跳动）多模态大语言模型实现
支持文本和图片输入，基于火山引擎API
"""

import json
import logging
import os
import requests
import time
from typing import Any, Dict, List, Optional, Union, Iterator
from langchain_core.language_models.llms import LLM
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun
from pydantic import Field, PrivateAttr

logger = logging.getLogger(__name__)

def get_doubao_api_key() -> str:
    """获取豆包API密钥"""
    return os.getenv("DOUBAO_API_KEY", "")

class DoubaoMultimodalLLM(BaseChatModel):
    """豆包多模态聊天模型实现"""
    
    headers: Dict[str, str] = Field(default_factory=dict, exclude=True)
    base_url: str
    model: str
    api_key: str = Field(default_factory=get_doubao_api_key, exclude=True)
    max_tokens: int = Field(default=32768)
    temperature: float = Field(default=0.7)
    timeout: int = Field(default=180)
    max_retries: int = Field(default=3)
    request_timeout: int = Field(default=180)
    streaming: bool = Field(default=False)
    
    # 多模态配置
    multimodal_enabled: bool = Field(default=True)
    max_image_size: str = Field(default="20MB")
    supported_formats: List[str] = Field(
        default_factory=lambda: ["jpeg", "jpg", "png", "gif", "webp"]
    )
    
    # 豆包特性
    thinking_mode: bool = Field(default=True)
    vision_analysis: bool = Field(default=True)
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        if not self.api_key:
            self.api_key = get_doubao_api_key()
        if not self.api_key:
            raise ValueError("API key is required for Doubao model")
        
        # 设置请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info(f"🤖 初始化豆包多模态模型: {self.model}")
        logger.info(f"   API端点: {self.base_url}")
        logger.info(f"   多模态支持: {self.multimodal_enabled}")
        logger.info(f"   思考模式: {self.thinking_mode}")

    @property
    def _llm_type(self) -> str:
        return "doubao_multimodal"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成聊天响应"""
        
        # 转换消息格式
        doubao_messages = self._convert_messages_to_doubao_format(messages)
        
        # 构建请求体
        request_data = {
            "model": self.model,
            "messages": doubao_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": self.streaming
        }
        
        # 添加停止词
        if stop:
            request_data["stop"] = stop
        
        # 执行API调用
        try:
            response_text = self._call_api(request_data)
            
            # 创建响应
            message = AIMessage(content=response_text)
            generation = ChatGeneration(message=message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"❌ 豆包API调用失败: {str(e)}")
            # 返回错误信息
            error_message = AIMessage(content=f"豆包模型调用失败: {str(e)}")
            generation = ChatGeneration(message=error_message)
            return ChatResult(generations=[generation])

    def _convert_messages_to_doubao_format(self, messages: List[BaseMessage]) -> List[Dict]:
        """将LangChain消息格式转换为豆包API格式"""
        doubao_messages = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                # 检查是否包含图片内容
                if self._has_image_content(message.content):
                    doubao_message = self._process_multimodal_message(message)
                else:
                    doubao_message = {
                        "role": "user",
                        "content": str(message.content)
                    }
            elif isinstance(message, AIMessage):
                doubao_message = {
                    "role": "assistant", 
                    "content": str(message.content)
                }
            else:
                # 其他类型消息转为用户消息
                doubao_message = {
                    "role": "user",
                    "content": str(message.content)
                }
            
            doubao_messages.append(doubao_message)
        
        return doubao_messages

    def _has_image_content(self, content: Any) -> bool:
        """检查内容是否包含图片"""
        if isinstance(content, list):
            return any(
                isinstance(item, dict) and item.get("type") == "image_url"
                for item in content
            )
        return False

    def _process_multimodal_message(self, message: HumanMessage) -> Dict:
        """处理包含图片的多模态消息"""
        if isinstance(message.content, list):
            # 直接使用已有的多模态格式
            content_parts = []
            for item in message.content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        content_parts.append({
                            "type": "text",
                            "text": item.get("text", "")
                        })
                    elif item.get("type") == "image_url":
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": item.get("image_url", {}).get("url", "")
                            }
                        })
            
            return {
                "role": "user",
                "content": content_parts
            }
        else:
            # 纯文本消息
            return {
                "role": "user",
                "content": str(message.content)
            }

    def _call_api(self, request_data: Dict) -> str:
        """调用豆包API"""
        url = f"{self.base_url}/chat/completions"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 豆包API调用 (尝试 {attempt + 1}/{self.max_retries})")
                
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=request_data,
                    timeout=self.request_timeout
                )
                
                if response.status_code == 200:
                    response_json = response.json()
                    
                    # 提取响应内容
                    if "choices" in response_json and len(response_json["choices"]) > 0:
                        content = response_json["choices"][0]["message"]["content"]
                        logger.info(f"✅ 豆包API调用成功，响应长度: {len(content)} 字符")
                        return content
                    else:
                        raise ValueError("API响应格式错误：缺少choices字段")
                        
                else:
                    error_msg = f"API调用失败，状态码: {response.status_code}"
                    if response.text:
                        error_msg += f"，错误信息: {response.text}"
                    raise ValueError(error_msg)
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ 豆包API调用超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise ValueError(f"API调用超时，已重试{self.max_retries}次")
                time.sleep(2 ** attempt)  # 指数退避
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"🌐 豆包API网络错误: {str(e)} (尝试 {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise ValueError(f"网络连接错误: {str(e)}")
                time.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"❌ 豆包API调用异常: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)

    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            test_message = [HumanMessage(content="你好，请简单回复")]
            result = self._generate(test_message)
            logger.info("✅ 豆包API连接测试成功")
            return True
        except Exception as e:
            logger.error(f"❌ 豆包API连接测试失败: {str(e)}")
            return False

    def test_multimodal(self, image_url: str, text: str = "图片主要讲了什么？") -> str:
        """测试多模态功能"""
        try:
            multimodal_message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            )
            
            result = self._generate([multimodal_message])
            response = result.generations[0].message.content
            logger.info(f"✅ 豆包多模态测试成功: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ 豆包多模态测试失败: {str(e)}")
            raise


# 兼容性别名
DoubaoLLM = DoubaoMultimodalLLM


if __name__ == "__main__":
    # 测试代码
    print("🤖 测试豆包多模态LLM...")
    
    # 从配置文件加载参数
    try:
        import yaml
        from pathlib import Path
        
        conf_file = Path(__file__).parent.parent.parent / "conf.yaml"
        with open(conf_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        doubao_config = config.get("DOUBAO_MODEL", {})
        
        if doubao_config.get("api_key"):
            llm = DoubaoMultimodalLLM(
                base_url=doubao_config.get("base_url", "https://ark.cn-beijing.volces.com/api/v3"),
                model=doubao_config.get("model"),
                api_key=doubao_config.get("api_key"),
                max_tokens=doubao_config.get("max_tokens", 32768),
                temperature=doubao_config.get("temperature", 0.7)
            )
            
            # 测试基础文本功能
            print("\n📝 测试文本对话...")
            if llm.test_connection():
                print("✅ 文本功能正常")
            
            # 测试多模态功能（如果有图片URL）
            test_image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
            print(f"\n🖼️ 测试多模态功能...")
            try:
                response = llm.test_multimodal(test_image_url)
                print(f"✅ 多模态功能正常")
                print(f"🤖 豆包回复: {response[:200]}...")
            except Exception as e:
                print(f"❌ 多模态测试失败: {e}")
        else:
            print("❌ 请在conf.yaml中配置豆包API密钥")
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}") 