"use client"

import * as React from "react"
import {
  CaretSortIcon,
  PlusIcon,
  MagicWandIcon,
  PersonIcon,
  Pencil2Icon,
  TrashIcon,
} from "@radix-ui/react-icons"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Skeleton
} from "@/components/ui/skeleton"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"
import AddPromotionForm from "@/components/addpromotionform"

export type Promotion = {
  id: number;
  is_active: boolean;
  promotion_name: string;
  display_description: string | null;
  ai_description: string | null;
  is_ai_generated: boolean;
  // Add additional fields from your data sample here
  ai_discount_dollars_max: number | null;
  ai_discount_dollars_min: number | null;
  ai_discount_percent_max: number | null;
  ai_discount_percent_min: number | null;
  discount_code: string | null;
  discount_dollars: number | null;
  discount_percent: number | null;
  display_title: string | null;
  image_url: string | null;
  impulse_user_id: number;
};

interface PromotionsTableProps {
  session_user_id: any;
}

export function PromotionsTable({ session_user_id }: PromotionsTableProps) {
  const [data, setData] = React.useState<Promotion[]>([]);
  const [isLoading, setIsLoading] = React.useState(true); // Add loading state
  const [editPromotionDialogOpen, setEditPromotionDialogOpen] = React.useState(false);
  const [addPromotionDialogOpen, setAddPromotionDialogOpen] = React.useState(false);

   async function fetchData() {
    setIsLoading(true); // Set loading to true when fetch starts
    fetch(`http://localhost:5000/user_promotions/${session_user_id}`)
      .then(response => response.json())
      .then(data => {
        //console.log(data)
        setData(data);
      })
      .finally(() => setIsLoading(false)); // Set loading to false when fetch is complete
    }

  React.useEffect(() => {
     fetchData();
  }, [session_user_id]);

  const columns: ColumnDef<Promotion>[] = [
    // {
    //   id: "select",
    //   header: ({ table }) => (
    //     <Checkbox
    //       checked={
    //         table.getIsAllPageRowsSelected() ||
    //         (table.getIsSomePageRowsSelected() && "indeterminate")
    //       }
    //       onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
    //       aria-label="Select all"
    //     />
    //   ),
    //   cell: ({ row }) => (
    //     <Checkbox
    //       checked={row.getIsSelected()}
    //       onCheckedChange={(value) => row.toggleSelected(!!value)}
    //       aria-label="Select row"
    //     />
    //   ),
    //   enableSorting: false,
    //   enableHiding: false,
    // },
    {
      accessorKey: "is_active",
      header: "Active",
      cell: ({ row }) => (
        <div>
          {/* {row.getValue("is_active") ? <CheckIcon /> : <CrossCircledIcon />} */}
          <Switch 
            defaultChecked={row.getValue("is_active")} 
            onCheckedChange={(checked) => {
              fetch(`http://localhost:5000/promotions/update/${row.original.id}`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ is_active: checked }),
              })
              .then(response => response.json())
              .then(data => {
                // emit toast
                toast(`'${row.getValue("promotion_name")}' promotion set to ${data['values']['is_active'] ? "active" : "inactive"}.`)
              })
            }}
          />
        </div>
      ),
    },
    {
      accessorKey: "promotion_name",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Name
            <CaretSortIcon className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => <div className="lowercase">{row.getValue("promotion_name")}</div>,
    },
    {
      accessorKey: "display_description",
      header: () => <div className="">Description</div>,
      cell: ({ row }) => {
        // First, try to get the display_description
        let res : any = row.getValue("display_description");
        // If display_description is null or undefined, use ai_description
        if (res == null) {
          res = row.original.ai_description;
        }
        let sliced : String = res.length > 30 ? res.slice(0, 30) + '...' : res
        return (<div>
          {sliced}
        </div>);
      },
    },
    {
      accessorKey: "is_ai_generated",
      header: () => <div className="">AI / Manual</div>,
      cell: ({ row }) => {
        return (<div>
          {row.getValue("is_ai_generated") ? <MagicWandIcon width="20" height="20" /> : <PersonIcon width="20" height="20" />}
        </div>);
      },
    },
    {
      id: "edit",
      header: "Edit",
      enableHiding: false,
      cell: ({ row }) => {
        const promotion = row.original
  
        return (
          <Dialog open={editPromotionDialogOpen} onOpenChange={setEditPromotionDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="icon">
                    <Pencil2Icon width="20" height="20" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                  <DialogHeader>
                    <DialogTitle>Edit promotion</DialogTitle>
                    <DialogDescription>
                      Make changes to your promotion. Click save when you're done.
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target as HTMLFormElement);
                    const formProps = Object.fromEntries(formData);
                    fetch(`http://localhost:5000/promotions/update/${promotion.id}`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify(formProps),
                    })
                    .then(response => response.json())
                    .then(data => {
                      // Close the dialog after form submission
                      setEditPromotionDialogOpen(false);
                      fetchData();
                      // emit toast
                      toast(`'${row.getValue("promotion_name")}' promotion successfully edited.`)
                    })
                    .catch((error) => {
                      //console.error('Error:', error);
                    });
                  }}>
                    <div id="promotionEditFormContent" className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="name" className="text-right">
                          Promotion Name
                        </Label>
                        <Input
                          name="promotion_name"
                          defaultValue={promotion.promotion_name}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="description" className="text-right">
                          Description
                        </Label>
                        <Input
                          name={promotion.display_description ? "display_description" : "ai_description"}
                          defaultValue={promotion.display_description ? promotion.display_description : promotion.ai_description || ""}
                          className="col-span-3"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="submit">Save changes</Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
          </Dialog>
        )
      },
    },
    {
      id: "delete",
      header: "Delete",
      enableHiding: false,
      cell: ({ row }) => {
        const promotion = row.original
  
        return (
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button className="bg-red-600 hover:bg-red-800" size="icon">
                <TrashIcon width="20" height="20" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete this promotion?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. This will permanently delete the promotion <i>{promotion.promotion_name}</i>.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  fetch(`http://localhost:5000/promotions/delete/${promotion.id}`, {
                    method: 'DELETE'
                  })
                  .then(response => response.json())
                  .then(data => {
                    fetchData()
                    // emit toast
                    toast(`'${row.getValue("promotion_name")}' promotion successfully deleted.`)
                  })
                }}>
                  <AlertDialogAction type="submit" className="bg-red-600 hover:bg-red-800">Continue</AlertDialogAction>
                </form>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )
      },
    },
  ]

  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  })

  return (
    <div className="w-full">
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter promotions by name..."
          value={(table.getColumn("promotion_name")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("promotion_name")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />

        <Dialog open={addPromotionDialogOpen} onOpenChange={setAddPromotionDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" className="ml-auto bg-gray-900 text-white hover:bg-gray-700 hover:text-white">
              <PlusIcon className="mr-2 h-4 w-4" /> New promotion 
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <AddPromotionForm session_user_id={session_user_id} dialogSetter={setAddPromotionDialogOpen} tableDataFetcher={fetchData} />
          </DialogContent>
        </Dialog>

        {/* <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="ml-auto">
              Columns <ChevronDownIcon className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter((column) => column.getCanHide())
              .map((column) => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) =>
                      column.toggleVisibility(!!value)
                    }
                  >
                    {column.id}
                  </DropdownMenuCheckboxItem>
                )
              })}
          </DropdownMenuContent>
        </DropdownMenu> */}
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              // Render skeleton components when data is loading
              Array.from({ length: 5 }).map((_, index) => (
                <TableRow key={index}>
                  {Array.from({ length: columns.length }).map((_, cellIndex) => (
                    <TableCell key={cellIndex}>
                      <Skeleton className="w-[100px] h-[20px] rounded-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : table.getRowModel().rows?.length ? (
              // Your existing code for rendering rows
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        {/* <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div> */}
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}

