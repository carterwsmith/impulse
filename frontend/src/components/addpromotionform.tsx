"use client"

import * as React from "react"
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
import { Input, BigInput } from "@/components/ui/input"
import { Switch  } from "@/components/ui/switch"
  import {
    Pagination,
    PaginationContent,
    PaginationEllipsis,
    PaginationItem,
    PaginationLink,
    PaginationNext,
    PaginationPrevious,
  } from "@/components/ui/pagination"
  import {
    MagicWandIcon,
  } from "@radix-ui/react-icons"
  import {
    DollarSign,
    Percent,
    Loader2,
  } from "lucide-react"
  import { toast } from "sonner"
   
function FormPagination({ formPage, setFormPage }: { formPage: number, setFormPage: Function }) {
    return (
        <Pagination>
        <PaginationContent>
            {formPage > 0 && 
            <PaginationItem>
            <PaginationPrevious onClick={() => setFormPage(formPage - 1)} />
            </PaginationItem>}
            {formPage < 1 && <PaginationItem>
            <PaginationNext onClick={() => setFormPage(formPage + 1)} />
            </PaginationItem> }
        </PaginationContent>
        </Pagination>
    )
}

const formSchema = z.object({
  is_active: z.boolean(),
  impulse_user_id: z.number(),
  is_ai_generated: z.boolean(),
  ai_description: z.string().max(250).optional(),
  ai_discount_percent_min: z.coerce.number().min(0).max(100).optional(),
  ai_discount_percent_max: z.coerce.number().min(0).max(100).optional(),
  ai_discount_dollars_min: z.coerce.number().min(0).optional(),
  ai_discount_dollars_max: z.coerce.number().min(0).optional(),
  promotion_name: z.string().max(50).min(1, { message: `Required` }),
  image_url: z.string().url().optional().or(z.literal('')),
  display_title: z.string().max(50).optional(),
  display_description: z.string().max(250).optional(),
  discount_percent: z.coerce.number().min(0).max(100).optional(),
  discount_dollars: z.coerce.number().min(0).optional(),
  discount_code: z.string().max(20),
}).refine(schema => {
    return !(
        schema.is_ai_generated &&
        (
            schema.ai_description == ""
        )
    ); 
}, {message: "Required", path: ["ai_description"]})
.superRefine((schema, ctx) => {
    if (schema.is_ai_generated &&
        (
            (schema.ai_discount_dollars_max == 0 &&
              schema.ai_discount_dollars_min == 0 &&
              schema.ai_discount_percent_max == 0 &&
              schema.ai_discount_percent_min == 0)
        )) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["ai_discount_dollars_min"],
        fatal: false,
        message: "One discount must be set",
      });
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["ai_discount_dollars_max"],
        fatal: false,
        message: "One discount must be set",
      });
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["ai_discount_percent_min"],
        fatal: false,
        message: "One discount must be set",
      });
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["ai_discount_percent_max"],
        fatal: false,
        message: "One discount must be set",
      });
    }

    if (schema.is_ai_generated && schema.ai_discount_dollars_min == 0 && schema.ai_discount_dollars_max != 0) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["ai_discount_dollars_min"],
                fatal: false,
                message: "Required",
            });
        }

    if (schema.is_ai_generated && schema.ai_discount_percent_min == 0 && schema.ai_discount_percent_max != 0) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["ai_discount_percent_min"],
                fatal: false,
                message: "Required",
            });
        }

    if (schema.is_ai_generated && schema.ai_discount_dollars_max !== undefined && schema.ai_discount_dollars_min !== undefined &&
        (
            schema.ai_discount_dollars_max < schema.ai_discount_dollars_min
        )) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["ai_discount_dollars_min"],
                fatal: false,
                message: "Must be less than max discount",
            });
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["ai_discount_dollars_max"],
                fatal: false,
                message: "Must be greater than min discount",
            });
        }

    if (schema.is_ai_generated && schema.ai_discount_percent_max !== undefined && schema.ai_discount_percent_min !== undefined &&
        (
            schema.ai_discount_percent_max < schema.ai_discount_percent_min
        )) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["ai_discount_percent_min"],
                fatal: false,
                message: "Must be less than max discount",
            });
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ["ai_discount_percent_max"],
                fatal: false,
                message: "Must be greater than min discount",
            });
        }
})
.superRefine((schema, ctx) => {
    if (!schema.is_ai_generated &&
        (
            (schema.discount_dollars == 0 &&
              schema.discount_percent == 0)
        )) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["discount_dollars"],
        fatal: false,
        message: "One discount must be set",
      });
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["discount_percent"],
        fatal: false,
        message: "One discount must be set",
      });
    }

    if (
        (
            schema.discount_code == ""
        )
    ) {
        ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["discount_code"],
            fatal: false,
            message: "Required",
          });
    }

    if (
        !schema.is_ai_generated &&
        (
            schema.display_title == ""
        )
    ) {
        ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["display_title"],
            fatal: false,
            message: "Required",
          });
    }
})

export default function AddPromotionForm({ session_user_id, dialogSetter, tableDataFetcher }: { session_user_id: any, dialogSetter: any, tableDataFetcher: any }) {
  const [formPage, setFormPage] = React.useState(0);
  const [dollarOrPercentSwitchValue, setDollarOrPercentSwitchValue] = React.useState(false);

  const [isSubmitting, setIsSubmitting] = React.useState(false);

  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
        is_active: true,
        impulse_user_id: session_user_id,
        is_ai_generated: false,
        ai_description: '',
        ai_discount_percent_min: 0, // Ensure this is a sensible default
        ai_discount_percent_max: 0, // Ensure this is a sensible default
        ai_discount_dollars_min: 0, // Ensure this is a sensible default
        ai_discount_dollars_max: 0, // Ensure this is a sensible default
        promotion_name: '',
        image_url: '',
        display_title: '',
        display_description: '',
        discount_percent: 0, // Ensure this is a sensible default
        discount_dollars: 0, // Ensure this is a sensible default
        discount_code: '',
    }
  })

  const { watch, handleSubmit} = form
  const ai_generated_switch_value = watch('is_ai_generated')
 
  // ERROR HANDLING
  // Field to page mapping
  const fieldToPageMap = {
    promotion_name: 0,
    display_title: 0,
    display_description: 0,
    image_url: 0,
    ai_description: 0,
    discount_dollars: 1,
    discount_percent: 1,
    discount_code: 1,
    ai_discount_dollars_min: 1,
    ai_discount_dollars_max: 1,
    ai_discount_percent_min: 1,
    ai_discount_percent_max: 1
  };

  // Navigate to the first page with an error
  const navigateToFirstErrorPage = (formErrors: any) => {
    const firstErrorField = Object.keys(formErrors)[0] as keyof typeof fieldToPageMap;
    const errorPage = fieldToPageMap[firstErrorField];
    if (errorPage !== undefined) {
      setFormPage(errorPage);
    }
  };
 
  // 2. Define a submit handler.
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.
    setIsSubmitting(true);
    fetch('http://localhost:5000/promotions/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    })
    .then(response => response.json())
    .then(data => {
        // Close the dialog after form submission
        dialogSetter(false);
        tableDataFetcher();
        // emit toast
        toast(`Promotion successfully added.`)
    })
    .catch((error) => {
      //console.error('Error:', error);
    })
    .finally(() => setIsSubmitting(false));
  }
  
  function onError(formErrors: any) {
    navigateToFirstErrorPage(formErrors);
  }

  return (
    <Form {...form}>
      <form onSubmit={handleSubmit(onSubmit, onError)} className="space-y-6">
        <DialogTitle>
            Add new promotion
        </DialogTitle>
        { formPage === 0 && <> <FormField
            control={form.control}
            name="is_ai_generated"
            render={({ field }) => (
            <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                <div className="space-y-0.5">
                <FormLabel className="text-base">
                    <div style={{ display: 'flex', alignItems: 'center' }}>AI generated? <MagicWandIcon className="ml-2" /></div>
                </FormLabel>
                <FormDescription>
                    Describe your ideal promotion and discount parameters; we'll take care of the rest.
                </FormDescription>
                </div>
                <FormControl>
                <Switch
                    checked={field.value}
                    onCheckedChange={field.onChange}
                />
                </FormControl>
            </FormItem>
            )}
        />
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
                Used to identify your promotion in Onpulse.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        /> </>}
        { !ai_generated_switch_value && formPage === 0 && <>
            <FormField
            control={form.control}
            name="display_title"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Display title</FormLabel>
                <FormControl>
                    <Input {...field}/>
                </FormControl>
                <FormDescription>
                    Shown to customers in title text. Best under 20 characters.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="display_description"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Display description (optional)</FormLabel>
                <FormControl>
                    <Input {...field}/>
                </FormControl>
                <FormDescription>
                    Shown to customers in subtitle text.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="image_url"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Image URL (optional)</FormLabel>
                <FormControl>
                    <Input {...field}/>
                </FormControl>
                <FormDescription>
                    Include an image to be shown with the promotion.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
        </>}
        {
            ai_generated_switch_value && formPage === 0 && <>
            <FormField
            control={form.control}
            name="ai_description"
            render={({ field }) => (
                <FormItem>
                <FormLabel>AI description</FormLabel>
                <FormControl>
                    <BigInput {...field}/>
                </FormControl>
                <FormDescription>
                    Describe your ideal target audience and copy style in natural language.<br/><br/>
                    Example: <i>A summer sale for shoppers interested in our recent release of tank tops and sundresses. Use a cheerful tone and summer themes.</i>
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
        </>}

        { formPage === 1 && 
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                <DollarSign size={30} style={{padding: '0 4px 0 0'}}/>
                <Switch
                    checked={dollarOrPercentSwitchValue}
                    onCheckedChange={(value) => {
                        if (value) {
                            form.setValue('discount_dollars', 0);
                            form.setValue('ai_discount_dollars_min', 0);
                            form.setValue('ai_discount_dollars_max', 0);
                        } else {
                            form.setValue('discount_percent', 0);
                            form.setValue('ai_discount_percent_min', 0);
                            form.setValue('ai_discount_percent_max', 0);
                        }
                        setDollarOrPercentSwitchValue(value);
                    }}
                />
                <Percent size={30} style={{padding: '0 0 0 4px'}}/>
            </div>
        }

        { !ai_generated_switch_value && formPage === 1 && !dollarOrPercentSwitchValue && <>
            <FormField
            control={form.control}
            name="discount_dollars"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Discount</FormLabel>
                <div className="flex w-full max-w-sm items-center space-x-2">
                    <p>$</p>
                    <FormControl>
                        <Input {...field} className="dollarInput" placeholder="5.00"/>
                    </FormControl>
                </div>
                <FormDescription>
                    Your desired discount in dollars off.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
        </>}

        { !ai_generated_switch_value && formPage === 1 && dollarOrPercentSwitchValue && <>
            <FormField
            control={form.control}
            name="discount_percent"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Discount</FormLabel>
                <div className="flex w-full max-w-sm items-center space-x-2">   
                    <FormControl>
                        <Input {...field} className="percentInput" placeholder="15"/>
                    </FormControl>
                    <p>%</p>
                </div>
                <FormDescription>
                    Your desired discount in percent off.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
        </>}
    
        { ai_generated_switch_value && formPage === 1 && !dollarOrPercentSwitchValue && <>
            <FormField
            control={form.control}
            name="ai_discount_dollars_min"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Minimum discount</FormLabel>
                <div className="flex w-full max-w-sm items-center space-x-2">
                    <p>$</p>
                    <FormControl>
                        <Input {...field} className="dollarInput" placeholder="5.00"/>
                    </FormControl>
                </div>
                <FormDescription>
                    The lowest discount the AI will give in dollars.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />

            <FormField
            control={form.control}
            name="ai_discount_dollars_max"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Maximum discount</FormLabel>
                <div className="flex w-full max-w-sm items-center space-x-2">
                    <p>$</p>
                    <FormControl>
                        <Input {...field} className="dollarInput" placeholder="10.00"/>
                    </FormControl>
                </div>
                <FormDescription>
                    The highest discount the AI will give in dollars.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
        </>}

        { ai_generated_switch_value && formPage === 1 && dollarOrPercentSwitchValue && <>
            <FormField
            control={form.control}
            name="ai_discount_percent_min"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Minimum discount</FormLabel>
                <div className="flex w-full max-w-sm items-center space-x-2">   
                    <FormControl>
                        <Input {...field} className="percentInput" placeholder="15"/>
                    </FormControl>
                    <p>%</p>
                </div>
                <FormDescription>
                    The lowest discount the AI will give in percent off.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />

            <FormField
            control={form.control}
            name="ai_discount_percent_max"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Maximum discount</FormLabel>
                <div className="flex w-full max-w-sm items-center space-x-2">   
                    <FormControl>
                        <Input {...field} className="percentInput" placeholder="20"/>
                    </FormControl>
                    <p>%</p>
                </div>
                <FormDescription>
                    The highest discount the AI will give in percent off.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
        </>}

        { formPage === 1 &&
            <FormField
            control={form.control}
            name="discount_code"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Discount code</FormLabel>
                <FormControl>
                    <Input {...field} placeholder="5OFF"/>
                </FormControl>
                <FormDescription>
                    Your discount code registered with your storefront.
                </FormDescription>
                <FormMessage />
                </FormItem>
            )}
            />
        }

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', justifyContent: 'flex-end', cursor: 'pointer' }}>
                <FormPagination formPage={formPage} setFormPage={setFormPage} />
            </div>
            {formPage === 1 && <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Submit"}
            </Button>}
        </div>
      </form>
    </Form>
  )
}
