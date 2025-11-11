import { Link, useLocation } from 'react-router-dom'
import { Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Navigation() {
  const location = useLocation()

  const navItems = [
    { name: 'Home', href: '/' },
    { name: 'Upload', href: '/upload' },
    { name: 'Reports', href: '/reports' },
    { name: 'About', href: '/about' }
  ]

  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/'
    return location.pathname.startsWith(href)
  }

  return (
    <nav className="sticky top-0 z-50 glass-card border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="p-2 rounded-lg bg-gradient-to-br from-apex-cyan to-apex-magenta">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold text-apex-text group-hover:text-apex-cyan smooth-transition">
              ApexAutoAI
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'text-sm font-medium smooth-transition relative',
                  isActive(item.href)
                    ? 'text-apex-cyan'
                    : 'text-apex-text-muted hover:text-apex-text'
                )}
              >
                {item.name}
                {isActive(item.href) && (
                  <div className="absolute -bottom-6 left-0 right-0 h-0.5 bg-apex-cyan glow-cyan" />
                )}
              </Link>
            ))}
          </div>

          {/* Right-side placeholder to balance layout (no theme toggle in dark-only mode) */}
          <div className="hidden md:block w-6" />
        </div>
      </div>
    </nav>
  )
}