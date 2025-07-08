import os
from dotenv import load_dotenv
import time

# --- 调试代码开始 ---
print(f"[app.py] Attempting to load .env file. Current PWD: {os.getcwd()}")
loaded = load_dotenv() 
print(f"[app.py] .env file loaded status: {loaded}")
retrieved_key = os.getenv('SERPAPI_API_KEY')
if retrieved_key:
    print(f"[app.py] SERPAPI_API_KEY successfully retrieved from environment: YES (length: {len(retrieved_key)})")
else:
    print("[app.py] SERPAPI_API_KEY NOT FOUND in environment after load_dotenv()")
# --- 调试代码结束 ---

# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import base64
import json
import logging
from typing import List, cast
from uuid import uuid4
import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessageChunk, ToolMessage, BaseMessage
from langgraph.types import Command

from src.graph.builder import build_graph_with_memory
from src.podcast.graph.builder import build_graph as build_podcast_graph
from src.ppt.graph.builder import build_graph as build_ppt_graph
from src.prose.graph.builder import build_graph as build_prose_graph
from src.server.chat_request import (
    ChatMessage,
    ChatRequest,
    GeneratePodcastRequest,
    GeneratePPTRequest,
    GenerateProseRequest,
    TTSRequest,
    LargeReportRequest,
    ReportSectionRequest,
    ReportMergeRequest,
)
from src.server.mcp_request import MCPServerMetadataRequest, MCPServerMetadataResponse
from src.server.mcp_utils import load_mcp_tools
from src.tools import VolcengineTTS
from src.server.batch_report_api import include_batch_report_routes
from src.server.batch_api import router as batch_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="DeerFlow API",
    description="API for Deer",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# 挂载 FunASR 静态文件目录
# 获取项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
funasr_static_path = os.path.join(project_root, "Funasr3", "static")

if os.path.exists(funasr_static_path):
    app.mount("/funasr/static", StaticFiles(directory=funasr_static_path), name="funasr_static")
    logger.info(f"📂 FunASR静态文件目录已挂载: {funasr_static_path}")
else:
    logger.warning(f"⚠️ FunASR静态文件目录不存在: {funasr_static_path}")
    # 尝试创建目录结构
    os.makedirs(funasr_static_path, exist_ok=True)
    os.makedirs(os.path.join(funasr_static_path, "js"), exist_ok=True)
    logger.info(f"📁 已创建FunASR静态文件目录: {funasr_static_path}")

# 本地语音识别配置（不依赖外部服务器）
USE_LOCAL_SPEECH_RECOGNITION = True

graph = build_graph_with_memory()

# 在app创建后添加分批报告路由
include_batch_report_routes(app)

# 添加分批输出管理器API路由
app.include_router(batch_router)

# 添加增强报告管理API路由
try:
    from src.server.enhanced_report_api import router as report_router
    app.include_router(report_router)
    logger.info("✅ 增强报告管理API已加载")
except ImportError as e:
    logger.warning(f"⚠️ 无法加载增强报告API: {e}")

# 添加健康检查API路由
try:
    from src.server.health_api import router as health_router
    app.include_router(health_router)
    logger.info("✅ 健康检查API已加载")
except ImportError as e:
    logger.warning(f"⚠️ 无法加载健康检查API: {e}")

# 添加Gemini深度研究API路由
try:
    from src.server.gemini_deep_research_api import router as gemini_research_router
    app.include_router(gemini_research_router)
    logger.info("✅ Gemini深度研究API已加载")
except ImportError as e:
    logger.warning(f"⚠️ 无法加载Gemini深度研究API: {e}")

# ==================== 本地语音识别集成 ====================

@app.get("/speech")
async def speech_interface():
    """
    返回本地语音识别测试页面
    """
    # 返回内联HTML页面，不依赖外部文件
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>本地语音识别</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        .mic-button {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4CAF50, #45a049);
            border: none;
            color: white;
            font-size: 40px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            margin: 20px auto;
            display: block;
        }
        .mic-button:hover {
            transform: scale(1.05);
        }
        .mic-button.recording {
            background: linear-gradient(135deg, #f44336, #d32f2f);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .status {
            text-align: center;
            margin: 20px 0;
            font-size: 1.2em;
            font-weight: 500;
        }
        .result {
            background: rgba(255,255,255,0.9);
            color: #333;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            min-height: 100px;
            font-size: 1.1em;
            line-height: 1.6;
        }
        .error {
            background: rgba(244, 67, 54, 0.9);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        .lang-select {
            padding: 10px;
            border-radius: 5px;
            border: none;
            margin: 0 10px;
            font-size: 1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align: center;">🎤 本地语音识别</h1>
        
        <div class="controls">
            <select id="languageSelect" class="lang-select">
                <option value="zh-CN">中文</option>
                <option value="en-US">English</option>
                <option value="ja-JP">日本語</option>
            </select>
        </div>
        
        <button id="micButton" class="mic-button">🎤</button>
        <div id="status" class="status">点击麦克风开始语音识别</div>
        <div id="error" class="error" style="display: none;"></div>
        
        <div class="result">
            <h3>识别结果：</h3>
            <div id="result">等待语音输入...</div>
        </div>
    </div>

    <script>
        class LocalSpeechRecognition {
            constructor() {
                this.recognition = null;
                this.isRecording = false;
                this.initRecognition();
            }

                         initRecognition() {
                 console.log('🔧 初始化语音识别...');
                 
                 // 检查浏览器支持
                 const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                 if (!SpeechRecognition) {
                     console.error('❌ 浏览器不支持语音识别');
                     const errorDiv = document.getElementById('error');
                     errorDiv.style.display = 'block';
                     errorDiv.textContent = '您的浏览器不支持语音识别。请使用最新版本的Chrome、Edge或Safari浏览器。';
                     return false;
                 }
                 
                 this.recognition = new SpeechRecognition();
                 console.log('✅ 语音识别对象创建成功');

                this.recognition.continuous = true;
                this.recognition.interimResults = true;
                this.recognition.lang = 'zh-CN';

                                 this.recognition.onstart = () => {
                     console.log('🎤 语音识别已启动');
                     this.isRecording = true;
                     this.updateUI();
                     
                     const statusDiv = document.getElementById('status');
                     statusDiv.textContent = '正在听取您的语音...';
                 };

                this.recognition.onresult = (event) => {
                    let finalTranscript = '';
                    let interimTranscript = '';

                    for (let i = event.resultIndex; i < event.results.length; ++i) {
                        if (event.results[i].isFinal) {
                            finalTranscript += event.results[i][0].transcript;
                        } else {
                            interimTranscript += event.results[i][0].transcript;
                        }
                    }

                    const resultDiv = document.getElementById('result');
                    if (finalTranscript) {
                        resultDiv.innerHTML += '<div><strong>最终结果：</strong>' + finalTranscript + '</div>';
                        
                        // 通过WebSocket发送到服务器
                        this.sendToServer(finalTranscript);
                    }
                    if (interimTranscript) {
                        resultDiv.innerHTML += '<div style="color: #666;"><em>临时结果：</em>' + interimTranscript + '</div>';
                    }
                };

                this.recognition.onerror = (event) => {
                    console.error('语音识别错误:', event.error);
                    const errorDiv = document.getElementById('error');
                    errorDiv.style.display = 'block';
                    errorDiv.textContent = '语音识别错误: ' + event.error;
                };

                this.recognition.onend = () => {
                    console.log('🛑 语音识别已结束');
                    this.isRecording = false;
                    this.updateUI();
                };

                return true;
            }

            setLanguage(lang) {
                if (this.recognition) {
                    this.recognition.lang = lang;
                }
            }

                         start() {
                 if (this.recognition && !this.isRecording) {
                     console.log('🚀 启动语音识别...');
                     try {
                         this.recognition.start();
                         console.log('✅ 语音识别启动成功');
                     } catch (error) {
                         console.error('❌ 启动语音识别失败:', error);
                         const errorDiv = document.getElementById('error');
                         errorDiv.style.display = 'block';
                         errorDiv.textContent = '启动语音识别失败: ' + error.message;
                     }
                 } else {
                     console.log('⚠️ 语音识别不可用或正在录音中');
                 }
             }

            stop() {
                if (this.recognition && this.isRecording) {
                    this.recognition.stop();
                }
            }

            updateUI() {
                const button = document.getElementById('micButton');
                const status = document.getElementById('status');
                
                if (this.isRecording) {
                    button.classList.add('recording');
                    button.textContent = '🛑';
                    status.textContent = '正在录音... 点击停止';
                } else {
                    button.classList.remove('recording');
                    button.textContent = '🎤';
                    status.textContent = '点击麦克风开始语音识别';
                }
            }

            sendToServer(text) {
                // 通过WebSocket发送识别结果到服务器
                fetch('/api/speech/result', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text,
                        timestamp: new Date().toISOString(),
                        language: this.recognition.lang
                    })
                }).then(response => response.json())
                  .then(data => console.log('服务器响应:', data))
                  .catch(error => console.error('发送到服务器失败:', error));
            }
        }

                 // 检查麦克风权限
         async function checkMicrophonePermission() {
             try {
                 const result = await navigator.permissions.query({ name: 'microphone' });
                 console.log('🎤 麦克风权限状态:', result.state);
                 
                 if (result.state === 'denied') {
                     const errorDiv = document.getElementById('error');
                     errorDiv.style.display = 'block';
                     errorDiv.textContent = '麦克风权限被拒绝。请在浏览器设置中允许麦克风访问权限。';
                     return false;
                 }
                 return true;
             } catch (error) {
                 console.log('📱 无法检查麦克风权限，可能是旧版浏览器');
                 return true; // 旧版浏览器可能不支持权限API
             }
         }

         // 初始化
         document.addEventListener('DOMContentLoaded', async () => {
             console.log('🚀 页面加载完成，开始初始化...');
             
             // 检查麦克风权限
             const hasPermission = await checkMicrophonePermission();
             if (!hasPermission) {
                 document.getElementById('micButton').disabled = true;
                 return;
             }
             
             const speechRecognition = new LocalSpeechRecognition();
             
             if (!speechRecognition.recognition) {
                 document.getElementById('error').style.display = 'block';
                 document.getElementById('error').textContent = '抱歉，您的浏览器不支持语音识别功能。请使用Chrome、Edge或Safari。';
                 document.getElementById('micButton').disabled = true;
                 return;
             }

                         // 麦克风按钮事件
             document.getElementById('micButton').addEventListener('click', () => {
                 console.log('🖱️ 麦克风按钮被点击');
                 console.log('📊 当前录音状态:', speechRecognition.isRecording);
                 
                 // 清除之前的错误信息
                 document.getElementById('error').style.display = 'none';
                 
                 if (speechRecognition.isRecording) {
                     console.log('🛑 停止录音');
                     speechRecognition.stop();
                 } else {
                     console.log('🎤 开始录音');
                     speechRecognition.start();
                 }
             });

            // 语言选择事件
            document.getElementById('languageSelect').addEventListener('change', (e) => {
                speechRecognition.setLanguage(e.target.value);
            });

            // 清除错误信息
            document.getElementById('micButton').addEventListener('click', () => {
                document.getElementById('error').style.display = 'none';
            });
        });
    </script>
</body>
</html>
    """
    return Response(content=html_content, media_type="text/html")

@app.post("/api/speech/result")
async def speech_result(request: Request):
    """
    接收浏览器语音识别结果
    """
    try:
        data = await request.json()
        text = data.get("text", "")
        timestamp = data.get("timestamp", "")
        language = data.get("language", "zh-CN")
        
        logger.info(f"🎤 收到语音识别结果: {text} (语言: {language})")
        
        # 这里可以添加后续处理逻辑
        # 比如保存到数据库、触发其他服务等
        
        return {
            "status": "success",
            "message": "语音识别结果已接收",
            "data": {
                "text": text,
                "timestamp": timestamp,
                "language": language,
                "length": len(text)
            }
        }
    except Exception as e:
        logger.error(f"❌ 处理语音识别结果时出错: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api/speech/status")
async def speech_status():
    """
    检查本地语音识别服务状态
    """
    return {
        "status": "online",
        "type": "local_browser_speech_recognition",
        "message": "本地语音识别服务正常",
        "supported_languages": [
            {"code": "zh-CN", "name": "中文"},
            {"code": "en-US", "name": "English"},
            {"code": "ja-JP", "name": "日本語"},
            {"code": "ko-KR", "name": "한국어"},
            {"code": "es-ES", "name": "Español"},
            {"code": "fr-FR", "name": "Français"},
            {"code": "de-DE", "name": "Deutsch"}
        ],
        "note": "依赖浏览器内置语音识别API，需要Chrome、Edge或Safari浏览器"
    }

# ==================== 原有的路由保持不变 ====================

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    thread_id = request.thread_id
    if thread_id == "__default__":
        thread_id = str(uuid4())
    return StreamingResponse(
        _astream_workflow_generator(
            request.model_dump()["messages"],
            thread_id,
            request.max_plan_iterations,
            request.max_step_num,
            request.max_search_results,
            request.auto_accepted_plan,
            request.interrupt_feedback,
            request.mcp_settings,
            request.enable_background_investigation,
            request.enable_multi_model_report,
        ),
        media_type="text/event-stream",
    )


async def _astream_workflow_generator(
    messages: List[ChatMessage],
    thread_id: str,
    max_plan_iterations: int,
    max_step_num: int,
    max_search_results: int,
    auto_accepted_plan: bool,
    interrupt_feedback: str,
    mcp_settings: dict,
    enable_background_investigation,
    enable_multi_model_report: bool,
):
    input_ = {
        "messages": messages,
        "plan_iterations": 0,
        "final_report": "",
        "current_plan": None,
        "observations": [],
        "auto_accepted_plan": auto_accepted_plan,
        "enable_background_investigation": enable_background_investigation,
        "enable_multi_model_report": enable_multi_model_report,
    }
    if not auto_accepted_plan and interrupt_feedback:
        if interrupt_feedback == "accepted":
            # 简单的接受反馈，不影响LangGraph流处理
            resume_msg = "[accepted] 完美！开始研究吧。"
        else:
            resume_msg = f"[{interrupt_feedback}]"
            # add the last message to the resume message  
            if messages:
                resume_msg += f" {messages[-1]['content']}"
        
        input_ = Command(resume=resume_msg)
    async for agent, _, event_data in graph.astream(
        input_,
        config={
            "thread_id": thread_id,
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num,
            "max_search_results": max_search_results,
            "mcp_settings": mcp_settings,
            "recursion_limit": 200,
        },
        stream_mode=["messages", "updates"],
        subgraphs=True,
    ):
        if isinstance(event_data, dict):
            if "__interrupt__" in event_data:
                yield _make_event("interrupt", {
                    "thread_id": thread_id,
                    "id": event_data["__interrupt__"][0].ns[0],
                    "role": "assistant",
                    "content": event_data["__interrupt__"][0].value,
                    "finish_reason": "interrupt",
                    "options": [
                        {"text": "Edit plan", "value": "edit_plan"},
                        {"text": "Start research", "value": "accepted"},
                    ],
                })
            continue
        message_chunk, message_metadata = cast(
            tuple[BaseMessage, dict[str, any]], event_data
        )
        event_stream_message: dict[str, any] = {
            "thread_id": thread_id,
            "agent": agent[0].split(":")[0],
            "id": message_chunk.id,
            "role": "assistant",
            "content": message_chunk.content,
        }
        if message_chunk.response_metadata.get("finish_reason"):
            event_stream_message["finish_reason"] = message_chunk.response_metadata.get(
                "finish_reason"
            )
        if isinstance(message_chunk, ToolMessage):
            # Tool Message - Return the result of the tool call
            event_stream_message["tool_call_id"] = message_chunk.tool_call_id
            yield _make_event("tool_call_result", event_stream_message)
        elif isinstance(message_chunk, AIMessageChunk):
            # AI Message - Raw message tokens
            if message_chunk.tool_calls:
                # AI Message - Tool Call
                event_stream_message["tool_calls"] = message_chunk.tool_calls
                event_stream_message["tool_call_chunks"] = (
                    message_chunk.tool_call_chunks
                )
                yield _make_event("tool_calls", event_stream_message)
            elif message_chunk.tool_call_chunks:
                # AI Message - Tool Call Chunks
                event_stream_message["tool_call_chunks"] = (
                    message_chunk.tool_call_chunks
                )
                yield _make_event("tool_call_chunks", event_stream_message)
            else:
                # AI Message - Raw message tokens
                yield _make_event("message_chunk", event_stream_message)


def _make_event(event_type: str, data: dict[str, any]):
    if data.get("content") == "":
        data.pop("content")
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using volcengine TTS API."""
    try:
        app_id = os.getenv("VOLCENGINE_TTS_APPID", "")
        if not app_id:
            raise HTTPException(
                status_code=400, detail="VOLCENGINE_TTS_APPID is not set"
            )
        access_token = os.getenv("VOLCENGINE_TTS_ACCESS_TOKEN", "")
        if not access_token:
            raise HTTPException(
                status_code=400, detail="VOLCENGINE_TTS_ACCESS_TOKEN is not set"
            )
        cluster = os.getenv("VOLCENGINE_TTS_CLUSTER", "volcano_tts")
        voice_type = os.getenv("VOLCENGINE_TTS_VOICE_TYPE", "BV700_V2_streaming")

        tts_client = VolcengineTTS(
            appid=app_id,
            access_token=access_token,
            cluster=cluster,
            voice_type=voice_type,
        )
        # Call the TTS API
        result = tts_client.text_to_speech(
            text=request.text[:1024],
            encoding=request.encoding,
            speed_ratio=request.speed_ratio,
            volume_ratio=request.volume_ratio,
            pitch_ratio=request.pitch_ratio,
            text_type=request.text_type,
            with_frontend=request.with_frontend,
            frontend_type=request.frontend_type,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=str(result["error"]))

        # Decode the base64 audio data
        audio_data = base64.b64decode(result["audio_data"])

        # Return the audio file
        return Response(
            content=audio_data,
            media_type=f"audio/{request.encoding}",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=tts_output.{request.encoding}"
                )
            },
        )
    except Exception as e:
        logger.exception(f"Error in TTS endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/podcast/generate")
async def generate_podcast(request: GeneratePodcastRequest):
    try:
        report_content = request.content
        print(report_content)
        workflow = build_podcast_graph()
        final_state = workflow.invoke({"input": report_content})
        audio_bytes = final_state["output"]
        return Response(content=audio_bytes, media_type="audio/mp3")
    except Exception as e:
        logger.exception(f"Error occurred during podcast generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ppt/generate")
async def generate_ppt(request: GeneratePPTRequest):
    try:
        report_content = request.content
        print(report_content)
        workflow = build_ppt_graph()
        final_state = workflow.invoke({"input": report_content})
        generated_file_path = final_state["generated_file_path"]
        with open(generated_file_path, "rb") as f:
            ppt_bytes = f.read()
        return Response(
            content=ppt_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    except Exception as e:
        logger.exception(f"Error occurred during ppt generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prose/generate")
async def generate_prose(request: GenerateProseRequest):
    try:
        logger.info(f"Generating prose for prompt: {request.prompt}")
        workflow = build_prose_graph()
        events = workflow.astream(
            {
                "content": request.prompt,
                "option": request.option,
                "command": request.command,
            },
            stream_mode="messages",
            subgraphs=True,
        )
        return StreamingResponse(
            (f"data: {event[0].content}\n\n" async for _, event in events),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.exception(f"Error occurred during prose generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp/server/metadata", response_model=MCPServerMetadataResponse)
async def mcp_server_metadata(request: MCPServerMetadataRequest):
    """Get information about an MCP server."""
    try:
        # Set default timeout with a longer value for this endpoint
        timeout = 300  # Default to 300 seconds for this endpoint

        # Use custom timeout from request if provided
        if request.timeout_seconds is not None:
            timeout = request.timeout_seconds

        # Load tools from the MCP server using the utility function
        tools = await load_mcp_tools(
            server_type=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            timeout_seconds=timeout,
        )

        # Create the response with tools
        response = MCPServerMetadataResponse(
            transport=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            tools=tools,
        )

        return response
    except Exception as e:
        if not isinstance(e, HTTPException):
            logger.exception(f"Error in MCP server metadata endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        raise


@app.post("/api/report/section/save")
async def save_report_section(request: ReportSectionRequest):
    """
    保存报告章节到本地存储
    
    @param {ReportSectionRequest} request - 包含章节信息的请求
    @returns {dict} 保存结果和章节路径
    """
    try:
        from src.utils.report_manager import ReportManager
        
        # 创建报告管理器实例
        report_manager = ReportManager(
            report_name=request.report_name,
            base_dir=request.base_dir or "./outputs/reports",
            keep_chunks=request.keep_chunks
        )
        
        # 保存章节
        section_path = report_manager.save_section(
            title=request.section_title,
            content=request.section_content,
            section_number=request.section_number,
            metadata=request.section_metadata
        )
        
        return {
            "success": True,
            "section_path": section_path,
            "section_number": request.section_number,
            "section_title": request.section_title,
            "message": f"章节 '{request.section_title}' 已成功保存"
        }
        
    except Exception as e:
        logger.error(f"保存报告章节时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存章节失败: {str(e)}")


@app.post("/api/report/merge")
async def merge_report_sections(request: ReportMergeRequest):
    """
    合并所有报告章节为完整报告
    
    @param {ReportMergeRequest} request - 合并请求参数
    @returns {dict} 合并结果和完整报告路径
    """
    try:
        from src.utils.report_manager import ReportManager
        
        # 创建报告管理器实例
        report_manager = ReportManager(
            report_name=request.report_name,
            base_dir=request.base_dir or "./outputs/reports",
            keep_chunks=request.keep_chunks
        )
        
        # 合并报告
        final_path = report_manager.merge_report(
            include_toc=request.include_toc,
            sort_by_number=request.sort_by_number
        )
        
        # 获取统计信息
        stats = report_manager.get_stats()
        
        return {
            "success": True,
            "final_report_path": final_path,
            "report_stats": stats,
            "message": f"报告已成功合并，共 {stats['total_sections']} 个章节"
        }
        
    except Exception as e:
        logger.error(f"合并报告时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"合并报告失败: {str(e)}")


@app.get("/api/report/download/{report_name}")
async def download_report(report_name: str, base_dir: str = "./outputs/reports"):
    """
    下载完整报告文件
    
    @param {string} report_name - 报告名称
    @param {string} base_dir - 报告存储目录
    @returns {Response} 文件下载响应
    """
    try:
        import os
        from fastapi.responses import FileResponse
        
        # 构建报告文件路径
        report_path = os.path.join(base_dir, report_name, f"{report_name}_complete.md")
        
        if not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail="报告文件不存在")
        
        return FileResponse(
            path=report_path,
            filename=f"{report_name}_complete.md",
            media_type="text/markdown"
        )
        
    except Exception as e:
        logger.error(f"下载报告时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")


@app.get("/api/report/list")
async def list_reports(base_dir: str = "./outputs/reports"):
    """
    列出所有可用的报告
    
    @param {string} base_dir - 报告存储目录
    @returns {dict} 报告列表和统计信息
    """
    try:
        import os
        from datetime import datetime
        
        reports = []
        
        if os.path.exists(base_dir):
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path):
                    # 检查是否有完整报告文件
                    complete_file = os.path.join(item_path, f"{item}_complete.md")
                    if os.path.exists(complete_file):
                        stat = os.stat(complete_file)
                        reports.append({
                            "name": item,
                            "path": complete_file,
                            "size": stat.st_size,
                            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
        
        return {
            "success": True,
            "reports": reports,
            "total_count": len(reports)
        }
        
    except Exception as e:
        logger.error(f"列出报告时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取报告列表失败: {str(e)}")


@app.post("/api/chat/stream/large")
async def chat_stream_large_report(request: LargeReportRequest):
    """
    处理大型报告生成的流式响应，支持分批输出
    
    @param {LargeReportRequest} request - 大型报告请求
    @returns {StreamingResponse} 分批流式响应
    """
    thread_id = request.thread_id
    if thread_id == "__default__":
        thread_id = str(uuid4())
    
    return StreamingResponse(
        _astream_large_report_generator(
            request.model_dump()["messages"],
            thread_id,
            request.max_plan_iterations,
            request.max_step_num,
            request.max_search_results,
            request.auto_accepted_plan,
            request.interrupt_feedback,
            request.mcp_settings,
            request.enable_background_investigation,
            request.enable_multi_model_report,
            request.report_name,
            request.chunk_size,
            request.auto_save_sections,
            request.base_dir,
        ),
        media_type="text/event-stream",
    )


async def _astream_large_report_generator(
    messages: List[ChatMessage],
    thread_id: str,
    max_plan_iterations: int,
    max_step_num: int,
    max_search_results: int,
    auto_accepted_plan: bool,
    interrupt_feedback: str,
    mcp_settings: dict,
    enable_background_investigation: bool,
    enable_multi_model_report: bool,
    report_name: str,
    chunk_size: int,
    auto_save_sections: bool,
    base_dir: str,
):
    """
    大型报告的流式生成器，支持分批输出和自动保存
    """
    from src.utils.report_manager import ReportManager
    
    # 初始化报告管理器
    report_manager = None
    if auto_save_sections:
        report_manager = ReportManager(
            report_name=report_name,
            base_dir=base_dir or "./outputs/reports",
            keep_chunks=True
        )
    
    current_section = ""
    section_count = 0
    accumulated_content = ""
    
    input_ = {
        "messages": messages,
        "plan_iterations": 0,
        "final_report": "",
        "current_plan": None,
        "observations": [],
        "auto_accepted_plan": auto_accepted_plan,
        "enable_background_investigation": enable_background_investigation,
        "enable_multi_model_report": enable_multi_model_report,
    }
    
    if not auto_accepted_plan and interrupt_feedback:
        if interrupt_feedback == "accepted":
            # 简单的接受反馈，不影响LangGraph流处理
            resume_msg = "[accepted] 完美！开始研究吧。"
        else:
            resume_msg = f"[{interrupt_feedback}]"
            # add the last message to the resume message  
            if messages:
                resume_msg += f" {messages[-1]['content']}"
        
        input_ = Command(resume=resume_msg)
    
    async for agent, _, event_data in graph.astream(
        input_,
        config={
            "thread_id": thread_id,
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num,
            "max_search_results": max_search_results,
            "mcp_settings": mcp_settings,
            "recursion_limit": 200,
        },
        stream_mode=["messages", "updates"],
        subgraphs=True,
    ):
        if isinstance(event_data, dict):
            if "__interrupt__" in event_data:
                yield _make_event(
                    "interrupt",
                    {
                        "thread_id": thread_id,
                        "id": event_data["__interrupt__"][0].ns[0],
                        "role": "assistant",
                        "content": event_data["__interrupt__"][0].value,
                        "finish_reason": "interrupt",
                        "options": [
                            {"text": "Edit plan", "value": "edit_plan"},
                            {"text": "Start research", "value": "accepted"},
                        ],
                    },
                )
            continue
            
        message_chunk, message_metadata = cast(
            tuple[BaseMessage, dict[str, any]], event_data
        )
        
        content = message_chunk.content
        accumulated_content += content
        
        # 检查是否需要分批输出
        if len(accumulated_content) >= chunk_size:
            # 尝试在合适的位置分割（如段落结束）
            split_pos = accumulated_content.rfind('\n\n')
            if split_pos == -1:
                split_pos = accumulated_content.rfind('\n')
            if split_pos == -1:
                split_pos = chunk_size
            
            chunk_content = accumulated_content[:split_pos]
            accumulated_content = accumulated_content[split_pos:]
            
            # 检测章节标题
            if chunk_content.strip().startswith('#'):
                section_count += 1
                section_title = chunk_content.split('\n')[0].strip('#').strip()
                
                # 保存上一个章节
                if current_section and report_manager:
                    try:
                        section_path = report_manager.save_section(
                            title=f"Section_{section_count-1}",
                            content=current_section,
                            section_number=section_count-1
                        )
                        yield _make_event("section_saved", {
                            "thread_id": thread_id,
                            "section_number": section_count-1,
                            "section_path": section_path,
                            "message": f"章节 {section_count-1} 已保存"
                        })
                    except Exception as e:
                        logger.error(f"保存章节时出错: {str(e)}")
                
                current_section = chunk_content
            else:
                current_section += chunk_content
            
            # 发送分块内容
            event_stream_message = {
                "thread_id": thread_id,
                "agent": agent[0].split(":")[0],
                "id": message_chunk.id,
                "role": "assistant",
                "content": chunk_content,
                "chunk_number": section_count,
                "is_chunk": True,
            }
            
            if message_chunk.response_metadata.get("finish_reason"):
                event_stream_message["finish_reason"] = message_chunk.response_metadata.get("finish_reason")
            
            yield _make_event("message_chunk", event_stream_message)
        
        # 处理其他类型的消息
        elif isinstance(message_chunk, ToolMessage):
            event_stream_message = {
                "thread_id": thread_id,
                "agent": agent[0].split(":")[0],
                "id": message_chunk.id,
                "role": "assistant",
                "content": content,
                "tool_call_id": message_chunk.tool_call_id,
            }
            yield _make_event("tool_call_result", event_stream_message)
        
        elif isinstance(message_chunk, AIMessageChunk):
            event_stream_message = {
                "thread_id": thread_id,
                "agent": agent[0].split(":")[0],
                "id": message_chunk.id,
                "role": "assistant",
                "content": content,
            }
            
            if message_chunk.response_metadata.get("finish_reason"):
                event_stream_message["finish_reason"] = message_chunk.response_metadata.get("finish_reason")
            
            if message_chunk.tool_calls:
                event_stream_message["tool_calls"] = message_chunk.tool_calls
                event_stream_message["tool_call_chunks"] = message_chunk.tool_call_chunks
                yield _make_event("tool_calls", event_stream_message)
            elif message_chunk.tool_call_chunks:
                event_stream_message["tool_call_chunks"] = message_chunk.tool_call_chunks
                yield _make_event("tool_call_chunks", event_stream_message)
            else:
                yield _make_event("message_chunk", event_stream_message)
    
    # 处理剩余内容和最后一个章节
    if accumulated_content.strip():
        current_section += accumulated_content
    
    if current_section and report_manager:
        try:
            section_path = report_manager.save_section(
                title=f"Section_{section_count}",
                content=current_section,
                section_number=section_count
            )
            yield _make_event("section_saved", {
                "thread_id": thread_id,
                "section_number": section_count,
                "section_path": section_path,
                "message": f"最后章节 {section_count} 已保存"
            })
            
            # 自动合并报告
            final_path = report_manager.merge_report(include_toc=True, sort_by_number=True)
            stats = report_manager.get_stats()
            
            yield _make_event("report_completed", {
                "thread_id": thread_id,
                "final_report_path": final_path,
                "report_stats": stats,
                "message": f"完整报告已生成，共 {stats['total_sections']} 个章节"
            })
            
        except Exception as e:
            logger.error(f"完成报告时出错: {str(e)}")


@app.post("/api/generate-complete-report")
async def generate_complete_report_endpoint(request: Request):
    """
    生成完整的8批次研究报告
    
    @param {dict} request - 包含报告名称和其他配置的请求
    @returns {dict} 生成结果和进度信息
    """
    try:
        # 解析请求数据
        data = await request.json()
        report_name = data.get("report_name", "DXA影像AI预测研究")
        
        # 导入完整报告生成器
        from src.utils.complete_report_generator import CompleteReportGenerator
        from src.models.factory import get_model_client
        
        # 创建生成器
        generator = CompleteReportGenerator(
            report_name=report_name,
            output_dir="./outputs/complete_reports"
        )
        
        # 获取模型客户端
        model_client = get_model_client("gemini")
        
        # 生成报告
        batch_results = []
        
        for batch_num in range(8):  # 8个批次
            try:
                # 获取当前批次的提示
                prompt = generator.get_next_batch_prompt()
                if not prompt:
                    break
                
                logger.info(f"正在生成第{batch_num + 1}/8批次...")
                
                # 调用模型生成内容
                response = model_client.chat([{"role": "user", "content": prompt}])
                content = response.strip()
                
                # 保存当前批次内容
                batch_result = generator.save_section(content)
                batch_results.append(batch_result)
                
                logger.info(f"✅ 第{batch_num + 1}批次完成: {batch_result['section_title']}")
                
                # 添加延时避免API限制
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"第{batch_num + 1}批次生成失败: {str(e)}")
                continue
        
        # 检查是否完成所有批次
        if generator.is_complete():
            # 生成最终完整报告
            final_result = generator.generate_final_report()
            
            return {
                "success": True,
                "message": "完整报告生成成功",
                "final_result": final_result,
                "batch_results": batch_results,
                "progress": 100
            }
        else:
            # 部分完成
            progress = generator.get_progress()
            return {
                "success": False,
                "message": "报告生成部分完成",
                "progress": progress['progress_percentage'],
                "batch_results": batch_results,
                "next_section": progress.get('next_section')
            }
            
    except Exception as e:
        logger.error(f"生成完整报告时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成完整报告失败: {str(e)}")
