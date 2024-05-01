import NextAuth from "next-auth"
import PostgresAdapter from "@auth/pg-adapter"
import Resend from "next-auth/providers/resend"
import { Pool } from "pg"
import type { Provider } from "next-auth/providers"
import { render } from "@react-email/render"
import LinkEmail from "@/emails/LinkEmail"
 
const providers: Provider[] = [
  Resend({
    from: "auth@onpulsehq.com",
    async sendVerificationRequest({
      identifier: to,
      provider,
      url,
      theme,
    }) {
      const { host } = new URL(url)
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${provider.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "Onpulse <auth@onpulsehq.com>",
          to,
          subject: `Sign in to Onpulse`,
          html: render(LinkEmail({ url, host })),
          text: text({ url, host }),
        }),
      })

      // Email Text body (fallback for email clients that don't render HTML, e.g. feature phones)
      function text({ url, host }: { url: string; host: string }) {
        return `Sign in to ${host}\n${url}\n\n`
      }
    
      if (!res.ok)
        throw new Error("Resend error: " + JSON.stringify(await res.json()))
    },
  }),
]

export const providerMap = providers.map((provider) => {
  if (typeof provider === "function") {
    const providerData = provider()
    return { id: providerData.id, name: providerData.name }
  } else {
    return { id: provider.id, name: provider.name }
  }
})
 
const pool = new Pool({
  host: process.env.DATABASE_HOST,
  user: process.env.DATABASE_USER,
  //password: process.env.DATABASE_PASSWORD,
  database: process.env.DATABASE_NAME,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
})
 
export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PostgresAdapter(pool),
  providers: providers,
  pages: {
    signIn: "/auth/signin",
    verifyRequest: "/auth/verify-request",
  },
})