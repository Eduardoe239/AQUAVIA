import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { Skeleton, ErrorState } from "../components/ui/states";
import { api, ApiError } from "../lib/api/client";

export function RequireAuth({ children }: { children: ReactNode }) {
  const me = useQuery({ queryKey: ["me"], queryFn: api.me, retry: false });
  if (me.isLoading) return <main className="page"><Skeleton height={120} /></main>;
  if (me.error instanceof ApiError && me.error.status === 401) return <Navigate to="/login" replace />;
  if (me.isError) return <main className="page"><ErrorState error={me.error} onRetry={() => me.refetch()} /></main>;
  return <>{children}</>;
}
