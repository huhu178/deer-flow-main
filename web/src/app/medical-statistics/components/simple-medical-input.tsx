// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { FileText, Mic, Send, Upload, X, Settings, Server } from "lucide-react";
import React, { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Textarea } from "~/components/ui/textarea";
import { cn } from "~/lib/utils";

// 语音识别类型声明
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: (event: SpeechRecognitionEvent) => void;
  onstart: () => void;
  onend: () => void;
  onerror: (event: SpeechRecognitionErrorEvent) => void;
}

interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

declare const SpeechRecognition: {
  prototype: SpeechRecognition;
  new (): SpeechRecognition;
};

/**
 * 简化的医学统计分析输入框组件
 * @param className 自定义样式类名
 * @param responding 是否正在响应
 * @param onSend 发送消息的回调函数
 */
export function SimpleMedicalInput({
  className,
  responding,
  onSend,
}: {
  className?: string;
  responding?: boolean;
  onSend: (message: string) => void;
}) {
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState("点击开始语音输入");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [useBrowserASR, setUseBrowserASR] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // --- Backend URL Configuration Logic ---
  const [backendUrl, setBackendUrl] = useState("");
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    const savedUrl = localStorage.getItem("backendUrl");
    if (savedUrl) {
      setBackendUrl(savedUrl);
    } else {
      setBackendUrl("http://localhost:8000");
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem("backendUrl", backendUrl);
    alert(`后端地址已保存: ${backendUrl}`);
    setShowSettings(false);
  };
  // --- End of Logic ---

  const handleSendMessage = useCallback(() => {
    if (message.trim() && !responding) {
      let finalMessage = message.trim();
      if (uploadedFiles.length > 0) {
        const fileList = uploadedFiles
          .map((file) => `📎 ${file.name} (${(file.size / 1024).toFixed(1)}KB)`)
          .join("\n");
        finalMessage = `${finalMessage}\n\n上传的文件:\n${fileList}`;
      }
      onSend?.(finalMessage);
      setMessage("");
      setUploadedFiles([]);
    }
  }, [message, responding, uploadedFiles, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const initBrowserASR = useCallback(() => {
    if (typeof window === "undefined") return false;

    const SpeechRecognitionClass =
      window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!SpeechRecognitionClass) {
      setVoiceError("浏览器不支持语音识别");
      return false;
    }

    const recognition = new SpeechRecognitionClass();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "zh-CN";

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result?.isFinal && result[0]) {
          finalTranscript += result[0].transcript;
        }
      }
      if (finalTranscript) {
        setMessage((prev) => prev + finalTranscript);
        setVoiceStatus(`识别完成: ${finalTranscript.substring(0, 15)}...`);
      }
    };

    recognition.onstart = () => {
      setIsRecording(true);
      setVoiceStatus("正在听取语音...");
      setVoiceError(null);
    };

    recognition.onend = () => {
      setIsRecording(false);
      setVoiceStatus("点击开始语音输入");
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      setIsRecording(false);
      let errorMessage = "语音识别出错";
      switch (event.error) {
        case "no-speech":
          errorMessage = "没有检测到语音";
          break;
        case "audio-capture":
          errorMessage = "无法访问麦克风";
          break;
        case "not-allowed":
          errorMessage = "麦克风权限被拒绝";
          break;
        case "network":
          errorMessage = "网络错误";
          break;
        default:
          errorMessage = `语音识别错误: ${event.error}`;
      }
      setVoiceStatus(errorMessage);
      setVoiceError(errorMessage);
      setTimeout(() => {
        setVoiceStatus("点击开始语音输入");
        setVoiceError(null);
      }, 3000);
    };

    recognitionRef.current = recognition;
    return true;
  }, []);

  const initFunASR = useCallback(async () => {
    try {
      setVoiceStatus("正在初始化语音识别...");
      mediaStreamRef.current = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const WEBSOCKET_URL = "ws://localhost:8001/ws/asr";
      wsRef.current = new WebSocket(WEBSOCKET_URL);

      wsRef.current.onopen = () => {
        setVoiceStatus("语音识别就绪");
        const startFrame = {
          chunk_size: 2048,
          chunk_interval: 10,
          wav_name: "medical_input.wav",
          is_speaking: true,
          chunk_num: 0,
        };
        wsRef.current?.send(JSON.stringify(startFrame));
      };

      wsRef.current.onmessage = (event: MessageEvent<string>) => {
        try {
          const result = JSON.parse(event.data) as {
            text?: string;
            nbest?: { text: string }[];
          };
          let text = "";
          if (result.text) {
            text = result.text;
          } else if (result.nbest?.length) {
            text = result.nbest[0]?.text ?? "";
          }

          if (text.trim()) {
            setMessage((prev) => prev + text);
            setVoiceStatus(`识别完成: ${text.substring(0, 15)}...`);
          }
        } catch (e) {
          console.error("解析FunASR结果失败:", e);
        }
      };

      wsRef.current.onerror = () => {
        setVoiceStatus("语音识别连接失败，尝试使用浏览器语音识别");
        setVoiceError("FunASR服务不可用");
        setUseBrowserASR(true);
        void initBrowserASR();
      };

      wsRef.current.onclose = () => {
        if (!useBrowserASR) {
          setVoiceStatus("连接已断开，尝试使用浏览器语音识别");
          setUseBrowserASR(true);
          void initBrowserASR();
        }
      };

      const context = new AudioContext();
      audioContextRef.current = context;
      const source = context.createMediaStreamSource(mediaStreamRef.current);
      const processor = context.createScriptProcessor(2048, 1, 1);

      processor.onaudioprocess = (e: AudioProcessingEvent) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          wsRef.current.send(inputData.buffer);
        }
      };

      source.connect(processor);
      processor.connect(context.destination);
      return true;
    } catch (err) {
      console.error("FunASR初始化失败:", err);
      setVoiceStatus("FunASR初始化失败，请检查服务是否可用");
      setVoiceError("FunASR初始化失败");
      setUseBrowserASR(true);
      return initBrowserASR();
    }
  }, [initBrowserASR, useBrowserASR]);

  const handleVoiceClick = useCallback(async () => {
    if (!isRecording) {
      setVoiceError(null);
      try {
        if (useBrowserASR || !("mediaDevices" in navigator)) {
          if (initBrowserASR()) {
            recognitionRef.current?.start();
          }
        } else {
          const initialized = await initFunASR();
          if (initialized) {
            setIsRecording(true);
            setVoiceStatus("正在录音... 点击停止");
          }
        }
      } catch (error) {
        console.error("Failed to start voice recording:", error);
        setVoiceStatus("开始录音失败");
        setVoiceError("无法启动录音功能");
      }
    } else {
      if (useBrowserASR) {
        recognitionRef.current?.stop();
      } else {
        mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          const endFrame = { is_speaking: false };
          wsRef.current.send(JSON.stringify(endFrame));
        }
        wsRef.current?.close();
      }
      setIsRecording(false);
      setVoiceStatus("点击开始语音输入");
    }
  }, [isRecording, useBrowserASR, initBrowserASR, initFunASR]);

  useEffect(() => {
    // 默认使用浏览器ASR
    initBrowserASR();
    setUseBrowserASR(true);
  }, [initBrowserASR]);

  useEffect(() => {
    return () => {
      wsRef.current?.close();
      mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
      void audioContextRef.current?.close();
      recognitionRef.current?.stop();
    };
  }, []);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    if (files.length > 0) {
      setIsProcessingFile(true);
      setUploadedFiles((prev) => [...prev, ...files]);
      setTimeout(() => {
        setIsProcessingFile(false);
      }, 1000);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className={cn("relative w-full", className)}>
      {/* File Uploads Display */}
      {uploadedFiles.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2">
          {uploadedFiles.map((file, index) => (
            <div key={index} className="flex items-center bg-blue-100 text-blue-800 px-2 py-1 rounded-lg text-sm">
              <FileText className="w-3 h-3 mr-1" />
              <span className="max-w-32 truncate">{file.name}</span>
              <Button variant="ghost" size="sm" className="h-4 w-4 p-0 ml-1 hover:bg-blue-200" onClick={() => removeFile(index)} title={`删除文件 ${file.name}`}>
                <X className="w-2 h-2" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Main Textarea and Action Buttons */}
      <div className="relative flex items-center">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="请描述您的研究需求或数据分析要求..."
          className="w-full resize-none rounded-lg border bg-white p-3 pr-24 text-base text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={1}
          disabled={responding}
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-1">
          <Button variant="ghost" size="icon" className={cn("h-8 w-8", isRecording ? "text-red-500" : "text-gray-500")} title={voiceStatus} onClick={handleVoiceClick} disabled={responding}>
            <Mic className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-500" title="上传文件" onClick={() => fileInputRef.current?.click()} disabled={responding}>
            <Upload className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Bottom row with Settings and Send button */}
      <div className="mt-2 flex items-center justify-end gap-2">
        <div className="relative">
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setShowSettings(!showSettings)} title="配置后端地址">
            <Settings className="h-5 w-5 text-gray-500" />
          </Button>
          {showSettings && (
            <div className="absolute bottom-full right-0 mb-2 w-80 rounded-md border bg-background p-4 shadow-lg z-10">
              <h4 className="font-medium text-base">配置后端服务地址</h4>
              <p className="mt-1 text-sm text-muted-foreground">请输入您暴露的本地后端 URL。</p>
              <div className="mt-4 flex items-center gap-2">
                <Server className="h-4 w-4 text-muted-foreground" />
                <Input type="url" placeholder="https://...ngrok-free.app" value={backendUrl} onChange={(e) => setBackendUrl(e.target.value)} className="h-9 text-sm"/>
              </div>
              <Button className="mt-4 w-full h-9 text-sm" onClick={handleSave}>保存</Button>
            </div>
          )}
        </div>
        <Button onClick={handleSendMessage} disabled={responding || !message.trim()} className="h-9">
          <Send className="h-4 w-4" />
        </Button>
      </div>

      {/* Hidden file input */}
      <form><input ref={fileInputRef} type="file" multiple onChange={handleFileUpload} className="hidden" /></form>
    </div>
  );
}