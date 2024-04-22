"use client"

import * as React from "react"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { LoaderCircle } from "lucide-react"

import Header from "@/components/header"
import Promotions from "@/components/promotions"
import Sessions from "@/components/sessions"
import Onboarding from "@/components/onboarding"

interface ContentProps {
    session_user_id: any;
}

function Content({ session_user_id }: ContentProps) {
    const [isUserDataLoading, setIsUserDataLoading] = React.useState(true);
    const [isDomainSet, setIsDomainSet] = React.useState(false);
    const [userDict, setUserDict] = React.useState<any>(null);

    React.useEffect(() => {
        setIsUserDataLoading(true);
        fetch(`http://localhost:5000/user/${session_user_id}`)
            .then(response => response.json())
            .then(data => {
                setUserDict(data);
                setIsUserDataLoading(false);
            });
    }, [session_user_id, isDomainSet]);

    return (
        <>
            <Header session_user_id={session_user_id} userDict={userDict} isUserDataLoading={isUserDataLoading}/>

            {
                isUserDataLoading ? (
                    <div className="w-full mx-auto flex justify-center items-start">
                        <div className="animate-spin">
                            <LoaderCircle size={64} strokeWidth={2} />
                        </div>
                    </div>
                ) : (
                    userDict.is_domain_configured ? (
                        <div className="w-full mx-auto flex justify-center">
                            <Tabs defaultValue="promotions" className="w-[80%]">
                                <TabsList className="flex justify-center mb-4">
                                    <TabsTrigger value="promotions">Promotions</TabsTrigger>
                                    <TabsTrigger value="sessions">Sessions</TabsTrigger>
                                </TabsList>
                                <TabsContent value="promotions" className="w-full mx-auto"><Promotions session_user_id={session_user_id}/></TabsContent>
                                <TabsContent value="sessions" className="w-full mx-auto bg-red-500"><Sessions/></TabsContent>
                            </Tabs>
                        </div>
                    ) : (
                        <div className="w-full mx-auto flex justify-center">
                            <Onboarding session_user_id={session_user_id} setIsDomainSet={setIsDomainSet} />
                        </div>            
                    )
                )
            }
        </>
    )
}

export default Content;