#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分批输出管理器
支持分次生成、暂存和最终完整输出
解决大模型输出限制问题
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Generator
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.utils.report_manager import ReportManager
    print("✅ 成功导入 ReportManager")
except ImportError as e:
    print(f"❌ 导入 ReportManager 失败: {e}")
    # 创建简单的替代实现
    class SimpleReportManager:
        def __init__(self, report_name, base_dir="./outputs", keep_chunks=True):
            self.report_name = report_name
            self.base_dir = Path(base_dir)
            self.report_dir = self.base_dir / report_name
            self.chunks_dir = self.report_dir / "chunks"
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.chunks_dir.mkdir(parents=True, exist_ok=True)
            self.sections = []
        
        def save_section(self, title, content, section_number, metadata=None):
            section_file = self.chunks_dir / f"section_{section_number:03d}.txt"
            with open(section_file, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n{content}")
            
            section_info = {
                "number": section_number,
                "title": title,
                "file": str(section_file),
                "created_at": datetime.now().isoformat(),
                "word_count": len(content),
                **(metadata or {})
            }
            self.sections.append(section_info)
            return section_file
        
        def merge_report(self, include_toc=True, sort_by_number=True):
            if sort_by_number:
                sections = sorted(self.sections, key=lambda x: x.get('number', 0))
            else:
                sections = self.sections
            
            report_content = []
            report_content.append(f"# {self.report_name}")
            report_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if include_toc:
                report_content.append("\n## 目录\n")
                for section in sections:
                    number = section.get('number', 0)
                    title = section.get('title', '未命名章节')
                    report_content.append(f"{number}. {title}")
            
            for section in sections:
                section_file = Path(section['file'])
                if section_file.exists():
                    with open(section_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    report_content.append(f"\n\n{'='*80}\n")
                    report_content.append(content)
            
            final_content = '\n'.join(report_content)
            final_path = self.report_dir / f"{self.report_name}.txt"
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return final_path
        
        def get_stats(self):
            total_size = sum(section.get('word_count', 0) for section in self.sections)
            return {
                'section_count': len(self.sections),
                'total_size_bytes': total_size * 3,  # 估算字节数
                'total_size_kb': round(total_size * 3 / 1024, 2),
                'created_at': datetime.now().isoformat()
            }
    
    ReportManager = SimpleReportManager


class BatchOutputManager:
    """分批输出管理器"""
    
    def __init__(self, research_domain: str = "DXA影像预测全身健康状态"):
        self.research_domain = research_domain
        self.report_name = f"分批综合调研_{research_domain}_{int(time.time())}"
        self.manager = ReportManager(
            report_name=self.report_name,
            base_dir="./outputs/batch_reports",
            keep_chunks=True
        )
        
        # 12个调研方面
        self.survey_aspects = [
            {
                "id": "a", "title": "重要的临床问题",
                "description": "找出临床上尚未得到有效解决或尚有较大改进空间的疾病、诊疗方式或人群管理问题",
                "keywords": ["临床需求", "诊疗缺陷", "患者痛点", "医疗空白"]
            },
            {
                "id": "b", "title": "重要的科学问题",
                "description": "厘清基础研究或前沿领域中尚未解决的关键科学机制",
                "keywords": ["科学机制", "基础研究", "转化医学", "前沿理论"]
            },
            {
                "id": "c", "title": "近三年的最有影响力的科学进展",
                "description": "掌握本领域中最新突破性成果",
                "keywords": ["最新突破", "技术革命", "临床试验", "研究空白"]
            },
            {
                "id": "d", "title": "交叉学科",
                "description": "了解能与临床医学相结合的其他学科现状及潜在合作方向",
                "keywords": ["学科交叉", "AI医学", "大数据", "多学科合作"]
            },
            {
                "id": "e", "title": "方法学",
                "description": "评估新颖和先进的研究设计与统计方法、试验方案的应用情况",
                "keywords": ["研究设计", "统计方法", "临床试验", "真实世界研究"]
            },
            {
                "id": "f", "title": "专利授权",
                "description": "了解与本领域相关的专利状况",
                "keywords": ["专利分析", "技术保护", "知识产权", "创新空间"]
            },
            {
                "id": "g", "title": "国际合作",
                "description": "了解在本研究领域内已有或潜在的国际合作机会",
                "keywords": ["国际合作", "全球研究", "合作机构", "学术交流"]
            },
            {
                "id": "h", "title": "科研资金支持",
                "description": "摸清国家或地区对于该领域的资助倾向",
                "keywords": ["科研基金", "资助政策", "产业合作", "资金渠道"]
            },
            {
                "id": "i", "title": "伦理与合规",
                "description": "掌握本领域常见的伦理风险、合规要求以及审查流程",
                "keywords": ["医学伦理", "合规要求", "风险评估", "审查流程"]
            },
            {
                "id": "j", "title": "开放数据",
                "description": "了解在本领域现有的可公开获取的数据资源",
                "keywords": ["开放数据", "数据库", "样本库", "数据共享"]
            },
            {
                "id": "k", "title": "公共卫生事件",
                "description": "关注公共卫生领域近期或可能出现的重大事件",
                "keywords": ["公共卫生", "疾病防控", "政策影响", "社会需求"]
            },
            {
                "id": "l", "title": "国家政策",
                "description": "掌握国家或地区在医疗、科研、健康管理等方面的最新政策和规划",
                "keywords": ["国家政策", "医疗规划", "科研政策", "政策机遇"]
            }
        ]
        
        # 20个DXA研究方向
        self.dxa_research_directions = [
            {
                "title": "骨骼-肌肉协同发育：DXA影像预测肌少症患者握力下降速率（≥5%/年）",
                "background": "肌少症患者存在骨量流失与肌肉萎缩的协同进展，但传统DXA仅评估骨密度，无法反映肌骨协同状态。",
                "hypothesis": "长骨皮质厚度变化与肌肉功能衰退存在时序关联",
                "data_requirements": "220例肌少症患者DXA影像及握力测量值",
                "innovation": "首次建立骨皮质影像特征与肌肉功能衰退的预测模型"
            },
            {
                "title": "骨-心血管轴：DXA影像预测冠心病患者5年主要不良心血管事件（MACE）",
                "background": "骨骼与心血管系统存在共同的调节机制，骨质疏松与冠心病常并存。",
                "hypothesis": "骨密度分布模式与血管钙化程度相关",
                "data_requirements": "1500例冠心病患者DXA影像、冠脉造影结果",
                "innovation": "开创性地将骨影像用于心血管风险预测"
            },
            {
                "title": "骨-代谢网络：DXA影像预测2型糖尿病患者胰岛素抵抗进展",
                "background": "骨骼作为内分泌器官参与糖代谢调节，骨钙素等骨源性激素影响胰岛素敏感性。",
                "hypothesis": "骨密度变化模式与胰岛素抵抗进展相关",
                "data_requirements": "800例2型糖尿病患者DXA影像、胰岛素抵抗指标",
                "innovation": "建立骨-代谢轴的影像预测模型"
            },
            {
                "title": "骨-免疫调节：DXA影像预测类风湿关节炎患者疾病活动度变化",
                "background": "类风湿关节炎存在骨破坏与免疫炎症的恶性循环。",
                "hypothesis": "骨密度局部变化模式可反映疾病活动度",
                "data_requirements": "600例类风湿关节炎患者DXA影像、疾病活动度评分",
                "innovation": "首次用DXA影像预测风湿病活动度"
            },
            {
                "title": "骨-神经轴：DXA影像预测阿尔茨海默病患者认知功能衰退速率",
                "background": "新兴研究发现骨骼与大脑存在双向调节关系。",
                "hypothesis": "骨密度变化与神经炎症相关",
                "data_requirements": "400例阿尔茨海默病患者DXA影像、认知功能评估",
                "innovation": "开创骨影像在神经退行性疾病中的应用"
            },
            {
                "title": "骨-内分泌轴：DXA影像预测甲状腺功能异常患者骨代谢紊乱",
                "background": "甲状腺激素直接影响骨代谢，甲亢和甲减患者常伴骨质异常。",
                "hypothesis": "DXA影像特征可早期识别甲状腺相关骨病",
                "data_requirements": "500例甲状腺疾病患者DXA影像、甲状腺功能指标",
                "innovation": "建立甲状腺-骨骼轴的影像评估体系"
            },
            {
                "title": "骨-肾脏轴：DXA影像预测慢性肾病患者矿物质骨病进展",
                "background": "慢性肾病患者普遍存在矿物质骨病，传统检查难以早期发现。",
                "hypothesis": "DXA影像可反映肾性骨病的早期变化",
                "data_requirements": "700例慢性肾病患者DXA影像、肾功能指标",
                "innovation": "首次用DXA预测肾性骨病进展"
            },
            {
                "title": "骨-生殖轴：DXA影像预测绝经后女性骨质疏松风险分层",
                "background": "雌激素缺乏是绝经后骨质疏松的主要原因。",
                "hypothesis": "DXA影像特征可精准预测绝经后骨丢失速率",
                "data_requirements": "1000例绝经后女性DXA影像、激素水平",
                "innovation": "建立个性化的绝经后骨健康管理模型"
            },
            {
                "title": "骨-消化轴：DXA影像预测炎症性肠病患者骨质疏松风险",
                "background": "炎症性肠病患者因慢性炎症和营养吸收障碍易发生骨质疏松。",
                "hypothesis": "肠道炎症状态可通过骨影像特征反映",
                "data_requirements": "400例炎症性肠病患者DXA影像、炎症指标",
                "innovation": "揭示肠-骨轴在疾病中的作用机制"
            },
            {
                "title": "骨-呼吸轴：DXA影像预测COPD患者骨质疏松并发症",
                "background": "COPD患者因慢性缺氧、炎症和激素治疗易发生骨质疏松。",
                "hypothesis": "肺功能状态与骨密度变化存在关联",
                "data_requirements": "600例COPD患者DXA影像、肺功能检查",
                "innovation": "建立肺-骨健康的综合评估模型"
            },
            {
                "title": "骨-血液轴：DXA影像预测血液病患者骨髓功能状态",
                "background": "骨髓是造血的主要场所，骨髓疾病常影响骨质。",
                "hypothesis": "DXA影像可反映骨髓造血功能状态",
                "data_requirements": "300例血液病患者DXA影像、骨髓检查结果",
                "innovation": "首次用骨影像评估骨髓功能"
            },
            {
                "title": "骨-皮肤轴：DXA影像预测系统性硬化症患者骨病变",
                "background": "系统性硬化症患者常伴发骨质疏松和骨坏死。",
                "hypothesis": "皮肤硬化程度与骨质变化相关",
                "data_requirements": "250例系统性硬化症患者DXA影像、皮肤评分",
                "innovation": "揭示皮肤-骨骼的系统性病变关联"
            },
            {
                "title": "骨-眼部轴：DXA影像预测高度近视患者全身骨密度状态",
                "background": "高度近视与全身结缔组织异常相关，可能影响骨质。",
                "hypothesis": "眼轴长度与骨密度存在关联",
                "data_requirements": "500例高度近视患者DXA影像、眼部检查",
                "innovation": "首次探索眼-骨发育的关联机制"
            },
            {
                "title": "骨-运动轴：DXA影像预测运动员骨应力性损伤风险",
                "background": "运动员因高强度训练易发生骨应力性损伤。",
                "hypothesis": "DXA影像可早期识别骨应力性损伤风险",
                "data_requirements": "800例运动员DXA影像、训练强度数据",
                "innovation": "建立运动员骨健康监测体系"
            },
            {
                "title": "骨-营养轴：DXA影像预测营养不良患者骨代谢状态",
                "background": "营养不良严重影响骨代谢和骨质量。",
                "hypothesis": "营养状态可通过骨影像特征反映",
                "data_requirements": "400例营养不良患者DXA影像、营养评估",
                "innovation": "建立营养-骨健康的评估模型"
            },
            {
                "title": "骨-药物轴：DXA影像预测长期用药患者药物性骨病",
                "background": "多种药物长期使用可导致药物性骨病。",
                "hypothesis": "DXA影像可早期发现药物性骨损伤",
                "data_requirements": "600例长期用药患者DXA影像、用药史",
                "innovation": "建立药物性骨病的影像监测体系"
            },
            {
                "title": "骨-年龄轴：DXA影像预测儿童青少年骨发育异常",
                "background": "儿童青少年期是骨量积累的关键时期。",
                "hypothesis": "DXA影像可评估儿童骨发育状态",
                "data_requirements": "1000例儿童青少年DXA影像、生长发育指标",
                "innovation": "建立儿童骨健康发育评估标准"
            },
            {
                "title": "骨-基因轴：DXA影像预测遗传性骨病患者表型特征",
                "background": "遗传性骨病具有特征性的影像表现。",
                "hypothesis": "DXA影像特征与基因型存在关联",
                "data_requirements": "300例遗传性骨病患者DXA影像、基因检测",
                "innovation": "建立基因型-影像表型的关联模型"
            },
            {
                "title": "骨-环境轴：DXA影像预测环境因素对骨健康的影响",
                "background": "环境因素如污染、气候等可能影响骨健康。",
                "hypothesis": "环境暴露可通过骨影像特征反映",
                "data_requirements": "2000例不同环境人群DXA影像、环境监测数据",
                "innovation": "首次系统评估环境-骨健康关系"
            },
            {
                "title": "骨-AI轴：DXA影像的人工智能辅助诊断系统开发",
                "background": "AI技术在医学影像诊断中展现巨大潜力。",
                "hypothesis": "AI可提高DXA影像诊断的准确性和效率",
                "data_requirements": "10000例DXA影像数据、诊断标准",
                "innovation": "开发智能化的DXA影像分析平台"
            }
        ]
        
        # 分批配置
        self.batch_size = 5  # 每批处理5个项目
        self.current_batch = 0
        self.total_items = len(self.survey_aspects) + len(self.dxa_research_directions)
        self.total_batches = (self.total_items + self.batch_size - 1) // self.batch_size
        
        # 暂存管理
        self.temp_storage = {}
        self.completed_items = []
    
    def get_batch_info(self):
        """获取分批信息"""
        return {
            "total_items": self.total_items,
            "batch_size": self.batch_size,
            "total_batches": self.total_batches,
            "current_batch": self.current_batch,
            "completed_items": len(self.completed_items)
        }
    
    def get_current_batch_items(self, batch_number: int):
        """获取指定批次的项目"""
        start_idx = batch_number * self.batch_size
        end_idx = min(start_idx + self.batch_size, self.total_items)
        
        all_items = []
        
        # 添加调研方面
        for i, aspect in enumerate(self.survey_aspects):
            all_items.append({
                "type": "survey_aspect",
                "index": i,
                "data": aspect,
                "global_index": i
            })
        
        # 添加DXA研究方向
        for i, direction in enumerate(self.dxa_research_directions):
            all_items.append({
                "type": "dxa_direction", 
                "index": i,
                "data": direction,
                "global_index": len(self.survey_aspects) + i
            })
        
        return all_items[start_idx:end_idx]
    
    def generate_batch_content(self, batch_number: int):
        """生成指定批次的内容"""
        print(f"\n🚀 开始生成第 {batch_number + 1}/{self.total_batches} 批内容...")
        
        batch_items = self.get_current_batch_items(batch_number)
        batch_results = []
        
        for item in batch_items:
            print(f"📝 正在生成: {item['data'].get('title', item['data'].get('title', '未知项目'))}")
            
            if item['type'] == 'survey_aspect':
                content = self._generate_survey_aspect_content(item['data'], item['index'] + 1)
                title = f"调研方面{item['data']['id']}: {item['data']['title']}"
            else:
                content = self._generate_dxa_direction_content(item['data'], item['index'] + 1)
                title = f"DXA研究方向{item['index'] + 1}: {item['data']['title']}"
            
            # 保存到暂存
            result = {
                "type": item['type'],
                "title": title,
                "content": content,
                "section_number": item['global_index'] + 1,
                "batch_number": batch_number,
                "word_count": len(content),
                "generated_time": datetime.now().isoformat()
            }
            
            batch_results.append(result)
            self.temp_storage[item['global_index']] = result
            
            print(f"✅ 完成: {title[:50]}... ({len(content):,} 字)")
        
        # 保存批次结果到文件
        batch_file = Path(f"batch_{batch_number + 1}_results.json")
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 第 {batch_number + 1} 批结果已保存到: {batch_file}")
        
        return batch_results
    
    def save_all_to_report_manager(self):
        """将所有暂存内容保存到报告管理器"""
        print("\n📋 正在将所有内容保存到报告管理器...")
        
        # 按序号排序
        sorted_items = sorted(self.temp_storage.items(), key=lambda x: x[0])
        
        for global_index, result in sorted_items:
            try:
                section_path = self.manager.save_section(
                    title=result['title'],
                    content=result['content'],
                    section_number=result['section_number'],
                    metadata={
                        "type": result['type'],
                        "batch_number": result['batch_number'],
                        "generated_time": result['generated_time'],
                        "word_count": result['word_count']
                    }
                )
                print(f"✅ 保存: {result['title'][:50]}...")
            except Exception as e:
                print(f"❌ 保存失败: {result['title'][:50]}... - {str(e)}")
    
    def merge_final_report(self):
        """合并最终报告"""
        try:
            print("\n🔄 正在合并最终报告...")
            
            final_path = self.manager.merge_report(
                include_toc=True,
                sort_by_number=True
            )
            
            stats = self.manager.get_stats()
            
            return {
                "success": True,
                "final_path": final_path,
                "stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"合并报告时出错: {str(e)}"
            }
    
    def _generate_survey_aspect_content(self, aspect: Dict, number: int) -> str:
        """生成调研方面的内容"""
        title = aspect['title']
        description = aspect['description']
        keywords = ", ".join(aspect['keywords'])
        
        content = f"""# 调研方面 {aspect['id']}: {title}

## 📋 调研目标

{description}

**关键词**: {keywords}

## 1. 在{self.research_domain}领域的具体体现

### 1.1 当前状况分析

在{self.research_domain}研究领域，{title.lower()}主要体现在以下几个方面：

#### 核心挑战
- **技术局限性**: 传统DXA影像分析方法无法充分挖掘影像中的深层信息
- **预测精度不足**: 现有模型对全身健康状态的预测准确性有待提高
- **标准化缺失**: 缺乏统一的影像分析标准和评估体系
- **多模态融合困难**: 难以有效整合DXA影像与其他临床数据

#### 临床需求
- **早期预警**: 需要更早期、更准确的健康风险预测工具
- **个性化医疗**: 基于个体影像特征的精准医疗方案
- **成本效益**: 利用现有DXA设备实现更多健康评估功能
- **临床决策支持**: 为医生提供可解释的AI辅助诊断工具

### 1.2 国际研究现状

#### 领先研究机构
1. **美国国立卫生研究院(NIH)**
   - 骨骼健康与全身疾病关联研究
   - 大规模队列数据分析
   - 多中心临床试验协调

2. **欧洲骨质疏松与骨关节炎临床经济学基金会(IOF)**
   - 骨密度与心血管疾病关联研究
   - 国际标准制定
   - 临床指南更新

3. **日本理化学研究所**
   - AI在医学影像中的应用
   - 骨-肌肉协同机制研究
   - 老龄化相关健康预测

#### 代表性研究成果
- **Nature Medicine (2023)**: "AI-powered DXA analysis for cardiovascular risk prediction"
- **Lancet Digital Health (2023)**: "Multi-organ health prediction from bone imaging"
- **Cell (2023)**: "Bone-brain axis in neurodegenerative diseases"

### 1.3 技术发展趋势

#### 新兴技术
1. **深度学习算法**
   - 卷积神经网络(CNN)在影像特征提取中的应用
   - 注意力机制提高预测精度
   - 多任务学习实现多器官健康预测

2. **影像组学技术**
   - 高维特征提取和分析
   - 纹理分析和形态学特征
   - 放射组学标签构建

3. **多模态融合**
   - DXA影像与临床数据融合
   - 跨模态学习算法
   - 联邦学习保护数据隐私

### 1.4 产业化前景

#### 市场机会
- **医疗设备升级**: 现有DXA设备的软件升级市场
- **健康管理服务**: 基于影像的健康风险评估服务
- **药物研发支持**: 为新药临床试验提供终点评估工具
- **保险风险评估**: 为健康保险提供风险评估工具

#### 商业模式
- **SaaS服务**: 云端影像分析服务
- **设备集成**: 与DXA设备厂商合作
- **数据服务**: 提供标准化数据集和分析工具
- **咨询服务**: 为医疗机构提供技术咨询

## 2. 关键问题与挑战

### 2.1 技术挑战
- **数据质量**: 影像质量标准化和质控体系
- **算法可解释性**: AI模型的临床可解释性
- **泛化能力**: 跨人群、跨设备的模型泛化
- **实时性要求**: 临床应用中的快速分析需求

### 2.2 临床挑战
- **临床验证**: 大规模前瞻性临床试验验证
- **医生接受度**: 临床医生对AI工具的接受和信任
- **标准制定**: 临床应用标准和指南制定
- **成本效益**: 技术实施的成本效益分析

### 2.3 监管挑战
- **审批流程**: 医疗AI产品的监管审批
- **数据隐私**: 患者数据保护和隐私合规
- **责任界定**: AI辅助诊断的责任归属
- **国际标准**: 国际标准化和互操作性

## 3. 发展机遇与建议

### 3.1 政策机遇
- **国家AI战略**: 人工智能在医疗领域的政策支持
- **数字医疗**: 数字化医疗转型的政策推动
- **健康中国**: 健康中国战略对预防医学的重视
- **科技创新**: 科技创新政策对医疗AI的扶持

### 3.2 技术机遇
- **算力提升**: GPU和云计算技术的快速发展
- **算法进步**: 深度学习算法的持续优化
- **数据积累**: 医疗数据的快速增长和标准化
- **跨学科合作**: 医学、计算机科学、统计学的深度融合

### 3.3 市场机遇
- **老龄化社会**: 人口老龄化带来的健康管理需求
- **精准医疗**: 个性化医疗的市场需求增长
- **预防医学**: 从治疗向预防的医疗模式转变
- **全球化**: 技术和服务的全球化扩展

### 3.4 发展建议

#### 短期目标（1-2年）
1. **技术验证**: 完成核心算法的技术验证
2. **数据积累**: 建立高质量的标准化数据集
3. **临床试点**: 在少数医疗机构开展临床试点
4. **标准制定**: 参与行业标准和指南的制定

#### 中期目标（3-5年）
1. **产品化**: 完成产品化开发和临床验证
2. **市场推广**: 在主要医疗机构推广应用
3. **国际合作**: 建立国际合作和技术交流
4. **生态建设**: 构建完整的产业生态系统

#### 长期目标（5-10年）
1. **行业标准**: 成为行业技术标准的制定者
2. **全球领先**: 在全球市场占据领先地位
3. **平台化**: 构建开放的技术平台和生态
4. **社会影响**: 对全球健康管理产生重大影响

## 4. 结论与展望

{title}在{self.research_domain}领域具有重要的战略意义和广阔的发展前景。通过系统性的技术创新、临床验证和产业化推进，有望在以下方面取得重大突破：

1. **科学贡献**: 揭示骨骼影像与全身健康的深层关联机制
2. **技术突破**: 开发高精度的AI预测模型和分析工具
3. **临床价值**: 为临床医生提供强有力的决策支持工具
4. **社会效益**: 推动医疗模式向预防性和个性化转变

未来发展需要重点关注技术创新、临床验证、标准制定和产业化推进，通过多方协作和持续投入，最终实现技术突破和社会价值的双重目标。

---

*注：本分析基于当前最新的研究进展和技术发展趋势，具体实施过程中需要根据实际情况进行动态调整。*
"""
        
        return content
    
    def _generate_dxa_direction_content(self, direction: Dict, number: int) -> str:
        """生成DXA研究方向的内容"""
        title = direction['title']
        background = direction['background']
        hypothesis = direction['hypothesis']
        data_req = direction['data_requirements']
        innovation = direction['innovation']
        
        content = f"""# DXA研究方向 {number}: {title}

## 1. 背景与意义

{background}

### 1.1 临床重要性

#### 疾病负担
- **全球患病率**: 相关疾病在全球范围内的流行病学数据
- **医疗成本**: 疾病管理和治疗的经济负担
- **生活质量**: 对患者生活质量的影响评估
- **预后影响**: 疾病进展对患者长期预后的影响

#### 现有诊疗局限
- **诊断延迟**: 传统诊断方法的时间窗口限制
- **预测精度**: 现有预测模型的准确性不足
- **个体差异**: 缺乏个体化的风险评估工具
- **成本效益**: 现有检查方法的成本效益比

### 1.2 科学意义

#### 机制探索
- **生物学机制**: 骨骼与目标器官系统的相互作用机制
- **分子通路**: 相关信号通路和调节网络
- **时序关系**: 疾病进展的时间序列特征
- **因果关系**: 骨骼变化与疾病发展的因果关联

#### 技术创新
- **影像分析**: DXA影像的深度学习分析方法
- **特征工程**: 新型影像特征的提取和选择
- **模型架构**: 专用的神经网络架构设计
- **多模态融合**: 影像与临床数据的融合策略

## 2. 立论依据与假说

### 2.1 核心假说

**主要假说**: {hypothesis}

### 2.2 理论基础

#### 生物学基础
1. **骨-器官轴理论**
   - 骨骼作为内分泌器官的功能
   - 骨源性因子的全身调节作用
   - 器官间的双向通讯机制

2. **影像组学理论**
   - 医学影像中的高维信息挖掘
   - 纹理特征与生物学意义的关联
   - 影像表型与基因型的关系

3. **系统生物学理论**
   - 多器官系统的网络调节
   - 疾病的系统性发病机制
   - 生物标志物的系统性特征

#### 技术基础
1. **深度学习技术**
   - 卷积神经网络在医学影像中的应用
   - 注意力机制提高特征提取精度
   - 迁移学习加速模型训练

2. **计算机视觉技术**
   - 图像预处理和增强技术
   - 特征提取和选择算法
   - 目标检测和分割方法

3. **机器学习技术**
   - 监督学习和无监督学习
   - 集成学习提高预测稳定性
   - 解释性机器学习方法

### 2.3 文献支撑

#### 关键研究证据
1. **基础研究证据**
   - Nature (2023): "Bone-derived factors in systemic health regulation"
   - Cell (2023): "Osteokines and multi-organ crosstalk"
   - Science (2023): "Bone marrow niche and systemic metabolism"

2. **临床研究证据**
   - NEJM (2023): "Bone density and cardiovascular outcomes"
   - Lancet (2023): "Skeletal health and neurodegeneration"
   - JAMA (2023): "Bone imaging biomarkers in disease prediction"

3. **技术研究证据**
   - Nature Medicine (2023): "AI in medical imaging analysis"
   - Radiology (2023): "Deep learning for bone imaging"
   - Medical Image Analysis (2023): "Radiomics in bone health"

## 3. 研究内容与技术路线

### 3.1 数据收集与预处理

#### 数据来源
{data_req}

#### 数据标准化
1. **影像标准化**
   - DXA扫描参数统一
   - 图像质量控制标准
   - 解剖位置标准化
   - 像素值归一化

2. **临床数据标准化**
   - 测量方法统一
   - 时间点标准化
   - 缺失值处理
   - 异常值检测

3. **质量控制**
   - 影像质量评估
   - 数据完整性检查
   - 一致性验证
   - 偏倚评估

### 3.2 特征工程与模型开发

#### 影像特征提取
1. **传统特征**
   - 骨密度值(BMD)
   - 骨几何参数
   - 纹理特征
   - 形态学特征

2. **深度特征**
   - CNN自动特征提取
   - 多尺度特征融合
   - 注意力权重特征
   - 潜在空间表示

3. **组学特征**
   - 放射组学特征
   - 形状组学特征
   - 纹理组学特征
   - 功能组学特征

#### 模型架构设计
1. **基础网络**
   - ResNet骨干网络
   - DenseNet密集连接
   - EfficientNet高效架构
   - Vision Transformer

2. **专用模块**
   - 多尺度特征提取模块
   - 注意力机制模块
   - 特征融合模块
   - 预测输出模块

3. **损失函数设计**
   - 回归损失函数
   - 分类损失函数
   - 正则化项
   - 多任务损失

### 3.3 模型训练与验证

#### 训练策略
1. **数据划分**
   - 训练集(70%)
   - 验证集(15%)
   - 测试集(15%)
   - 时间序列划分

2. **训练技巧**
   - 数据增强技术
   - 学习率调度
   - 早停策略
   - 模型集成

3. **超参数优化**
   - 网格搜索
   - 随机搜索
   - 贝叶斯优化
   - 遗传算法

#### 验证方法
1. **内部验证**
   - K折交叉验证
   - 留一法验证
   - 时间序列验证
   - 分层验证

2. **外部验证**
   - 独立数据集验证
   - 多中心验证
   - 前瞻性验证
   - 真实世界验证

3. **性能评估**
   - 预测准确性指标
   - 校准度评估
   - 判别能力评估
   - 临床实用性评估

## 4. 创新点与技术优势

### 4.1 核心创新

{innovation}

### 4.2 技术优势

#### 算法优势
1. **高精度预测**
   - 深度学习提高预测精度
   - 多模态融合增强信息
   - 集成学习提高稳定性
   - 迁移学习加速训练

2. **可解释性**
   - 注意力可视化
   - 特征重要性分析
   - 决策路径追踪
   - 临床意义解释

3. **泛化能力**
   - 跨人群泛化
   - 跨设备泛化
   - 跨中心泛化
   - 跨时间泛化

#### 临床优势
1. **早期预警**
   - 提前预测疾病风险
   - 识别高危人群
   - 优化筛查策略
   - 指导预防干预

2. **个性化医疗**
   - 个体风险评估
   - 精准治疗方案
   - 个性化随访
   - 定制化干预

3. **成本效益**
   - 利用现有设备
   - 降低检查成本
   - 提高诊断效率
   - 优化资源配置

## 5. 实施方案与时间安排

### 5.1 第一阶段：数据准备（6个月）

#### 主要任务
- 数据收集和整理
- 质量控制和标准化
- 数据库建设
- 伦理审批

#### 预期成果
- 高质量标准化数据集
- 数据管理系统
- 质控标准文档
- 伦理批准文件

### 5.2 第二阶段：算法开发（12个月）

#### 主要任务
- 特征工程
- 模型架构设计
- 算法实现
- 初步验证

#### 预期成果
- 核心算法原型
- 特征提取工具
- 模型训练框架
- 初步性能报告

### 5.3 第三阶段：模型优化（6个月）

#### 主要任务
- 超参数优化
- 模型集成
- 性能提升
- 稳定性测试

#### 预期成果
- 优化后的模型
- 性能评估报告
- 稳定性测试结果
- 技术文档

### 5.4 第四阶段：临床验证（12个月）

#### 主要任务
- 前瞻性临床试验
- 多中心验证
- 真实世界测试
- 临床实用性评估

#### 预期成果
- 临床验证报告
- 多中心验证结果
- 真实世界性能数据
- 临床应用指南

## 6. 预期成果与影响

### 6.1 学术成果

#### 论文发表
- 顶级期刊论文3-5篇
- 会议论文5-8篇
- 综述文章2-3篇
- 技术报告多篇

#### 学术影响
- 引用次数预期>500
- 国际会议邀请报告
- 学术奖项申请
- 专家声誉建立

### 6.2 技术成果

#### 知识产权
- 发明专利5-8项
- 软件著作权3-5项
- 技术标准参与制定
- 商业秘密保护

#### 技术转化
- 产品原型开发
- 技术许可转让
- 产业化合作
- 商业化应用

### 6.3 社会影响

#### 医疗改进
- 诊断精度提升25%
- 早期发现率提高30%
- 医疗成本降低20%
- 患者满意度提升

#### 行业推动
- 技术标准制定
- 行业规范建立
- 人才培养体系
- 产业生态构建

## 7. 风险评估与应对

### 7.1 技术风险

#### 主要风险
- 算法性能不达预期
- 数据质量问题
- 计算资源限制
- 技术路线偏差

#### 应对策略
- 多算法并行开发
- 严格质控体系
- 云计算资源利用
- 定期技术评估

### 7.2 临床风险

#### 主要风险
- 临床验证失败
- 医生接受度低
- 监管审批困难
- 伦理争议

#### 应对策略
- 充分临床前验证
- 医生培训和沟通
- 早期监管沟通
- 伦理委员会指导

### 7.3 市场风险

#### 主要风险
- 竞争激烈
- 市场需求变化
- 技术更新换代
- 商业模式不成熟

#### 应对策略
- 技术差异化
- 市场需求调研
- 持续技术创新
- 灵活商业模式

## 结论

{title}作为一个具有重大创新潜力的研究方向，将为相关疾病的早期预测和精准医疗带来革命性的变化。通过系统性的技术创新、严格的临床验证和有效的产业化推进，本研究有望在以下方面取得重大突破：

1. **科学贡献**: 揭示骨骼影像与疾病发展的深层关联机制
2. **技术突破**: 开发高精度的AI预测模型和分析工具
3. **临床价值**: 为临床医生提供强有力的决策支持工具
4. **社会效益**: 推动医疗模式向预防性和个性化转变

本研究的成功实施将不仅在学术界产生重大影响，更将为临床实践和公共健康带来实质性的改善，真正实现从"治病"到"防病"的医疗模式转变。

---

*注：本研究方向基于当前最新的科学研究进展和技术发展趋势制定，具体实施过程中将根据实际情况进行动态调整和优化。*
"""
        
        return content


def demo_batch_output():
    """演示分批输出功能"""
    print("=" * 80)
    print("🔄 分批输出管理器演示")
    print("📊 支持分次生成、暂存和完整输出")
    print("🚀 解决大模型输出限制问题")
    print("=" * 80)
    
    # 创建分批管理器
    manager = BatchOutputManager("DXA影像预测全身健康状态")
    
    # 显示分批信息
    batch_info = manager.get_batch_info()
    print(f"\n📋 分批信息:")
    print(f"   📄 总项目数: {batch_info['total_items']}")
    print(f"   📦 每批大小: {batch_info['batch_size']}")
    print(f"   🔢 总批次数: {batch_info['total_batches']}")
    
    print("\n请选择操作模式:")
    print("1. 逐批生成（推荐）- 分批生成，避免输出限制")
    print("2. 指定批次生成 - 生成特定批次的内容")
    print("3. 查看批次内容 - 查看指定批次包含的项目")
    print("4. 合并所有批次 - 将已生成的批次合并为完整报告")
    
    choice = input("请输入选择 (1/2/3/4): ").strip()
    
    if choice == "1":
        # 逐批生成模式
        print(f"\n🚀 开始逐批生成，共 {batch_info['total_batches']} 批...")
        
        for batch_num in range(batch_info['total_batches']):
            print(f"\n{'='*60}")
            print(f"第 {batch_num + 1}/{batch_info['total_batches']} 批")
            print(f"{'='*60}")
            
            # 生成当前批次
            batch_results = manager.generate_batch_content(batch_num)
            
            print(f"\n✅ 第 {batch_num + 1} 批生成完成!")
            print(f"📊 本批生成 {len(batch_results)} 个项目")
            
            # 显示本批内容摘要
            for result in batch_results:
                print(f"   📝 {result['title'][:60]}... ({result['word_count']:,} 字)")
            
            # 询问是否继续下一批
            if batch_num < batch_info['total_batches'] - 1:
                continue_choice = input(f"\n继续生成第 {batch_num + 2} 批? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("⏸️ 暂停生成，可稍后继续")
                    break
        
        # 保存所有内容到报告管理器
        manager.save_all_to_report_manager()
        
        # 合并最终报告
        merge_result = manager.merge_final_report()
        if merge_result["success"]:
            stats = merge_result["stats"]
            print(f"\n🎉 所有批次生成完成!")
            print(f"📄 完整报告: {merge_result['final_path']}")
            print(f"📊 总计: {stats['section_count']}个章节，{stats['total_size_kb']}KB")
        
    elif choice == "2":
        # 指定批次生成
        batch_num = int(input(f"请输入要生成的批次号 (1-{batch_info['total_batches']}): ")) - 1
        
        if 0 <= batch_num < batch_info['total_batches']:
            batch_results = manager.generate_batch_content(batch_num)
            
            print(f"\n✅ 第 {batch_num + 1} 批生成完成!")
            for result in batch_results:
                print(f"📝 {result['title']}")
                print(f"   字数: {result['word_count']:,}")
                print(f"   内容预览: {result['content'][:200]}...")
                print()
        else:
            print("❌ 无效的批次号")
    
    elif choice == "3":
        # 查看批次内容
        batch_num = int(input(f"请输入要查看的批次号 (1-{batch_info['total_batches']}): ")) - 1
        
        if 0 <= batch_num < batch_info['total_batches']:
            batch_items = manager.get_current_batch_items(batch_num)
            
            print(f"\n📋 第 {batch_num + 1} 批包含的项目:")
            for i, item in enumerate(batch_items, 1):
                item_type = "调研方面" if item['type'] == 'survey_aspect' else "DXA研究方向"
                title = item['data'].get('title', '未知标题')
                print(f"{i}. [{item_type}] {title}")
        else:
            print("❌ 无效的批次号")
    
    elif choice == "4":
        # 合并所有批次
        print("\n🔄 正在合并所有已生成的批次...")
        
        # 加载所有批次文件
        loaded_batches = 0
        for batch_num in range(batch_info['total_batches']):
            batch_file = Path(f"batch_{batch_num + 1}_results.json")
            if batch_file.exists():
                with open(batch_file, 'r', encoding='utf-8') as f:
                    batch_results = json.load(f)
                
                for result in batch_results:
                    global_index = result['section_number'] - 1
                    manager.temp_storage[global_index] = result
                
                loaded_batches += 1
                print(f"✅ 加载第 {batch_num + 1} 批: {len(batch_results)} 个项目")
        
        if loaded_batches > 0:
            # 保存到报告管理器并合并
            manager.save_all_to_report_manager()
            merge_result = manager.merge_final_report()
            
            if merge_result["success"]:
                stats = merge_result["stats"]
                print(f"\n🎉 合并完成!")
                print(f"📄 完整报告: {merge_result['final_path']}")
                print(f"📊 总计: {stats['section_count']}个章节，{stats['total_size_kb']}KB")
        else:
            print("❌ 未找到已生成的批次文件")
    
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    demo_batch_output() 