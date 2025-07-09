// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useRef } from "react";

import { LoadingAnimation } from "~/components/deer-flow/loading-animation";
import { Markdown } from "~/components/deer-flow/markdown";
// import { SimpleEnhancedRenderer } from "~/components/deer-flow/simple-enhanced-renderer"; // Temporarily disabled - component is empty
import { useMessage } from "~/core/store";
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

  const contentRef = useRef<HTMLDivElement>(null);

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
