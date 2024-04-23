import { DTable } from "@/components/dtable";

import { Construction } from "lucide-react";

function Sessions() {
    return (
        <div className="flex flex-col items-center justify-center mt-20">
            <Construction size={128} strokeWidth={2} />
            <p className="text-3xl font-bold mt-2">Coming soon</p>
        </div>
        //<DTable/>
    )
}

export default Sessions;