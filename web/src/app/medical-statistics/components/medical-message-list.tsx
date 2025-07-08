// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";
import React, { useCallback, useMemo, useState } from "react";

import { Markdown } from "~/components/deer-flow/markdown";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import type { Message, Option } from "~/core/messages";
import { useStore } from "~/core/store";
import { parseJSON } from "~/core/utils";
import { cn } from "~/lib/utils";

/**
 * 医学统计专用消息列表组件
 */
export function MedicalMessageList({
  className,
  onFeedback,
  onSendMessage,
}: {
  className?: string;
  onFeedback?: (feedback: { option: Option }) => void;
  onSendMessage?: (
    message: string,
    options?: { interruptFeedback?: string },
  ) => void;
}) {
  const messageIds = useStore((state) => state.messageIds);
  const messages = useStore((state) => state.messages);

  const interruptMessage = useMemo(() => {
    for (const messageId of [...messageIds].reverse()) {
      const message = messages.get(messageId);
      if (message?.options?.length) {
        return message;
      }
    }
    return null;
  }, [messageIds, messages]);

  const waitForFeedback = useMemo(
    () => interruptMessage !== null,
    [interruptMessage],
  );

  return (
    <div
      className={cn(
        "flex-1 overflow-y-auto p-4 space-y-4 bg-blue-50 border-0 scrollbar-hide",
        className,
      )}
      style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
    >
      {messageIds.map((messageId) => {
        const msg = messages.get(messageId);
        if (!msg) return null;

        const isPlanner = (msg.agent as string) === "planner";
        const isJsonPlan =
          msg.content &&
          msg.content.includes('"title"') &&
          msg.content.includes('"steps"');

        if (isPlanner || isJsonPlan) {
          return (
            <div key={messageId} className="flex justify-start">
              <MedicalPlanCard
                message={msg}
                interruptMessage={interruptMessage}
                waitForFeedback={waitForFeedback}
                onFeedback={onFeedback}
                onSendMessage={onSendMessage}
              />
            </div>
          );
        }

        return (
          <div
            key={messageId}
            className={cn(
              "flex",
              msg.role === "user" ? "justify-end" : "justify-start",
            )}
          >
            <div
              className={cn(
                "max-w-3xl p-3 rounded-lg border-0",
                msg.role === "user"
                  ? "bg-blue-300 text-black shadow-sm"
                  : "bg-white text-black shadow-sm border border-blue-200",
              )}
            >
              {msg.role !== "user" && (
                <div className="flex items-center mb-1">
                  <span className="text-sm font-medium text-blue-700">
                    {{
                      researcher: "研究员",
                      coder: "代码分析师",
                      reporter: "报告生成器",
                      planner: "医学研究规划师",
                    }[msg.agent as string] ?? "智能助手"}
                  </span>
                </div>
              )}
              <div className="text-lg text-black">
                {(() => {
                  const parsed = parseThinkingContent(msg.content ?? "");
                  return (
                    <>
                      {parsed.hasThinking && (
                        <ThinkingDisplay content={parsed.thinkingContent} />
                      )}
                      <Markdown className="prose prose-lg max-w-none text-black [&_*]:text-black [&_h1]:text-2xl [&_h1]:font-bold [&_h1]:mb-3 [&_h2]:text-xl [&_h2]:font-semibold [&_h2]:mb-2 [&_h3]:text-lg [&_h3]:font-medium [&_h3]:mb-2 [&_strong]:font-bold [&_em]:italic [&_code]:bg-gray-100 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_pre]:bg-gray-100 [&_pre]:p-3 [&_pre]:rounded [&_ul]:list-disc [&_ul]:ml-4 [&_ol]:list-decimal [&_ol]:ml-4 [&_li]:mb-1 [&_p]:mb-2 [&_blockquote]:border-l-4 [&_blockquote]:border-blue-300 [&_blockquote]:pl-4 [&_blockquote]:italic">
                        {parsed.mainContent}
                      </Markdown>
                    </>
                  );
                })()}
                {msg.isStreaming && <span className="animate-pulse">▋</span>}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/**
 * 医学研究计划卡片组件
 */
function MedicalPlanCard({
  className,
  message,
  interruptMessage,
  onFeedback,
  waitForFeedback,
  onSendMessage,
}: {
  className?: string;
  message: Message;
  interruptMessage?: Message | null;
  onFeedback?: (feedback: { option: Option }) => void;
  onSendMessage?: (
    message: string,
    options?: { interruptFeedback?: string },
  ) => void;
  waitForFeedback?: boolean;
}) {
  const plan = useMemo<{
    title?: string;
    thought?: string;
    steps?: { title?: string; description?: string }[];
  }>(() => {
    return parseJSON(message.content ?? "", {});
  }, [message.content]);

  const GREETINGS = useMemo(
    () => ["太好了", "看起来不错", "很棒", "非常好", "完美"],
    [],
  );

  const handleAccept = useCallback(async () => {
    if (onSendMessage) {
      onSendMessage(
        `${GREETINGS[Math.floor(Math.random() * GREETINGS.length)] ?? "开始研究吧"}！开始研究吧。`,
        {
          interruptFeedback: "accepted",
        },
      );
    }
  }, [onSendMessage, GREETINGS]);

  return (
    <Card
      className={cn(
        "w-full max-w-4xl bg-white border border-blue-200 shadow-sm",
        className,
      )}
    >
      <CardHeader className="bg-white">
        <CardTitle className="text-black">
          <Markdown className="text-black [&_*]:text-black" animate>
            {`### ${
              plan.title !== undefined && plan.title !== ""
                ? plan.title
                : "医学统计深度研究"
            }`}
          </Markdown>
        </CardTitle>
      </CardHeader>
      <CardContent className="bg-white text-black">
        <Markdown className="text-black [&_*]:text-black" animate>
          {plan.thought}
        </Markdown>
        {plan.steps && (
          <ul className="my-2 flex list-decimal flex-col gap-4 border-l-[2px] border-blue-300 pl-8">
            {plan.steps.map((step, i) => (
              <li key={`step-${i}`}>
                <h3 className="mb text-lg font-medium text-black">
                  <Markdown className="text-black [&_*]:text-black" animate>
                    {step.title}
                  </Markdown>
                </h3>
                <div className="text-black text-sm">
                  <Markdown className="text-black [&_*]:text-black" animate>
                    {step.description}
                  </Markdown>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
      <CardFooter className="flex justify-end bg-white">
        {interruptMessage?.options?.length && !message.isStreaming && (
          <motion.div
            className="flex gap-2"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            {interruptMessage.options.map((option) => (
              <Button
                key={option.value}
                variant={option.value === "accepted" ? "default" : "outline"}
                disabled={!waitForFeedback}
                className={cn(
                  option.value === "accepted"
                    ? "bg-blue-600 hover:bg-blue-700 text-white"
                    : "border-blue-300 text-blue-700 hover:bg-blue-50",
                )}
                onClick={() => {
                  if (option.value === "accepted") {
                    void handleAccept();
                  } else if (option.value === "edit_plan") {
                    onSendMessage?.(
                      "[EDIT_PLAN] 请根据我的要求修改研究计划",
                      {
                        interruptFeedback: "edit_plan",
                      },
                    );
                  } else {
                    onFeedback?.({ option });
                  }
                }}
              >
                {option.text}
              </Button>
            ))}
          </motion.div>
        )}
      </CardFooter>
    </Card>
  );
}

function parseThinkingContent(content: string) {
  const thinkingRegex = /<thinking>([\s\S]*?)<\/thinking>/;
  const match = thinkingRegex.exec(content);

  if (match?.[1]) {
    const thinkingContent = match[1].trim();
    const remainingContent = content.replace(thinkingRegex, "").trim();
    return {
      hasThinking: true,
      thinkingContent,
      mainContent: remainingContent,
    };
  }

  return {
    hasThinking: false,
    thinkingContent: "",
    mainContent: content,
  };
}

function ThinkingDisplay({ content }: { content: string }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="mb-3 border border-purple-200 rounded-lg bg-purple-50">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 text-left text-sm font-medium text-purple-700 hover:bg-purple-100 rounded-t-lg flex items-center justify-between"
      >
        <span className="flex items-center">
          🧠 AI思考过程
          <span className="ml-1 text-xs text-purple-500">
            (点击查看/隐藏)
          </span>
        </span>
        <span className="text-purple-500">{isExpanded ? "▼" : "▶"}</span>
      </button>
      {isExpanded && (
        <div className="px-3 py-2 border-t border-purple-200 bg-white rounded-b-lg">
          <div className="text-sm text-gray-700 italic whitespace-pre-wrap">
            {content}
          </div>
        </div>
      )}
    </div>
  );
} 