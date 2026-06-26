'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Search, 
  Database, 
  MessageSquare, 
  Sparkles, 
  Settings, 
  Sun, 
  Moon, 
  Menu, 
  X, 
  BrainCircuit 
} from 'lucide-react';
import { useTheme } from './Providers';
import { useMemories } from '@/lib/hooks';

export default function Sidebar() {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const { data: memories } = useMemories();

  const totalMemories = memories?.length || 0;

  const menuItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Search', href: '/search', icon: Search },
    { name: 'Memories', href: '/memories', icon: Database },
    { name: 'Chat', href: '/chat', icon: MessageSquare },
    { name: 'Insights', href: '/insights', icon: Sparkles },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const toggleSidebar = () => setIsOpen(!isOpen);

  const sidebarContent = (
    <div className="flex flex-col h-full bg-card-app/40 border-r border-border-app p-6 glass-panel select-none">
      {/* Brand logo */}
      <div className="flex items-center gap-3 mb-8">
        <div className="p-2.5 bg-primary/10 rounded-xl text-primary border border-primary/20">
          <BrainCircuit className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-wide bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Memento
          </span>
          <p className="text-[10px] text-muted-app font-medium tracking-wider uppercase">Internet Memory</p>
        </div>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 space-y-1.5">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={() => setIsOpen(false)}
              className={`flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 group text-sm font-medium ${
                isActive
                  ? 'bg-primary text-white shadow-lg shadow-primary/25 border-l-4 border-accent'
                  : 'text-muted-app hover:text-fg-app hover:bg-card-app border border-transparent'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-5 h-5 transition-transform duration-200 group-hover:scale-105 ${isActive ? 'text-white' : 'text-muted-app group-hover:text-fg-app'}`} />
                <span>{item.name}</span>
              </div>
              {item.name === 'Memories' && totalMemories > 0 && (
                <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                  isActive 
                    ? 'bg-white/20 text-white' 
                    : 'bg-primary/10 text-primary dark:bg-primary/20'
                }`}>
                  {totalMemories}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom controls */}
      <div className="pt-4 border-t border-border-app mt-auto space-y-4">
        {/* Memory status simple card */}
        <div className="p-3 bg-card-app/30 border border-border-app rounded-xl">
          <div className="flex justify-between items-center text-xs mb-1">
            <span className="text-muted-app">System status</span>
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
            </span>
          </div>
          <p className="text-[10px] text-muted-app truncate">Connected to local db</p>
        </div>

        {/* Theme Toggle button */}
        <button
          onClick={toggleTheme}
          className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-muted-app hover:text-fg-app hover:bg-card-app border border-transparent transition-all duration-200 text-sm font-medium"
        >
          {theme === 'dark' ? (
            <>
              <Sun className="w-5 h-5 text-yellow-500" />
              <span>Light Mode</span>
            </>
          ) : (
            <>
              <Moon className="w-5 h-5 text-indigo-500" />
              <span>Dark Mode</span>
            </>
          )}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Top Header */}
      <header className="md:hidden flex items-center justify-between px-6 py-4 border-b border-border-app bg-card-app/40 backdrop-blur-md sticky top-0 z-30 w-full">
        <Link href="/" className="flex items-center gap-2">
          <BrainCircuit className="w-6 h-6 text-primary" />
          <span className="font-bold tracking-wide text-md">Memento</span>
        </Link>
        <button
          onClick={toggleSidebar}
          className="p-2 border border-border-app rounded-lg text-muted-app hover:text-fg-app"
          aria-label="Toggle Menu"
        >
          <Menu className="w-5 h-5" />
        </button>
      </header>

      {/* Mobile Slide-over Drawer Backdrop */}
      {isOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
          onClick={toggleSidebar}
        />
      )}

      {/* Mobile Sidebar Container */}
      <aside className={`md:hidden fixed top-0 bottom-0 left-0 w-72 z-50 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="absolute top-5 right-5 z-50">
          <button
            onClick={toggleSidebar}
            className="p-1.5 bg-card-app border border-border-app rounded-lg hover:bg-border-app"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        {sidebarContent}
      </aside>

      {/* Desktop Sidebar (Permanent) */}
      <aside className="hidden md:flex flex-col w-64 h-screen sticky top-0 z-20 shrink-0">
        {sidebarContent}
      </aside>
    </>
  );
}
