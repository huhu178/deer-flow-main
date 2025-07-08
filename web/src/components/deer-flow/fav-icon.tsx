// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { cn } from "~/lib/utils";

/**
 * 判断字符串是否是有效URL
 */
function isValidUrl(urlString: string): boolean {
  try {
    const url = new URL(urlString);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch (e) {
    return false;
  }
}

/**
 * 获取网站图标URL
 */
function getFaviconUrl(url: string): string {
  try {
    if (!isValidUrl(url)) {
      throw new Error("无效URL");
    }
    
    const urlObj = new URL(url);
    return urlObj.origin + "/favicon.ico";
  } catch (e) {
    // 返回默认图标
    console.warn("无法解析URL获取favicon:", url, e);
    return "https://perishablepress.com/wp/wp-content/images/2021/favicon-standard.png";
  }
}

export function FavIcon({
  className,
  url,
  title,
}: {
  className?: string;
  url: string;
  title?: string;
}) {
  // 获取favicon URL，包含错误处理
  const faviconUrl = getFaviconUrl(url);
  
  return (
    <img
      className={cn("bg-accent h-4 w-4 rounded-full shadow-sm", className)}
      width={16}
      height={16}
      src={faviconUrl}
      alt={title || "网站图标"}
      onError={(e) => {
        e.currentTarget.src =
          "https://perishablepress.com/wp/wp-content/images/2021/favicon-standard.png";
      }}
    />
  );
}
