// 不再使用外部解析库
// import { parse } from "best-effort-json-parser";

/**
 * A best-effort JSON parser that tries to parse a JSON string and returns a
 * fallback value if parsing fails.
 */
export function parseJSON<T>(json: string | null | undefined, fallback: T) {
  if (!json) {
    return fallback;
  }
  try {
    return JSON.parse(json) as T;
  } catch {
    // 初始解析失败，尝试修复
    try {
      // 1. 尝试移除尾随逗号 (最常见的问题)
      const fixedJson = json.replace(/,\s*([}\]])/g, "$1");

      // 2. 尝试处理未闭合的字符串 (例如, "content": "hello)
      // 这是一个更复杂的场景，这里只做一个简单的检查
      if (
        (fixedJson.match(/"/g) ?? []).length % 2 !== 0
      ) {
        // 如果引号数量是奇数，可能存在未闭合的字符串
        // 在这里可以添加更复杂的修复逻辑，但为了简单起见，我们直接返回
        console.warn("JSON parsing failed, likely due to an unterminated string.");
        return fallback;
      }
      
      return JSON.parse(fixedJson) as T;

    } catch (finalError) {
      console.warn(
        `Failed to parse JSON even after attempting fixes: ${
          (finalError as Error).message
        }`,
      );
      return fallback;
    }
  }
}
