import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center animate-fade-in-up">
      <div className="glass rounded-3xl p-12 max-w-4xl mx-auto flex flex-col items-center">
        <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight">
          <span className="gradient-text">ScholarAI</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-2xl leading-relaxed">
          Intelligent education opportunity discovery powered by Retrieval-Augmented Generation and deterministic eligibility verification.
        </p>

        <div className="flex flex-col sm:flex-row gap-6 mt-4">
          <Link href="/opportunities" className="btn-primary text-lg px-8 py-4 rounded-xl">
            Explore Opportunities
          </Link>
          <Link href="/dashboard" className="btn-secondary text-lg px-8 py-4 rounded-xl">
            Go to Dashboard
          </Link>
        </div>
      </div>

      <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl">
        <div className="card text-left glass-hover">
          <h3 className="text-xl font-bold mb-3 gradient-text-accent">Hybrid Retrieval</h3>
          <p className="text-gray-400">Discover hidden opportunities using semantic search combined with BM25 keyword matching for maximum precision.</p>
        </div>
        <div className="card text-left glass-hover">
          <h3 className="text-xl font-bold mb-3 text-emerald-400">Eligibility Engine</h3>
          <p className="text-gray-400">Deterministic rules evaluate your profile against strict criteria, guaranteeing you only apply where you qualify.</p>
        </div>
        <div className="card text-left glass-hover">
          <h3 className="text-xl font-bold mb-3 text-indigo-400">Grounded Q&A</h3>
          <p className="text-gray-400">Ask questions and get transparent answers cited directly from official source documents using RAG.</p>
        </div>
      </div>
    </div>
  );
}
