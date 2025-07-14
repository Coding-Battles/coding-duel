import React from 'react'

interface FeatureProp {
  index: number;
  icon: React.ReactNode;
  title: string;
  description: string;
  image: string;
  size: string;
}

export const FeatureBoxes = ({index, icon, title, description, image, size} : FeatureProp) => {
  return (
    <div key={index} className="relative h-auto p-6 transition-shadow border-2 border-solid rounded-lg border-border bg-card hover:shadow-lg">
      {/* Icon in top left */}
      <div className="absolute flex items-center justify-center w-10 h-10 rounded-lg lg:w-14 lg:h-14 top-4 left-4 bg-accent/10">
        {icon}
      </div>
      
      {/* Content layout */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr] items-start gap-8 h-auto">
        {/* Text content on the left */}
        <div className="flex-1 mt-20">
          <h3 className="mb-3 text-lg font-semibold lg:text-xl">
            {title}
          </h3>
          <p className="text-sm leading-relaxed text-foreground/70 lg:text-base">
            {description}
          </p>
        </div>
        
        {/* Image on the right */}
        <div className="relative p-3 overflow-hidden shadow-inner rounded-xl bg-gradient-to-br from-accent/5 to-accent/10">
          <div className="relative w-full aspect-video">
            <img 
              src={image} 
              alt={title}
              className="w-full h-full object-cover rounded-lg shadow-md transition-transform duration-300 hover:scale-[1.02] border border-border/20"
            />
            {/* Enhanced placeholder when image fails to load */}
            <div className="absolute inset-0 flex items-center justify-center hidden w-full h-full text-sm font-medium border rounded-lg bg-gradient-to-br from-accent/10 to-accent/20 text-accent/60 border-border/20">
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-3 opacity-50">
                  <svg fill="currentColor" viewBox="0 0 24 24">
                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                  </svg>
                </div>
                Feature Preview
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
