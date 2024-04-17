'use client';

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from "@/components/ui/dropdown-menu"
import { signOut } from "next-auth/react"
import Image from 'next/image'
  

export default function HeaderAvatar() {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger>
                <Avatar>
                    <AvatarImage asChild src="/png/ggp.png">
                        <Image src={`/png/ggp.png`} alt="" width="64" height="64"/>
                    </AvatarImage>
                    <AvatarFallback>o</AvatarFallback>
                </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem style={{ cursor: 'pointer' }}>Settings</DropdownMenuItem>
                <DropdownMenuItem onClick={() => signOut()} style={{ cursor: 'pointer' }}>Sign out</DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}