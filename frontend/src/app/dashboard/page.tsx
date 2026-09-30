export default function DashboardPage() {
  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Student Dashboard</h1>
        <p className="page-subtitle">Your personalized overview of education opportunities.</p>
      </div>

      <div className="grid-2">
        <div className="card glass-hover">
          <h2 className="text-xl font-bold mb-4 text-indigo-400">Profile Configuration</h2>
          <p className="text-gray-400 mb-4">View and update your academic and demographic details to refine eligibility matching.</p>
          <div className="h-32 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--border-subtle)] flex items-center justify-center">
            <span className="text-gray-500">Profile Module (Coming Soon)</span>
          </div>
        </div>

        <div className="card glass-hover">
          <h2 className="text-xl font-bold mb-4 text-emerald-400">Top Recommendations</h2>
          <p className="text-gray-400 mb-4">Opportunities ranked by our deterministic Eligibility Engine and multi-factor scorer.</p>
          <div className="h-32 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--border-subtle)] flex items-center justify-center">
            <span className="text-gray-500">Recommendations Module (Coming Soon)</span>
          </div>
        </div>

        <div className="card glass-hover">
          <h2 className="text-xl font-bold mb-4 text-amber-400">Eligibility Status</h2>
          <p className="text-gray-400 mb-4">See transparent breakdowns of why you pass or fail specific scholarship criteria.</p>
          <div className="h-32 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--border-subtle)] flex items-center justify-center">
            <span className="text-gray-500">Eligibility Module (Coming Soon)</span>
          </div>
        </div>

        <div className="card glass-hover">
          <h2 className="text-xl font-bold mb-4 text-cyan-400">RAG Assistant</h2>
          <p className="text-gray-400 mb-4">Chat with official documents to clarify requirements or required documents.</p>
          <div className="h-32 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--border-subtle)] flex items-center justify-center">
            <span className="text-gray-500">Chat Module (Coming Soon)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
