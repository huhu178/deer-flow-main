'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Button } from '~/components/ui/button'
import { Progress } from '~/components/ui/progress'
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card'
import { Badge } from '~/components/ui/badge'
import { ScrollArea } from '~/components/ui/scroll-area'
import { Download, Play, RefreshCw, Square } from 'lucide-react'

interface ReportSection {
  direction_number: number
  title: string
  content: string
  word_count: number
  progress: string
  percentage: number
}

interface ReportStats {
  total_tokens: number;
  total_words: number;
  total_cost: number;
  time_taken: number;
}

interface BatchReportViewerProps {
  onSectionGenerated?: (section: ReportSection) => void
  onComplete?: (finalPath: string, stats: ReportStats) => void
  onError?: (error: string) => void
}

export default function BatchReportViewer({
  onSectionGenerated,
  onComplete,
  onError
}: BatchReportViewerProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [sections, setSections] = useState<ReportSection[]>([])
  const [currentProgress, setCurrentProgress] = useState(0)
  const [totalSections, setTotalSections] = useState(20)
  const [reportName, setReportName] = useState('')
  const [mode, setMode] = useState<'all' | 'demo'>('demo')
  const [finalReportPath, setFinalReportPath] = useState('')
  const [stats, setStats] = useState<ReportStats | null>(null)
  const [error, setError] = useState('')
  
  const eventSourceRef = useRef<EventSource | null>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // 自动滚动到最新内容
  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }

  // 开始生成报告
  const startGeneration = async () => {
    try {
      setIsGenerating(true)
      setError('')
      setSections([])
      setCurrentProgress(0)
      
      // 生成报告名称
      const timestamp = Date.now()
      const newReportName = `DXA_分批研究报告_${timestamp}`
      setReportName(newReportName)
      
      // 启动流式生成
      const eventSource = new EventSource(
        `/api/batch-report/stream/${newReportName}?mode=${mode}`
      )
      eventSourceRef.current = eventSource
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          switch (data.type) {
            case 'start':
              setTotalSections(data.total)
              console.log(`开始生成 ${data.total} 个研究方向`)
              break
              
            case 'section_complete':
              const newSection: ReportSection = {
                direction_number: data.direction_number,
                title: data.title,
                content: data.content,
                word_count: data.word_count,
                progress: data.progress,
                percentage: data.percentage
              }
              
              setSections(prev => [...prev, newSection])
              setCurrentProgress(data.percentage)
              
              // 调用回调函数
              onSectionGenerated?.(newSection)
              
              // 自动滚动
              setTimeout(scrollToBottom, 100)
              break
              
            case 'complete':
              setFinalReportPath(data.final_path)
              setStats(data.stats)
              setIsGenerating(false)
              
              // 调用完成回调
              onComplete?.(data.final_path, data.stats)
              console.log('报告生成完成:', data.final_path)
              break
              
            case 'error':
              setError(data.error)
              setIsGenerating(false)
              onError?.(data.error)
              console.error('生成错误:', data.error)
              break
          }
        } catch (err) {
          console.error('解析事件数据失败:', err)
        }
      }
      
      eventSource.onerror = (err) => {
        console.error('EventSource 错误:', err)
        setError('连接中断，请重试')
        setIsGenerating(false)
        eventSource.close()
      }
      
    } catch (err) {
      console.error('启动生成失败:', err)
      setError('启动失败，请重试')
      setIsGenerating(false)
    }
  }

  // 停止生成
  const stopGeneration = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setIsGenerating(false)
  }

  // 下载完整报告
  const downloadReport = async () => {
    if (!finalReportPath) return
    
    try {
      // 这里应该调用下载API
      const response = await fetch(`/api/report/download/${reportName}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${reportName}.txt`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (err) {
      console.error('下载失败:', err)
    }
  }

  // 清理资源
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-4">
      {/* 控制面板 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>🏥 DXA研究报告分批生成器</span>
            <Badge variant={isGenerating ? "default" : "secondary"}>
              {isGenerating ? "生成中" : "就绪"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 模式选择 */}
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium">生成模式:</label>
            <div className="flex space-x-2">
              <Button
                variant={mode === 'demo' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setMode('demo')}
                disabled={isGenerating}
              >
                演示模式 (5个方向)
              </Button>
              <Button
                variant={mode === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setMode('all')}
                disabled={isGenerating}
              >
                完整模式 (20个方向)
              </Button>
            </div>
          </div>

          {/* 控制按钮 */}
          <div className="flex items-center space-x-2">
            {!isGenerating ? (
              <Button onClick={startGeneration} className="flex items-center space-x-2">
                <Play className="w-4 h-4" />
                <span>开始生成</span>
              </Button>
            ) : (
              <Button onClick={stopGeneration} variant="destructive" className="flex items-center space-x-2">
                <Square className="w-4 h-4" />
                <span>停止生成</span>
              </Button>
            )}
            
            {finalReportPath && (
              <Button onClick={downloadReport} variant="outline" className="flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>下载完整报告</span>
              </Button>
            )}
          </div>

          {/* 进度条 */}
          {isGenerating && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>生成进度</span>
                <span>{sections.length}/{totalSections} ({currentProgress.toFixed(1)}%)</span>
              </div>
              <Progress value={currentProgress} className="w-full" />
            </div>
          )}

          {/* 错误信息 */}
          {error && (
            <div className="text-red-500 text-sm p-2 bg-red-50 rounded">
              错误: {error}
            </div>
          )}

          {/* 统计信息 */}
          {stats && (
            <Card>
              <CardHeader>
                <CardTitle>报告统计</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="p-4 bg-gray-100 rounded-lg">
                  <p className="text-sm text-gray-600">总Token数</p>
                  <p className="text-2xl font-bold">{stats.total_tokens}</p>
                </div>
                <div className="p-4 bg-gray-100 rounded-lg">
                  <p className="text-sm text-gray-600">总字数</p>
                  <p className="text-2xl font-bold">{stats.total_words}</p>
                </div>
                <div className="p-4 bg-gray-100 rounded-lg">
                  <p className="text-sm text-gray-600">预估费用</p>
                  <p className="text-2xl font-bold">${stats.total_cost.toFixed(4)}</p>
                </div>
                <div className="p-4 bg-gray-100 rounded-lg">
                  <p className="text-sm text-gray-600">总耗时</p>
                  <p className="text-2xl font-bold">{stats.time_taken.toFixed(2)}s</p>
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {/* 报告内容展示 */}
      {sections.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>📄 生成的研究方向</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[600px] w-full" ref={scrollAreaRef}>
              <div className="space-y-6">
                {sections.map((section, index) => (
                  <div key={section.direction_number} className="border-b pb-4 last:border-b-0">
                    {/* 章节标题 */}
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-blue-600">
                        第 {section.direction_number} 个方向
                      </h3>
                      <Badge variant="outline">
                        {section.word_count.toLocaleString()} 字
                      </Badge>
                    </div>
                    
                    {/* 研究标题 */}
                    <h4 className="text-md font-medium mb-3 text-gray-800">
                      {section.title}
                    </h4>
                    
                    {/* 内容预览 */}
                    <div className="bg-gray-50 p-4 rounded-md">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                        {section.content.substring(0, 500)}
                        {section.content.length > 500 && (
                          <span className="text-blue-500">
                            ... (还有 {section.content.length - 500} 个字符)
                          </span>
                        )}
                      </pre>
                    </div>
                    
                    {/* 生成时间指示器 */}
                    <div className="mt-2 text-xs text-gray-500">
                      生成于 {new Date().toLocaleTimeString()}
                    </div>
                  </div>
                ))}
                
                {/* 生成中指示器 */}
                {isGenerating && sections.length < totalSections && (
                  <div className="flex items-center justify-center p-8 text-gray-500">
                    <RefreshCw className="w-6 h-6 animate-spin mr-2" />
                    <span>正在生成下一个研究方向...</span>
                  </div>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* 使用说明 */}
      <Card>
        <CardHeader>
          <CardTitle>💡 使用说明</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-600 space-y-2">
          <p>• <strong>演示模式</strong>: 生成前5个研究方向，适合快速预览</p>
          <p>• <strong>完整模式</strong>: 生成全部20个研究方向，每个约3000-4000字</p>
          <p>• <strong>实时展示</strong>: 每个方向生成完成后立即显示，无需等待全部完成</p>
          <p>• <strong>自动保存</strong>: 所有内容自动保存到本地文件，支持下载完整报告</p>
          <p>• <strong>突破限制</strong>: 通过分批生成解决16k token输出限制问题</p>
        </CardContent>
      </Card>
    </div>
  )
} 