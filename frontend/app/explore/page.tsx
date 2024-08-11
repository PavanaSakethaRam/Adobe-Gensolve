"use client";
import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { FileUpload } from "@/components/ui/file-upload";

export default function ExplorePage() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedOption, setSelectedOption] =
    useState<string>("Choose an Option");
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleDropdownToggle = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleOptionSelect = (option: string) => {
    setSelectedOption(option);
    setIsDropdownOpen(false);
  };

  const handleFileUpload = (uploadedFiles: File[]) => {
    const validFiles = uploadedFiles.filter((file) =>
      ["text/csv", "image/png", "image/jpeg", "image/jpg"].includes(file.type)
    );
    if (validFiles.length > 0) {
      setFiles([validFiles[0]]); // Keep only the most recent file
    }
    setPreviewImage(null);
    setError(null);
  };

  const handleRemoveFile = () => {
    setFiles([]);
    setPreviewImage(null);
    setError(null);
  };

  const handleMouseMove = (
    e: React.MouseEvent<HTMLDivElement, MouseEvent>,
    id: string
  ) => {
    const card = document.getElementById(id);
    const rect = card?.getBoundingClientRect();
    const x = e.clientX - (rect?.left ?? 0);
    const y = e.clientY - (rect?.top ?? 0);

    const rotateX = (y / (rect?.height ?? 1) - 0.5) * 20;
    const rotateY = (x / (rect?.width ?? 1) - 0.5) * -20;

    card?.style.setProperty("--rotateX", `${rotateX}deg`);
    card?.style.setProperty("--rotateY", `${rotateY}deg`);
  };

  const handleMouseLeave = (id: string) => {
    const card = document.getElementById(id);
    card?.style.setProperty("--rotateX", `0deg`);
    card?.style.setProperty("--rotateY", `0deg`);
  };

  const handleSend = async () => {
    if (!files.length || selectedOption === "Choose an Option") {
      setError("Please select a file and an option.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", files[0]);

    let endpoint = "";
    switch (selectedOption) {
      case "Get Regularization from CSV":
        endpoint = `${process.env.NEXT_PUBLIC_ML_URL}/regularization_csv`;
        break;
      case "Get Regularization from PNG":
        endpoint = `${process.env.NEXT_PUBLIC_ML_URL}/regularization_png`;
        break;
      case "Get Symmetry Lines":
        endpoint = `${process.env.NEXT_PUBLIC_ML_URL}/detect_symmetry_png`;
        break;
      default:
        setError("Invalid option selected.");
        setIsLoading(false);
        return;
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to fetch the data. Please try again.");
      }

      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      setPreviewImage(imageUrl);
    } catch (err: any) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 pt-8 pl-8 pr-8">
      <header className="mb-12 text-center flex">
        <div className="flex justify-start items-start w-[10rem]">
          <div className="flex">
            <a href="/">
              <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeInOut" }}
                className="relative inline-flex h-12 animate-shimmer items-center justify-center rounded-md border border-slate-800 bg-[linear-gradient(110deg,#000103,45%,#0b3a42,55%,#000103)] bg-[length:200%_100%] px-6 font-medium text-slate-400 transition-colors focus:outline-none focus:ring-1 focus:ring-cyan-400 focus:ring-offset-1 focus:ring-offset-slate-900 before:absolute before:-inset-1.5 before:rounded-md before:bg-cyan-400 before:opacity-0 before:blur-2xl before:z-[-1] before:transition-opacity before:duration-300 hover:before:opacity-50 active:before:opacity-75"
              >
                Go Back
              </motion.button>
            </a>
          </div>
        </div>
        <div className="flex flex-col justify-center items-center w-full">
          <motion.h1
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            className="text-4xl md:text-6xl font-bold bg-gradient-to-br from-slate-300 to-slate-500 bg-clip-text text-transparent"
          >
            Curvetopia - Adobe Gensolve
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeInOut" }}
            className="mt-4 text-lg md:text-2xl text-gray-400"
          >
            Explore the features of Curvetopia, a journey into the world of
            curves.
          </motion.p>
        </div>
      </header>

      <div className="relative mb-12" ref={dropdownRef}>
        <motion.button
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
          onClick={handleDropdownToggle}
          className="relative inline-flex h-12 w-96 animate-shimmer items-center justify-center rounded-md border border-slate-800 bg-[linear-gradient(110deg,#000103,45%,#0b3a42,55%,#000103)] bg-[length:200%_100%] px-6 font-medium text-slate-400 transition-colors focus:outline-none focus:ring-1 focus:ring-cyan-400 focus:ring-offset-1 focus:ring-offset-slate-900 before:absolute before:-inset-1.5 before:rounded-md before:bg-cyan-400 before:opacity-0 before:blur-2xl before:z-[-1] before:transition-opacity before:duration-300 hover:before:opacity-50 active:before:opacity-75"
        >
          {selectedOption}
          <span className="ml-2">&#x25BC;</span>
        </motion.button>
        <motion.div
          initial={{ height: 0 }}
          animate={{ height: isDropdownOpen ? "auto" : 0 }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
          className="absolute top-full left-0 w-full md:w-1/2 bg-slate-800 rounded-lg shadow-lg overflow-hidden mt-2 z-50"
        >
          <ul
            className={`text-slate-300 ${isDropdownOpen ? "block" : "hidden"}`}
          >
            <li
              className="py-2 px-4 hover:bg-slate-700 transition-colors cursor-pointer"
              onClick={() => handleOptionSelect("Get Regularization from CSV")}
            >
              Get Regularization from CSV
            </li>
            <li
              className="py-2 px-4 hover:bg-slate-700 transition-colors cursor-pointer"
              onClick={() => handleOptionSelect("Get Regularization from PNG")}
            >
              Get Regularization from PNG
            </li>
            <li
              className="py-2 px-4 hover:bg-slate-700 transition-colors cursor-pointer"
              onClick={() => handleOptionSelect("Get Symmetry Lines")}
            >
              Get Symmetry Lines
            </li>
          </ul>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <motion.div
          id="uploadCard"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
          className="rounded-lg"
          onMouseMove={(e) => handleMouseMove(e, "uploadCard")}
          onMouseLeave={() => handleMouseLeave("uploadCard")}
          style={{
            perspective: "1000px",
            transformStyle: "preserve-3d",
            transform:
              "rotateX(var(--rotateX, 0deg)) rotateY(var(--rotateY, 0deg))",
            transition: "transform 0.1s ease-out",
          }}
        >
          <FileUpload
            onChange={handleFileUpload}
            onRemove={handleRemoveFile}
            file={files.length > 0 ? files[0] : null}
          />
        </motion.div>

        <motion.div
          id="imageCard"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
          className="bg-slate-800 p-6 rounded-lg shadow-lg flex items-center justify-center cursor-pointer"
          onMouseMove={(e) => handleMouseMove(e, "imageCard")}
          onMouseLeave={() => handleMouseLeave("imageCard")}
          style={{
            perspective: "1000px",
            transformStyle: "preserve-3d",
            transform:
              "rotateX(var(--rotateX, 0deg)) rotateY(var(--rotateY, 0deg))",
            transition: "transform 0.1s ease-out",
          }}
        >
          <div className="w-full h-96 bg-slate-900 rounded-lg flex items-center justify-center text-slate-400">
            {isLoading ? (
              <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full text-cyan-400"></div>
            ) : previewImage ? (
              <img
                src={previewImage}
                alt="Preview"
                className="max-h-full max-w-full"
              />
            ) : (
              <span className="text-lg">Your Image Preview Here</span>
            )}
          </div>
        </motion.div>
      </div>

      {error && <div className="text-red-500 text-center mt-4">{error}</div>}
      <div className="flex justify-center items-center mt-4">
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
          className="bg-cyan-500 hover:bg-cyan-600 text-white font-medium py-3 px-6 rounded-lg shadow-lg transition-all duration-300"
          onClick={handleSend}
        >
          Send
        </motion.button>
      </div>
    </div>
  );
}
