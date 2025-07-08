"use client";

// import { EnhancedReportRenderer } from "~/components/deer-flow/enhanced-report-renderer";

const REPORT_CONTENT_PLACEHOLDER = `# 报告标题

这是一些报告内容。由于渲染组件暂时不可用，这里只显示纯文本。`;

const ReportDemoPage = () => {
  return (
    <div className="bg-gray-50 min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">报告预览</h1>
        {/* <EnhancedReportRenderer content={reportContent} /> */}
        <div>报告渲染功能已暂时禁用以修复部署问题。</div>
        <div>{REPORT_CONTENT_PLACEHOLDER}</div>
      </div>
    </div>
  );
};

export default ReportDemoPage; 