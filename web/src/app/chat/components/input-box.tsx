// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { AnimatePresence, motion } from "framer-motion";
import { ArrowUp, X, Mic } from "lucide-react";
import {
  type KeyboardEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

// 导入 ASRClient
import ASRClient from "../../../lib/asrClient"; // <--- 确认路径正确

import { Detective } from "~/components/deer-flow/icons/detective";
import { Tooltip } from "~/components/deer-flow/tooltip";
import { Button } from "~/components/ui/button";
import type { Option } from "~/core/messages";
import {
  setEnableBackgroundInvestigation,
  useSettingsStore,
} from "~/core/store";
import { cn } from "~/lib/utils";

export function InputBox({
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

  // --- 语音识别相关状态 ---
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState('准备就绪 (语音)'); // 添加初始状态
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const asrClientRef = useRef<ASRClient | null>(null);
  const accumulatedTextRef = useRef<string>('');
  const PROXY_WEBSOCKET_URL = 'ws://localhost:8001/ws/asr'; // 确保代理服务在此端口运行
  // --- 结束语音识别相关状态 ---

  useEffect(() => {
    if (feedback) {
      setMessage(""); // 清空文本输入框，因为我们选择了 feedback
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

  // --- 语音识别结果处理 ---
  const handleRecognitionResult = useCallback((event: Event) => {
    const customEvent = event as CustomEvent<string>;
    try {
      const data = JSON.parse(customEvent.detail);
      let recognizedText = '';
      if (data.text) {
        recognizedText = data.text;
      } else if (data.nbest && data.nbest.length > 0) {
        recognizedText = data.nbest[0].text;
      }

      if (recognizedText) {
        accumulatedTextRef.current += recognizedText;
        // 更新 message state，将识别的文本追加到输入框
        // 如果希望替换，则 setMessage(accumulatedTextRef.current)
        setMessage(prevMessage => prevMessage + recognizedText); 
        setVoiceStatus('识别到: ' + recognizedText.substring(0, 20) + '...');
      }
    } catch (e) {
      console.error('InputBox: Error parsing recognition result', e);
      setVoiceError('解析识别结果失败');
    }
  }, []); // 依赖项中移除了 setMessage，因为它会导致 Effect 重复执行
  // --- 结束语音识别结果处理 ---

  // --- 初始化和清理 ASRClient ---
  useEffect(() => {
    if (!ASRClient) {
        setVoiceError('ASRClient 模块未加载');
        console.error("ASRClient class is not available. Make sure asrClient.js is correctly loaded and ASRClient is exported as default.");
        return;
    }

    console.log(`InputBox: Initializing ASRClient with URL: ${PROXY_WEBSOCKET_URL}`);
    const client = new ASRClient(PROXY_WEBSOCKET_URL);
    asrClientRef.current = client;

    const initializeASR = async () => {
      try {
        setVoiceStatus('正在初始化音频设备...');
        const initialized = await client.init();
        if (!initialized) {
          setVoiceError('无法访问麦克风，请检查权限设置。');
          setVoiceStatus('初始化失败');
          return;
        }
        client.connect();
        setVoiceStatus('准备就绪 (语音)');
        window.addEventListener('recognition-result', handleRecognitionResult);
      } catch (e: any) {
        console.error('InputBox: ASR Initialization error', e);
        setVoiceError(`ASR初始化失败: ${e.message}`);
        setVoiceStatus('初始化失败');
      }
    };

    initializeASR();

    return () => { // Cleanup
      console.log('InputBox: Cleaning up ASRClient...');
      window.removeEventListener('recognition-result', handleRecognitionResult);
      if (asrClientRef.current) {
        asrClientRef.current.disconnect();
      }
      asrClientRef.current = null;
    };
  }, [PROXY_WEBSOCKET_URL, handleRecognitionResult]);
  // --- 结束初始化和清理 ASRClient ---

  const handleSendMessage = useCallback(() => {
    console.log("InputBox: handleSendMessage CALLED. Message:", message, "Responding:", responding);
    if (responding) {
      console.log("InputBox: Currently responding, calling onCancel.");
      onCancel?.();
    } else {
      if (message.trim() === "") {
        console.log("InputBox: Message is empty, not sending.");
        return;
      }
      if (onSend) {
        console.log("InputBox: Calling onSend prop with message:", message);
        onSend(message, {
          interruptFeedback: feedback?.option.value,
        });
        setMessage("");
        onRemoveFeedback?.();
        accumulatedTextRef.current = "";
      } else {
        console.error("InputBox: onSend prop is undefined or not a function!");
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

  // --- 语音按钮点击处理 ---
  const handleVoiceButtonClick = () => {
    if (!asrClientRef.current) {
      setVoiceError('ASR客户端未初始化');
      return;
    }
    const client = asrClientRef.current;

    if (!isRecording) {
      setVoiceError(null);
      accumulatedTextRef.current = ""; 
      // 如果希望开始语音时清空文本框，可以取消下一行注释
      // setMessage(""); 
      setIsRecording(true);
      setVoiceStatus('正在录音...');
      client.startRecording();
    } else {
      setIsRecording(false);
      setVoiceStatus('处理中...');
      client.stopRecording();
      // 语音识别结果通过 handleRecognitionResult 持续更新 message state
      // 用户点击停止后，可以认为累积在 message 中的就是最终结果
      // 无需在此处特别处理 accumulatedTextRef，因为它已通过 setMessage 更新了输入框
      // 您可以根据需要决定是否在停止时立即发送消息，或者让用户手动点发送按钮
    }
  };
  // --- 结束语音按钮点击处理 ---

  return (
    <div className={cn("bg-card relative rounded-[24px] border", className)}>
      <div className="w-full">
        <AnimatePresence>
          {feedback && (
            <motion.div
              ref={feedbackRef}
              className="bg-background border-brand absolute top-0 left-0 mt-3 ml-2 flex items-center justify-center gap-1 rounded-2xl border px-2 py-0.5"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              transition={{ duration: 0.2, ease: "easeInOut" }}
            >
              <div className="text-brand flex h-full w-full items-center justify-center text-sm opacity-90">
                {feedback.option.text}
              </div>
              <X
                className="cursor-pointer opacity-60"
                size={16}
                onClick={onRemoveFeedback}
              />
            </motion.div>
          )}
        </AnimatePresence>
        <textarea
          ref={textareaRef}
          className={cn(
            "m-0 w-full resize-none border-none px-4 py-3 text-2xl",
            size === "large" ? "min-h-32" : "min-h-4",
            // 如果希望在录音时textarea变暗或禁用，可以在这里添加条件样式
            isRecording && "opacity-70" 
          )}
          style={{ textIndent: feedback ? `${indent}px` : 0 }}
          placeholder={
            isRecording 
            ? "正在聆听..." 
            : feedback
              ? `Describe how you ${feedback.option.text.toLocaleLowerCase()}?`
              : "我能为您做些什么？"
          }
          value={message}
          onCompositionStart={() => setImeStatus("active")}
          onCompositionEnd={() => setImeStatus("inactive")}
          onKeyDown={handleKeyDown}
          onChange={(event) => {
            setMessage(event.target.value);
          }}
          readOnly={isRecording} // 录音时禁止手动输入 (可选)
        />
      </div>
      <div className="flex items-center px-4 py-2">
        <div className="flex grow">
          <Tooltip
            className="max-w-60"
            title={
              <div>
                <h3 className="mb-2 font-bold">
                  调研模式: {backgroundInvestigation ? "开启" : "关闭"}
                </h3>
                <p>
                  启用后，AigenMed 会在规划前执行快速搜索。这对于与当前事件和新闻相关的研究很有用。
                </p>
              </div>
            }
          >
            <Button
              className={cn(
                "rounded-2xl",
                backgroundInvestigation && "!border-brand !text-brand",
              )}
              variant="outline"
              size="lg"
              onClick={() =>
                setEnableBackgroundInvestigation(!backgroundInvestigation)
              }
            >
              <Detective /> 调研模式
            </Button>
          </Tooltip>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <Tooltip title={isRecording ? "停止录音" : "语音输入"}>
            <Button
              variant="outline"
              size="icon"
              className={cn(
                  "h-10 w-10 rounded-full",
                  isRecording && "bg-red-500 hover:bg-red-600 text-white" // 录音时改变样式
              )}
              onClick={handleVoiceButtonClick} // <--- 修改onClick处理器
              disabled={!!voiceError && !isRecording} // 如果初始化失败则禁用 (除非已在录音)
            >
              <Mic size={20} />
            </Button>
          </Tooltip>
          <Tooltip title={responding ? "停止" : "发送"}>
            <Button
              variant="outline"
              size="icon"
              className={cn("h-10 w-10 rounded-full")}
              onClick={() => {
                console.log("SEND BUTTON CLICKED!"); // <--- 临时添加的日志
                handleSendMessage();
              }} // <--- 修改 onClick 处理器
            >
              {responding ? (
                <div className="flex h-10 w-10 items-center justify-center">
                  <div className="bg-foreground h-4 w-4 rounded-sm opacity-70" />
                </div>
              ) : (
                <ArrowUp />
              )}
            </Button>
          </Tooltip>
        </div>
      </div>
      {/* 显示语音状态和错误 */}
      {(voiceStatus !== '准备就绪 (语音)' || voiceError) && (
        <div className="px-4 pb-2 text-xs text-gray-500">
          {voiceError ? <span style={{color: 'red'}}>{voiceError}</span> : voiceStatus}
        </div>
      )}
    </div>
  );
}
