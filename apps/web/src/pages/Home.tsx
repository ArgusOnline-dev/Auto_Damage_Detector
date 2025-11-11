import { Link } from 'react-router-dom'
import { Upload, FileImage, DollarSign, FileText, ArrowRight, Camera, Brain, Calculator } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import heroImage from '@/assets/hero-car.jpg'

export default function Home() {
  const features = [
    {
      icon: Upload,
      title: 'Upload Photos',
      description: 'Drag and drop multiple vehicle damage photos for instant analysis'
    },
    {
      icon: Brain,
      title: 'Per-Part Damage Detection',
      description: 'AI identifies specific vehicle parts and damage types with precision'
    },
    {
      icon: Calculator,
      title: 'Severity & Cost Ranges',
      description: 'Get detailed cost estimates with minimum, likely, and maximum ranges'
    },
    {
      icon: FileText,
      title: 'PDF Reports',
      description: 'Generate professional reports ready for insurance claims'
    }
  ]

  const steps = [
    {
      number: '01',
      title: 'Upload Images',
      description: 'Take photos of vehicle damage from multiple angles'
    },
    {
      number: '02', 
      title: 'AI Analysis',
      description: 'Our AI detects damage and identifies affected parts'
    },
    {
      number: '03',
      title: 'Get Estimate',
      description: 'Receive detailed cost breakdown and PDF report'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Hero background image */}
        <div className="absolute inset-0 bg-cover bg-center opacity-10"
             style={{ backgroundImage: `url(${heroImage})` }}>
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent"></div>
        
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center">
            {/* Car silhouette background */}
            <div className="absolute inset-0 flex items-center justify-center opacity-5">
              <svg 
                width="800" 
                height="400" 
                viewBox="0 0 800 400" 
                className="text-apex-cyan"
              >
                <path 
                  d="M150 250 L200 200 L300 180 L500 180 L600 200 L650 250 L680 280 L650 320 L600 320 L580 300 L220 300 L200 320 L150 320 L120 280 Z" 
                  fill="currentColor"
                  stroke="currentColor"
                  strokeWidth="2"
                />
                <circle cx="220" cy="300" r="30" fill="none" stroke="currentColor" strokeWidth="2" />
                <circle cx="580" cy="300" r="30" fill="none" stroke="currentColor" strokeWidth="2" />
              </svg>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-apex-text mb-6 relative z-10">
              See the damage.
              <br />
              <span className="bg-gradient-to-r from-apex-cyan to-apex-magenta bg-clip-text text-transparent">
                Know the cost.
              </span>
            </h1>
            
            <p className="text-xl text-apex-text-muted mb-12 max-w-2xl mx-auto relative z-10">
              Advanced AI-powered vehicle damage assessment that delivers accurate cost estimates in seconds.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center relative z-10">
              <Button asChild variant="hero" size="xl">
                <Link to="/upload">
                  <Camera className="mr-2 h-5 w-5" />
                  Start Estimate
                </Link>
              </Button>
              
              <Button asChild variant="neon" size="xl">
                <Link to="/reports">
                  <FileText className="mr-2 h-5 w-5" />
                  View Reports
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-apex-text mb-4">
              Powerful AI-Driven Features
            </h2>
            <p className="text-xl text-apex-text-muted">
              Everything you need for accurate vehicle damage assessment
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Card key={index} className="glass-card border-white/10 hover:border-apex-cyan/30 smooth-transition group">
                  <CardHeader className="text-center">
                    <div className="mx-auto mb-4 p-4 rounded-full bg-gradient-to-br from-apex-cyan/20 to-apex-magenta/20 w-fit group-hover:from-apex-cyan/30 group-hover:to-apex-magenta/30 smooth-transition">
                      <Icon className="h-8 w-8 text-apex-cyan" />
                    </div>
                    <CardTitle className="text-apex-text">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-apex-text-muted text-center">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-apex-surface/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-apex-text mb-4">
              How It Works
            </h2>
            <p className="text-xl text-apex-text-muted">
              Simple process, professional results
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="text-center relative">
                <div className="mb-6 relative">
                  <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-apex-cyan to-apex-magenta flex items-center justify-center text-white font-bold text-xl glow-cyan">
                    {step.number}
                  </div>
                  {index < steps.length - 1 && (
                    <div className="hidden md:block absolute top-1/2 -translate-y-1/2 left-[calc(100%+1rem)] z-10 pointer-events-none">
                      <ArrowRight className="h-6 w-6 text-apex-text-muted" />
                    </div>
                  )}
                </div>
                
                <h3 className="text-xl font-semibold text-apex-text mb-3">
                  {step.title}
                </h3>
                
                <p className="text-apex-text-muted">
                  {step.description}
                </p>

                
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Button asChild variant="glass" size="lg">
              <Link to="/upload">
                Get Started Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}