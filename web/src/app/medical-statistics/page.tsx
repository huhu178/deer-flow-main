// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 医学统计分析页面
 * @description 智能数据分析平台的主界面，包含设计分析智能体、聊天界面和数据库智能体
 */

import type { Metadata } from "next";
import { MedicalStatisticsInterface } from "./components/medical-statistics-interface";

export const metadata: Metadata = {
  title: "医学统计分析 | 智能数据分析平台",
  description: "国家健康医疗大数据研究院 - 智能数据分析平台，提供流行病学研究设计与分析方法",
};

export default function MedicalStatisticsPage() {
  return <MedicalStatisticsInterface />;
} 