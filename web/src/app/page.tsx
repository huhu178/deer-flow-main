// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import Link from "next/link";
import Image from "next/image";
import { useMemo } from "react";

import { Jumbotron } from "./landing/components/jumbotron";
import { Ray } from "./landing/components/ray";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center">
      <Header />
      <main className="container flex flex-col items-center justify-center gap-16 md:gap-24 pt-8">
        <Jumbotron />
      </main>
      <Footer />
      <Ray />
    </div>
  );
}
function Header() {
  return (
    <header className="sticky top-0 left-0 z-40 w-full bg-indigo-800 px-6 py-4 text-white shadow-md">
      <div className="flex w-full items-center">
        <div className="mr-4 flex-shrink-0">
          <div
            className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-gray-100 p-1.5"
          >
            <Image
              src="/images/logo2.png"
              alt="平台Logo"
              width={56}
              height={56}
              className="object-contain"
            />
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 sm:gap-x-4">
          <span className="whitespace-nowrap text-3xl font-medium">
            国家健康医疗大数据研究院
          </span>
          <span className="hidden text-gray-300 sm:inline">|</span>
          <span className="whitespace-nowrap text-6xl font-semibold">
            医学研究设计与分析AI智能平台
          </span>
          <span className="hidden text-gray-300 md:inline">|</span>
          <span className="whitespace-nowrap text-2xl text-gray-200">
            AI Agent Platform for Medical Research Design and Analysis
          </span>
        </div>
      </div>
    </header>
  );
}

function Footer() {
  const year = useMemo(() => new Date().getFullYear(), []);
  return (
    <footer className="container mt-32 flex flex-col items-center justify-center">
      <hr className="from-border/0 via-border/70 to-border/0 m-0 h-px w-full border-none bg-gradient-to-r dark:via-gray-600/70" />
      <div className="text-muted-foreground container flex h-20 flex-col items-center justify-center text-sm">
      </div>
    
    </footer>
  );
}
