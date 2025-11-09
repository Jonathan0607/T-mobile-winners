interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  // Logo is served from public folder - Vite serves files in public/ from root
  // Using tmobile_logo.png from the root directory
  const logoSrc = '/tmobile_logo.png';

  return (
    <>
      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-screen w-[21rem] bg-[#1A1A1A] border-r border-[#555555] z-50 transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ resize: 'none' }}
      >
        <div className="p-4 pt-6">
          {/* Logo */}
          <div className="mb-4 -mt-9 overflow-hidden" style={{ marginTop: '-35px' }}>
            {logoSrc ? (
              <div className="bg-black p-2 rounded-lg overflow-hidden">
                <img
                  src={logoSrc}
                  alt="T-Mobile Logo"
                  className="w-full h-auto select-none"
                  draggable={false}
                  style={{
                    userSelect: 'none',
                    WebkitUserSelect: 'none',
                    transform: 'scale(1.2)',
                    transformOrigin: 'center top',
                  }}
                />
              </div>
            ) : (
              <div className="text-white text-2xl font-bold">🎯 T-Mobile</div>
            )}
          </div>

          <hr className="border-[#555555] mb-4" />

          {/* Navigation Links */}
          <nav className="space-y-2">
            <div className="bg-[#E20074] text-white px-4 py-3 rounded-md text-base font-semibold">
              Home Page
            </div>
            <div className="text-[#CCCCCC] px-4 py-3 rounded-md text-base font-medium hover:bg-[#3C3C3C] transition-colors cursor-pointer">
              🔧 Network Engineering
            </div>
            <div className="text-[#CCCCCC] px-4 py-3 rounded-md text-base font-medium hover:bg-[#3C3C3C] transition-colors cursor-pointer">
              💬 Social Media
            </div>
            <div className="text-[#CCCCCC] px-4 py-3 rounded-md text-base font-medium hover:bg-[#3C3C3C] transition-colors cursor-pointer">
              📈 Sales
            </div>
          </nav>
        </div>
      </aside>

      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className={`fixed top-4 z-50 bg-[#2C2C2C] text-white p-2 rounded-md hover:bg-[#3C3C3C] transition-all duration-300 ${
          isOpen ? 'left-[21.5rem]' : 'left-4'
        }`}
        aria-label="Toggle sidebar"
      >
        {isOpen ? '✕' : '☰'}
      </button>
    </>
  );
}

