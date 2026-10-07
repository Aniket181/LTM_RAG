'use client';

import { useState, useEffect } from 'react';
import { User, Save, CheckCircle2, Info, AlertCircle, PlusCircle } from 'lucide-react';
import { useStudent } from '@/lib/useStudent';
import type { StudentProfile, EducationLevel, Category, InstitutionType } from '@/lib/types';
import { DEFAULT_PROFILE_FORM } from '@/lib/types';

const EDUCATION_LEVELS: EducationLevel[] = ['Class 10', 'Class 12', 'Diploma', 'UG', 'PG', 'PhD'];
const CATEGORIES: Category[] = ['General', 'OBC', 'SC', 'ST', 'EWS', 'Minority', 'PwD'];
const INSTITUTION_TYPES: InstitutionType[] = ['Government', 'Private', 'Deemed University', 'Central University', 'Any'];
const STATES = [
  'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Delhi','Goa','Gujarat',
  'Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra',
  'Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu',
  'Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal',
];

function FormSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card" style={{ marginBottom: '1.25rem' }}>
      <div style={{
        fontSize: '0.75rem', fontWeight: 700, color: '#818cf8',
        letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '1.25rem',
        paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-subtle)',
      }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <label className="label">{label}</label>
      {children}
    </div>
  );
}

export default function ProfilePage() {
  const { student, studentId, loading, error, createAndPersist, saveStudent } = useStudent();

  // Initialize form from student record if loaded, else use empty defaults
  const [profile, setProfile] = useState<Omit<StudentProfile, 'id'>>(DEFAULT_PROFILE_FORM);
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [saveError, setSaveError] = useState<string | null>(null);
  const isNewStudent = !studentId;

  // Populate form from backend data when student loads
  useEffect(() => {
    if (student) {
      const { id: _id, created_at: _c, updated_at: _u, ...rest } = student as any;
      setProfile(rest);
    }
  }, [student]);

  const update = (field: keyof StudentProfile, value: unknown) =>
    setProfile((p) => ({ ...p, [field]: value }));

  const handleSave = async () => {
    setSaveState('saving');
    setSaveError(null);
    try {
      if (isNewStudent) {
        // First time: create a real student record via API
        await createAndPersist(profile);
      } else {
        // Update existing student
        await saveStudent(profile);
      }
      setSaveState('saved');
      setTimeout(() => setSaveState('idle'), 2500);
    } catch (err) {
      setSaveState('error');
      setSaveError(err instanceof Error ? err.message : 'Failed to save profile.');
    }
  };

  if (loading) {
    return (
      <div className="animate-fade-in">
        <div className="page-header">
          <h1 className="page-title"><span className="gradient-text">Student Profile</span></h1>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 120 }} />)}
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">
              <span className="gradient-text">Student Profile</span>
            </h1>
            <p className="page-subtitle">
              {isNewStudent
                ? 'Create your profile to get personalized scholarship recommendations.'
                : 'Your profile is used to filter and rank scholarships. Keep it accurate.'}
            </p>
          </div>
          <button
            className="btn-primary"
            onClick={handleSave}
            id="save-profile-btn"
            disabled={saveState === 'saving'}
          >
            {saveState === 'saving' && <User size={15} className="animate-spin-slow" />}
            {saveState === 'saved' && <CheckCircle2 size={15} />}
            {saveState === 'error' && <AlertCircle size={15} />}
            {(saveState === 'idle' || saveState === 'saving') && !student && <PlusCircle size={15} />}
            {saveState === 'idle' && student && <Save size={15} />}
            {saveState === 'saving' ? 'Saving...' : saveState === 'saved' ? 'Saved!' : isNewStudent ? 'Create Profile' : 'Save Profile'}
          </button>
        </div>
      </div>

      {/* Error from hook (stale ID, network) */}
      {error && saveState !== 'error' && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.75rem',
          padding: '0.875rem 1.1rem', marginBottom: '1.25rem',
          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: '0.75rem', fontSize: '0.8rem', color: '#f87171',
        }}>
          <AlertCircle size={15} style={{ flexShrink: 0 }} />
          {error}
        </div>
      )}

      {/* Save error */}
      {saveState === 'error' && saveError && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.75rem',
          padding: '0.875rem 1.1rem', marginBottom: '1.25rem',
          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: '0.75rem', fontSize: '0.8rem', color: '#f87171',
        }}>
          <AlertCircle size={15} style={{ flexShrink: 0 }} />
          {saveError}
        </div>
      )}

      {/* Info notice */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.75rem',
        padding: '0.875rem 1.1rem', marginBottom: '1.5rem',
        background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)',
        borderRadius: '0.75rem', fontSize: '0.8rem', color: '#a5b4fc',
      }}>
        <Info size={15} style={{ flexShrink: 0 }} />
        {isNewStudent
          ? 'Fill in your details and click "Create Profile" to get personalized scholarship recommendations from our backend.'
          : 'Profile data is used only for eligibility matching. Only provide information you are comfortable sharing.'}
        {studentId && (
          <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
            ID: {studentId.substring(0, 8)}…
          </span>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* Left column */}
        <div>
          <FormSection title="Academic Details">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Field label="Education Level">
                <select className="select" value={profile.education_level || ''} onChange={(e) => update('education_level', e.target.value as EducationLevel)} id="edu-level">
                  <option value="">Select level</option>
                  {EDUCATION_LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
                </select>
              </Field>
              <Field label="Course">
                <input className="input" placeholder="e.g. B.Tech, MBBS, M.Sc" value={profile.course || ''} onChange={(e) => update('course', e.target.value)} id="course" />
              </Field>
              <Field label="Branch / Specialization">
                <input className="input" placeholder="e.g. Computer Science" value={profile.branch ?? ''} onChange={(e) => update('branch', e.target.value)} id="branch" />
              </Field>
              <Field label="Year of Study">
                <input className="input" type="number" min={1} max={6} placeholder="1–6" value={profile.year_of_study ?? ''} onChange={(e) => update('year_of_study', Number(e.target.value))} id="year" />
              </Field>
              <Field label="CGPA (out of 10)">
                <input className="input" type="number" min={0} max={10} step={0.01} placeholder="e.g. 8.5" value={profile.cgpa ?? ''} onChange={(e) => update('cgpa', Number(e.target.value))} id="cgpa" />
              </Field>
              <Field label="Percentage (%)">
                <input className="input" type="number" min={0} max={100} step={0.1} placeholder="e.g. 85.0" value={profile.percentage ?? ''} onChange={(e) => update('percentage', Number(e.target.value))} id="percentage" />
              </Field>
            </div>
            <Field label="Institution Type">
              <select className="select" value={profile.institution_type ?? ''} onChange={(e) => update('institution_type', e.target.value as InstitutionType)} id="institution-type">
                <option value="">Select type</option>
                {INSTITUTION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </Field>
          </FormSection>

          <FormSection title="Personal Details">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Field label="Name (optional)">
                <input className="input" placeholder="Your name" value={profile.name ?? ''} onChange={(e) => update('name', e.target.value)} id="name" />
              </Field>
              <Field label="Age (optional)">
                <input className="input" type="number" min={14} max={45} placeholder="Age" value={profile.age ?? ''} onChange={(e) => update('age', Number(e.target.value))} id="age" />
              </Field>
              <Field label="Gender (optional)">
                <select className="select" value={profile.gender ?? ''} onChange={(e) => update('gender', e.target.value)} id="gender">
                  <option value="">Prefer not to say</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </Field>
              <Field label="Nationality">
                <input className="input" placeholder="e.g. Indian" value={profile.nationality ?? 'Indian'} onChange={(e) => update('nationality', e.target.value)} id="nationality" />
              </Field>
            </div>
          </FormSection>
        </div>

        {/* Right column */}
        <div>
          <FormSection title="Eligibility Criteria">
            <Field label="Annual Family Income (₹)">
              <input className="input" type="number" min={0} step={1000} placeholder="e.g. 300000" value={profile.annual_family_income ?? ''} onChange={(e) => update('annual_family_income', Number(e.target.value))} id="income" />
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                Enter total annual family income from all sources
              </div>
            </Field>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Field label="State">
                <select className="select" value={profile.state ?? ''} onChange={(e) => update('state', e.target.value)} id="state">
                  <option value="">Select state</option>
                  {STATES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </Field>
              <Field label="Domicile State">
                <select className="select" value={profile.domicile ?? ''} onChange={(e) => update('domicile', e.target.value)} id="domicile">
                  <option value="">Select state</option>
                  {STATES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </Field>
            </div>

            <Field label="Category / Reservation">
              <select className="select" value={profile.category} onChange={(e) => update('category', e.target.value as Category)} id="category">
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </Field>
          </FormSection>

          <FormSection title="Interests (optional)">
            <Field label="Academic Interests (comma separated)">
              <input
                className="input"
                placeholder="e.g. Machine Learning, Data Science"
                value={(profile.academic_interests ?? []).join(', ')}
                onChange={(e) => update('academic_interests', e.target.value.split(',').map((s) => s.trim()).filter(Boolean))}
                id="academic-interests"
              />
            </Field>
            <Field label="Career Interests (comma separated)">
              <input
                className="input"
                placeholder="e.g. Software Engineering, Research"
                value={(profile.career_interests ?? []).join(', ')}
                onChange={(e) => update('career_interests', e.target.value.split(',').map((s) => s.trim()).filter(Boolean))}
                id="career-interests"
              />
            </Field>
          </FormSection>

          {/* Profile Completeness */}
          <div className="card">
            <div className="section-title">Profile Completeness</div>
            {(() => {
              const fields = [
                profile.education_level, profile.course, profile.cgpa,
                profile.annual_family_income, profile.state, profile.category,
                profile.institution_type, profile.gender, profile.branch,
              ];
              const filled = fields.filter(Boolean).length;
              const pct = Math.round((filled / fields.length) * 100);
              return (
                <>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{filled}/{fields.length} fields filled</span>
                    <span className="gradient-text" style={{ fontWeight: 700 }}>{pct}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${pct}%` }} />
                  </div>
                  {pct < 80 && (
                    <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: '#f59e0b' }}>
                      <Info size={11} style={{ display: 'inline', marginRight: 4 }} />
                      Complete your profile for more accurate eligibility matching
                    </div>
                  )}
                </>
              );
            })()}
          </div>
        </div>
      </div>
    </div>
  );
}
