"use client"

import * as React from "react"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

interface CheckboxProps {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
  className?: string
  children?: React.ReactNode
  id?: string
}

function Checkbox({ 
  checked = false, 
  onCheckedChange, 
  className, 
  children, 
  id,
  ...props 
}: CheckboxProps) {
  return (
    <div className="flex items-center space-x-2">
      <button
        type="button"
        role="checkbox"
        aria-checked={checked}
        id={id}
        onClick={() => onCheckedChange?.(!checked)}
        className={cn(
          "peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          checked ? "bg-primary text-primary-foreground" : "bg-transparent",
          className
        )}
        {...props}
      >
        {checked && (
          <Check className="h-3 w-3 text-current" />
        )}
      </button>
      {children && (
        <label 
          htmlFor={id}
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
        >
          {children}
        </label>
      )}
    </div>
  )
}

export { Checkbox }