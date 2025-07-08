// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 医学聊天界面组件
 * @description 中间的聊天界面，集成现有的AigenMed聊天系统，专门用于医学统计分析
 */

import { motion } from "framer-motion";
import { useCallback, useRef, useState } from "react";
import { Button } from "~/components/ui/button";
import { Textarea } from "~/components/ui/textarea";
import { ChevronLeft, ChevronRight, Upload, Send, Bot } from "lucide-react";
import { useStore, sendMessage } from "~/core/store";
import { cn } from "~/lib/utils";
import type { Option } from "~/core/messages";

import { MedicalConversationStarter } from "./medical-conversation-starter";
import { SimpleMedicalInput } from "./simple-medical-input";
import { MedicalMessageList } from "./medical-message-list";

interface MedicalChatInterfaceProps {
  className?: string;
  leftPanelVisible?: boolean;
  rightPanelVisible?: boolean;
  onToggleLeftPanel?: () => void;
  onToggleRightPanel?: () => void;
}

/**
 * 医学统计分析聊天界面组件
 * @param className 自定义样式类名
 * @param leftPanelVisible 左侧面板是否可见
 * @param rightPanelVisible 右侧面板是否可见
 * @param onToggleLeftPanel 切换左侧面板的函数
 * @param onToggleRightPanel 切换右侧面板的函数
 */
export function MedicalChatInterface({ 
  className,
  leftPanelVisible = true, 
  rightPanelVisible = true, 
  onToggleLeftPanel, 
  onToggleRightPanel 
}: MedicalChatInterfaceProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // 从store获取状态
  const responding = useStore((state) => state.responding);
  const messageIds = useStore((state) => state.messageIds);
  const messages = useStore((state) => state.messages);
  const messageCount = useStore((state) => state.messageIds.length);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [feedback, setFeedback] = useState<{ option: Option } | null>(null);

  const handleSendMessage = async () => {
    if (message.trim() && !responding) {
      setMessage("");
      
      // 调用现有的sendMessage接口
      await sendMessage(message.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSend = useCallback(
    async (message: string, options?: { interruptFeedback?: string }) => {
      const abortController = new AbortController();
      abortControllerRef.current = abortController;
      try {
        await sendMessage(
          message,
          {
            interruptFeedback:
              options?.interruptFeedback ?? feedback?.option.value,
          },
          {
            abortSignal: abortController.signal,
          },
        );
      } catch {}
    },
    [feedback],
  );

  const handleCancel = useCallback(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
  }, []);

  const handleFeedback = useCallback(
    (feedback: { option: Option }) => {
      setFeedback(feedback);
    },
    [setFeedback],
  );

  const handleRemoveFeedback = useCallback(() => {
    setFeedback(null);
  }, [setFeedback]);

  return (
    <div className={cn("flex-1 flex flex-col overflow-hidden relative bg-blue-50 border-0", className)} style={{border: 'none', outline: 'none'}}>
      {/* 切换左侧面板按钮 */}
      <Button
        variant="outline"
        size="icon"
        className="absolute left-0 top-1/2 transform -translate-y-1/2 bg-blue-50 border border-blue-200 rounded-r-md p-1 shadow-md z-10 hover:bg-blue-100"
        onClick={onToggleLeftPanel}
        title={leftPanelVisible ? "隐藏左侧面板" : "显示左侧面板"}
      >
        <ChevronLeft className="h-5 w-5" />
      </Button>

      {/* 切换右侧面板按钮 */}
      <Button
        variant="outline"
        size="icon"
        className="absolute right-0 top-1/2 transform -translate-y-1/2 bg-blue-50 border border-blue-200 rounded-l-md p-1 shadow-md z-10 hover:bg-blue-100"
        onClick={onToggleRightPanel}
        title={rightPanelVisible ? "隐藏右侧面板" : "显示右侧面板"}
      >
        <ChevronRight className="h-5 w-5" />
      </Button>

      {/* 消息列表视图 */}
      <MedicalMessageList
        className="w-full border-0"
        onFeedback={handleFeedback}
        onSendMessage={handleSend}
      />

      {/* 输入区域和对话启动器 */}
      <div className="border-t border-blue-200 p-4 bg-blue-50 border-0" style={{borderTop: '1px solid #dbeafe', borderLeft: 'none', borderRight: 'none', borderBottom: 'none'}}>
        {!responding && messageCount === 0 && (
          <MedicalConversationStarter
            className="absolute top-[-218px] left-0"
            onSend={handleSend}
          />
        )}
        <SimpleMedicalInput
          className="w-full"
          responding={responding}
          onSend={(message) => handleSend(message)}
        />
        <div className="mt-3 text-lg text-gray-600 font-normal">
          按Enter发送，Shift+Enter换行。您可以从左侧选择流行病学设计方法或使用右侧的数据库智能体。
        </div>
        <div className="mt-2 text-base text-gray-600 font-medium">
          💡 语音输入提示：点击麦克风图标开始语音输入。如果遇到网络问题，语音识别可能不可用，请使用键盘输入。
        </div>
      </div>

      {/* 欢迎界面（仅在没有消息时显示） */}
      {!responding && messageCount === 0 && (
        <motion.div
          className="fixed inset-0 flex items-center justify-center pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="text-center text-muted-foreground mb-20">
            <h3 className="mb-4 text-3xl font-medium">🩺 医学统计AI助手</h3>
            <p className="text-lg">
              欢迎使用医学统计分析智能平台，我可以帮助您进行流行病学研究设计与分析
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
} 