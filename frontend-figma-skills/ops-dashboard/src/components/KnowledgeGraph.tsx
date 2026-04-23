import React from 'react';
import { GlassCard } from './GlassCard';

interface Node {
  id: string;
  label: string;
  group: 'channel' | 'user' | 'type';
  val: number;
}

interface Edge {
  source: string;
  target: string;
  value: number;
}

interface KnowledgeGraphProps {
  nodes: Node[];
  edges: Edge[];
}

export const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ nodes }) => {
  // Mock layout to simulate d3-force positioning without heavy dependencies
  // Maps group to approximate coordinate areas for visual structure
  const getCoordinates = (index: number, total: number, group: string) => {
    let cx = 50, cy = 50, radius = 35;
    
    if (group === 'channel') { cx = 50; cy = 50; radius = 20; }
    else if (group === 'user') { cx = 20; cy = 50; radius = 30; }
    else if (group === 'type') { cx = 80; cy = 50; radius = 30; }

    const angle = (index / total) * Math.PI * 2;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle)
    };
  };

  const groupNodes = (nodes: Node[]) => {
    const grouped: Record<string, typeof nodes> = { channel: [], user: [], type: [] };
    nodes.forEach(n => grouped[n.group].push(n));
    return grouped;
  };
  
  const grouped = groupNodes(nodes);

  return (
    <GlassCard padding="none" className="h-[600px] w-full flex items-center justify-center relative overflow-hidden bg-[radial-gradient(ellipse_at_center,rgba(255,71,86,0.05)_0%,transparent_70%)]">
      
      {/* Background Grid */}
      <div 
        className="absolute inset-0 opacity-10 pointer-events-none" 
        style={{ 
          backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)', 
          backgroundSize: '40px 40px' 
        }} 
      />

      <div className="relative w-full h-full p-10">
        {/* Render simulated SVG edges */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
          <defs>
            <linearGradient id="edgeGlow" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(255,71,86,0.1)" />
              <stop offset="50%" stopColor="rgba(255,71,86,0.4)" />
              <stop offset="100%" stopColor="rgba(255,71,86,0.1)" />
            </linearGradient>
          </defs>
          <path d="M 250 250 Q 400 350 550 250" fill="none" stroke="url(#edgeGlow)" strokeWidth="2" strokeDasharray="4 4" className="animate-pulse" />
          <path d="M 250 350 Q 400 250 550 350" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
          <path d="M 400 200 L 400 400" fill="none" stroke="rgba(255,71,86,0.2)" strokeWidth="1.5" />
        </svg>

        {/* Render simulated Nodes */}
        {Object.entries(grouped).map(([groupKey, groupNodes]) => (
          groupNodes.map((node, i) => {
            const pos = getCoordinates(i, groupNodes.length, groupKey);
            const size = node.val * 2 + 30; // Scale base size
            const glowColor = groupKey === 'channel' ? 'rgba(255,71,86,0.6)' : groupKey === 'type' ? 'rgba(255,109,120,0.6)' : 'rgba(255,255,255,0.4)';
            const bgColor = groupKey === 'channel' ? 'bg-[#ff4756]/20' : groupKey === 'type' ? 'bg-[#ff6d78]/20' : 'bg-white/10';
            const brColor = groupKey === 'channel' ? 'border-[#ff4756]/50' : groupKey === 'type' ? 'border-[#ff6d78]/50' : 'border-white/20';

            return (
              <div 
                key={node.id}
                className={`absolute -translate-x-1/2 -translate-y-1/2 ${bgColor} border ${brColor} rounded-full flex items-center justify-center cursor-pointer transition-all hover:scale-110 glass-panel shadow-lg group`}
                style={{
                  left: `${pos.x}%`,
                  top: `${pos.y}%`,
                  width: `${size}px`,
                  height: `${size}px`,
                  boxShadow: `0 0 20px ${glowColor}`,
                  zIndex: 10
                }}
              >
                <span className="text-[10px] font-bold text-white text-center leading-tight drop-shadow-md px-2">
                  {node.label}
                </span>

                {/* Tooltip on hover */}
                <div className="absolute top-full mt-2 w-max px-3 py-1.5 bg-black/90 border border-white/10 rounded-md text-xs text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                  <span className="font-mono text-[#ff4756]">{node.val}</span> connections
                </div>
              </div>
            );
          })
        ))}
      </div>
    </GlassCard>
  );
};
