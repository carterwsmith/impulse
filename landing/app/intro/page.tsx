import MarketingLayout from '@/app/(marketing)/layout';
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeftIcon } from "@radix-ui/react-icons";

export default function IntroPage() {
  return (
    <MarketingLayout>
        <section
        id="content"
        className="relative mx-auto max-w-[80rem] px-6 pb-20 md:px-8"
      >
        <article className="prose lg:prose-xl m-auto pt-28">
        <Link href="/">
          <Button className="cursor-pointer mb-8 gap-1 rounded-lg text-black">
            <ArrowLeftIcon className="ml-1 size-4 transition-transform duration-300 ease-in-out group-hover:translate-x-1" />
            <span>Go back </span>
          </Button>
        </Link>
          <h1 className="text-5xl font-bold mb-12">Introducing Onpulse: Ecommerce experiences powered by AI</h1>
          <p className="text-lg">Modern AI tools are incredibly powerful but lack integrations with consumer experiences, especially online stores. Onpulse and its AI-enabled tooling allows ecommerce stores to show every one of their shoppers the <strong>perfect promotion in real-time</strong> by analyzing their browsing behavior.
<br/><br/>
There are three crucial parts to Onpulse; <strong>browsing sessions</strong>, <strong>promotions</strong>, and your business's <strong>storefront</strong>.
<br/><br/>
Every time a user visits your storefront, where Onpulse.js is running, they start a unique and anonymous Onpulse session. We track the user's behavior on your website and use AI to determine what the purpose of their session is. <strong>No third-party tracking is used and the data collected is strictly from your website.</strong>
<br/><br/>
Then we compare information from the session to your <strong>promotions</strong>. A promotion is a discount that is already configured on your storefront, such as a discount code set up in Shopify. You can easily add and manage your promotions in the Onpulse dashboard, with one for each discount code.
<br/><br/>
If we find a promotion that fits the AI-inferred intent of user's session, we immediately show it to them in the form of a popup modal that contains a title, description, and discount code that you have pre-configured in the Onpulse dashboard. Optionally, use Onpulse AI to generate copy in a tone you specify, tailored to the user's session.</p>
        </article>
      </section>
    </MarketingLayout>
  );
}