import { redirect } from "next/navigation";

/** Registration is JIT via Google OAuth — keep a single login entry point. */
export default function SignupPage() {
  redirect("/login");
}
