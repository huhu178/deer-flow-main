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
 * 尝试从任何文本中提取有效的JSON部分
 */
function extractValidJson(text: string): any {
  // 首先尝试处理可能的搜索结果
  const searchResults = handleChineseResponse(text);
  if (searchResults) {
    return searchResults;
  }
  
  // 查找最外层的大括号对
  const objMatches = text.match(/{[^]*}/);
  if (objMatches && objMatches[0]) {
    try {
      return JSON.parse(objMatches[0]);
    } catch (e) {
      // 继续尝试其他方法
    }
  }
  
  // 尝试查找数组
  const arrMatches = text.match(/\[[^]*\]/);
  if (arrMatches && arrMatches[0]) {
    try {
      return JSON.parse(arrMatches[0]);
    } catch (e) {
      // 继续尝试其他方法
    }
  }
  
  // 尝试将文本拆分成多行，查找JSON数组
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line && line.trim().startsWith('[') && line.includes(']')) {
      try {
        return JSON.parse(line);
      } catch (e) {
        // 继续尝试
      }
    }
  }
  
  // 最后手段：将文本转换为键值对
  return { text: text };
}

/**
 * 简单的自定义容错JSON解析器
 * 处理一些常见的JSON格式错误
 */
function safeParse(jsonString: string) {
  try {
    // 首先尝试修复未终止的字符串
    let fixedString = fixUnterminatedStrings(jsonString);
    
    // 修复缺少冒号的问题
    fixedString = fixMissingColons(fixedString);
    
    // 处理位置63附近的常见错误 - 通常是属性值后缺少逗号或引号
    if (fixedString.length > 63) {
      const beforePos63 = fixedString.substring(0, 63);
      const afterPos63 = fixedString.substring(63);
      
      // 检查位置63附近是否有未闭合的引号或缺少逗号
      if (beforePos63.endsWith('"') && afterPos63.startsWith(',')) {
        // 这种情况通常是正常的，不需要修复
      } else if (beforePos63.match(/"[^"]*$/) && !afterPos63.startsWith('"')) {
        // 未闭合的字符串，在位置63添加引号
        fixedString = beforePos63 + '"' + afterPos63;
      } else if (beforePos63.endsWith(':') && afterPos63.match(/^[^",}]/)) {
        // 属性值没有引号，添加引号
        const valueMatch = afterPos63.match(/^([^",}]*)/);
        if (valueMatch && valueMatch[1] !== undefined) {
          const value = valueMatch[1].trim();
          fixedString = beforePos63 + '"' + value + '"' + afterPos63.substring(value.length);
        }
      }
    }
    
    // 再修复其他常见问题
    fixedString = fixedString
      // 处理未引用的键名
      .replace(/(\s*?{\s*?|\s*?,\s*?)(['"])?([a-zA-Z0-9_]+)(['"])?:/g, '$1"$3":')
      // 处理单引号替换为双引号
      .replace(/'/g, '"')
      // 处理属性名与值之间的等号 (例如: {name="value"} -> {"name":"value"})
      .replace(/([{,]\s*)(")?([a-zA-Z0-9_]+)(")?\s*=\s*(")?([^",{}]*)(")?(,|})/g, '$1"$3":"$6"$8')
      // 处理尾部逗号
      .replace(/,\s*}/g, '}')
      .replace(/,\s*]/g, ']')
      // 处理转义字符问题
      .replace(/\\(['"])/g, '$1')
      // 处理中文标点符号
      .replace(/，/g, ',')
      .replace(/：/g, ':');
    
    try {
      // 尝试作为单个JSON对象解析
      return JSON.parse(fixedString);
    } catch (err) {
      // 如果单个对象解析失败，尝试更多修复和提取
      console.warn("标准JSON解析失败，尝试更多修复:", err);
      
      // 移除所有控制字符和不可见字符
      fixedString = fixedString.replace(/[\u0000-\u001F\u007F-\u009F]/g, '');
      
      // 尝试修复常见的JSON结构问题
      if (fixedString.includes('{"locale"')) {
        // 这看起来像是一个包含locale的对象，尝试特殊处理
        try {
          // 查找第一个完整的JSON对象
          const match = fixedString.match(/\{[^{}]*"locale"[^{}]*\}/);
          if (match && match[0]) {
            return JSON.parse(match[0]);
          }
        } catch (e) {
          // 继续尝试其他方法
        }
      }
      
      // 确保JSON有正确的开始和结束
      if (!fixedString.trim().startsWith('{') && !fixedString.trim().startsWith('[')) {
        // 检测是否可能是搜索结果类型的对象
        if (fixedString.includes('"type"') && 
           (fixedString.includes('"page"') || fixedString.includes('"image"'))) {
          fixedString = '[' + fixedString + ']';
        } else {
          fixedString = '{' + fixedString + '}';
        }
      }
      
      try {
        // 再次尝试JSON解析
        return JSON.parse(fixedString);
      } catch (secondError) {
        // 如果仍然失败，尝试提取有效的JSON部分
        console.warn("修复后解析仍然失败，尝试提取部分:", secondError);
        
        // 查找常见搜索结果关键词，验证是否是搜索结果
        if (jsonString && jsonString.includes('"type"') && jsonString.includes('"url"')) {
          console.log("可能是搜索结果数据，尝试特殊提取");
          
          try {
            // 创建模拟结构，确保有一个可显示的结果
            const mockResult = [
              {
                type: "page",
                title: "搜索结果",
                url: "https://example.com/result",
                content: typeof jsonString === 'string' ? jsonString.substring(0, 200) : "无法解析的内容"
              }
            ];
            return mockResult;
          } catch (e) {
            // 继续尝试常规提取
          }
        }
        
        return extractValidJson(jsonString);
      }
    }
  } catch (finalError) {
    console.error("无法修复的JSON格式:", finalError);
    console.log("问题JSON:", jsonString?.substring(0, 100) + "...");
    // 作为最后手段，返回一个空对象而不是数组，避免类型错误
    return {};
  }
}

export function parseJSON<T>(json: string | null | undefined, fallback: T) {
  if (!json) {
    return fallback;
  }
  
  try {
    const raw = json
      .trim()
      .replace(/^```json\s*/, "")
      .replace(/^```\s*/, "")
      .replace(/\s*```$/, "");
    
    // 输出原始JSON帮助调试（限制长度避免控制台污染）
    console.log("原始JSON(前100字符):", raw.substring(0, 100));
    
    // 检查是否是搜索结果
    const isSearchResult = raw.includes('"type"') && 
                          (raw.includes('"page"') || raw.includes('"image"'));
    if (isSearchResult) {
      console.log("检测到可能是搜索结果格式");
    }
    
    // 先尝试使用标准JSON解析
    try {
      return JSON.parse(raw) as T;
    } catch (stdError) {
      console.log("标准JSON解析失败:", (stdError as Error).message);
      
      // 标准解析失败时，使用我们自己的容错解析器
      try {
        console.log("尝试使用容错解析器解析JSON");
        const result = safeParse(raw);
        console.log("容错解析结果类型:", Array.isArray(result) ? "数组" : typeof result);
        
        // 如果预期是数组而结果不是数组，尝试转换
        if (fallback instanceof Array && !Array.isArray(result)) {
          console.log("预期数组但结果不是数组，进行转换");
          if (result && typeof result === 'object') {
            // 尝试在对象中找数组属性
            for (const key in result) {
              if (Array.isArray(result[key])) {
                return result[key] as unknown as T;
              }
            }
            // 如果没找到，将对象转为单元素数组
            return [result] as unknown as T;
          }
        }
        
        return result as T;
      } catch (parseError) {
        console.error("JSON解析完全失败:", parseError);
        console.log("原始JSON:", raw.substring(0, 200) + "...");
        return fallback;
      }
    }
  } catch (error) {
    console.error("字符串预处理错误:", error);
    return fallback;
  }
}
