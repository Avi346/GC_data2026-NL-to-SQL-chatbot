import React, { useState, type MouseEvent } from 'react';

interface Ripple {
  id: number;
  x: number;
  y: number;
  size: number;
}

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  interactive?: boolean;
  glow?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  interactive = false,
  glow = false,
  padding = 'md'
}) => {
  const [ripples, setRipples] = useState<Ripple[]>([]);

  const handleClick = (e: MouseEvent<HTMLDivElement>) => {
    if (!interactive) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    const newRipple: Ripple = {
      id: Date.now(),
      x,
      y,
      size
    };
    
    setRipples(prev => [...prev, newRipple]);
    setTimeout(() => {
      setRipples(prev => prev.filter(r => r.id !== newRipple.id));
    }, 800);
  };

  const paddingClass = {
    none: 'p-0',
    sm: 'p-5',
    md: 'p-6',
    lg: 'p-8'
  }[padding];

  const baseClasses = `rounded-2xl relative overflow-hidden ${paddingClass} ${className}`;
  const glassClasses = interactive ? 'glass-interactive cursor-pointer glass-panel' : 'glass-panel';
  
  return (
    <div className={`${baseClasses} ${glassClasses}`} onClick={handleClick}>
      {/* Liquid Ripple Layer */}
      {interactive && (
        <div className="ripple-container">
          {ripples.map(ripple => (
            <span
              key={ripple.id}
              className="ripple"
              style={{
                top: ripple.y,
                left: ripple.x,
                width: ripple.size,
                height: ripple.size
              }}
            />
          ))}
        </div>
      )}

      {/* Subtle Glow Effect Layer */}
      {glow && (
        <div className="absolute -top-24 -right-24 w-80 h-80 bg-[#ff4756]/10 rounded-full blur-[100px] pointer-events-none z-0" />
      )}
      
      {children}
    </div>
  );
};
