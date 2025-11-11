import { useState } from 'react'
import { Calendar, DollarSign, FileText, Eye, Download, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { mockReports, type Report } from '@/lib/mockData'
import { useToast } from '@/hooks/use-toast'

export default function Reports() {
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)
  const { toast } = useToast()

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const printReport = () => {
    window.print()
    toast({
      title: "Report printed",
      description: "The damage assessment report has been sent to your printer."
    })
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-apex-text mb-4">
            Damage Reports
          </h1>
          <p className="text-xl text-apex-text-muted">
            View and manage your vehicle damage assessment reports
          </p>
        </div>

        {/* Reports Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockReports.map((report) => (
            <Card key={report.id} className="glass-card border-white/10 hover:border-apex-cyan/30 smooth-transition group">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <CardTitle className="text-apex-text text-lg leading-tight">
                      {report.title}
                    </CardTitle>
                    <div className="flex items-center text-apex-text-muted text-sm">
                      <Calendar className="h-4 w-4 mr-1" />
                      {formatDate(report.date)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-apex-cyan font-bold text-lg">
                      ${report.totalLikely.toLocaleString()}
                    </div>
                    <div className="text-apex-text-muted text-sm">
                      Est. Cost
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-apex-text-muted">Damage Areas:</span>
                    <span className="text-apex-text">{report.detections.length}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-apex-text-muted">Labor Rate:</span>
                    <span className="text-apex-text">${report.laborRate}/hr</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-apex-text-muted">Parts:</span>
                    <span className="text-apex-text capitalize">{report.partsPreference}</span>
                  </div>
                </div>

                <Dialog>
                  <DialogTrigger asChild>
                    <Button 
                      variant="glass" 
                      className="w-full group-hover:border-apex-cyan/40"
                      onClick={() => setSelectedReport(report)}
                    >
                      <Eye className="mr-2 h-4 w-4" />
                      View Details
                    </Button>
                  </DialogTrigger>
                  
                  <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-apex-surface border-white/10">
                    <DialogHeader>
                      <DialogTitle className="text-apex-text">{report.title}</DialogTitle>
                      <DialogDescription className="text-apex-text-muted">
                        Damage Assessment Report - {formatDate(report.date)}
                      </DialogDescription>
                    </DialogHeader>

                    {selectedReport && (
                      <div className="space-y-6">
                        {/* Image Gallery */}
                        <div>
                          <h3 className="text-lg font-semibold text-apex-text mb-3">Vehicle Images</h3>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {selectedReport.images.map((image, index) => (
                              <div key={index} className="relative aspect-video bg-apex-surface rounded-lg overflow-hidden">
                                <div className="absolute inset-0 flex items-center justify-center text-apex-text-muted">
                                  <FileText className="h-8 w-8" />
                                  <span className="ml-2">Image {index + 1}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Damage Details Table */}
                        <div>
                          <h3 className="text-lg font-semibold text-apex-text mb-3">Damage Assessment</h3>
                          <Table>
                            <TableHeader>
                              <TableRow className="border-white/10">
                                <TableHead className="text-apex-text">Part</TableHead>
                                <TableHead className="text-apex-text">Damage Type</TableHead>
                                <TableHead className="text-apex-text">Severity</TableHead>
                                <TableHead className="text-apex-text">Labor Hours</TableHead>
                                <TableHead className="text-apex-text">Parts Cost</TableHead>
                                <TableHead className="text-apex-text">Subtotal</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {selectedReport.detections.map((detection) => {
                                const laborCost = detection.laborHours * selectedReport.laborRate
                                const partsCost = selectedReport.partsPreference === 'oem' 
                                  ? detection.partsNew 
                                  : detection.partsUsed
                                const subtotal = laborCost + partsCost

                                return (
                                  <TableRow key={detection.id} className="border-white/10">
                                    <TableCell className="text-apex-text">{detection.part}</TableCell>
                                    <TableCell className="text-apex-text">{detection.damage}</TableCell>
                                    <TableCell>
                                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                                        detection.severity === 'severe' ? 'bg-red-500/20 text-red-400' :
                                        detection.severity === 'moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                                        'bg-green-500/20 text-green-400'
                                      }`}>
                                        {detection.severity}
                                      </span>
                                    </TableCell>
                                    <TableCell className="text-apex-text">{detection.laborHours}</TableCell>
                                    <TableCell className="text-apex-text">${partsCost}</TableCell>
                                    <TableCell className="text-apex-text font-semibold">${subtotal.toLocaleString()}</TableCell>
                                  </TableRow>
                                )
                              })}
                            </TableBody>
                          </Table>
                        </div>

                        {/* Cost Summary */}
                        <Card className="glass-card border-apex-cyan/20">
                          <CardHeader>
                            <CardTitle className="text-apex-text">Cost Summary</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="grid grid-cols-3 gap-4 text-center">
                              <div>
                                <div className="text-2xl font-bold text-apex-text">${selectedReport.totalMin.toLocaleString()}</div>
                                <div className="text-apex-text-muted">Minimum</div>
                              </div>
                              <div>
                                <div className="text-3xl font-bold text-apex-cyan">${selectedReport.totalLikely.toLocaleString()}</div>
                                <div className="text-apex-text-muted">Most Likely</div>
                              </div>
                              <div>
                                <div className="text-2xl font-bold text-apex-text">${selectedReport.totalMax.toLocaleString()}</div>
                                <div className="text-apex-text-muted">Maximum</div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        {/* Actions */}
                        <div className="flex gap-2 pt-4">
                          <Button onClick={printReport} variant="hero" className="flex-1">
                            <Download className="mr-2 h-4 w-4" />
                            Print Report
                          </Button>
                        </div>
                      </div>
                    )}
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {mockReports.length === 0 && (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-apex-text-muted mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-apex-text mb-2">No reports yet</h3>
            <p className="text-apex-text-muted mb-6">Upload some vehicle images to get started with damage assessment.</p>
            <Button asChild variant="hero">
              <a href="/upload">
                Create First Report
              </a>
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}