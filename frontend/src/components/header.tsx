import HeaderAvatar from "@/components/headeravatar";

function Header() {
    return (
        <div className="w-[80%] mx-auto flex items-center justify-between pt-4 pb-4">
            <div className="text-2xl font-bold">onpulse</div>
            <HeaderAvatar/>
        </div>
    )
}

export default Header;