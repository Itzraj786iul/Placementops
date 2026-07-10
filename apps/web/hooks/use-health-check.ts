"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchHealthCheck } from "@/services/api-client";

export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: fetchHealthCheck,
  });
}
