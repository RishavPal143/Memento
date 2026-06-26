'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  Calendar, 
  Tag, 
  ExternalLink, 
  Trash2, 
  Copy, 
  Check, 
  Eye, 
  Award 
} from 'lucide-react';
import { useDeleteMemory } from '@/lib/hooks';

interface MemoryCardProps {
  id: number;
  title: string | null;
  url: string;
  summary: string | null;
  tags: string[] | null;
  importance_score: number | null;
  created_at: string;
}

export default function MemoryCard({
  id,
  title,
  url,
  summary,
  tags,
  importance_score,
  created_at
}: MemoryCardProps) {
  const [copied, setCopied] = useState(false);
  const deleteMutation = useDeleteMemory();

  let domain = url;
  try {
    domain = new URL(url).hostname;
  } catch {
    // fallback to raw URL
  }

  const handleCopy = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this memory?')) {
      deleteMutation.mutate(id);
    }
  };

  const formattedDate = new Date(created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });

  // Decide score badge styling
  const score = importance_score || 50;
  let scoreColor = 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  if (score >= 80) {
    scoreColor = 'bg-green-500/10 text-green-500 border-green-500/20';
  } else if (score >= 60) {
    scoreColor = 'bg-blue-500/10 text-blue-500 border-blue-500/20';
  } else if (score >= 40) {
    scoreColor = 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
  } else {
    scoreColor = 'bg-red-500/10 text-red-500 border-red-500/20';
  }

  return (
    <div className="glass-panel glass-card-hover rounded-2xl p-5 border border-border-app flex flex-col justify-between h-full group relative overflow-hidden">
      {/* Background glow for premium look */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-all duration-300 pointer-events-none" />
      
      <div>
        {/* Card Header (Domain and Importance Score) */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-xs font-semibold text-primary truncate max-w-[70%]">
            {domain}
          </span>
          <div className={`flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${scoreColor}`}>
            <Award className="w-3.5 h-3.5" />
            <span>{score}</span>
          </div>
        </div>

        {/* Title */}
        <h3 className="font-bold text-md leading-snug text-fg-app group-hover:text-primary transition-colors duration-200 line-clamp-2 mb-2">
          <Link href={`/memory/${id}`}>
            {title || 'Untitled Webpage'}
          </Link>
        </h3>

        {/* Summary Snippet */}
        <p className="text-xs text-muted-app leading-relaxed line-clamp-3 mb-4 font-normal">
          {summary || 'No description extracted. Click to view webpage content.'}
        </p>
      </div>

      <div>
        {/* Tags row */}
        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {tags.map((tag) => (
              <span 
                key={tag} 
                className="text-[10px] font-semibold bg-card-app border border-border-app px-2 py-0.5 rounded-md text-muted-app flex items-center gap-1"
              >
                <Tag className="w-2.5 h-2.5" />
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Footer actions */}
        <div className="flex items-center justify-between border-t border-border-app/50 pt-3 mt-auto">
          <span className="text-[10px] text-muted-app flex items-center gap-1 font-medium">
            <Calendar className="w-3.5 h-3.5" />
            {formattedDate}
          </span>
          
          <div className="flex items-center gap-1">
            {/* View Details */}
            <Link 
              href={`/memory/${id}`}
              className="p-1.5 bg-card-app hover:bg-primary/10 border border-border-app hover:border-primary/20 text-muted-app hover:text-primary rounded-lg transition-colors duration-200"
              title="View full memory"
            >
              <Eye className="w-3.5 h-3.5" />
            </Link>

            {/* Open original link */}
            <a 
              href={url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="p-1.5 bg-card-app hover:bg-primary/10 border border-border-app hover:border-primary/20 text-muted-app hover:text-primary rounded-lg transition-colors duration-200"
              title="Open website"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>

            {/* Copy link */}
            <button 
              onClick={handleCopy}
              className="p-1.5 bg-card-app hover:bg-primary/10 border border-border-app hover:border-primary/20 text-muted-app hover:text-primary rounded-lg transition-colors duration-200"
              title="Copy URL"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
            </button>

            {/* Delete Memory */}
            <button 
              onClick={handleDelete}
              className="p-1.5 bg-card-app hover:bg-red-500/10 border border-border-app hover:border-red-500/20 text-muted-app hover:text-red-500 rounded-lg transition-colors duration-200"
              title="Delete memory"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
