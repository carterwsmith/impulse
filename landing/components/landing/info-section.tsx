"use client";

import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { CheckIcon } from "@radix-ui/react-icons";
import { motion } from "framer-motion";
import { Loader } from "lucide-react";
import { useState } from "react";

export default function InfoSection() {
  return (
    <section id="info">
      <div className="mx-auto flex max-w-screen-xl flex-col gap-8 px-4 md:px-8">
        <div className="mx-auto max-w-5xl text-center">
          {/* <h4 className="text-xl font-bold tracking-tight text-black dark:text-white">
            Info
          </h4> */}

          <h2 className="text-5xl font-bold tracking-tight text-black dark:text-white sm:text-6xl">
            product info goes here
          </h2>

          <p className="mt-6 text-xl leading-8 text-black/80 dark:text-white">
            Choose an <strong>affordable plan</strong> that&apos;s packed with
            the best features for engaging your audience, creating customer
            loyalty, and driving sales.
          </p>
        </div>
      </div>
    </section>
  );
}
