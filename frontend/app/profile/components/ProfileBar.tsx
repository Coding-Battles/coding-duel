"use client"
import { Button } from '@/components/ui/button';
import { UserStats } from '@/interfaces/UserStats';
import { getSession, useSession } from '@/lib/auth-client';
import { Calendar, Edit, TrendingUp, User } from 'lucide-react'
import React, { ChangeEvent, useEffect, useRef, useState } from 'react'

export const ProfileBar = () => {
  const userStats: UserStats = {
    totalSolved: 342,
    easySolved: 156,
    mediumSolved: 142,
    hardSolved: 44,
    totalSubmissions: 1247,
    acceptanceRate: 67.2,
    ranking: 12543,
    streak: 23
  };

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file ) {
      setSelectedFile(file);
      console.log('Selected file:', file.name);
    }
  };

  const {data: session} = useSession();

  console.log("Session data:", session);

    
  return (
    <div className="flex items-center space-x-4">
      
      <div className="w-16 h-16 bg-orange-500 rounded-full flex items-center justify-center relative">
        <User className="w-8 h-8 text-white" />
        <button className='w-16 h-16 absolute opacity-0 hover:opacity-50 rounded-full bg-white flex items-center justify-center transition cursor-pointer z-30' onClick={() => {(fileInputRef.current?.click())}}>
          {<Edit/>}
        </button>
        <input className='hidden' type="file" accept="image/*" ref={fileInputRef} onChange={handleFileChange} />
      </div>
      <div>
        <h1 className="text-2xl font-bold text-gray-800">{session?.user?.name || "Unknown User"}</h1>
        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <Calendar className="w-4 h-4" />
            <span>Joined Jan 2023</span>
          </div>
          <div className="flex items-center space-x-1">
            <TrendingUp className="w-4 h-4" />
            <span>Rank #{userStats.ranking.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
