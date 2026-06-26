'use client';

import React from 'react';
import Sidebar from './Sidebar';
import { useMemories } from '@/lib/hooks';
import { AlertCircle } from 'lucide-react';

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const { isError, error } = useMemories();

  return (
    <div className="flex flex-col md:flex-row min-h-screen bg-bg-app text-fg-app transition-colors duration-200">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        {/* Backend Connectivity Alert banner */}
        {isError && (
          <div className="bg-red-500/10 border-b border-red-500/20 text-red-500 px-6 py-3 flex items-center gap-3 text-xs font-semibold backdrop-blur-sm animate-slide-down">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>
              Could not connect to FastAPI server. Run the server (`uvicorn main:app --reload` in `backend/`) to fetch your memories. Details: {error instanceof Error ? error.message : 'Connection failed'}
            </span>
          </div>
        )}
        <div className="flex-1 p-6 md:p-10 max-w-7xl w-full mx-auto space-y-8">
          {children}
        </div>
      </main>
    </div>
  );
}
