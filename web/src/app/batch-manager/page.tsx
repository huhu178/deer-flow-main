'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Square, 
  Download, 
  Plus, 
  Trash2, 
  RefreshCw,
  Eye,
  Edit
} from 'lucide-react';

import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Input } from '~/components/ui/input';
import { Progress } from '~/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import { Textarea } from '~/components/ui/textarea';

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
  metadata: Record<string, unknown>;
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
        await loadTasks();
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
        await loadTaskDetails(currentTask);
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
        const data = JSON.parse(event.data) as { type: string; data: unknown };
        
        // 添加日志
        const timestamp = new Date().toLocaleTimeString();
        setStreamLogs(prev => [...prev, `[${timestamp}] ${data.type}: ${JSON.stringify(data.data)}`]);
        
        // 处理不同类型的事件
        switch (data.type) {
          case 'progress':
            setProgress(data.data as BatchProgress);
            break;
          case 'result':
            setResults(prev => [...prev, data.data as BatchResult]);
            break;
          case 'error':
            setProgress(prev => prev ? { ...prev, error_message: data.data as string } : null);
            break;
          case 'complete':
            eventSource.close();
            setIsGenerating(false);
            break;
        }
      } catch (error) {
        console.error('处理流式数据失败:', error);
      }
    };
    
    eventSource.onerror = () => {
      setStreamLogs(prev => [...prev, '与服务器断开连接，尝试重新连接...']);
      setIsGenerating(false);
      // EventSource 会自动重连，这里只更新UI状态
    };
  };
  
  // 停止生成
  const stopGeneration = async () => {
    if (!currentTask) {
      alert('没有正在进行的任务');
      return;
    }
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    
    try {
      await fetch(`${API_BASE}/stop/${currentTask}`, { method: 'POST' });
      setIsGenerating(false);
      setStreamLogs(prev => [...prev, '手动停止任务。']);
    } catch (error) {
      console.error('停止任务失败:', error);
    }
  };
  
  // 下载报告
  const downloadReport = async (taskName: string) => {
    try {
      const response = await fetch(`${API_BASE}/download/${taskName}`);
      if (!response.ok) {
        throw new Error('报告下载失败');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${taskName}_report.md`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      console.error('下载报告失败:', error);
      alert('下载报告失败');
    }
  };

  // 删除任务
  const deleteTask = async (taskName: string) => {
    if (window.confirm(`确定要删除任务 "${taskName}" 吗？`)) {
      try {
        const response = await fetch(`${API_BASE}/delete/${taskName}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
          await loadTasks();
        } else {
          alert(`删除失败: ${data.message}`);
        }
      } catch (error) {
        console.error('删除任务失败:', error);
      }
    }
  };

  // 快速创建DXA任务
  const quickCreateDXATask = async () => {
    try {
      const response = await fetch(`${API_BASE}/quick-create-dxa`, { method: 'POST' });
      const data = await response.json();
      if (data.success) {
        await loadTasks();
        setCurrentTask(data.task_name);
        await loadTaskDetails(data.task_name);
        setActiveTab('items');
      } else {
        alert('快速创建失败');
      }
    } catch (error) {
      console.error('快速创建失败:', error);
    }
  };

  useEffect(() => {
    loadTasks().catch(console.error);
  }, []);
  
  useEffect(() => {
    if (currentTask) {
      loadTaskDetails(currentTask).catch(console.error);
    }
  }, [currentTask]);

  return (
    <div className="bg-gray-100 min-h-screen p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800">批量报告生成管理器</h1>
          <p className="text-gray-600 mt-2">创建、监控和管理您的批量报告生成任务。</p>
        </header>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="tasks">任务列表</TabsTrigger>
            <TabsTrigger value="items" disabled={!currentTask}>项目配置</TabsTrigger>
            <TabsTrigger value="generation" disabled={!currentTask}>生成与监控</TabsTrigger>
            <TabsTrigger value="results" disabled={!currentTask}>结果预览</TabsTrigger>
          </TabsList>

          <TabsContent value="tasks">
            <Card>
              <CardHeader>
                <CardTitle>创建新任务</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="任务名称 (例如 dxa_report_batch_01)"
                  value={newTaskForm.task_name}
                  onChange={e => setNewTaskForm({ ...newTaskForm, task_name: e.target.value })}
                />
                <Input
                  placeholder="报告名称 (例如 DXA骨密度分析报告)"
                  value={newTaskForm.report_name}
                  onChange={e => setNewTaskForm({ ...newTaskForm, report_name: e.target.value })}
                />
                <Button onClick={createTask}>创建任务</Button>
                <Button variant="secondary" onClick={quickCreateDXATask}>快速创建DXA任务</Button>
              </CardContent>
            </Card>
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>所有任务</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {tasks.map(task => (
                    <div key={task.task_name} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h3 className="font-bold">{task.task_name}</h3>
                        <p className="text-sm text-gray-500">{task.report_name}</p>
                        <Badge variant={task.status === '完成' ? 'default' : 'secondary'}>{task.status}</Badge>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="w-40">
                          <Progress value={task.progress_percentage} />
                          <span className="text-xs text-gray-500">{task.completed_items} / {task.total_items}</span>
                        </div>
                        <Button size="sm" onClick={() => { setCurrentTask(task.task_name); setActiveTab('items'); }}>查看</Button>
                        <Button size="sm" variant="destructive" onClick={() => deleteTask(task.task_name).catch(console.error)}>删除</Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="items">
            <Card>
              <CardHeader>
                <CardTitle>为任务 "{currentTask}" 添加项目</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="项目ID (唯一标识, 例如 patient_001)"
                  value={newItemForm.item_id}
                  onChange={e => setNewItemForm({ ...newItemForm, item_id: e.target.value })}
                />
                <Input
                  placeholder="项目标题"
                  value={newItemForm.title}
                  onChange={e => setNewItemForm({ ...newItemForm, title: e.target.value })}
                />
                <Textarea
                  placeholder="内容生成模板 (使用{key}引用元数据)"
                  value={newItemForm.content_template}
                  onChange={e => setNewItemForm({ ...newItemForm, content_template: e.target.value })}
                />
                <Textarea
                  placeholder="元数据 (JSON格式)"
                  value={newItemForm.metadata}
                  onChange={e => setNewItemForm({ ...newItemForm, metadata: e.target.value })}
                />
                <Button onClick={addItem}>添加项目</Button>
              </CardContent>
            </Card>
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>项目列表</CardTitle>
              </CardHeader>
              <CardContent>
                {items.map(item => (
                  <div key={item.id} className="p-2 border-b">
                    <p><strong>ID:</strong> {item.id}</p>
                    <p><strong>标题:</strong> {item.title}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="generation">
            <Card>
              <CardHeader>
                <CardTitle>任务 "{currentTask}" 生成与监控</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 mb-4">
                  <Button onClick={startStreamGeneration} disabled={isGenerating}>
                    <Play className="mr-2 h-4 w-4" /> 开始生成
                  </Button>
                  <Button onClick={stopGeneration} disabled={!isGenerating} variant="destructive">
                    <Square className="mr-2 h-4 w-4" /> 停止
                  </Button>
                  <Button onClick={() => loadTaskDetails(currentTask).catch(console.error)}>
                    <RefreshCw className="mr-2 h-4 w-4" /> 刷新状态
                  </Button>
                </div>
                {progress && (
                  <div className="space-y-2 mb-4 p-4 bg-gray-50 rounded-lg">
                    <p>状态: <Badge>{progress.status}</Badge></p>
                    <p>进度: {progress.completed_items} / {progress.total_items} (批次 {progress.current_batch}/{progress.total_batches})</p>
                    <Progress value={progress.progress_percentage} />
                    <p>当前处理: {progress.current_item ?? 'N/A'}</p>
                    {progress.error_message && <p className="text-red-500">错误: {progress.error_message}</p>}
                  </div>
                )}
                <div className="bg-black text-white font-mono text-sm p-4 rounded-lg h-80 overflow-y-auto">
                  {streamLogs.map((log, index) => (
                    <p key={index}>{log}</p>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results">
            <Card>
              <CardHeader>
                <CardTitle>任务 "{currentTask}" 生成结果</CardTitle>
                <Button onClick={() => downloadReport(currentTask).catch(console.error)}>
                  <Download className="mr-2 h-4 w-4" /> 下载完整报告
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                {results.map(result => (
                  <Card key={result.item_id}>
                    <CardHeader>
                      <CardTitle className="flex justify-between items-center">
                        <span>{result.title}</span>
                        <Badge variant={result.status === '成功' ? 'default' : 'destructive'}>{result.status}</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <pre className="bg-gray-100 p-2 rounded whitespace-pre-wrap">{result.content}</pre>
                      {result.error_message && <p className="text-red-500 mt-2">错误: {result.error_message}</p>}
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default BatchManagerPage; 