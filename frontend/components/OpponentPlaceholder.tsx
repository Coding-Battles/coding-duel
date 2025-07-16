import React from 'react';
import { cn } from "@/lib/utils";

interface OpponentPlaceholderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function OpponentPlaceholder({ 
  size = 'lg',
  className = ""
}: OpponentPlaceholderProps) {
  // Size configurations
  const sizeConfig = {
    sm: { container: 'w-20 h-20', avatar: 'w-16 h-16', text: 'text-xs' },
    md: { container: 'w-32 h-32', avatar: 'w-28 h-28', text: 'text-sm' },
    lg: { container: 'w-40 h-40', avatar: 'w-36 h-36', text: 'text-base' }
  };

  const config = sizeConfig[size];

  return (
    <div className={cn("flex flex-col items-center", className)}>
      {/* Main Avatar Container */}
      <div className={cn(
        "relative transition-all duration-300 rounded-xl",
        config.container
      )}>
        {/* Theme-consistent border */}
        <div className="w-full h-full rounded-xl p-2 border-gradient-player2">
          {/* Matrix Rain Container */}
          <div className="w-full h-full rounded-lg bg-background flex items-center justify-center relative overflow-hidden">
            
            {/* Matrix Rain Background */}
            <div className="matrix-rain-container">
              {/* Additional matrix columns */}
              <div className="matrix-column-1">
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
                ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・."=*+-&lt;&gt;¦|çﾘｸ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&amp;*(){}[]&lt;&gt;/\?!.;:'"
              </div>
              <div className="matrix-column-2">
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
                01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ{"{"}{"}"}{`[]()<>/\\;:'".,?!@#$%^&*+-=_|~`}abcdefghijklmnopqrstuvwxyz
              </div>
              <div className="matrix-column-3">
                ¿¡÷×±∞∂∆∇∑∏∫∮∯∰∱∲∳∴∵∶∷∸∹∺∻∼∽∾∿≀≁≂≃≄≅≆≇≈≉≊≋≌≍≎≏≐≑≒≓≔≕≖≗≘≙≚≛≜≝≞≟≠≡≢≣≤≥≦≧≨≩≪≫≬≭≮≯≰≱≲≳≴≵≶≷≸≹≺≻≼≽≾≿⊀⊁⊂⊃⊄⊅⊆⊇⊈⊉⊊⊋⊌⊍⊎⊏⊐⊑⊒⊓⊔⊕⊖⊗⊘⊙⊚⊛⊜⊝⊞⊟⊠⊡⊢⊣⊤⊥⊦⊧⊨⊩⊪⊫⊬⊭⊮⊯⊰⊱⊲⊳⊴⊵⊶⊷⊸⊹⊺⊻⊼⊽⊾⊿⋀⋁⋂⋃⋄⋅⋆⋇⋈⋉⋊⋋⋌⋍⋎⋏⋐⋑⋒⋓⋔⋕⋖⋗⋘⋙⋚⋛⋜⋝⋞⋟⋠⋡⋢⋣⋤⋥⋦⋧⋨⋩⋪⋫⋬⋭⋮⋯⋰⋱⋲⋳⋴⋵⋶⋷⋸⋹⋺⋻⋼⋽⋾⋿
              </div>
            </div>
            
            {/* Centered Question Mark */}
            <div className="matrix-question-mark text-8xl font-bold">
              ?
            </div>
          </div>
        </div>
      </div>

      {/* Simple Status Text */}
      <div className={cn(
        "mt-3 text-center font-bold",
        config.text
      )}>
        <span className="text-foreground/60">
          Searching...
        </span>
      </div>
    </div>
  );
}