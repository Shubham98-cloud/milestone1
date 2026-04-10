import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata = {
  title: 'Zomato AI Recommendations',
  description: 'AI Powered Restaurant Recommendations built with Next.js',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="app-container">
          <Sidebar />
          <div className="main-area">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
