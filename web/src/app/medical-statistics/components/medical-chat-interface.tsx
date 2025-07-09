// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";
import { useCallback } from "react";
import { Button } from "~/components/ui/button";

import { useStore, sendMessage } from "~/core/store";
import { cn } from "~/lib/utils";
import type { Option } from "~/core/messages";

import { MedicalConversationStarter } from "./medical-conversation-starter";
import { SimpleMedicalInput } from "./simple-medical-input";
import { MedicalMessageList } from "./medical-message-list";

interface MedicalChatInterfaceProps {
  className?: string;
}

/**
 * 医学统计分析聊天界面组件
 * @param className 自定义样式类名
 */
export function MedicalChatInterface({
  className,
}: MedicalChatInterfaceProps) {
  const responding = useStore((state) => state.responding);
  const messageCount = useStore((state) => state.messageIds.length);

  const handleSend = useCallback(
    async (message: string, options?: { interruptFeedback?: string }) => {
      try {
        await sendMessage(message, {
          interruptFeedback: options?.interruptFeedback,
        });
      } catch {
        // Handle error if needed
      }
    },
    [],
  );

  const handleFeedback = useCallback((_feedback: { option: Option }) => {
    // Handle feedback if needed
  }, []);

  return (
    <div
      className={cn(
        "flex-1 flex flex-col overflow-hidden relative bg-blue-50 border-0",
        className,
      )}
      style={{ border: "none", outline: "none" }}
    >
      <MedicalMessageList
        className="w-full border-0"
        onFeedback={handleFeedback}
        onSendMessage={handleSend}
      />

      <div
        className="border-t border-blue-200 p-4 bg-blue-50 border-0"
        style={{
          borderTop: "1px solid #dbeafe",
          borderLeft: "none",
          borderRight: "none",
          borderBottom: "none",
        }}
      >
        {!responding && messageCount === 0 && (
          <MedicalConversationStarter
            className="absolute top-[-218px] left-0"
            onSend={handleSend}
          />
        )}
        <SimpleMedicalInput
          className="w-full"
          responding={responding}
          onSend={(message) => void handleSend(message)}
        />
        <div className="mt-3 text-lg text-gray-600 font-normal">
          按Enter发送，Shift+Enter换行。您可以从左侧选择流行病学设计方法或使用右侧的数据库智能体。
        </div>
        <div className="mt-2 text-base text-gray-600 font-medium">
          💡 语音输入提示：点击麦克风图标开始语音输入。如果遇到网络问题，语音识别可能不可用，请使用键盘输入。
        </div>
      </div>

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