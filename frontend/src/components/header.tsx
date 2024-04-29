import HeaderAvatar from "@/components/headeravatar";

import { Button } from "@/components/ui/button";
import { Settings, Home } from "lucide-react";

function Header({ session_user_id, userDict, isUserDataLoading, isSettingsOpen, setIsSettingsOpen }: { session_user_id: any, userDict: any, isUserDataLoading: any, isSettingsOpen: any, setIsSettingsOpen: any }) {
    return (
        <div className="w-[80%] mx-auto flex items-center justify-between pt-4 pb-4">
            <div className="text-2xl font-bold">onpulse</div>
            <div className="flex flex-row items-center">
                <div className="px-8 cursor-pointer hover:text-gray-600 transition duration-250 ease-in-out">
                    {!isUserDataLoading && !isSettingsOpen &&
                        <Button variant="ghost" onClick={() => setIsSettingsOpen(true)}>
                            <Settings />
                        </Button>
                    }
                    {!isUserDataLoading && isSettingsOpen &&
                        <Button variant="ghost" onClick={() => setIsSettingsOpen(false)}>
                            <Home />
                        </Button>
                    }
                </div>
                <HeaderAvatar session_user_id={session_user_id} userDict={userDict} isUserDataLoading={isUserDataLoading}/>
            </div>
        </div>
    )
}

export default Header;