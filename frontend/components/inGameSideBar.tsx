import { QuestionData } from "@/types/question";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
} from "@/components/ui/sidebar";

interface InGameSideBarProps {
  questionData: QuestionData | null;
}

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

  return (
    <Sidebar variant="sidebar">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{questionData.title}</SidebarGroupLabel>
          <SidebarGroupContent>
            <div className="space-y-4 p-4">
              <div
                className="prose prose-sm max-w-none text-sm"
                dangerouslySetInnerHTML={{ __html: questionData.description_html }}
              />
            </div>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}