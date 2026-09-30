import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 glass border-b border-[var(--border-subtle)] px-6 py-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold tracking-tight">
          <span className="gradient-text">ScholarAI</span>
        </Link>
        
        <div className="flex gap-8">
          <Link href="/" className="text-gray-300 hover:text-white transition">Home</Link>
          <Link href="/dashboard" className="text-gray-300 hover:text-white transition">Dashboard</Link>
          <Link href="/opportunities" className="text-gray-300 hover:text-white transition">Opportunities</Link>
        </div>
      </div>
    </nav>
  );
}
