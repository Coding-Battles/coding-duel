"use client";

import { useEffect } from "react";
import { authClient, initializeGoogleOneTap } from "@/lib/auth-client";

export default function GoogleOneTap() {
  useEffect(() => {
    initializeGoogleOneTap();
  }, []);

  return null;
}