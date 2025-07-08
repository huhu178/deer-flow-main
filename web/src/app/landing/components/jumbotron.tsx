// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { FlickeringGrid } from "~/components/magicui/flickering-grid";
import { Button } from "~/components/ui/button";

export function Jumbotron() {
  return (
    <section className="relative z-10 flex min-h-[calc(100vh-10rem)] w-full flex-col items-center justify-center py-12 md:py-20">
      <FlickeringGrid
        id="deer-hero-bg"
        className={`absolute inset-0 z-0 [mask-image:radial-gradient(800px_circle_at_center,white,transparent)]`}
        squareSize={4}
        gridGap={4}
        color="#BFDBFE"
        maxOpacity={0.1}
        flickerChance={0.05}
      />
      <FlickeringGrid
        id="aigenmed-text-hero"
        className="absolute inset-0 z-0 translate-y-[2vh] mask-[url(/images/aigenmed-mask.svg)] mask-size-[100vw] mask-center mask-no-repeat md:mask-size-[70vh] lg:mask-size-[60vh] xl:mask-size-[50vh]"
        squareSize={3}
        gridGap={4}
        color="#93C5FD"
        maxOpacity={0.4}
        flickerChance={0.07}
      />
      <div className="relative z-10 flex flex-col items-center justify-center gap-8 text-center">
        <h4 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-gray-50 sm:text-3xl md:text-3xl">
          您好，欢迎使用医学研究设计与分析AI智能平台......
        </h4>
        <p className="mt-4 text-lg text-gray-700 dark:text-gray-300 max-w-2xl text-center">
          探索深度研究的强大功能，获取全面洞察，助力您的决策与创新。
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Button className="text-lg px-8 py-6" size="lg" asChild>
            <Link href="/chat">
              开始研究 <ChevronRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
          <Button className="text-lg px-8 py-6 bg-blue-600 hover:bg-blue-700" size="lg" asChild>
            <Link href="/medical-statistics">
              医学统计分析 <ChevronRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
