"use client"

import { ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

import { toast } from "sonner"

function Settings({ userDict, setIsSettingsOpen }: { userDict: any, setIsSettingsOpen: any }) {
    return (
        <div className="w-full flex flex-col justify-center items-center">
            <div className="w-[80%] flex flex-row items-center cursor-pointer hover:text-gray-600 transition duration-250 ease-in-out mt-4 mb-8" >
                {/* <Button >
                    <ChevronLeft className="mr-2 h-4 w-4" /> Back
                </Button> */}
            </div>
            <form className="w-[40%]" onSubmit={(e) => {
                e.preventDefault();
                fetch(`http://localhost:5000/user/update/${userDict.id}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        max_popups_per_session: (e.target as HTMLFormElement).max_popups_per_session.value
                    }),
                }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const maxPopupsErrorElement = document.getElementById("max-popups-error");
                        if (maxPopupsErrorElement && maxPopupsErrorElement.textContent) {
                            maxPopupsErrorElement.textContent = '';
                        }
                        toast("Settings successfully updated.");
                    } else {
                        const maxPopupsErrorElement = document.getElementById("max-popups-error");
                        if (data.invalid_element === "max_popups_per_session" && maxPopupsErrorElement) {
                            maxPopupsErrorElement.textContent = data.message;
                        }
                        toast("Error updating settings.");
                    }
                });
            }}>
                <div className="mb-10">
                    <p className="text-4xl font-bold mb-2">Settings</p>
                    <p className="text-m">Manage your settings, including where and how promotions are shown.</p>
                </div>
                <div className="mb-10">
                    <p className="text-lg font-bold">Root domain</p>
                    <p className="text-sm mb-2">Your website where Onpulse.js is served and visitors will be shown promotions.</p>
                    <Input name="root_domain" disabled className="w-1/2" type="text" defaultValue={userDict.root_domain} />
                </div>
                <div className="mb-10">
                    <p className="text-lg font-bold">Maximum popups displayed per visit</p>
                    <p className="text-sm mb-2">When someone visits your website, <i>at most</i> how many promotions can be shown to them?</p>
                    <Input name="max_popups_per_session" className="w-1/5" type="text" defaultValue={userDict.max_popups_per_session} />
                    <p className="text-red-500 text-sm font-bold mt-2" id="max-popups-error"></p>
                </div>
                <div className="flex flex-row justify-end">
                    <Button onClick={() => setIsSettingsOpen(false)} variant="outline">
                        <ChevronLeft className="mr-2 h-4 w-4" /> Back
                    </Button>

                    <Button className="ml-4" type="submit">
                        Save changes
                    </Button>
                </div>
            </form>
        </div>
    )
}

export default Settings;