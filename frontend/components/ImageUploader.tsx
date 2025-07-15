"use client";

import React, { useState, useRef, ChangeEvent } from 'react';
import { Edit, Upload, Loader2 } from 'lucide-react';
import Image from 'next/image';

export interface ImageUploaderProps {
  currentImageUrl?: string;
  onUploadSuccess?: (imageUrl: string) => void;
  onUploadError?: (error: string) => void;
  onUploadStart?: () => void;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  uploadEndpoint?: string;
  userId?: string;
  accept?: string;
  maxSizeBytes?: number;
  disabled?: boolean;
  showEditIcon?: boolean;
  alt?: string;
}

const sizeClasses = {
  sm: 'w-12 h-12',
  md: 'w-16 h-16', 
  lg: 'w-24 h-24',
  xl: 'w-32 h-32'
};

const iconSizes = {
  sm: 'w-3 h-3',
  md: 'w-4 h-4',
  lg: 'w-6 h-6', 
  xl: 'w-8 h-8'
};

export default function ImageUploader({
  currentImageUrl,
  onUploadSuccess,
  onUploadError,
  onUploadStart,
  size = 'md',
  className = '',
  uploadEndpoint,
  userId,
  accept = 'image/*',
  maxSizeBytes = 5 * 1024 * 1024, // 5MB default
  disabled = false,
  showEditIcon = true,
  alt = 'Upload image'
}: ImageUploaderProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);


  const validateFile = (file: File): string | null => {
    if (file.size > maxSizeBytes) {
      return `File size must be less than ${Math.round(maxSizeBytes / 1024 / 1024)}MB`;
    }

    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      return 'Please select a valid image file (JPEG, PNG, GIF, or WebP)';
    }

    return null;
  };

  const handleFileSelect = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || disabled) return;

    // Validate userId is provided
    if (!userId && !uploadEndpoint) {
      onUploadError?.('User ID is required for upload');
      return;
    }

    // Validate file
    const validationError = validateFile(file);
    if (validationError) {
      onUploadError?.(validationError);
      return;
    }

    // Create preview
    const preview = URL.createObjectURL(file);
    setPreviewUrl(preview);
    setIsUploading(true);
    onUploadStart?.();

    // Upload file
    try {
      const formData = new FormData();
      formData.append('image', file);

      const endpoint = uploadEndpoint || `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/image/${userId}`;
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        onUploadSuccess?.(data.path || preview);
      } else {
        console.error('Upload failed:', {
          status: response.status,
          statusText: response.statusText,
          data: data,
          endpoint: endpoint
        });
        throw new Error(data.detail || data.message || `Upload failed: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      onUploadError?.(error instanceof Error ? error.message : 'Upload failed');
      // Revert preview on error
      setPreviewUrl(null);
      URL.revokeObjectURL(preview);
    } finally {
      setIsUploading(false);
    }

    // Clear file input
    event.target.value = '';
  };

  const handleClick = () => {
    if (!disabled && !isUploading) {
      fileInputRef.current?.click();
    }
  };

  const displayImage = previewUrl || currentImageUrl;

  return (
    <div className={`relative ${className} rounded-full`}>
      {displayImage ? (
        <Image
          src={displayImage}
          alt={alt}
          width={100}
          height={100}
          className="w-full h-auto rounded-full object-cover bg-muted transition-all duration-200"
        />
      ) : (
        <div className="w-full h-auto rounded bg-muted flex items-center justify-center aspect-square">
          <Upload className="w-6 h-6 text-gray-400" />
        </div>
      )}

      {/* Overlay - Different behavior for first upload vs re-upload */}
      <button 
        onClick={handleClick}
        disabled={disabled || isUploading}
        className={`
          ${displayImage 
            ? 'rounded-full absolute top-0 w-full h-full' 
            : 'absolute inset-0'
          }
          ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
          ${isUploading ? 'bg-black/70' : 'opacity-0 hover:opacity-100 hover:bg-black/30'}
          flex items-center justify-center transition-all duration-200
          ${showEditIcon ? '' : 'opacity-0'}
        `}
      >
        {isUploading ? (
          <Loader2 className="w-4 h-4 text-white animate-spin" />
        ) : showEditIcon ? (
          <Edit className="w-4 h-4 text-white transition-opacity" />
        ) : null}
      </button>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled || isUploading}
      />
    </div>
  );
}