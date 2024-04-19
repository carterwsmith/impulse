'use client';

import * as React from "react"
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
  

export default function HeaderAvatar({ session_user_id }: { session_user_id: any }) {
    const [isLoading, setIsLoading] = React.useState(true);
    const [userDict, setUserDict] = React.useState<any>(null);

    React.useEffect(() => {
        setIsLoading(true);
        fetch(`http://localhost:5000/user/${session_user_id}`)
            .then(response => response.json())
            .then(data => {
                setUserDict(data);
                setIsLoading(false);
            });
    }, [session_user_id]);

    return (
        <DropdownMenu>
            <DropdownMenuTrigger>
                <Avatar>
                { !isLoading ? 
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
                        !isLoading && 
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