import BatchReportViewer from '../chat/components/batch-report-viewer'

export default function BatchReportPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🏥 DXA研究报告分批生成系统
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            突破16k token输出限制，支持生成20个完整的颠覆性研究方向，
            每个方向包含详细的研究背景、技术路线、创新点等内容。
            实时展示生成进度，自动保存到本地文件。
          </p>
        </div>
        
        <BatchReportViewer
          onSectionGenerated={(section) => {
            console.log('新章节生成:', section.title)
          }}
          onComplete={(finalPath, stats) => {
            console.log('报告生成完成:', finalPath, stats)
          }}
          onError={(error) => {
            console.error('生成错误:', error)
          }}
        />
      </div>
    </div>
  )
} 