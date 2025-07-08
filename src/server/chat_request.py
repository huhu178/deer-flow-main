# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class ContentItem(BaseModel):
    type: str = Field(..., description="The type of content (text, image, etc.)")
    text: Optional[str] = Field(None, description="The text content if type is 'text'")
    image_url: Optional[str] = Field(
        None, description="The image URL if type is 'image'"
    )


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="The role of the message sender (user or assistant)"
    )
    content: Union[str, List[ContentItem]] = Field(
        ...,
        description="The content of the message, either a string or a list of content items",
    )


class ChatRequest(BaseModel):
    messages: Optional[List[ChatMessage]] = Field(
        [], description="History of messages between the user and the assistant"
    )
    debug: Optional[bool] = Field(False, description="Whether to enable debug logging")
    thread_id: Optional[str] = Field(
        "__default__", description="A specific conversation identifier"
    )
    max_plan_iterations: Optional[int] = Field(
        1, description="The maximum number of plan iterations"
    )
    max_step_num: Optional[int] = Field(
        3, description="The maximum number of steps in a plan"
    )
    max_search_results: Optional[int] = Field(
        3, description="The maximum number of search results"
    )
    auto_accepted_plan: Optional[bool] = Field(
        False, description="Whether to automatically accept the plan"
    )
    interrupt_feedback: Optional[str] = Field(
        None, description="Interrupt feedback from the user on the plan"
    )
    mcp_settings: Optional[dict] = Field(
        None, description="MCP settings for the chat request"
    )
    enable_background_investigation: Optional[bool] = Field(
        True, description="Whether to get background investigation before plan"
    )
    enable_multi_model_report: Optional[bool] = Field(
        False, description="Whether to enable multi-model report generation with doubao, deepseek, and qianwen"
    )


class TTSRequest(BaseModel):
    text: str = Field(..., description="The text to convert to speech")
    voice_type: Optional[str] = Field(
        "BV700_V2_streaming", description="The voice type to use"
    )
    encoding: Optional[str] = Field("mp3", description="The audio encoding format")
    speed_ratio: Optional[float] = Field(1.0, description="Speech speed ratio")
    volume_ratio: Optional[float] = Field(1.0, description="Speech volume ratio")
    pitch_ratio: Optional[float] = Field(1.0, description="Speech pitch ratio")
    text_type: Optional[str] = Field("plain", description="Text type (plain or ssml)")
    with_frontend: Optional[int] = Field(
        1, description="Whether to use frontend processing"
    )
    frontend_type: Optional[str] = Field("unitTson", description="Frontend type")


class GeneratePodcastRequest(BaseModel):
    content: str = Field(..., description="The content of the podcast")


class GeneratePPTRequest(BaseModel):
    content: str = Field(..., description="The content of the ppt")


class GenerateProseRequest(BaseModel):
    prompt: str = Field(..., description="The content of the prose")
    option: str = Field(..., description="The option of the prose writer")
    command: Optional[str] = Field(
        "", description="The user custom command of the prose writer"
    )


class LargeReportRequest(ChatRequest):
    """
    大型报告生成请求，继承自ChatRequest并添加分批处理相关参数
    """
    report_name: Optional[str] = Field(
        None, description="报告名称，如果不提供将使用时间戳"
    )
    chunk_size: Optional[int] = Field(
        8000, description="每个分块的字符数限制，默认8000字符"
    )
    auto_save_sections: Optional[bool] = Field(
        True, description="是否自动保存章节到本地存储"
    )
    base_dir: Optional[str] = Field(
        "./outputs/reports", description="报告存储的基础目录"
    )


class ReportSectionRequest(BaseModel):
    """
    报告章节保存请求
    """
    report_name: str = Field(..., description="报告名称")
    section_title: str = Field(..., description="章节标题")
    section_content: str = Field(..., description="章节内容")
    section_number: Optional[int] = Field(None, description="章节编号")
    section_metadata: Optional[dict] = Field(None, description="章节元数据")
    base_dir: Optional[str] = Field(
        "./outputs/reports", description="报告存储的基础目录"
    )
    keep_chunks: Optional[bool] = Field(
        True, description="是否保留中间章节文件"
    )


class ReportMergeRequest(BaseModel):
    """
    报告合并请求
    """
    report_name: str = Field(..., description="报告名称")
    include_toc: Optional[bool] = Field(
        True, description="是否包含目录"
    )
    sort_by_number: Optional[bool] = Field(
        True, description="是否按章节编号排序"
    )
    base_dir: Optional[str] = Field(
        "./outputs/reports", description="报告存储的基础目录"
    )
    keep_chunks: Optional[bool] = Field(
        False, description="合并后是否保留中间章节文件"
    )
