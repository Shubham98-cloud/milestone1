"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const pathname = usePathname();

  const navLinks = [
    { name: 'Home', path: '/', icon: '🏠' },
    { name: 'Dining', path: '/dining', icon: '🍴' },
    { name: 'Nightlife', path: '/nightlife', icon: '🍷' },
    { name: 'Zomaland', path: '/zomaland', icon: '🎪' },
    { name: 'Profile', path: '/profile', icon: '👤' },
  ];

  return (
    <div className="sidebar-container">
      {/* Red Left Margin styling */}
      <div className="ai-layer">
      </div>
      
      {/* Dark Inner Sidebar */}
      <div className="nav-layer">
        <div className="logo-text">zomato</div>
        <ul className="nav-menu">
          {navLinks.map((link) => {
            const isActive = pathname === link.path;
            return (
              <li key={link.name} className={`nav-item ${isActive ? 'active' : ''}`}>
                <Link href={link.path} style={{ textDecoration: 'none', color: 'inherit', display: 'flex', alignItems: 'center', gap: '12px', width: '100%' }}>
                  <span>{link.icon}</span> {link.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
