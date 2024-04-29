import { auth } from "@/auth"
import { redirect } from 'next/navigation'

import { Toaster } from "@/components/ui/sonner"

import Content from "@/components/content"

export default async function Home() {
  const session = await auth()

  if (!session || !session.user) {
    redirect('/api/auth/signin')
  } else {
    return (
      <>
        <Content session_user_id={session.user.id}/>
        <Toaster/>
      </>
    )
  }
}
