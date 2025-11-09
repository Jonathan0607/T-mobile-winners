const Sidebar = () => {
  const menuItems = [
    { id: 1, label: 'Dashboard', active: true },
    { id: 2, label: 'Analytics', active: false },
    { id: 3, label: 'Reports', active: false },
    { id: 4, label: 'Settings', active: false }
  ];

  return (
    <div className="w-64 bg-gray-800 h-screen flex flex-col">
      {/* T-Mobile Logo */}
      <div className="p-6 border-b border-gray-700">
        <div className="text-2xl font-bold text-magenta">T-Mobile</div>
        <div className="text-sm text-gray-400 mt-1">Vibe Check</div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.id}>
              <a
                href="#"
                className={`block px-4 py-3 rounded-lg transition-colors ${
                  item.active
                    ? 'bg-magenta/20 text-magenta border-l-4 border-magenta'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700 text-xs text-gray-400">
        <p>Mission Control</p>
        <p className="mt-1">© 2025 T-Mobile</p>
      </div>
    </div>
  );
};

export default Sidebar;
