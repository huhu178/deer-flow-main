'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Progress } from '~/components/ui/progress';
import { Badge } from '~/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import { 
  Play, 
  Pause, 
  Square, 
  Download, 
  Plus, 
  Trash2, 
  RefreshCw,
  FileText,
  Settings,
  Eye,
  Edit
} from 'lucide-react';

interface BatchTask {
  task_name: string;
  report_name: string;
  total_items: number;
  completed_items: number;
  status: string;
  progress_percentage: number;
}

interface BatchItem {
  id: string;
  type: string;
  title: string;
  content_template: string;
  metadata: Record<string, any>;
  section_number: number;
  estimated_tokens: number;
}

interface BatchProgress {
  total_items: number;
  completed_items: number;
  current_batch: number;
  total_batches: number;
  current_item: string | null;
  status: string;
  start_time: string;
  progress_percentage: number;
  error_message?: string;
}

interface BatchResult {
  batch_id: string;
  item_id: string;
  title: string;
  content: string;
  section_number: number;
  word_count: number;
  token_count: number;
  generated_time: string;
  status: string;
  error_message?: string;
}

const BatchManagerPage: React.FC = () => {
  // 状态管理
  const [tasks, setTasks] = useState<BatchTask[]>([]);
  const [currentTask, setCurrentTask] = useState<string>('');
  const [items, setItems] = useState<BatchItem[]>([]);
  const [progress, setProgress] = useState<BatchProgress | null>(null);
  const [results, setResults] = useState<BatchResult[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState('tasks');
  
  // 表单状态
  const [newTaskForm, setNewTaskForm] = useState({
    task_name: '',
    report_name: '',
    batch_size: 5,
    max_tokens_per_item: 4000
  });
  
  const [newItemForm, setNewItemForm] = useState({
    item_id: '',
    item_type: 'survey_aspect',
    title: '',
    content_template: '',
    metadata: '{}',
    estimated_tokens: 0
  });
  
  // 流式生成相关
  const eventSourceRef = useRef<EventSource | null>(null);
  const [streamLogs, setStreamLogs] = useState<string[]>([]);
  
  // API 基础URL
  const API_BASE = '/api/batch';
  
  // 加载任务列表
  const loadTasks = async () => {
    try {
      const response = await fetch(`${API_BASE}/list`);
      const data = await response.json();
      if (data.success) {
        setTasks(data.tasks);
      }
    } catch (error) {
      console.error('加载任务失败:', error);
    }
  };
  
  // 加载任务详情
  const loadTaskDetails = async (taskName: string) => {
    try {
      // 加载项目列表
      const itemsResponse = await fetch(`${API_BASE}/items/${taskName}`);
      const itemsData = await itemsResponse.json();
      if (itemsData.success) {
        setItems(itemsData.items);
      }
      
      // 加载进度
      const progressResponse = await fetch(`${API_BASE}/progress/${taskName}`);
      const progressData = await progressResponse.json();
      if (progressData.success) {
        setProgress(progressData.progress);
      }
      
      // 加载结果
      const resultsResponse = await fetch(`${API_BASE}/results/${taskName}`);
      const resultsData = await resultsResponse.json();
      if (resultsData.success) {
        setResults(resultsData.results);
      }
    } catch (error) {
      console.error('加载任务详情失败:', error);
    }
  };
  
  // 创建新任务
  const createTask = async () => {
    try {
      const response = await fetch(`${API_BASE}/create-task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTaskForm)
      });
      
      const data = await response.json();
      if (data.success) {
        setNewTaskForm({
          task_name: '',
          report_name: '',
          batch_size: 5,
          max_tokens_per_item: 4000
        });
        loadTasks();
        setCurrentTask(data.task_name);
        setActiveTab('items');
      } else {
        alert(`创建任务失败: ${data.message}`);
      }
    } catch (error) {
      console.error('创建任务失败:', error);
      alert('创建任务失败');
    }
  };
  
  // 添加项目
  const addItem = async () => {
    if (!currentTask) {
      alert('请先选择任务');
      return;
    }
    
    try {
      let metadata = {};
      try {
        metadata = JSON.parse(newItemForm.metadata);
      } catch {
        alert('元数据格式错误，请输入有效的JSON');
        return;
      }
      
      const response = await fetch(`${API_BASE}/add-item`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_name: currentTask,
          ...newItemForm,
          metadata
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setNewItemForm({
          item_id: '',
          item_type: 'survey_aspect',
          title: '',
          content_template: '',
          metadata: '{}',
          estimated_tokens: 0
        });
        loadTaskDetails(currentTask);
      } else {
        alert(`添加项目失败: ${data.message}`);
      }
    } catch (error) {
      console.error('添加项目失败:', error);
      alert('添加项目失败');
    }
  };
  
  // 开始流式生成
  const startStreamGeneration = () => {
    if (!currentTask) {
      alert('请先选择任务');
      return;
    }
    
    setIsGenerating(true);
    setStreamLogs([]);
    
    // 关闭现有连接
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    
    // 创建新的EventSource连接
    const eventSource = new EventSource(`${API_BASE}/generate-stream/${currentTask}`);
    eventSourceRef.current = eventSource;
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // 添加日志
        const timestamp = new Date().toLocaleTimeString();
        setStreamLogs(prev => [...prev, `[${timestamp}] ${data.type}: ${JSON.stringify(data.data)}`]);
        
        // 处理不同类型的事件
        switch (data.type) {
          case 'progress':
            setProgress(data.data);
            break;
          case 'item_completed':
            setResults(prev => [...prev, data.data]);
            break;
          case 'completed':
            setIsGenerating(false);
            loadTaskDetails(currentTask);
            break;
          case 'error':
            setIsGenerating(false);
            alert(`生成失败: ${data.data.error}`);
            break;
          case 'end':
            setIsGenerating(false);
            break;
        }
      } catch (error) {
        console.error('解析事件数据失败:', error);
      }
    };
    
    eventSource.onerror = (error) => {
      console.error('EventSource错误:', error);
      setIsGenerating(false);
      eventSource.close();
    };
  };
  
  // 停止生成
  const stopGeneration = async () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    
    if (currentTask) {
      try {
        await fetch(`${API_BASE}/cancel/${currentTask}`, { method: 'POST' });
      } catch (error) {
        console.error('取消生成失败:', error);
      }
    }
    
    setIsGenerating(false);
  };
  
  // 下载报告
  const downloadReport = async (taskName: string) => {
    try {
      const response = await fetch(`${API_BASE}/download/${taskName}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${taskName}_report.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('下载失败');
      }
    } catch (error) {
      console.error('下载失败:', error);
      alert('下载失败');
    }
  };
  
  // 删除任务
  const deleteTask = async (taskName: string) => {
    if (!confirm(`确定要删除任务 "${taskName}" 吗？`)) {
      return;
    }
    
    try {
      await fetch(`${API_BASE}/delete/${taskName}`, { method: 'DELETE' });
      loadTasks();
      if (currentTask === taskName) {
        setCurrentTask('');
        setItems([]);
        setProgress(null);
        setResults([]);
      }
    } catch (error) {
      console.error('删除任务失败:', error);
      alert('删除任务失败');
    }
  };
  
  // 快速创建DXA研究任务
  const quickCreateDXATask = async () => {
    const taskName = `dxa_research_${Date.now()}`;
    const reportName = `DXA影像预测全身健康状态研究_${new Date().toLocaleDateString()}`;
    
    try {
      const response = await fetch(`${API_BASE}/quick-create/dxa_research?task_name=${taskName}&report_name=${encodeURIComponent(reportName)}`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.success) {
        loadTasks();
        setCurrentTask(taskName);
        setActiveTab('items');
        setTimeout(() => loadTaskDetails(taskName), 500);
      } else {
        alert(`快速创建失败: ${data.message}`);
      }
    } catch (error) {
      console.error('快速创建失败:', error);
      alert('快速创建失败');
    }
  };
  
  // 组件挂载时加载数据
  useEffect(() => {
    loadTasks();
  }, []);
  
  // 当前任务变化时加载详情
  useEffect(() => {
    if (currentTask) {
      loadTaskDetails(currentTask);
    }
  }, [currentTask]);
  
  // 清理EventSource
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);
  
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">分批输出管理器</h1>
        <div className="flex gap-2">
          <Button onClick={quickCreateDXATask} variant="outline">
            <Plus className="w-4 h-4 mr-2" />
            快速创建DXA研究
          </Button>
          <Button onClick={loadTasks} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            刷新
          </Button>
        </div>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="tasks">任务管理</TabsTrigger>
          <TabsTrigger value="items">项目管理</TabsTrigger>
          <TabsTrigger value="generate">生成控制</TabsTrigger>
          <TabsTrigger value="results">结果查看</TabsTrigger>
          <TabsTrigger value="logs">生成日志</TabsTrigger>
        </TabsList>
        
        {/* 任务管理 */}
        <TabsContent value="tasks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>创建新任务</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">任务名称</label>
                  <Input
                    value={newTaskForm.task_name}
                    onChange={(e) => setNewTaskForm(prev => ({ ...prev, task_name: e.target.value }))}
                    placeholder="输入任务名称"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">报告名称</label>
                  <Input
                    value={newTaskForm.report_name}
                    onChange={(e) => setNewTaskForm(prev => ({ ...prev, report_name: e.target.value }))}
                    placeholder="输入报告名称"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">批次大小</label>
                  <Input
                    type="number"
                    value={newTaskForm.batch_size}
                    onChange={(e) => setNewTaskForm(prev => ({ ...prev, batch_size: parseInt(e.target.value) }))}
                    min="1"
                    max="20"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">每项最大Token数</label>
                  <Input
                    type="number"
                    value={newTaskForm.max_tokens_per_item}
                    onChange={(e) => setNewTaskForm(prev => ({ ...prev, max_tokens_per_item: parseInt(e.target.value) }))}
                    min="1000"
                    max="8000"
                  />
                </div>
              </div>
              <Button onClick={createTask} className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                创建任务
              </Button>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>任务列表</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {tasks.map((task) => (
                  <div
                    key={task.task_name}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      currentTask === task.task_name ? 'border-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setCurrentTask(task.task_name)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium">{task.task_name}</h3>
                        <p className="text-sm text-gray-600">{task.report_name}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant={task.status === 'completed' ? 'default' : 'secondary'}>
                            {task.status}
                          </Badge>
                          <span className="text-sm text-gray-500">
                            {task.completed_items}/{task.total_items} 项目
                          </span>
                          <span className="text-sm text-gray-500">
                            {task.progress_percentage.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {task.status === 'completed' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              downloadReport(task.task_name);
                            }}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteTask(task.task_name);
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    {task.progress_percentage > 0 && (
                      <Progress value={task.progress_percentage} className="mt-2" />
                    )}
                  </div>
                ))}
                {tasks.length === 0 && (
                  <p className="text-center text-gray-500 py-8">暂无任务</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* 项目管理 */}
        <TabsContent value="items" className="space-y-4">
          {currentTask ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>添加新项目</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">项目ID</label>
                      <Input
                        value={newItemForm.item_id}
                        onChange={(e) => setNewItemForm(prev => ({ ...prev, item_id: e.target.value }))}
                        placeholder="输入项目ID"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">项目类型</label>
                      <select
                        value={newItemForm.item_type}
                        onChange={(e) => setNewItemForm(prev => ({ ...prev, item_type: e.target.value }))}
                        className="w-full p-2 border rounded-md"
                        aria-label="选择项目类型"
                      >
                        <option value="survey_aspect">调研方面</option>
                        <option value="dxa_direction">DXA研究方向</option>
                        <option value="custom">自定义</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">项目标题</label>
                    <Input
                      value={newItemForm.title}
                      onChange={(e) => setNewItemForm(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="输入项目标题"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">内容模板</label>
                    <Textarea
                      value={newItemForm.content_template}
                      onChange={(e) => setNewItemForm(prev => ({ ...prev, content_template: e.target.value }))}
                      placeholder="输入内容模板"
                      rows={4}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">元数据 (JSON格式)</label>
                    <Textarea
                      value={newItemForm.metadata}
                      onChange={(e) => setNewItemForm(prev => ({ ...prev, metadata: e.target.value }))}
                      placeholder='{"key": "value"}'
                      rows={3}
                    />
                  </div>
                  <Button onClick={addItem} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    添加项目
                  </Button>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>项目列表 ({items.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {items.map((item) => (
                      <div key={item.id} className="p-3 border rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium">{item.title}</h4>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="outline">{item.type}</Badge>
                              <span className="text-sm text-gray-500">#{item.section_number}</span>
                              <span className="text-sm text-gray-500">{item.estimated_tokens} tokens</span>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <Edit className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                    {items.length === 0 && (
                      <p className="text-center text-gray-500 py-8">暂无项目</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-gray-500">请先选择一个任务</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        {/* 生成控制 */}
        <TabsContent value="generate" className="space-y-4">
          {currentTask ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>生成控制</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Button
                      onClick={startStreamGeneration}
                      disabled={isGenerating}
                      className="flex-1"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      开始生成
                    </Button>
                    <Button
                      onClick={stopGeneration}
                      disabled={!isGenerating}
                      variant="destructive"
                    >
                      <Square className="w-4 h-4 mr-2" />
                      停止生成
                    </Button>
                  </div>
                  
                  {progress && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>进度: {progress.completed_items}/{progress.total_items}</span>
                        <span>{progress.progress_percentage.toFixed(1)}%</span>
                      </div>
                      <Progress value={progress.progress_percentage} />
                      <div className="text-sm text-gray-600">
                        <p>状态: {progress.status}</p>
                        <p>当前批次: {progress.current_batch}/{progress.total_batches}</p>
                        {progress.current_item && <p>当前项目: {progress.current_item}</p>}
                        {progress.error_message && (
                          <p className="text-red-600">错误: {progress.error_message}</p>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-gray-500">请先选择一个任务</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        {/* 结果查看 */}
        <TabsContent value="results" className="space-y-4">
          {currentTask ? (
            <Card>
              <CardHeader>
                <CardTitle>生成结果 ({results.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {results.map((result) => (
                    <div key={result.item_id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{result.title}</h4>
                        <div className="flex items-center gap-2">
                          <Badge variant={result.status === 'completed' ? 'default' : 'destructive'}>
                            {result.status}
                          </Badge>
                          <span className="text-sm text-gray-500">{result.word_count} 字</span>
                        </div>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        生成时间: {new Date(result.generated_time).toLocaleString()}
                      </div>
                      <div className="bg-gray-50 p-3 rounded text-sm max-h-32 overflow-y-auto">
                        {result.content.substring(0, 200)}...
                      </div>
                      {result.error_message && (
                        <div className="text-red-600 text-sm mt-2">
                          错误: {result.error_message}
                        </div>
                      )}
                    </div>
                  ))}
                  {results.length === 0 && (
                    <p className="text-center text-gray-500 py-8">暂无结果</p>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-gray-500">请先选择一个任务</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        {/* 生成日志 */}
        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>生成日志</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-black text-green-400 p-4 rounded-lg h-96 overflow-y-auto font-mono text-sm">
                {streamLogs.map((log, index) => (
                  <div key={index} className="mb-1">
                    {log}
                  </div>
                ))}
                {streamLogs.length === 0 && (
                  <div className="text-gray-500">等待生成日志...</div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BatchManagerPage; 