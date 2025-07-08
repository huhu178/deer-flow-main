// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Download, FileText, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Progress } from "~/components/ui/progress";
import { Badge } from "~/components/ui/badge";
import { Markdown } from "~/components/deer-flow/markdown";
import { ScrollContainer, type ScrollContainerRef } from "~/components/deer-flow/scroll-container";
import { cn } from "~/lib/utils";

/**
 * 大型报告管理器组件
 * 支持分批显示、进度跟踪、自动保存和下载功能
 */

interface ReportSection {
  number: number;
  title: string;
  content: string;
  saved: boolean;
  path?: string;
}

interface ReportStats {
  total_sections: number;
  total_size: number;
  created_time: string;
  final_path?: string;
}

interface LargeReportManagerProps {
  className?: string;
  reportName?: string;
  onSectionSaved?: (section: ReportSection) => void;
  onReportCompleted?: (stats: ReportStats) => void;
  autoSave?: boolean;
  chunkSize?: number;
}

export function LargeReportManager({
  className,
  reportName = `report_${Date.now()}`,
  onSectionSaved,
  onReportCompleted,
  autoSave = true,
  chunkSize = 8000,
}: LargeReportManagerProps) {
  const [sections, setSections] = useState<ReportSection[]>([]);
  const [currentContent, setCurrentContent] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [reportStats, setReportStats] = useState<ReportStats | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const scrollRef = useRef<ScrollContainerRef>(null);

  /**
   * 添加新的报告章节
   */
  const addSection = useCallback((title: string, content: string, sectionNumber?: number) => {
    const newSection: ReportSection = {
      number: sectionNumber || sections.length + 1,
      title,
      content,
      saved: false,
    };

    setSections(prev => [...prev, newSection]);

    // 如果启用自动保存，保存章节到后端
    if (autoSave) {
      saveSectionToBackend(newSection);
    }

    // 触发回调
    onSectionSaved?.(newSection);
  }, [sections.length, autoSave, onSectionSaved]);

  /**
   * 更新当前正在生成的内容
   */
  const updateCurrentContent = useCallback((content: string) => {
    setCurrentContent(content);
    
    // 自动滚动到底部
    if (scrollRef.current) {
      scrollRef.current.scrollToBottom();
    }
  }, []);

  /**
   * 保存章节到后端
   */
  const saveSectionToBackend = async (section: ReportSection) => {
    try {
      const response = await fetch('/api/report/section/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_name: reportName,
          section_title: section.title,
          section_content: section.content,
          section_number: section.number,
          base_dir: "./outputs/reports",
          keep_chunks: true,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        
        // 更新章节状态
        setSections(prev => prev.map(s => 
          s.number === section.number 
            ? { ...s, saved: true, path: result.section_path }
            : s
        ));
      }
    } catch (error) {
      console.error('保存章节失败:', error);
    }
  };

  /**
   * 合并并下载完整报告
   */
  const mergeAndDownloadReport = async () => {
    try {
      // 首先合并报告
      const mergeResponse = await fetch('/api/report/merge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_name: reportName,
          include_toc: true,
          sort_by_number: true,
          base_dir: "./outputs/reports",
          keep_chunks: false,
        }),
      });

      if (mergeResponse.ok) {
        const mergeResult = await mergeResponse.json();
        setReportStats(mergeResult.report_stats);
        onReportCompleted?.(mergeResult.report_stats);

        // 然后下载报告
        const downloadResponse = await fetch(`/api/report/download/${reportName}?base_dir=./outputs/reports`);
        
        if (downloadResponse.ok) {
          const blob = await downloadResponse.blob();
          const url = window.URL.createObjectURL(blob);
          setDownloadUrl(url);
          
          // 自动下载
          const a = document.createElement('a');
          a.href = url;
          a.download = `${reportName}_complete.md`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }
      }
    } catch (error) {
      console.error('合并和下载报告失败:', error);
    }
  };

  /**
   * 手动保存所有未保存的章节
   */
  const saveAllSections = async () => {
    const unsavedSections = sections.filter(s => !s.saved);
    
    for (const section of unsavedSections) {
      await saveSectionToBackend(section);
    }
  };

  /**
   * 计算总进度
   */
  const calculateProgress = () => {
    if (sections.length === 0) return 0;
    const savedCount = sections.filter(s => s.saved).length;
    return Math.round((savedCount / sections.length) * 100);
  };

  useEffect(() => {
    setProgress(calculateProgress());
  }, [sections]);

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* 报告状态栏 */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              大型报告: {reportName}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={isGenerating ? "default" : "secondary"}>
                {isGenerating ? "生成中" : "已完成"}
              </Badge>
              {sections.length > 0 && (
                <Badge variant="outline">
                  {sections.length} 个章节
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {/* 进度条 */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>保存进度</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-2">
              <Button
                onClick={saveAllSections}
                disabled={sections.every(s => s.saved)}
                size="sm"
                variant="outline"
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                保存所有章节
              </Button>
              
              <Button
                onClick={mergeAndDownloadReport}
                disabled={sections.length === 0 || !sections.every(s => s.saved)}
                size="sm"
              >
                <Download className="h-4 w-4 mr-1" />
                合并并下载
              </Button>
            </div>

            {/* 报告统计 */}
            {reportStats && (
              <div className="text-sm text-muted-foreground">
                总计 {reportStats.total_sections} 个章节，
                大小 {Math.round(reportStats.total_size / 1024)} KB，
                创建时间 {new Date(reportStats.created_time).toLocaleString()}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 报告内容显示区域 */}
      <Card className="flex-1 overflow-hidden">
        <CardHeader className="pb-3">
          <CardTitle>报告内容</CardTitle>
        </CardHeader>
        <CardContent className="h-full overflow-hidden">
          <ScrollContainer
            ref={scrollRef}
            className="h-full"
            autoScrollToBottom
          >
            <div className="space-y-6">
              {/* 已保存的章节 */}
              {sections.map((section) => (
                <div key={section.number} className="border-l-4 border-blue-500 pl-4">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold">
                      第 {section.number} 章: {section.title}
                    </h3>
                    {section.saved ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                    )}
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <Markdown>{section.content}</Markdown>
                  </div>
                </div>
              ))}

              {/* 当前正在生成的内容 */}
              {currentContent && (
                <div className="border-l-4 border-orange-500 pl-4">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold">正在生成...</h3>
                    <Loader2 className="h-4 w-4 animate-spin text-orange-500" />
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <Markdown animate>{currentContent}</Markdown>
                  </div>
                </div>
              )}

              {/* 生成状态指示 */}
              {isGenerating && (
                <div className="flex items-center justify-center py-8">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>正在生成大型报告，请耐心等待...</span>
                  </div>
                </div>
              )}
            </div>
          </ScrollContainer>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * 大型报告生成钩子
 * 提供报告生成的状态管理和API调用
 */
export function useLargeReportGenerator() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportManager, setReportManager] = useState<any>(null);

  /**
   * 开始生成大型报告
   */
  const startGeneration = useCallback(async (
    messages: any[],
    options: {
      reportName?: string;
      chunkSize?: number;
      autoSave?: boolean;
      threadId?: string;
    } = {}
  ) => {
    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/chat/stream/large', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages,
          thread_id: options.threadId || "__default__",
          report_name: options.reportName || `report_${Date.now()}`,
          chunk_size: options.chunkSize || 8000,
          auto_save_sections: options.autoSave !== false,
          base_dir: "./outputs/reports",
          max_plan_iterations: 1,
          max_step_num: 3,
          max_search_results: 3,
          auto_accepted_plan: true,
          enable_background_investigation: true,
        }),
      });

      if (!response.ok) {
        throw new Error('生成报告失败');
      }

      return response;
    } catch (error) {
      setIsGenerating(false);
      throw error;
    }
  }, []);

  /**
   * 停止生成
   */
  const stopGeneration = useCallback(() => {
    setIsGenerating(false);
  }, []);

  return {
    isGenerating,
    startGeneration,
    stopGeneration,
    reportManager,
    setReportManager,
  };
} 