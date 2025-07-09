"use client"
import { UserStats } from '@/interfaces/UserStats';
import { updateUserProfile, useSession, getAvatarUrl } from '@/lib/auth-client';
import { Edit, Calendar, TrendingUp } from 'lucide-react'
import React, { useState } from 'react'
import ImageUploader from '@/components/ImageUploader';

interface CustomUser {
  username?: string;
  name?: string;
  image?: string;
  id?: string;
  selectedPfp?: number;
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

  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState((session?.user as CustomUser)?.username || session?.user?.name || "");
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);

  const handleUploadSuccess = (imageUrl: string) => {
    setUploadMessage('Upload successful!');
    // Update session user image if available
    if (session?.user) {
      (session.user as any).image = imageUrl;
    }
    // Clear message after 3 seconds
    setTimeout(() => setUploadMessage(null), 3000);
  };

  const handleUploadError = (error: string) => {
    setUploadMessage(`Upload failed: ${error}`);
    // Clear message after 5 seconds
    setTimeout(() => setUploadMessage(null), 5000);
  };
  return (
    <div className="flex items-center space-x-4">
      
      <ImageUploader
        currentImageUrl={getAvatarUrl(session?.user as CustomUser)}
        onUploadSuccess={handleUploadSuccess}
        onUploadError={handleUploadError}
        size="md"
        shape="circle"
        userId={session?.user?.id}
        alt="Profile picture"
      />
      <div>
        <div className="flex items-center space-x-2">
          {editingName ? (
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onBlur={async () => {
                setEditingName(false);
                if (newName && newName !== ((session?.user as CustomUser)?.username || session?.user?.name) || newName !== "") {
                  await updateUserProfile({
                    username: newName,
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
                {(session?.user as CustomUser)?.username || session?.user?.name || "Unknown User"}
              </h1>
              <Edit className="w-4 h-4 text-gray-500 cursor-pointer" onClick={() => setEditingName(true)} />
            </>
          )}
        </div>
        {uploadMessage && (
          <p className={`text-sm mt-1 ${uploadMessage.includes('failed') ? 'text-red-500' : 'text-green-500'}`}>
            {uploadMessage}
          </p>
        )}
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
