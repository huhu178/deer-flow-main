// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { PythonOutlined } from "@ant-design/icons";
import { motion } from "framer-motion";
import { LRUCache } from "lru-cache";
import { BookOpenText, PencilRuler, Search } from "lucide-react";
import { useTheme } from "next-themes";
import { useMemo } from "react";
import SyntaxHighlighter from "react-syntax-highlighter";
import {
  docco,
  dark,
} from "react-syntax-highlighter/dist/esm/styles/hljs";

import { FavIcon } from "~/components/deer-flow/fav-icon";
import Image from "~/components/deer-flow/image";
import { LoadingAnimation } from "~/components/deer-flow/loading-animation";
import { Markdown } from "~/components/deer-flow/markdown";
import { RainbowText } from "~/components/deer-flow/rainbow-text";
import { Tooltip } from "~/components/deer-flow/tooltip";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { Skeleton } from "~/components/ui/skeleton";
import { findMCPTool } from "~/core/mcp";
import type { ToolCallRuntime } from "~/core/messages";
import { useMessage, useStore } from "~/core/store";
import { parseJSON } from "~/core/utils";
import { cn } from "~/lib/utils";

export function ResearchActivitiesBlock({
  className,
  researchId,
}: {
  className?: string;
  researchId: string;
}) {
  const activityIds = useStore((state) =>
    state.researchActivityIds.get(researchId),
  );
  const ongoing = useStore((state) => state.ongoingResearchId === researchId);

  if (!activityIds) {
    return null;
  }

  return (
    <>
      <ul className={cn("flex flex-col py-4", className)}>
        {activityIds.map(
          (activityId, i) =>
            i !== 0 && (
              <motion.li
                key={activityId}
                style={{ transition: "all 0.4s ease-out" }}
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.4,
                  ease: "easeOut",
                }}
              >
                <ActivityMessage messageId={activityId} />
                <ActivityListItem messageId={activityId} />
                {i !== activityIds.length - 1 && <hr className="my-8" />}
              </motion.li>
            ),
        )}
      </ul>
      {ongoing && <LoadingAnimation className="mx-4 my-12" />}
    </>
  );
}

function ActivityMessage({ messageId }: { messageId: string }) {
  const message = useMessage(messageId);
  if (message?.agent && message.content) {
    if (message.agent !== "reporter" && message.agent !== "planner") {
      return (
        <div className="px-4 py-2">
          <Markdown animate>{message.content}</Markdown>
        </div>
      );
    }
  }
  return null;
}

function ActivityListItem({ messageId }: { messageId: string }) {
  const message = useMessage(messageId);
  if (message) {
    if (!message.isStreaming && message.toolCalls?.length) {
      for (const toolCall of message.toolCalls) {
        if (toolCall.name === "web_search") {
          return <WebSearchToolCall key={toolCall.id} toolCall={toolCall} />;
        } else if (toolCall.name === "crawl_tool") {
          return <CrawlToolCall key={toolCall.id} toolCall={toolCall} />;
        } else if (toolCall.name === "python_repl_tool") {
          return <PythonToolCall key={toolCall.id} toolCall={toolCall} />;
        } else {
          return <MCPToolCall key={toolCall.id} toolCall={toolCall} />;
        }
      }
    }
  }
  return null;
}

const __pageCache = new LRUCache<string, string>({ max: 100 });
type SearchResult =
  | {
      type: "page";
      title: string;
      url: string;
      content: string;
    }
  | {
      type: "image";
      image_url: string;
      image_description: string;
      url?: string; // Add url to image type for consistency
    };

// Define a more specific type for the tool call result
type ToolCallResult = {
  result?: string | SearchResult[];
  // other properties of toolCall can be added here
};

const getSearchResults = (
  toolCall: ToolCallResult,
): SearchResult[] | undefined => {
  try {
    console.log("Processing search results:", toolCall);

    if (!toolCall?.result) {
      console.warn("Search result is empty or invalid");
      return [];
    }

    let results: SearchResult[] | undefined;
    if (typeof toolCall.result === "string") {
      console.log("Result is a string, trying to parse as JSON");
      try {
        results = parseJSON<SearchResult[]>(toolCall.result, []);
      } catch (error) {
        console.error("Failed to parse search result:", error);
        results = [];
      }
    } else {
      results = toolCall.result;
    }

    if (!Array.isArray(results)) {
      console.log("Result is not an array, attempting to convert");
      if (results && typeof results === "object") {
        const possibleKeys = ["results", "items", "data", "pages", "images"];
        for (const key of possibleKeys) {
          const potentialArray = (results as any)[key];
          if (Array.isArray(potentialArray)) {
            results = potentialArray;
            break;
          }
        }
        if (!Array.isArray(results)) {
          results = [results as SearchResult];
        }
      } else {
        results = [];
      }
    }

    if (Array.isArray(results)) {
      results = results.map((item: Partial<SearchResult>) => {
        const type = item.type ?? "page";

        if (type === 'page') {
          const pageItem = item as Partial<{ type: 'page', title: string, url: string, content: string }>;
          return {
            type: 'page',
            title: pageItem.title ?? pageItem.url ?? "Untitled Page",
            url: pageItem.url ?? "",
            content: pageItem.content ?? "",
          } as SearchResult;
        } else { // type === 'image'
          const imageItem = item as Partial<{ type: 'image', image_url: string, image_description: string }>;
          return {
            type: 'image',
            image_url: imageItem.image_url ?? "",
            image_description: imageItem.image_description ?? "Untitled Image",
            url: imageItem.image_url ?? "",
          } as SearchResult;
        }
      });
    }

    return results as SearchResult[];
  } catch (error) {
    console.error("An error occurred while processing search results:", error);
    return [];
  }
};

function WebSearchToolCall({ toolCall }: { toolCall: ToolCallRuntime }) {
  const searching = useMemo(() => {
    return !toolCall.result;
  }, [toolCall.result]);

  const searchResults = useMemo(() => {
    if (searching) return undefined;
    return getSearchResults(toolCall);
  }, [searching, toolCall]);

  const pageResults = useMemo(
    () => searchResults?.filter((result) => result.type === "page"),
    [searchResults],
  );

  const imageResults = useMemo(
    () => searchResults?.filter((result) => result.type === "image"),
    [searchResults],
  );

  return (
    <section className="mt-4 pl-4">
      <div className="font-medium italic">
        <RainbowText
          className="flex items-center"
          animated={searchResults === undefined}
        >
          <Search size={16} className={"mr-2"} />
          <span>Searching for&nbsp;</span>
          <span className="max-w-[500px] overflow-hidden text-ellipsis whitespace-nowrap">
            {(toolCall.args as { query: string }).query}
          </span>
        </RainbowText>
      </div>
      <div className="pr-4">
        {pageResults && (
          <ul className="mt-2 flex flex-wrap gap-4">
            {searching &&
              [...Array(6)].map((_, i) => (
                <li
                  key={`search-result-${i}`}
                  className="flex h-40 w-40 gap-2 rounded-md text-sm"
                >
                  <Skeleton
                    className="to-accent h-full w-full rounded-md bg-gradient-to-tl from-slate-400"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                </li>
              ))}
            {pageResults
              .filter((result) => result.type === "page")
              .map((searchResult, i) => (
                <motion.li
                  key={`search-result-${i}`}
                  className="text-muted-foreground bg-accent flex max-w-40 gap-2 rounded-md px-2 py-1 text-sm"
                  initial={{ opacity: 0, y: 10, scale: 0.66 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{
                    duration: 0.2,
                    delay: i * 0.1,
                    ease: "easeOut",
                  }}
                >
                  <FavIcon
                    className="mt-1"
                    url={searchResult.url}
                    title={searchResult.title}
                  />
                  <a href={searchResult.url} target="_blank" rel="noopener noreferrer">
                    {searchResult.title}
                  </a>
                </motion.li>
              ))}
            {imageResults && imageResults.length > 0 && (
              <div className="mt-8 flex flex-wrap gap-2">
                {imageResults.map((result) => (
                  <a key={result.image_url} href={result.image_url} target="_blank" rel="noreferrer">
                    <Image
                      className="h-[150px] w-auto rounded-lg object-contain"
                      imageClassName="object-contain"
                      src={result.image_url}
                      alt={result.image_description}
                    />
                  </a>
                ))}
              </div>
            )}
          </ul>
        )}
      </div>
    </section>
  );
}

function CrawlToolCall({ toolCall }: { toolCall: ToolCallRuntime }) {
  const url = useMemo(
    () => (toolCall.args as { url: string }).url,
    [toolCall.args],
  );
  const title = useMemo(() => __pageCache.get(url), [url]);
  return (
    <section className="mt-4 pl-4">
      <div>
        <RainbowText
          className="flex items-center text-base font-medium italic"
          animated={toolCall.result === undefined}
        >
          <BookOpenText size={16} className={"mr-2"} />
          <span>Reading</span>
        </RainbowText>
      </div>
      <ul className="mt-2 flex flex-wrap gap-4">
        <motion.li
          className="text-muted-foreground bg-accent flex h-40 w-40 gap-2 rounded-md px-2 py-1 text-sm"
          initial={{ opacity: 0, y: 10, scale: 0.66 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{
            duration: 0.2,
            ease: "easeOut",
          }}
        >
          <FavIcon className="mt-1" url={url} title={title ?? undefined} />
          <a
            className="h-full flex-grow overflow-hidden text-ellipsis whitespace-nowrap"
            href={url}
            target="_blank"
            rel="noopener noreferrer"
          >
            {title ?? url}
          </a>
        </motion.li>
      </ul>
    </section>
  );
}

function PythonToolCall({ toolCall }: { toolCall: ToolCallRuntime }) {
  const code = useMemo<string>(() => {
    return (toolCall.args as { code: string }).code;
  }, [toolCall.args]);
  const { resolvedTheme } = useTheme();
  return (
    <section className="mt-4 pl-4">
      <div className="flex items-center">
        <PythonOutlined className={"mr-2"} />
        <RainbowText
          className="text-base font-medium italic"
          animated={toolCall.result === undefined}
        >
          Running Python code
        </RainbowText>
      </div>
      <div>
        <div className="bg-accent mt-2 max-h-[400px] max-w-[calc(100%-120px)] overflow-y-auto rounded-md p-2 text-sm">
          <SyntaxHighlighter
            language="python"
            style={resolvedTheme === "dark" ? dark : docco}
            customStyle={{
              background: "transparent",
              border: "none",
              boxShadow: "none",
            }}
          >
            {typeof code === 'string' ? code.trim() : ''}
          </SyntaxHighlighter>
        </div>
      </div>
    </section>
  );
}

function MCPToolCall({ toolCall }: { toolCall: ToolCallRuntime }) {
  const tool = useMemo(() => findMCPTool(toolCall.name), [toolCall.name]);
  const { resolvedTheme } = useTheme();
  return (
    <section className="mt-4 pl-4">
      <div className="w-fit overflow-y-auto rounded-md py-0">
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="item-1">
            <AccordionTrigger>
              <Tooltip title={tool?.description ?? "Custom tool"}>
                <div className="flex items-center font-medium italic">
                  <PencilRuler size={16} className={"mr-2"} />
                  <RainbowText
                    className="pr-0.5 text-base font-medium italic"
                    animated={toolCall.result === undefined}
                  >
                    Running {toolCall.name ? `${toolCall.name}()` : "MCP tool"}
                  </RainbowText>
                </div>
              </Tooltip>
            </AccordionTrigger>
            <AccordionContent>
              {toolCall.result && (
                <div className="bg-accent max-h-[400px] max-w-[560px] overflow-y-auto rounded-md text-sm">
                  <SyntaxHighlighter
                    language="json"
                    style={resolvedTheme === "dark" ? dark : docco}
                    customStyle={{
                      background: "transparent",
                      border: "none",
                      boxShadow: "none",
                    }}
                  >
                    {toolCall.result.trim()}
                  </SyntaxHighlighter>
                </div>
              )}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </section>
  );
}
