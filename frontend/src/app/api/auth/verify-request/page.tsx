'use client'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

import { MailCheck } from "lucide-react"

export default function verifyRequest() {
  return (
    <div className='h-screen flex items-center justify-center'>
        <Card className="w-[400px]">
        <CardHeader>
            <CardTitle>Onpulse</CardTitle>
            <CardDescription>Check your email for a link to continue.</CardDescription>
            <div className='flex items-center justify-center p-4'>
                <MailCheck size={50} />
            </div>
        </CardHeader>
        </Card>
    </div>
  )
}