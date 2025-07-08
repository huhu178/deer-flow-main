// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { AnimatePresence, motion } from "framer-motion";
import { ArrowUp, X, Upload, Send } from "lucide-react";
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

// All SpeechRecognition related types are temporarily disabled to fix build errors.
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

  // --- All speech recognition logic has been temporarily disabled. ---

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

  const handleSendMessage = useCallback(() => {
    if (responding) {
      onCancel?.();
    } else {
      if (message.trim() === "") {
        return;
      }
      onSend?.(message, {
        interruptFeedback: feedback?.option.value,
      });
      setMessage("");
      onRemoveFeedback?.();
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

  return (
    <motion.div
      className={cn(
        "bg-background/80 relative w-full rounded-2xl border p-4 shadow-lg backdrop-blur-md",
        className,
      )}
      initial={{ y: 10, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <div className="flex w-full items-start gap-4">
        <Textarea
          ref={textareaRef}
          className="bg-background/0 text-md min-h-[60px] flex-1 resize-none border-none p-0 shadow-none focus-visible:ring-0"
          placeholder="例如：请对这份DXA影像进行骨密度分析，并评估未来骨折风险..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => setImeStatus("active")}
          onCompositionEnd={() => setImeStatus("inactive")}
        />
        <Button
          variant="default"
          size="icon"
          className="h-10 w-10 shrink-0 rounded-full"
          onClick={handleSendMessage}
          disabled={!message.trim() || responding}
        >
          {responding ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-t-transparent" />
          ) : (
            <ArrowUp size={20} />
          )}
        </Button>
      </div>

      <AnimatePresence>
        {feedback && (
          <motion.div
            ref={feedbackRef}
            className="bg-brand/10 border-brand/20 text-brand mt-3 flex items-center justify-center gap-1 rounded-lg border px-2 py-1 text-sm"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <div>{feedback.option.text}</div>
            <X
              className="cursor-pointer opacity-60"
              size={16}
              onClick={onRemoveFeedback}
            />
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mt-4 flex items-center justify-between border-t pt-3">
        <div className="flex items-center gap-2">
          {/* Voice recognition button is temporarily disabled */}
          {/* <Tooltip title="语音输入">
            <Button variant="ghost" size="icon" className="text-muted-foreground">
              <Mic size={18} />
            </Button>
          </Tooltip> */}
          <Tooltip title="上传文件（即将推出）">
            <Button variant="ghost" size="icon" className="text-muted-foreground" disabled>
              <Upload size={18} />
            </Button>
          </Tooltip>
        </div>
        <div className="text-xs text-muted-foreground">
          按下 <kbd className="rounded-md border bg-muted px-1.5 py-0.5 text-xs">Enter</kbd> 发送, <kbd className="rounded-md border bg-muted px-1.5 py-0.5 text-xs">Shift + Enter</kbd> 换行
        </div>
      </div>
    </motion.div>
  );
} 