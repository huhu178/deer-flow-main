"use client";

import { useState } from "react";
import { EnhancedReportRenderer } from "~/components/deer-flow/enhanced-report-renderer";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";

const sampleReport = `# 基于人工智能和影像组学的桡骨DXA影像预测全身健康状态研究报告

## 📊 执行摘要

### 研究背景
DXA（双能X射线吸收测定法）作为骨密度检测的金标准，其临床应用已超过30年。随着人工智能技术的飞速发展，将AI技术与DXA影像相结合，不仅能够提高骨质疏松症的诊断精度，更具备了预测全身健康状况的巨大潜力。

> **核心假设**：桡骨DXA影像包含丰富的骨微结构信息，通过深度学习技术可以挖掘出与全身健康状态相关的隐藏特征，实现从局部骨骼影像到全身健康预测的跨越。

### 主要发现
- **技术突破**：首次实现基于单一桡骨DXA影像的多器官健康状态预测
- **临床价值**：提前5-10年识别心血管疾病、糖尿病等重大疾病风险
- **经济效益**：大幅降低健康筛查成本，提高早期诊断效率

## 🔬 研究方法

### 数据集概况
- **样本规模**：N=10,000大型队列数据
- **影像数据**：基线桡骨DXA影像
- **生化指标**：丰富的常规生化检测结果
- **随访时间**：至少5年的全疾病和全死因随访
- **特殊说明**：缺乏特异性骨/内分泌生物标志物

### AI模型架构

\`\`\`python
# 深度学习模型示例
import tensorflow as tf
from tensorflow.keras import layers

def create_dxa_health_predictor():
    # 输入层：DXA影像
    input_image = layers.Input(shape=(512, 512, 1))
    
    # 卷积特征提取
    x = layers.Conv2D(64, 3, activation='relu')(input_image)
    x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(128, 3, activation='relu')(x)
    x = layers.GlobalAveragePooling2D()(x)
    
    # 多任务输出
    cardiovascular_risk = layers.Dense(1, activation='sigmoid', name='cv_risk')(x)
    diabetes_risk = layers.Dense(1, activation='sigmoid', name='dm_risk')(x)
    bone_health = layers.Dense(3, activation='softmax', name='bone_health')(x)
    
    model = tf.keras.Model(
        inputs=input_image,
        outputs=[cardiovascular_risk, diabetes_risk, bone_health]
    )
    
    return model
\`\`\`

## 📈 核心研究方向

### 1. 基于Vision Transformer的DXA影像特征提取

**研究目标**：开发专门针对DXA影像的Vision Transformer模型，实现更精准的骨微结构特征提取。

**技术路线**：
1. 构建DXA专用的图像预处理管道
2. 设计适应性注意力机制
3. 多尺度特征融合策略
4. 迁移学习优化

**预期成果**：
- 特征提取精度提升30%以上
- 模型推理速度优化至毫秒级
- 发表顶级期刊论文2-3篇

### 2. 多模态融合的健康状态预测系统

**创新点**：
- 🔥 **首创**：DXA影像 + 生化指标的深度融合模型
- 🚀 **突破**：跨模态注意力机制设计
- 💡 **优势**：预测精度比单模态提升40%

| 模态类型 | 数据维度 | 权重分配 | 贡献度 |
|---------|---------|---------|--------|
| DXA影像 | 512×512×1 | 0.6 | 60% |
| 生化指标 | 50维向量 | 0.3 | 30% |
| 临床信息 | 20维向量 | 0.1 | 10% |

### 3. 可解释AI在医学影像中的应用

**背景意义**：医学AI系统的可解释性是临床应用的关键要求。

**技术方案**：
- **Grad-CAM可视化**：生成影像关注热力图
- **SHAP值分析**：量化每个特征的贡献度
- **因果推理**：建立特征与疾病的因果关系

## 🎯 预期影响

### 科学贡献
1. **理论突破**：建立骨骼-全身健康的AI预测理论框架
2. **技术创新**：开发多项原创性深度学习算法
3. **临床转化**：推动精准医学在骨科领域的应用

### 社会效益
- **健康管理**：实现个性化健康风险评估
- **医疗资源**：优化医疗资源配置效率
- **公共卫生**：提升人群健康管理水平

## 📚 参考文献

1. Smith, J. et al. (2023). "Deep learning applications in DXA imaging: A comprehensive review." *Nature Medicine*, 29(4), 123-145.

2. Wang, L. et al. (2024). "Multi-modal fusion for health prediction using bone density images." *IEEE Transactions on Medical Imaging*, 43(2), 234-256.

3. Chen, M. et al. (2023). "Explainable AI in medical imaging: Current challenges and future directions." *The Lancet Digital Health*, 5(8), 456-478.

---

**报告生成时间**：2025年1月11日  
**版本**：v2.0  
**作者**：DeerFlow AI研究团队  
**联系方式**：research@deerflow.ai`;

const sampleMetadata = {
  title: '基于人工智能和影像组学的桡骨DXA影像预测全身健康状态研究报告',
  generatedAt: new Date().toISOString(),
  wordCount: 2847,
  readingTime: 6,
  sections: 12,
  author: 'DeerFlow AI研究团队',
  version: '2.0',
  tags: ['人工智能', 'DXA影像', '影像组学', '健康预测', '深度学习', '医学AI']
};

export default function ReportDemoPage() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'academic' | 'modern'>('modern');
  const [showMetadata, setShowMetadata] = useState(true);
  const [showTOC, setShowTOC] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 页面头部 */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🎨 增强报告渲染器演示
              </h1>
              <p className="text-gray-600 mt-2">
                体验全新的医学研究报告展示效果，支持多主题、目录导航、全屏阅读等功能
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              <Badge variant="secondary" className="text-sm">
                演示版本 v2.0
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* 控制面板 */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">🎛️ 渲染选项</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">主题：</span>
                <div className="flex gap-2">
                  {(['light', 'dark', 'academic', 'modern'] as const).map((t) => (
                    <Button
                      key={t}
                      variant={theme === t ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setTheme(t)}
                    >
                      {t === 'light' && '☀️ 明亮'}
                      {t === 'dark' && '🌙 深色'}
                      {t === 'academic' && '📚 学术'}
                      {t === 'modern' && '✨ 现代'}
                    </Button>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant={showMetadata ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setShowMetadata(!showMetadata)}
                >
                  📊 元数据
                </Button>
                <Button
                  variant={showTOC ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setShowTOC(!showTOC)}
                >
                  📑 目录
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 功能特性展示 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  🎨
                </div>
                <h3 className="font-semibold">多主题支持</h3>
              </div>
              <p className="text-sm text-gray-600">
                支持明亮、深色、学术、现代四种主题，适应不同阅读场景和用户偏好
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  📑
                </div>
                <h3 className="font-semibold">智能目录</h3>
              </div>
              <p className="text-sm text-gray-600">
                自动提取标题生成目录，支持快速跳转和阅读进度跟踪
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  🔧
                </div>
                <h3 className="font-semibold">丰富功能</h3>
              </div>
              <p className="text-sm text-gray-600">
                全屏阅读、打印导出、分享链接、进度跟踪等实用功能
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 报告渲染区域 */}
      <div className="max-w-7xl mx-auto px-4 pb-8">
        <Card className="overflow-hidden">
          <div className="h-[800px]">
            <EnhancedReportRenderer
              content={sampleReport}
              metadata={sampleMetadata}
              theme={theme}
              showMetadata={showMetadata}
              showTOC={showTOC}
              enableFullscreen={true}
              enablePrint={true}
              enableShare={true}
              className="h-full"
            />
          </div>
        </Card>
      </div>
    </div>
  );
} 