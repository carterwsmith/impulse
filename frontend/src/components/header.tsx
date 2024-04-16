import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

function Header() {
    return (
        <div className="w-[80%] mx-auto flex items-center justify-between pt-4 pb-4">
            <div className="text-2xl font-bold">impulse</div>
            <Avatar>
                <AvatarImage src="https://github.com/shadcn.png" />
                <AvatarFallback>CN</AvatarFallback>
            </Avatar>
        </div>
    )
}

export default Header;