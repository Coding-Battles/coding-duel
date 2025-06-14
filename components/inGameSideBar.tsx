import { Calendar, Home, Inbox, Search, Settings } from "lucide-react"
import Link from "next/link" // Add this import
import {Collapsible} from "@/components/ui/collapsible"
import { CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { ChevronDown } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"

type Difficulty = "easy" | "medium" | "hard";

interface InGameSideBarProps {
  title: string;
  difficulty: Difficulty;
  QuestionContent: React.ReactNode | null;
  ExtraDetailsContent: React.ReactNode | null;
}

function SideBarCollapsableArrow() {
  return (
    <ChevronDown className="h-4 w-4 transition-transform duration-200 group-data-[state=closed]/collapsible:rotate-90" />
  )
}


export function InGameSideBar({ title, difficulty, QuestionContent, ExtraDetailsContent }: InGameSideBarProps) {
  return (
    <Sidebar variant="sidebar">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{title? title : "Question"}</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
                <Collapsible defaultOpen className="group/collapsible">
                  <SidebarMenuItem>
                    <CollapsibleTrigger asChild>
                      <SidebarMenuButton>
                        <div className="flex justify-between gap-2 w-full">
                          Question Details
                          {SideBarCollapsableArrow()}
                        </div>
                      </SidebarMenuButton>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      {QuestionContent ? QuestionContent : <p>No question content available</p>}
                    </CollapsibleContent>
                  </SidebarMenuItem>
                </Collapsible>
                <Collapsible defaultOpen className="group/collapsible">
                  <SidebarMenuItem>
                    <CollapsibleTrigger asChild>
                      <SidebarMenuButton>
                        <div className="flex justify-between gap-2 w-full">
                          Extra Details
                          {SideBarCollapsableArrow()}
                        </div>
                      </SidebarMenuButton>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      {ExtraDetailsContent ? ExtraDetailsContent : <p>No extra details content available</p>}
                    </CollapsibleContent>
                  </SidebarMenuItem>
                </Collapsible>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}