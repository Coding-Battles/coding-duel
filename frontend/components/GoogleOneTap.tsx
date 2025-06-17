"use client";

import { useEffect } from "react";
import { initializeGoogleOneTap } from "@/lib/auth-client";

export default function GoogleOneTap() {
  useEffect(() => {
    initializeGoogleOneTap();
  }, []);

  return null;
}