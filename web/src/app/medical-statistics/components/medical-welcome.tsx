// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";

import { cn } from "~/lib/utils";

/**
 * 医学统计分析欢迎界面组件
 * @param className 自定义样式类名
 */
export function MedicalWelcome({ className }: { className?: string }) {
  return (
    <motion.div
      className={cn("flex flex-col", className)}
      style={{ transition: "all 0.2s ease-out" }}
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <h3 className="mb-2 text-center text-3xl font-medium">
        👋 你好呀！
      </h3>
      <div className="text-muted-foreground px-4 text-center text-lg">
        欢迎使用 AigenMed，一个专于流行病学研究设计与分析的医学统计 AI 智能平台，它可
        以帮助您进行网络搜索、浏览信息和处理复杂任务。
      </div>
    </motion.div>
  );
} 