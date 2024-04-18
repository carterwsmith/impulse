import { PromotionsTable } from "@/components/promotionstable";

interface PromotionsProps {
    session_user_id: any;
}

function Promotions({ session_user_id }: PromotionsProps) {
    return (
        <PromotionsTable session_user_id={session_user_id}/>
    )
}

export default Promotions;