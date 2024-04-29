"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Clipboard, ClipboardCheck, LoaderCircle, Hourglass, Activity } from "lucide-react"

function Onboarding({ session_user_id, setIsDomainSet }: any) {
    const [isCopied, setIsCopied] = React.useState(false)
    const [isPingInProgress, setIsPingInProgress] = React.useState(false)
    const [isPingCooldown, setIsPingCooldown] = React.useState(false)
    const [pingError, setPingError] = React.useState('')

    const startPing = async (userId: number, rootDomain: string) => {
        setIsPingInProgress(true);

        // Assume the ping operation returns some data
        const response = await fetch(`http://localhost:5000/user/onboard/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'user_domain': rootDomain })
        });
        const pingData = await response.json();

        //console.log(pingData);
        if (pingData.status) {
            setIsDomainSet(true);
        } else {
            setPingError(pingData.message);
            setIsPingInProgress(false);
            setIsPingCooldown(true);

            // Start the cooldown period without waiting for it to finish before returning data
            setTimeout(() => {
                setIsPingCooldown(false);
            }, 5000); // 5 seconds cooldown
        }
    }

    return (
        <>
        <div className="flex flex-col">
            <div className="flex pt-4 pb-10">
                Welcome to Onpulse, let's get your website started in a few clicks.
            </div>
            <div className="flex">
                <div className="w-1/4 px-20">
                    <div className="flex flex-col items-center">
                        <div className="rounded-full h-24 w-24 flex items-center justify-center border-2 bg-black text-white text-xl font-bold">1</div>
                        <div className="border-dashed border-l-2 border-black h-40"></div>
                        <div className="rounded-full h-24 w-24 flex items-center justify-center border-2 bg-black text-white text-xl font-bold">2</div>
                        <div className="border-dashed border-l-2 border-black h-40"></div>
                        <div className="rounded-full h-24 w-24 flex items-center justify-center border-2 bg-black text-white text-xl font-bold">3</div>
                    </div>
                </div>
                <div className="onboarding-content w-3/4 mx-auto flex flex-col">
                    <div className="h40 flex flex-col">
                        <div className="text-2xl font-bold">Set your domain</div>
                        <div className="text-m">Where will you host Onpulse? Just the root domain, no subdomains or paths.</div>
                        <div className="w-1/2 pt-4"><Input id='onboardDomainInput' placeholder="https://example.com" /></div>
                        { pingError && <div className="text-red-500 font-bold pt-2">{pingError}</div>}
                    </div>
                    <div className="h-40 flex flex-col">
                        <div className="text-2xl font-bold">Add Onpulse.js to your website</div>
                        <div className="text-m">Include our script in the <span className="inline-code">&lt;head&gt;</span> element of each page in your website.</div>
                        <div className="pt-4 flex flex-row space-x-4 items-center">
                            <div className="w-4/5 inline-code" id="scriptCode">&lt;script src="https://path_to_cdn/onpulse.js"&gt;&lt;/script&gt; </div>
                            {!isCopied && <div><Button onClick={() => {navigator.clipboard.writeText(document.getElementById('scriptCode')?.textContent || ""); setIsCopied(true);}}><Clipboard className="h-4 w-4"/></Button></div>}
                            {isCopied && <Button className="bg-green-700 hover:bg-green-800" onClick={() => {navigator.clipboard.writeText(document.getElementById('scriptCode')?.textContent || "");}}><ClipboardCheck className="h-4 w-4" /></Button>}
                        </div>
                    </div>
                    <div className="h-40 flex flex-col">
                        <div className="text-2xl font-bold">Confirm installation</div>
                        <div className="text-m">We'll ping your domain to see if the script is loaded. This could take a few minutes.</div>
                        <div className="pt-4">
                            {!isPingInProgress && !isPingCooldown && <Button onClick={() => { startPing(session_user_id, (document.getElementById('onboardDomainInput') as HTMLInputElement)?.value);}}><Activity className="mr-2 h-4 w-4" />Check for Onpulse.js</Button>}
                            {isPingInProgress && <Button disabled><LoaderCircle className="mr-2 h-4 w-4 animate-spin" />Checking...</Button>}
                            {!isPingInProgress && isPingCooldown && <Button disabled><Hourglass className="mr-2 h-4 w-4" />Check again in 5 seconds</Button>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </>
    )
}

export default Onboarding;