import { Calendar, Home, Inbox, Search, Settings } from "lucide-react";
import Link from "next/link"; // Add this import
import { Collapsible } from "@/components/ui/collapsible";
import {
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";
import { QuestionData } from "@/types/question";

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
} from "@/components/ui/sidebar";

interface InGameSideBarProps {
  questionData: QuestionData | null;
}

function SideBarCollapsableArrow() {
  return (
    <ChevronDown className="h-4 w-4 transition-transform duration-200 group-data-[state=closed]/collapsible:rotate-90" />
  );
}

const getDifficultyColor = (difficulty: string) => {
  switch (difficulty.toLowerCase()) {
    case "easy":
      return "text-green-600 bg-green-100";
    case "medium":
      return "text-yellow-600 bg-yellow-100";
    case "hard":
      return "text-red-600 bg-red-100";
    default:
      return "text-gray-600 bg-gray-100";
  }
};

export function InGameSideBar({ questionData }: InGameSideBarProps) {
  if (!questionData) {
    return (
      <Sidebar variant="sidebar">
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Loading...</SidebarGroupLabel>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
    );
  }

  const questionContent = (
    <div className="space-y-4 p-2">
      {/* Header with difficulty and tags */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(
              questionData.difficulty
            )}`}
          >
            {questionData.difficulty}
          </span>
        </div>

        <div className="flex flex-wrap gap-1">
          {questionData.tags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-md"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Description */}
      <div className="space-y-2">
        <h4 className="font-semibold text-sm">Description</h4>
        <div
          className="prose prose-sm max-w-none text-sm"
          dangerouslySetInnerHTML={{ __html: questionData.description_html }}
        />
      </div>

      {/* Examples */}
      <div className="space-y-2">
        <h4 className="font-semibold text-sm">Examples</h4>
        <div
          className="prose prose-sm max-w-none text-sm"
          dangerouslySetInnerHTML={{ __html: questionData.examples_html }}
        />
      </div>

      {/* Constraints */}
      <div className="space-y-2">
        <h4 className="font-semibold text-sm">Constraints</h4>
        <div
          className="prose prose-sm max-w-none text-sm"
          dangerouslySetInnerHTML={{ __html: questionData.constraints_html }}
        />
      </div>
    </div>
  );

  const extraDetailsContent = (
    <div className="space-y-4 p-2">
      {/* Solution Approach */}
      {/* <div className="space-y-2">
        <h4 className="font-semibold text-sm">Solution Approach</h4>
        <div className="text-sm space-y-1">
          <div className="text-gray-500">
            Solution details will be available during the contest.
          </div>
        </div>
      </div> */}
    </div>
  );

  return (
    <Sidebar variant="sidebar">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{questionData.title}</SidebarGroupLabel>
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
                  <CollapsibleContent>{questionContent}</CollapsibleContent>
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
                  <CollapsibleContent>{extraDetailsContent}</CollapsibleContent>
                </SidebarMenuItem>
              </Collapsible>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
