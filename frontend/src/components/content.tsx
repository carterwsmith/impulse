import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

import Header from "@/components/header"
import Promotions from "@/components/promotions"
import Sessions from "@/components/sessions"

interface ContentProps {
    session_user_id: any;
}

function Content({ session_user_id }: ContentProps) {
    return (
        <>
            <Header/>

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
        </>
    )
}

export default Content;