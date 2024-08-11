"use client";
import React from "react";
import { motion } from "framer-motion";
import { LampContainer } from "./ui/lamp";

export function HomeMain() {
  return (
    <>
      <div className="flex items-center justify-center min-h-screen">
        <LampContainer>
          <motion.p
            initial={{ opacity: 0.5, y: 100 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{
              delay: 0.1,
              duration: 0.8,
              ease: "easeInOut",
            }}
            className="mt-8 bg-gradient-to-br from-slate-300 to-slate-500 py-4 bg-clip-text text-center text-4xl font-medium tracking-tight text-transparent md:text-7xl"
          >
            Adobe Gensolve
          </motion.p>
          <motion.div>
            <motion.p
              initial={{ opacity: 0, y: 100 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{
                delay: 0.2,
                duration: 0.8,
                ease: "easeInOut",
              }}
              className="text-center text-lg text-gray-400 md:text-xl"
            >
              Curvetopia - A Journey into the World of Curves
            </motion.p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{
              delay: 0.8,
              duration: 0.8,
              ease: "easeInOut",
            }}
            className="mt-10"
          >
            <a href="/explore">
              <button className="relative inline-flex h-12 animate-shimmer items-center justify-center rounded-md border border-slate-800 bg-[linear-gradient(110deg,#000103,45%,#0b3a42,55%,#000103)] bg-[length:200%_100%] px-6 font-medium text-slate-400 transition-colors focus:outline-none focus:ring-1 focus:ring-cyan-400 focus:ring-offset-1 focus:ring-offset-slate-900 before:absolute before:-inset-1.5 before:rounded-md before:bg-cyan-400 before:opacity-0 before:blur-2xl before:z-[-1] before:transition-opacity before:duration-300 hover:before:opacity-50 active:before:opacity-75">
                Explore
              </button>
            </a>
          </motion.div>
        </LampContainer>
      </div>
    </>
  );
}
