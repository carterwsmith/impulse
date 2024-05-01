'use client'

import * as React from "react"

import { useSearchParams } from 'next/navigation'
import { signIn } from 'next-auth/react'
import { Loader2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

export default function EmailSignInForm() {
  const searchParams = useSearchParams()
  const callbackUrl = searchParams.get('callbackUrl') || '/'
  const [isSubmitting, setIsSubmitting] = React.useState(false)

  async function handleSubmit(event: any) {
    event.preventDefault()
    const formData = new FormData(event.target)
    const email = formData.get('email')
    setIsSubmitting(true)
    await signIn('resend', { email, callbackUrl })
    setIsSubmitting(false)
  }

  return (
    <div className='h-screen flex items-center justify-center'>
        <Card className="w-[400px]">
        <CardHeader>
            <CardTitle>Onpulse</CardTitle>
            <CardDescription>Sign in or create an account with a magic link.</CardDescription>
        </CardHeader>
        <CardContent>
        <form onSubmit={handleSubmit}>
            <div className="grid w-full items-center gap-4">
                <div className="flex flex-col space-y-1.5">
                <Input
                    id='email'
                    name='email'
                    type='email'
                    placeholder='email@example.com'
                    autoComplete='email'
                    required
                />
                </div>
                <div className="flex flex-col space-y-1.5">
                <Button
                    type='submit'
                    className='mt-3 w-full'
                    disabled={isSubmitting}
                >
                    {isSubmitting ? <Loader2 className="animate-spin" /> : 'Continue with email'}
                </Button>
                </div>
            </div>
            </form>
        </CardContent>
        </Card>
    </div>
  )
}