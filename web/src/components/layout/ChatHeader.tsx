import Image from "next/image";
import Link from "next/link"; // 如果 logo 需要链接到首页

/**
 * @description 聊天页面的 Header 组件，仿照 src1 的样式。
 * @returns {JSX.Element}
 */
export function ChatHeader() {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-white px-4 py-3 shadow-sm dark:bg-gray-900 dark:border-gray-700"> {/* 浅色背景，深色模式下背景 */}
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {/* Logo */}
          <Link href="/" passHref> {/* 可选：让 logo 链接到首页 */}
            <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full bg-gray-100 p-1 dark:bg-gray-800">
              <Image
                src="/logo2.png" // Changed to /logo2.png assuming this is the AigenMed file
                alt="平台Logo" // Consistent alt text
                width={40}
                height={40}
                className="object-contain"
              />
            </div>
          </Link>

          {/* 标题组 - 修改后 */}
          <div className="flex items-center"> 
            <h1 className="text-lg font-semibold text-gray-800 dark:text-gray-100 whitespace-nowrap"> {/* 调整字体大小为 text-lg */}
              国家健康医疗大数据研究院
            </h1>
            {/* 副标题和分隔符已移除 */}
          </div>
        </div>

        {/* 右侧内容，例如用户菜单、设置按钮等，可以根据需要添加 */}
        {/* <div className="flex items-center space-x-3">
          <ThemeToggle />
        </div> */}
      </div>
    </header>
  );
} 