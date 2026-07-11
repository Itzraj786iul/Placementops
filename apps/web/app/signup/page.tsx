import { redirect } from "next/navigation";

/** Unified registration lives at /register (email/password + Google). */
export default function SignupPage() {
  redirect("/register");
}
