"use client";

import { cn } from "@/lib/utils";
import { BorderBeam } from "@/components/magicui/border-beam";
import TextShimmer from "@/components/magicui/text-shimmer";
import { Button } from "@/components/ui/button";
import { ArrowRightIcon } from "@radix-ui/react-icons";
import { useInView } from "framer-motion";
import Link from 'next/link';
import { useRef } from "react";

export default function HeroSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  return (
    <section
      id="hero"
      className="relative mx-auto mt-32 max-w-[80rem] px-6 text-center md:px-8"
    >
      <div className="backdrop-filter-[12px] inline-flex h-7 items-center justify-between rounded-full border border-white/5 bg-white/10 px-3 text-xs text-white transition-all ease-in hover:cursor-pointer hover:bg-white/20 group gap-1 translate-y-[-1rem] animate-fade-in opacity-0 cursor-pointer">
        <Link href="/intro">
          <TextShimmer className="inline-flex items-center justify-center">
            <span>✨ Introducing generative AI for ecommerce</span>{" "}
            <ArrowRightIcon className="ml-1 size-3 transition-transform duration-300 ease-in-out group-hover:translate-x-0.5" />
          </TextShimmer>
        </Link>
      </div>
      <h1 className="bg-gradient-to-br from-white from-30% to-white/40 bg-clip-text py-6 text-5xl font-medium leading-none tracking-tighter text-transparent text-balance sm:text-6xl md:text-7xl lg:text-8xl translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:200ms]">
        Turn  
        <span
          className={cn(
            `inline animate-gradient bg-gradient-to-r from-[#03A9F4] to-[#20b2aa] bg-[length:var(--bg-size)_100%] bg-clip-text text-transparent`,
          )}
        >
        &nbsp;browsers
        </span> into <span
          className={cn(
            `inline animate-gradient bg-gradient-to-r from-[#03A9F4] to-[#20b2aa] bg-[length:var(--bg-size)_100%] bg-clip-text text-transparent`,
          )}
        >
        buyers
        </span> with 
        <br className="hidden md:block" /> AI-driven promotions.
      </h1>
      <p className="mb-12 text-lg tracking-tight text-gray-400 md:text-xl text-balance translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:400ms]">
        Analyze customer behavior on your site <strong>in real time</strong>, and show them
        <br className="hidden md:block" /> the perfect promotion that will make them convert.
      </p>
      <Link href="https://forms.gle/JeH1JRvaMFFAP75GA" target="_blank">
        <Button className="translate-y-[-1rem] animate-fade-in gap-1 rounded-lg text-black opacity-0 ease-in-out [--animation-delay:600ms]">
          <span>Join our beta </span>
          <ArrowRightIcon className="ml-1 size-4 transition-transform duration-300 ease-in-out group-hover:translate-x-1" />
        </Button>
      </Link>
      <div
        ref={ref}
        className="relative mt-[8rem] animate-fade-up opacity-0 [--animation-delay:400ms] [perspective:2000px] after:absolute after:inset-0 after:z-50 after:[background:linear-gradient(to_top,hsl(var(--background))_10%,transparent)]"
      >
        <div
          className={`rounded-xl border border-white/10 bg-white bg-opacity-[0.01] before:absolute before:bottom-1/2 before:left-0 before:top-0 before:h-full before:w-full before:opacity-0 before:[filter:blur(180px)] before:[background-image:linear-gradient(to_bottom,#20b2aa,#20b2aa,transparent_40%)] ${
            inView ? "before:animate-image-glow" : ""
          }`}
        >
          <BorderBeam
            size={200}
            duration={12}
            delay={11}
            colorFrom="#03A9F4"
            colorTo="#20b2aa"
          />

          <img
            src="/hero.png"
            alt="Hero Image"
            className="relative w-full h-full rounded-[inherit] object-contain"
          />
        </div>
      </div>
    </section>
  );
}
