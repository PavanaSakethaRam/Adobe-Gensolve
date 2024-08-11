"use client";
import React, { useState, useEffect } from "react";
import { HomeMain } from "@/components/home";
import { LoadingScreen } from "@/components/loading";
import { motion, AnimatePresence } from "framer-motion";

export default function MainPage() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <AnimatePresence>
      {loading ? (
        <LoadingScreen key="loading" />
      ) : (
        <motion.div
          className="w-full"
          key="home"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        >
          <HomeMain />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
