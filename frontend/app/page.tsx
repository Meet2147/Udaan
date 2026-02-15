import Link from 'next/link';

export default function Home() {
  return (
    <div className="space-y-10">
      <section className="panel p-6 lg:p-10">
        <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-8 items-center">
          <div>
            <div className="label">Online Arts School</div>
            <h1 className="mt-3 text-4xl lg:text-5xl font-semibold leading-tight">
              Build your drawing skills with structured, mentor‑led courses.
            </h1>
            <p className="mt-4 text-lg text-slate-600">
              From fundamentals to expressive composition, Udaan helps students progress with clear lesson paths,
              feedback loops, and certificates on completion.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link href="/signup" className="btn-primary">Start Learning</Link>
              <Link href="/login" className="btn-ghost">Login</Link>
              <span className="chip">New batches every month</span>
            </div>
            <div className="mt-6 grid grid-cols-3 gap-3">
              <div className="kpi">
                <div className="text-xs text-slate-500">Skill Tracks</div>
                <div className="text-2xl font-semibold">2</div>
              </div>
              <div className="kpi">
                <div className="text-xs text-slate-500">Lessons</div>
                <div className="text-2xl font-semibold">20+</div>
              </div>
              <div className="kpi">
                <div className="text-xs text-slate-500">Certificates</div>
                <div className="text-2xl font-semibold">1</div>
              </div>
            </div>
          </div>

          <div className="panel p-5 bg-white/80">
            <div className="label">Student Journey</div>
            <div className="mt-2 text-xl font-semibold">What you’ll master</div>
            <div className="mt-4 space-y-3">
              <div className="list-card">
                <div className="text-sm text-slate-500">Week 1–4</div>
                <div className="text-lg font-semibold">Observation & Line Confidence</div>
                <div className="text-xs text-slate-600">Contours, proportions, and shape simplification.</div>
              </div>
              <div className="list-card">
                <div className="text-sm text-slate-500">Week 5–8</div>
                <div className="text-lg font-semibold">Value & Depth</div>
                <div className="text-xs text-slate-600">Light logic, shadow mapping, and textures.</div>
              </div>
              <div className="list-card">
                <div className="text-sm text-slate-500">Week 9–12</div>
                <div className="text-lg font-semibold">Composition & Style</div>
                <div className="text-xs text-slate-600">Story, framing, and expressive finishes.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid lg:grid-cols-2 gap-6">
        <div className="panel p-6">
          <div className="label">Custom Categories</div>
          <h2 className="mt-2 text-2xl font-semibold">Every tutor creates their own genres</h2>
          <p className="mt-2 text-slate-600">
            No fixed tracks. Admins can create categories that match their teaching style and niche.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="chip">Portrait</span>
            <span className="chip">Calligraphy</span>
            <span className="chip">Landscape</span>
            <span className="chip">Watercolor</span>
          </div>
        </div>
        <div className="panel p-6">
          <div className="label">Flexible Curriculum</div>
          <h2 className="mt-2 text-2xl font-semibold">Start teaching in minutes</h2>
          <p className="mt-2 text-slate-600">
            Create a course, upload lectures, and enroll students with your own structure.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="chip">Video lessons</span>
            <span className="chip">Certificates</span>
            <span className="chip">Progress</span>
          </div>
        </div>
      </section>

      <section className="panel p-6">
        <div className="label">Why Udaan</div>
        <div className="mt-2 text-2xl font-semibold">A studio-grade learning experience</div>
        <div className="mt-4 grid md:grid-cols-3 gap-4">
          <div className="list-card">
            <div className="text-lg font-semibold">Structured Path</div>
            <p className="text-sm text-slate-600">Clear milestones with progress tracking.</p>
          </div>
          <div className="list-card">
            <div className="text-lg font-semibold">Mentor Feedback</div>
            <p className="text-sm text-slate-600">Continuous guidance to keep momentum.</p>
          </div>
          <div className="list-card">
            <div className="text-lg font-semibold">Certificates</div>
            <p className="text-sm text-slate-600">Earn proof of completion for each course.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
