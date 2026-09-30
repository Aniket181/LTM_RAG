export default function OpportunitiesPage() {
  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Opportunity Explorer</h1>
        <p className="page-subtitle">Search, filter, and explore all available scholarships and education programs.</p>
      </div>

      <div className="card glass">
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <input 
            type="text" 
            placeholder="Search by keyword, provider, or title..." 
            className="input md:w-2/3"
            disabled
          />
          <button className="btn-primary md:w-1/3 justify-center disabled:opacity-50">
            Search
          </button>
        </div>

        <div className="h-64 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--border-subtle)] flex items-center justify-center">
          <span className="text-gray-500">Explorer UI (Coming Soon)</span>
        </div>
      </div>
    </div>
  );
}
