"""
MiniMax自定义LLM实现
处理MiniMax API的特殊响应格式
"""

from typing import Any, Dict, List, Optional, Sequence, Union, Iterator
import requests
import json
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, AIMessageChunk
from langchain_core.outputs import ChatGeneration, ChatResult, LLMResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.runnables.config import RunnableConfig
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.tools import BaseTool
from langchain_core.runnables import Runnable


class MiniMaxChatModel(BaseChatModel):
    """
    MiniMax聊天模型的自定义实现
    专门处理MiniMax API的特殊响应格式
    """
    
    base_url: str = "https://api.minimaxi.com/v1"
    model: str = "MiniMax-M1"
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 120
    
    @property
    def _llm_type(self) -> str:
        return "minimax"
    
    def bind_tools(
        self,
        tools: Sequence[BaseTool],
        **kwargs: Any,
    ) -> Runnable[Any, Any]:
        """
        绑定工具到模型
        注意：MiniMax可能不支持原生工具调用，这里返回self以保持兼容性
        """
        print(f"⚠️ MiniMax模型工具绑定: {len(tools)}个工具")
        print("   注意: MiniMax可能不支持原生工具调用功能")
        
        # 为了兼容性，我们返回self
        # 在实际项目中，您可能需要实现工具调用的转换逻辑
        return self
    
    def with_structured_output(
        self,
        schema: Any,
        **kwargs: Any,
    ) -> Runnable[Any, Any]:
        """
        结构化输出支持
        """
        print(f"⚠️ MiniMax模型结构化输出支持有限")
        return self
    
    def _convert_messages_to_minimax_format(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """将LangChain消息格式转换为MiniMax API格式"""
        minimax_messages = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            elif isinstance(message, SystemMessage):
                role = "system"
            else:
                role = "user"  # 默认处理
            
            minimax_messages.append({
                "role": role,
                "content": message.content
            })
        
        return minimax_messages
    
    def _call_minimax_api(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """直接调用MiniMax API"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        print(f"🔧 MiniMax API调用:")
        print(f"   URL: {url}")
        print(f"   Model: {self.model}")
        print(f"   消息数量: {len(messages)}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            print(f"   HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   响应结构: {list(result.keys())}")
                
                # 检查标准OpenAI格式的choices
                if result.get('choices') and len(result.get('choices', [])) > 0:
                    print(f"   ✅ 标准格式响应")
                    return result
                
                # 检查MiniMax特有的base_resp格式
                base_resp = result.get('base_resp', {})
                if base_resp.get('status_code') == 0:  # 成功状态码
                    # 尝试从base_resp中提取内容
                    if 'output' in base_resp or 'reply' in base_resp:
                        print(f"   ✅ MiniMax格式响应，进行格式转换")
                        # 转换为标准格式
                        content = base_resp.get('output', base_resp.get('reply', ''))
                        return {
                            'choices': [{
                                'message': {
                                    'role': 'assistant',
                                    'content': content
                                },
                                'finish_reason': 'stop'
                            }],
                            'usage': result.get('usage', {}),
                            'model': self.model
                        }
                
                # 如果都没有，检查是否有错误信息
                if base_resp.get('status_code') and base_resp.get('status_code') != 0:
                    error_msg = base_resp.get('status_msg', '未知错误')
                    print(f"   ❌ API错误: {base_resp.get('status_code')} - {error_msg}")
                    raise Exception(f"MiniMax API错误: {error_msg}")
                
                # 如果响应格式完全不符合预期，尝试直接使用响应内容
                print(f"   ⚠️ 未知响应格式，尝试解析: {json.dumps(result, ensure_ascii=False)[:200]}...")
                
                # 尝试从其他可能的字段中提取内容
                for possible_key in ['text', 'content', 'response', 'answer', 'result']:
                    if possible_key in result:
                        content = result[possible_key]
                        if isinstance(content, str) and content.strip():
                            print(f"   ✅ 从{possible_key}字段提取内容")
                            return {
                                'choices': [{
                                    'message': {
                                        'role': 'assistant',
                                        'content': content
                                    },
                                    'finish_reason': 'stop'
                                }]
                            }
                
                raise Exception(f"无法解析MiniMax响应格式: {result}")
            
            else:
                error_text = response.text
                print(f"   ❌ HTTP错误: {error_text[:200]}...")
                raise Exception(f"MiniMax API HTTP错误 {response.status_code}: {error_text}")
                
        except requests.RequestException as e:
            print(f"   ❌ 请求异常: {e}")
            raise Exception(f"MiniMax API请求失败: {e}")
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成聊天响应"""
        
        # 转换消息格式
        minimax_messages = self._convert_messages_to_minimax_format(messages)
        
        # 调用API
        response_data = self._call_minimax_api(minimax_messages)
        
        # 解析响应
        choices = response_data.get('choices', [])
        if not choices:
            raise ValueError("MiniMax API响应中没有choices字段")
        
        generations = []
        for choice in choices:
            message_data = choice.get('message', {})
            content = message_data.get('content', '')
            
            ai_message = AIMessage(content=content)
            generation = ChatGeneration(message=ai_message)
            generations.append(generation)
        
        # 返回结果
        return ChatResult(generations=generations)

    def stream(
        self,
        input: Union[List[BaseMessage], LanguageModelInput],
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Iterator[AIMessageChunk]:
        """
        实现流式输出，但由于MiniMax不支持真正的流式，
        这里模拟流式输出以提高用户体验
        """
        print("🔧 MiniMax不支持流式输出，使用模拟流式模式")
        
        # 首先获取完整响应
        result = self.invoke(input, config=config, stop=stop, **kwargs)
        
        # 将响应内容分块模拟流式输出
        content = result.content
        chunk_size = 50  # 每块字符数
        
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i + chunk_size]
            yield AIMessageChunk(content=chunk_content)
            
            # 添加小延迟模拟流式效果
            import time
            time.sleep(0.05)
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回标识参数"""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        } 