// 不再使用外部解析库
// import { parse } from "best-effort-json-parser";

/**
 * 修复未终止的字符串
 */
function fixUnterminatedStrings(jsonString: string): string {
  try {
    // 查找所有字符串开始位置
    const stringStarts: number[] = [];
    let inString = false;
    let escapeNext = false;
    
    for (let i = 0; i < jsonString.length; i++) {
      const char = jsonString[i];
      
      if (escapeNext) {
        escapeNext = false;
        continue;
      }
      
      if (char === '\\') {
        escapeNext = true;
        continue;
      }
      
      if (char === '"') {
        if (!inString) {
          stringStarts.push(i);
          inString = true;
        } else {
          inString = false;
        }
      }
    }
    
    // 如果有未终止的字符串，尝试修复
    if (inString && stringStarts.length > 0) {
      const lastStart = stringStarts[stringStarts.length - 1];
      if (lastStart !== undefined) {
        // 在字符串末尾添加引号
        let fixedString = jsonString;
        
        // 查找合适的位置添加引号
        let insertPos = jsonString.length;
        
        // 向后查找，找到合适的位置（避免在JSON结构中间插入）
        for (let i = jsonString.length - 1; i > lastStart; i--) {
          const char = jsonString[i];
          if (char === ',' || char === '}' || char === ']') {
            insertPos = i;
            break;
          }
        }
        
        // 插入引号
        fixedString = jsonString.slice(0, insertPos) + '"' + jsonString.slice(insertPos);
        return fixedString;
      }
    }
    
    return jsonString;
  } catch (e) {
    console.warn("修复未终止字符串时出错:", e);
    return jsonString;
  }
}

/**
 * 修复缺少冒号的问题
 */
function fixMissingColons(jsonString: string): string {
  // 修复属性名后缺少冒号的问题
  return jsonString.replace(/("[\w\s]+")(\s*)([^:])/g, '$1:$3');
}

/**
 * 处理中文响应和搜索结果
 */
function handleChineseResponse(text: string): any {
  try {
    // 检查是否包含搜索结果标识
    if (text.includes('"type"') && (text.includes('"page"') || text.includes('"image"'))) {
      // 尝试提取搜索结果数组
      const arrayMatch = text.match(/\[[\s\S]*\]/);
      if (arrayMatch) {
        return JSON.parse(arrayMatch[0]);
      }
      
      // 如果没有找到数组，尝试提取单个对象并包装成数组
      const objMatch = text.match(/{[\s\S]*}/);
      if (objMatch) {
        const obj = JSON.parse(objMatch[0]);
        return [obj];
      }
    }
  } catch (e) {
    console.error("搜索结果数组提取失败:", e);
  }
  
  return null;
}

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
  } catch (error) {
    // 初始解析失败，尝试修复
    try {
      // 1. 尝试移除尾随逗号 (最常见的问题)
      const fixedJson = json.replace(/,\s*([}\]])/g, "$1");

      // 2. 尝试处理未闭合的字符串 (例如, "content": "hello)
      // 这是一个更复杂的场景，这里只做一个简单的检查
      if (
        (fixedJson.match(/"/g) || []).length % 2 !== 0
      ) {
        // 如果引号数量是奇数，可能存在未闭合的字符串
        // 在这里可以添加更复杂的修复逻辑，但为了简单起见，我们直接返回
        console.warn("JSON parsing failed, likely due to an unterminated string.");
        return fallback;
      }
      
      return JSON.parse(fixedJson) as T;

    } catch (e) {
      console.warn(
        `Failed to parse JSON even after attempting fixes: ${
          (e as Error).message
        }`,
      );
      return fallback;
    }
  }
}
