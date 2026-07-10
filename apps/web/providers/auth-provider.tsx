"use client";

import type { AuthTokens, User } from "@placementos/types";
import { useRouter } from "next/navigation";
import * as React from "react";
import { toast } from "sonner";

import { AuthApiError, fetchCurrentUser, logout } from "@/services/auth-client";

type AuthContextValue = {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (tokens: AuthTokens) => void;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const refreshUser = React.useCallback(async () => {
    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
    } catch (error) {
      setUser(null);
      if (error instanceof AuthApiError && error.statusCode !== 401) {
        toast.error(error.message);
      }
    }
  }, []);

  React.useEffect(() => {
    const loadUser = async () => {
      setIsLoading(true);
      await refreshUser();
      setIsLoading(false);
    };
    void loadUser();
  }, [refreshUser]);

  const signIn = React.useCallback((tokens: AuthTokens) => {
    setUser(tokens.user);
  }, []);

  const signOut = React.useCallback(async () => {
    try {
      await logout();
      setUser(null);
      router.push("/login");
      toast.success("Signed out successfully");
    } catch (error) {
      const message =
        error instanceof AuthApiError
          ? error.message
          : "Unable to sign out. Please try again";
      toast.error(message);
    }
  }, [router]);

  const value = React.useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: user !== null,
      signIn,
      signOut,
      refreshUser,
    }),
    [user, isLoading, signIn, signOut, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

export function useRequireAuth(redirectTo = "/login"): AuthContextValue {
  const auth = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      router.replace(redirectTo);
    }
  }, [auth.isLoading, auth.isAuthenticated, router, redirectTo]);

  return auth;
}
