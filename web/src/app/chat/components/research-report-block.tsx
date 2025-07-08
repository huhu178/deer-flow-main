// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useCallback, useRef } from "react";

import { LoadingAnimation } from "~/components/deer-flow/loading-animation";
import { Markdown } from "~/components/deer-flow/markdown";
// import { SimpleEnhancedRenderer } from "~/components/deer-flow/simple-enhanced-renderer"; // Temporarily disabled - component is empty
import ReportEditor from "~/components/editor";
import { useReplay } from "~/core/replay";
import { useMessage, useStore } from "~/core/store";
import { cn } from "~/lib/utils";

export function ResearchReportBlock({
  className,
  messageId,
}: {
  className?: string;
  researchId: string;
  messageId: string;
}) {
  const message = useMessage(messageId);
  const { isReplay } = useReplay();
  const handleMarkdownChange = useCallback(
    (markdown: string) => {
      if (message) {
        message.content = markdown;
        useStore.setState({
          messages: new Map(useStore.getState().messages).set(
            message.id,
            message,
          ),
        });
      }
    },
    [message],
  );
  const contentRef = useRef<HTMLDivElement>(null);
  const isCompleted = message?.isStreaming === false && message?.content !== "";
  // TODO: scroll to top when completed, but it's not working
  // useEffect(() => {
  //   if (isCompleted && contentRef.current) {
  //     setTimeout(() => {
  //       contentRef
  //         .current!.closest("[data-radix-scroll-area-viewport]")
  //         ?.scrollTo({
  //           top: 0,
  //           behavior: "smooth",
  //         });
  //     }, 500);
  //   }
  // }, [isCompleted]);

  // 生成报告元数据
  const generateMetadata = () => {
    const content = message?.content || '';
    const wordCount = content.length;
    const readingTime = Math.ceil(wordCount / 500); // 假设每分钟阅读500字
    const sections = (content.match(/^#{1,6}\s+/gm) || []).length;
    
    return {
      title: '医学研究报告',
      generatedAt: new Date().toISOString(),
      wordCount,
      readingTime,
      sections,
      author: 'DeerFlow AI系统',
      version: '2.0',
      tags: ['医学研究', 'DXA影像', 'AI预测', '全身健康']
    };
  };

  return (
    <div
      ref={contentRef}
      className={cn("relative flex flex-col pt-4 pb-8", className)}
    >
      {/* Temporarily using Markdown component for both cases until SimpleEnhancedRenderer is implemented */}
      <Markdown animate>{message?.content}</Markdown>
      {message?.isStreaming && <LoadingAnimation className="my-12" />}
    </div>
  );
}
