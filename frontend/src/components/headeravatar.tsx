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
import { Skeleton } from "@/components/ui/skeleton"
import { signOut } from "next-auth/react"
import Image from 'next/image'
  

export default function HeaderAvatar({ session_user_id, userDict, isUserDataLoading }: { session_user_id: any, userDict: any, isUserDataLoading: any }) {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger>
                <Avatar>
                { !isUserDataLoading ? 
                    (userDict.image == null ? 
                        <AvatarFallback>O</AvatarFallback> :
                        <AvatarImage asChild src={userDict.image}>
                            <Image src={userDict.image} alt="" width="64" height="64"/>
                        </AvatarImage>
                    ) 
                    : <Skeleton className="w-[64px] h-[64px] rounded-full" />
                }
                </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
                <DropdownMenuLabel>
                    My Account
                    {
                        !isUserDataLoading && 
                        <p className="text-xs font-normal">
                            {userDict.email}
                        </p>
                    }
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem style={{ cursor: 'pointer' }}>Settings</DropdownMenuItem>
                <DropdownMenuItem onClick={() => signOut()} style={{ cursor: 'pointer' }}>Sign out</DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}