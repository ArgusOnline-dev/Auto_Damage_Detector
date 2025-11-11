import { Link } from 'react-router-dom'
import { Zap } from 'lucide-react'

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-apex-surface/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="p-2 rounded-lg bg-gradient-to-br from-apex-cyan to-apex-magenta">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-bold text-apex-text">
                ApexAutoAI
              </span>
            </div>
            <p className="text-apex-text-muted max-w-md">
              Advanced AI-powered vehicle damage assessment for accurate cost estimation and streamlined insurance processing.
            </p>
            <div className="mt-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
              <p className="text-sm text-yellow-400 font-medium">
                ⚠️ For academic demonstration purposes only
              </p>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-apex-text uppercase tracking-wider mb-4">
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-apex-text-muted hover:text-apex-cyan smooth-transition">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/upload" className="text-apex-text-muted hover:text-apex-cyan smooth-transition">
                  Upload Photos
                </Link>
              </li>
              <li>
                <Link to="/reports" className="text-apex-text-muted hover:text-apex-cyan smooth-transition">
                  View Reports
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-apex-text-muted hover:text-apex-cyan smooth-transition">
                  About Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-sm font-semibold text-apex-text uppercase tracking-wider mb-4">
              Support
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-apex-text-muted hover:text-apex-cyan smooth-transition">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="text-apex-text-muted hover:text-apex-cyan smooth-transition">
                  API Reference
                </a>
              </li>
              <li>
                <a href="#" className="text-apex-text-muted hover:text-apex-cyan smooth-transition">
                  Help Center
                </a>
              </li>
              <li>
                <a href="#" className="text-apex-text-muted hover:text-apex-cyan smooth-transition">
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-white/10">
          <p className="text-center text-apex-text-muted text-sm">
            © 2024 ApexAutoAI. Built for educational purposes. Not for commercial use.
          </p>
        </div>
      </div>
    </footer>
  )
}