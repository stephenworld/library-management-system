import { useState } from "react";

export default function App() {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="min-h-screen bg-blue-700 text-white flex flex-col justify-between selection:bg-white/20">
      <nav className="relative px-10 py-7 flex justify-between items-center text-sm font-medium">
        <div className="flex items-center gap-2.5">
          <span className="w-2.5 h-2.5 rounded-full bg-white inline-block"></span>
          <span>LMS</span>
        </div>

        <button
          onClick={() => setIsOpen((prev) => !prev)}
          aria-expanded={isOpen}
          aria-label="Toggle Menu"
          className="p-1 hover:opacity-80 transition-opacity focus:outline-none"
        >
          {isOpen ? (
            <img src="#" alt="menu close" />
          ) : (
            <img src="#" alt="menu open" />
          )}
        </button>

        {isOpen && (
          <div
            className="absolute top-full right-10 mt-2 w-48 bg-blue-800 border border-blue-400/30 rounded-lg shadow-xl z-50 overflow-hidden"
          >
            <ul className="flex flex-col py-1">
              <li>
                <a
                  href="#register"
                  className="block px-4 py-2.5 hover:bg-blue-600/50 transition-colors"
                >
                  Register LMS
                </a>
              </li>
              <li>
                <a
                  href="#login"
                  className="block px-4 py-2.5 hover:bg-blue-600/50 transition-colors"
                >
                  Login
                </a>
              </li>
            </ul>
          </div>
        )}
      </nav>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 border-t border-blue-200">
        <section className="lg:col-span-5 px-10 py-16 flex flex-col justify-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-normal leading-[1.08] tracking-tight mb-8">
            A library for <br />
            every individual.
          </h1>
          <p className="text-white/70 text-sm sm:text-base leading-relaxed max-w-sm font-light">
            Lorem, ipsum dolor sit amet consectetur adipisicing elit. Consectetur sit rem dolorem quis iusto quaerat perferendis, suscipit itaque corporis. Dolorum nihil voluptatibus quibusdam.
          </p>
        </section>

        <section className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 grid-rows-2 lg:border-l border-blue-100">
          <article className="p-8 sm:p-10 border-b border-r sm:border-r border-blue-100 flex flex-col justify-between min-h-[220px]">
            <div className="flex justify-between items-start">
              <img src="#" alt="member image" />
              <span className="text-3xl sm:text-4xl font-light tracking-tight">2.4M</span>
            </div>
            <div>
              <h3 className="text-md font-medium mb-1">Members Reached</h3>
              <p className="text-sm font-light">Lorem ipsum dolor sit amet.</p>
            </div>
          </article>

          <article className="p-8 sm:p-10 border-b border-blue-100 flex flex-col justify-between min-h-[220px]">
            <div className="flex justify-between items-start">
              <img src="#" alt="librarnian" />
              <span className="text-3xl sm:text-4xl font-light tracking-tight">1,284</span>
            </div>
            <div>
              <h3 className="text-md font-medium text-white mb-1">Active Librarian</h3>
              <p className="text-sm font-light">Lorem ipsum dolor sit amet consectetur adipisicing.</p>
            </div>
          </article>

          <article className="p-8 sm:p-10 border-b sm:border-b-0 border-r border-blue-100 flex flex-col justify-between min-h-[220px]">
            <div className="flex justify-between items-start">
              <img src="#" alt="Libraries" />
              <span className="text-3xl sm:text-4xl font-light tracking-tight">38K</span>
            </div>
            <div>
              <h3 className="text-md font-medium mb-1">Active Libraries</h3>
              <p className="text-sm font-light">Lorem ipsum dolor sit amet consectetur.</p>
            </div>
          </article>

          <article className="p-8 sm:p-10 flex flex-col justify-between min-h-[220px]">
            <div className="flex justify-between items-start">
              <img src="#" alt="Image" />
              <span className="text-3xl sm:text-4xl font-light tracking-tight">3.1×</span>
            </div>
            <div>
              <h3 className="text-md font-medium mb-1">Borrowed books</h3>
              <p className="text-sm font-light">Lorem ipsum dolor sit amet consectetur adipisicing elit.</p>
            </div>
          </article>
        </section>
      </main>

      <footer className="px-10 py-6 border-t border-blue-200 flex flex-col sm:flex-row justify-between items-center text-xs gap-2">
        <span>© 2026 Library management System</span>
        <span>Developed by Stephen</span>
      </footer>
    </div>
  );
}