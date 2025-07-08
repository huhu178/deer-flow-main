// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { AnimatePresence, motion } from "framer-motion";
import { ArrowUp, X, Mic, Upload, Send } from "lucide-react";
import {
  type KeyboardEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { Detective } from "~/components/deer-flow/icons/detective";
import { Tooltip } from "~/components/deer-flow/tooltip";
import { Button } from "~/components/ui/button";
import { Textarea } from "~/components/ui/textarea";
import type { Option } from "~/core/messages";
import {
  setEnableBackgroundInvestigation,
  useSettingsStore,
} from "~/core/store";
import { cn } from "~/lib/utils";

// 语音识别类型定义 - 暂时移除以避免构建错误
/*
interface CustomSpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: (event: CustomSpeechRecognitionEvent) => void;
  onstart: () => void;
  onend: () => void;
  onerror: (event: CustomSpeechRecognitionErrorEvent) => void;
}

interface CustomSpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: CustomSpeechRecognitionResultList;
}

interface CustomSpeechRecognitionErrorEvent extends Event {
  error: string;
}

interface CustomSpeechRecognitionResultList {
  length: number;
  [index: number]: CustomSpeechRecognitionResult;
}

interface CustomSpeechRecognitionResult {
  isFinal: boolean;
  [index: number]: CustomSpeechRecognitionAlternative;
}

interface CustomSpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

declare global {
  interface Window {
    SpeechRecognition: new() => CustomSpeechRecognition;
    webkitSpeechRecognition: new() => CustomSpeechRecognition;
  }
}
*/

/**
 * 医学统计分析输入框组件 - 匹配原始界面样式
 * @param className 自定义样式类名
 * @param size 大小（大号或正常）
 * @param responding 是否正在响应
 * @param feedback 反馈选项
 * @param onSend 发送消息的回调函数
 * @param onCancel 取消的回调函数
 * @param onRemoveFeedback 移除反馈的回调函数
 */
export function MedicalInputBox({
  className,
  size,
  responding,
  feedback,
  onSend,
  onCancel,
  onRemoveFeedback,
}: {
  className?: string;
  size?: "large" | "normal";
  responding?: boolean;
  feedback?: { option: Option } | null;
  onSend?: (message: string, options?: { interruptFeedback?: string }) => void;
  onCancel?: () => void;
  onRemoveFeedback?: () => void;
}) {
  const [message, setMessage] = useState("");
  const [imeStatus, setImeStatus] = useState<"active" | "inactive">("inactive");
  const [indent, setIndent] = useState(0);
  const backgroundInvestigation = useSettingsStore(
    (state) => state.general.enableBackgroundInvestigation,
  );
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const feedbackRef = useRef<HTMLDivElement>(null);

  // --- 语音识别相关状态 (浏览器内置API) - 暂时禁用 ---
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState('语音功能已禁用');
  const [voiceError, setVoiceError] = useState<string | null>('语音功能已禁用');
  // const recognitionRef = useRef<SpeechRecognition | null>(null);
  // --- 结束语音识别相关状态 ---

  useEffect(() => {
    if (feedback) {
      setMessage("");
      setTimeout(() => {
        if (feedbackRef.current) {
          setIndent(feedbackRef.current.offsetWidth);
        }
      }, 200);
    }
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  }, [feedback]);

  // --- 初始化浏览器语音识别 ---
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // 检查浏览器是否支持语音识别
      const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (!SpeechRecognitionClass) {
        setVoiceError('您的浏览器不支持语音识别功能');
        setVoiceStatus('语音识别不可用');
        return;
      }

      const recognition = new SpeechRecognitionClass();
      
      // 配置语音识别
      recognition.continuous = false; // 不连续识别
      recognition.interimResults = true; // 显示临时结果
      recognition.lang = 'zh-CN'; // 设置为中文

      // 处理识别结果
      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result && result[0]) {
            const transcript = result[0].transcript;
            if (result.isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }
        }

        // 更新消息内容
        if (finalTranscript) {
          setMessage(prev => prev + finalTranscript);
          setVoiceStatus(`识别完成: ${finalTranscript.substring(0, 20)}...`);
        } else if (interimTranscript) {
          setVoiceStatus(`正在识别: ${interimTranscript.substring(0, 20)}...`);
        }
      };

      // 处理识别开始
      recognition.onstart = () => {
        setIsRecording(true);
        setVoiceStatus('正在听取语音...');
        setVoiceError(null);
        console.log('语音识别已开始');
      };

      // 处理识别结束
      recognition.onend = () => {
        setIsRecording(false);
        setVoiceStatus('点击开始语音输入');
        console.log('语音识别已结束');
      };

      // 处理识别错误
      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        setIsRecording(false);
        
        let errorMessage = '';
        switch (event.error) {
          case 'no-speech':
            errorMessage = '没有检测到语音，请重试';
            break;
          case 'audio-capture':
            errorMessage = '无法访问麦克风，请检查权限';
            break;
          case 'not-allowed':
            errorMessage = '麦克风权限被拒绝';
            break;
          case 'network':
            errorMessage = '网络连接问题，语音识别服务暂时不可用';
            break;
          case 'service-not-allowed':
            errorMessage = '语音识别服务不可用';
            break;
          default:
            errorMessage = `语音识别遇到问题: ${event.error}`;
        }
        
        setVoiceStatus(errorMessage);
        setVoiceError(errorMessage);
        
        console.error('语音识别错误:', event.error);
        
        // 5秒后重置状态
        setTimeout(() => {
          setVoiceStatus('点击开始语音输入');
          setVoiceError(null);
        }, 5000);
      };

      // recognitionRef.current = recognition;
    }

    return () => {
      // if (recognitionRef.current) {
      //   recognitionRef.current.stop();
      //   recognitionRef.current = null;
      // }
    };
  }, []);
  // --- 结束初始化浏览器语音识别 ---

  const handleSendMessage = useCallback(() => {
    console.log("MedicalInputBox: handleSendMessage CALLED. Message:", message, "Responding:", responding);
    if (responding) {
      console.log("MedicalInputBox: Currently responding, calling onCancel.");
      onCancel?.();
    } else {
      if (message.trim() === "") {
        console.log("MedicalInputBox: Message is empty, not sending.");
        return;
      }
      if (onSend) {
        console.log("MedicalInputBox: Calling onSend prop with message:", message);
        onSend(message, {
          interruptFeedback: feedback?.option.value,
        });
        setMessage("");
        onRemoveFeedback?.();
      } else {
        console.error("MedicalInputBox: onSend prop is undefined or not a function!");
      }
    }
  }, [responding, onCancel, message, onSend, feedback, onRemoveFeedback]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      if (responding) {
        return;
      }
      if (
        event.key === "Enter" &&
        !event.shiftKey &&
        !event.metaKey &&
        !event.ctrlKey &&
        imeStatus === "inactive"
      ) {
        event.preventDefault();
        handleSendMessage();
      }
    },
    [responding, imeStatus, handleSendMessage],
  );

  // --- 语音按钮点击处理 (使用浏览器API) ---
  const handleVoiceButtonClick = useCallback(() => {
    // if (!recognitionRef.current) {
    //   setVoiceError('语音识别功能未初始化');
    //   return;
    // }

    // if (!isRecording) {
    //   try {
    //     // 开始语音识别
    //     recognitionRef.current.start();
    //   } catch (error) {
    //     console.error('启动语音识别失败:', error);
    //     setVoiceError('启动语音识别失败');
    //   }
    // } else {
    //   try {
    //     // 停止语音识别
    //     recognitionRef.current.stop();
    //   } catch (error) {
    //     console.error('停止语音识别失败:', error);
    //     setVoiceError('停止语音识别失败');
    //   }
    // }
  }, []);
  // --- 结束语音按钮点击处理 ---

  const handleSendButtonClick = useCallback(() => {
    handleSendMessage();
  }, [handleSendMessage]);

  return (
    <div className="flex items-center space-x-2">
      <div
        className={cn(
          "flex-1 relative",
          className,
        )}
      >
        <AnimatePresence>
          {feedback && (
            <motion.div
              ref={feedbackRef}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              className="flex items-center gap-1 whitespace-nowrap"
            >
              <div className="text-muted-foreground rounded-full border px-2 py-1 text-xs">
                {feedback.option.value}
              </div>
              <Button
                size="sm"
                variant="ghost"
                className="h-5 w-5 rounded-full p-0"
                onClick={onRemoveFeedback}
              >
                <X size={12} />
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
        <Tooltip title={voiceError || voiceStatus}>
          <Button
            variant={isRecording ? "default" : "outline"}
            size="icon"
            className={cn(
              "h-10 w-10 rounded-full",
              isRecording && "animate-pulse bg-red-500 hover:bg-red-600 text-white",
              voiceError && "bg-red-100 text-red-600 hover:bg-red-200",
              !voiceError && !isRecording && "hover:bg-blue-50 hover:border-blue-300"
            )}
            onClick={handleVoiceButtonClick}
            disabled={!!voiceError && !recognitionRef.current}
            title="语音输入"
          >
            <Mic className="h-4 w-4" />
          </Button>
        </Tooltip>
        <Textarea
          ref={textareaRef}
          placeholder={responding ? "AI正在分析中..." : "请描述您的研究需求或数据分析要求..."}
          className="w-full p-4 pr-10 border rounded-lg resize-none h-16 focus:outline-none focus:ring-2 focus:ring-blue-500 text-xl leading-relaxed scrollbar-hide text-gray-800 bg-white placeholder-gray-500 border-blue-200"
          style={{
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
            fontSize: '20px',
            lineHeight: '1.5',
            color: '#1f2937',
            backgroundColor: '#ffffff'
          }}
          rows={1}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => {
            setImeStatus("active");
          }}
          onCompositionEnd={() => {
            setImeStatus("inactive");
          }}
          disabled={responding}
        />
        <div className="absolute right-2 top-4">
          <Button 
            variant="ghost" 
            size="icon"
            className="text-gray-400 hover:text-gray-600 h-8 w-8"
            title="上传文件"
          >
            <Upload className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <Tooltip title="启用深度调研">
        <Button
          size={size === "large" ? "lg" : "sm"}
          variant={backgroundInvestigation ? "default" : "ghost"}
          className="h-8 w-8 shrink-0 rounded-full p-0"
          onClick={() => {
            setEnableBackgroundInvestigation(!backgroundInvestigation);
          }}
        >
          <Detective className={size === "large" ? "h-5 w-5" : "h-4 w-4"} />
        </Button>
      </Tooltip>
      <Button
        size={size === "large" ? "lg" : "sm"}
        variant={responding ? "destructive" : "default"}
        className="h-8 w-8 shrink-0 rounded-full p-0"
        onClick={handleSendButtonClick}
        disabled={!responding && message.trim() === ""}
      >
        {responding ? <X size={16} /> : <ArrowUp size={16} />}
      </Button>
    </div>
  );
} 