"use client"
import { Button } from '@/components/ui/button';
import { UserStats } from '@/interfaces/UserStats';
import { authClient, getSession, useSession } from '@/lib/auth-client';
import { Calendar, Edit, TrendingUp, User } from 'lucide-react'
import React, { ChangeEvent, useEffect, useRef, useState } from 'react'

interface ProfileBarProps {
  id: string;
}

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

export const ProfileBar = () => {

  const {data: session} = useSession();
  console.log("Session data:", session);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewURL, setPreviewURL] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null); //for displaying messages if needed
  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState(session?.user?.name || "");


  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewURL(URL.createObjectURL(file));  // generate preview

      const formData = new FormData();
      formData.append("image", file);

      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/image/${session?.user.id}`, {
          method: "POST",
          body: formData,
        });

        const data = await res.json();
        if (res.ok) {
          setMessage(`Upload successful: ${data.path}`);
          if(session) session.user.image = data.path; // update session user image
        } else {
          setMessage(`Upload failed: ${data.detail || "Unknown error"}`);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        setMessage('Failed to upload image. Please try again.');
      }
    }
  }
  return (
    <div className="flex items-center space-x-4">
      
      <div className="w-16 h-16  rounded-full flex items-center justify-center relative">
        <img
          src={previewURL ?? session?.user.image ?? "/default-avatar.png"}
          className="h-full w-full rounded-full object-cover"
        />
        <button className='w-full h-full rounded-full absolute opacity-0 hover:opacity-50 bg-white flex items-center justify-center transition cursor-pointer z-30' onClick={() => {(fileInputRef.current?.click())}}>
          {<Edit/>}
        </button>
        <input className='hidden' type="file" accept="image/*" ref={fileInputRef} onChange={handleFileUpload} />
      </div>
      <div>
        <div className="flex items-center space-x-2">
          {editingName ? (
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onBlur={async () => {
                setEditingName(false);
                if (newName && newName !== session?.user?.name || newName !== "") {
                  await authClient.updateUser({
                    name: newName,
                  })
                }
              }}
              className="text-2xl font-bold border-b border-gray-300 outline-none"
              autoFocus
            />
          ) : (
            <>
              <h1
                className="text-2xl font-bold text-gray-800 cursor-pointer"
                onClick={() => setEditingName(true)}
              >
                {session?.user?.name || "Unknown User"}
              </h1>
              <Edit className="w-4 h-4 text-gray-500 cursor-pointer" onClick={() => setEditingName(true)} />
            </>
          )}
        </div>
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
