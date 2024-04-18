"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  is_active: z.boolean(),
  is_ai_generated: z.boolean(),
  ai_description: z.string().max(250).nullable(),
  ai_discount_percent_min: z.number().min(0).max(100).nullable(),
  ai_discount_percent_max: z.number().min(0).max(100).nullable(),
  ai_discount_dollars_min: z.number().min(0).nullable(),
  ai_discount_dollars_max: z.number().min(0).nullable(),
  promotion_name: z.string().max(50),
  image_url: z.string().max(250).nullable(),
  display_title: z.string().max(50).nullable(),
  display_description: z.string().max(250).nullable(),
  discount_percent: z.number().min(0).max(100).nullable(),
  discount_dollars: z.number().min(0).nullable(),
  discount_code: z.string().max(20).nullable(),
})

export default function AddPromotionForm() {
  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })
 
  // 2. Define a submit handler.
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <DialogTitle>
            Add promotion
        </DialogTitle>
        <FormField
          control={form.control}
          name="promotion_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Promotion name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormDescription>
                Used to identify your promotion.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
