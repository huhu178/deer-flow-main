// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { env } from "~/env";

export function resolveServiceURL(path: string): string {
  // 优先从 localStorage 获取后端地址
  if (typeof window !== "undefined") {
    const customBackendUrl = localStorage.getItem("backendUrl");
    if (customBackendUrl) {
      // 确保 URL 后面有斜杠，路径前面没有
      const baseUrl = customBackendUrl.endsWith('/') ? customBackendUrl.slice(0, -1) : customBackendUrl;
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
