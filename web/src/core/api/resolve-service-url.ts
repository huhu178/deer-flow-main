// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { env } from "~/env";

export function resolveServiceURL(path: string): string {
  // 优先从 localStorage 获取后端地址
  if (typeof window !== "undefined") {
    const customBackendUrl = localStorage.getItem("backendUrl");
    if (customBackendUrl) {
      // 确保基础 URL 后面有 /api，并且没有多余的斜杠
      let baseUrl = customBackendUrl.endsWith('/') ? customBackendUrl.slice(0, -1) : customBackendUrl;
      if (!baseUrl.endsWith('/api')) {
        baseUrl += '/api';
      }
      
      const cleanPath = path.startsWith('/') ? path.slice(1) : path;
      return `${baseUrl}/${cleanPath}`;
    }
  }

  // 否则，使用环境变量或默认值
  let BASE_URL = env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/";

  if (!BASE_URL.endsWith("/")) {
    BASE_URL += "/";
  }

  const cleanPath = path.startsWith('/') ? path.slice(1) : path;

  return `${BASE_URL}${cleanPath}`;
}
