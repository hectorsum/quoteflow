"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  {
    href: "/requests",
    label: "Solicitudes",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M22 12h-6l-2 3h-4l-2-3H2" />
        <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
      </svg>
    ),
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 shrink-0 border-r border-line min-h-screen px-5 py-7 flex flex-col">
      <div className="px-2 mb-9">
        <h1 className="font-serif text-2xl font-semibold text-ink-900 leading-none">QuoteFlow</h1>
        <p className="font-serif text-clay-500 text-sm mt-1">de cotizaciones</p>
        <p className="text-ink-400 text-[10px] tracking-[0.18em] uppercase mt-3">AndesPro Industrial</p>
      </div>

      <nav className="flex flex-col gap-1">
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                active
                  ? "bg-cream-200 text-clay-600 font-medium"
                  : "text-ink-700 hover:bg-cream-200/60"
              }`}
            >
              <span className={active ? "text-clay-500" : "text-ink-400"}>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <Link
        href="/requests?new=1"
        className="mt-auto flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm text-ink-700 hover:bg-cream-200/60 transition-colors"
      >
        <span className="text-ink-400">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </span>
        Nueva solicitud
      </Link>
    </aside>
  );
}
