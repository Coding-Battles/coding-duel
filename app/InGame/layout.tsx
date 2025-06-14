"use client"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { InGameSideBar } from "@/components/inGameSideBar"
import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"
import { usePathname } from "next/navigation"

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isFinished = pathname.includes("finished");

  return (
    <div className="flex h-[100%] w-[100%] w-max-screen">
      <SidebarProvider>
        <InGameSideBar title="Reverse Linked List" difficulty="easy" QuestionContent={undefined} ExtraDetailsContent={undefined}/>
        <SidebarInset>
          <header className="flex h-16 shrink-0 justify-between items-center gap-2 border-b px-4">
            <SidebarTrigger className="-ml-1" />
            <h1 className="text-lg font-semibold">BATTLE</h1>
            {!isFinished ?
              <div className="flex gap-2 justify-self-end">
              <Button className='text-black border-black border-2 cursor-pointer bg-transparent hover:bg-gray-200'>
                Run
              </Button>
              <Button className='text-green-300 border-green-300 border-2 cursor-pointer bg-transparent hover:bg-green-100'>
                <Check/>
                Submit
              </Button>
            </div> : <div></div>}
          </header>
          <div className="flex flex-1 flex-col gap-4 p-4">
            {children}
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  )
}