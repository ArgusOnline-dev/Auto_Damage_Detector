import { Users, Target, Lightbulb, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function About() {
  const team = [
    {
      name: 'Dr. Sarah Chen',
      role: 'AI Research Lead',
      bio: 'PhD in Computer Vision from Stanford. 8+ years in automotive AI systems.',
      image: 'SC'
    },
    {
      name: 'Marcus Rodriguez', 
      role: 'Software Engineer',
      bio: 'Full-stack developer specializing in React and machine learning integration.',
      image: 'MR'
    },
    {
      name: 'Emily Watson',
      role: 'Insurance Domain Expert',
      bio: 'Former insurance adjuster with 12 years of vehicle damage assessment experience.',
      image: 'EW'
    },
    {
      name: 'Alex Kim',
      role: 'Product Designer',
      bio: 'UX/UI designer focused on creating intuitive interfaces for complex AI systems.',
      image: 'AK'
    }
  ]

  const limitations = [
    'AI accuracy depends on image quality and lighting conditions',
    'Cost estimates are approximate and may vary by location and shop',
    'Complex structural damage may require professional inspection',
    'System trained primarily on common vehicle makes and models',
    'Not suitable for antique or heavily modified vehicles'
  ]

  const futureWork = [
    'Integration with real-time parts pricing APIs',
    'Support for more vehicle types and damage categories',
    'Mobile app with augmented reality damage visualization',
    'Direct integration with insurance claim systems',
    'Multi-language support and international market expansion'
  ]

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-apex-text mb-4">
            About ApexAutoAI
          </h1>
          <p className="text-xl text-apex-text-muted">
            Revolutionizing vehicle damage assessment through artificial intelligence
          </p>
        </div>

        {/* Purpose Section */}
        <Card className="glass-card border-white/10 mb-8">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Target className="h-6 w-6 text-apex-cyan" />
              <CardTitle className="text-apex-text">Our Purpose</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-apex-text-muted leading-relaxed">
              ApexAutoAI was developed to streamline the vehicle damage assessment process using cutting-edge artificial intelligence. 
              Our system analyzes vehicle damage photos to provide accurate cost estimates, reducing assessment time from hours to minutes 
              while maintaining professional-grade accuracy. This technology empowers insurance adjusters, auto repair shops, and vehicle 
              owners with instant, reliable damage evaluations that facilitate faster claim processing and repair decisions.
            </p>
          </CardContent>
        </Card>

        {/* Team Section */}
        <Card className="glass-card border-white/10 mb-8">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Users className="h-6 w-6 text-apex-cyan" />
              <CardTitle className="text-apex-text">Meet the Team</CardTitle>
            </div>
            <CardDescription className="text-apex-text-muted">
              The experts behind ApexAutoAI's innovative technology
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {team.map((member, index) => (
                <div key={index} className="flex space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-apex-cyan to-apex-magenta flex items-center justify-center text-white font-bold text-lg">
                      {member.image}
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-apex-text">{member.name}</h3>
                    <p className="text-apex-cyan text-sm font-medium mb-2">{member.role}</p>
                    <p className="text-apex-text-muted text-sm">{member.bio}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Limitations Section */}
        <Card className="glass-card border-white/10 mb-8">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-6 w-6 text-yellow-400" />
              <CardTitle className="text-apex-text">Current Limitations</CardTitle>
            </div>
            <CardDescription className="text-apex-text-muted">
              Important considerations when using ApexAutoAI
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {limitations.map((limitation, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-yellow-400 mt-2 flex-shrink-0" />
                  <span className="text-apex-text-muted">{limitation}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Future Work Section */}
        <Card className="glass-card border-white/10">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Lightbulb className="h-6 w-6 text-apex-magenta" />
              <CardTitle className="text-apex-text">Future Development</CardTitle>
            </div>
            <CardDescription className="text-apex-text-muted">
              Planned enhancements and new features
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {futureWork.map((item, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-apex-magenta mt-2 flex-shrink-0" />
                  <span className="text-apex-text-muted">{item}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Academic Notice */}
        <div className="mt-8 p-6 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-6 w-6 text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-yellow-400 mb-2">Academic Demonstration</h3>
              <p className="text-yellow-300/90 text-sm leading-relaxed">
                This application is developed for educational and demonstration purposes only. It is not intended for commercial use 
                or real-world damage assessments. The AI models and cost estimates are simulated and should not be used for actual 
                insurance claims or repair decisions. For production use, comprehensive validation, regulatory compliance, and 
                professional oversight would be required.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}