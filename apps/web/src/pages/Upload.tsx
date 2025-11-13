import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload as UploadIcon, X, Download, Save, Loader2, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { uploadImages, runInference, getEstimate, downloadPDFReport, type Detection, type EstimateResponse } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

// Frontend DamageDetection interface (for UI display)
interface DamageDetection {
  id: string
  imageId: string
  part: string
  damage: string
  severity: 'minor' | 'moderate' | 'severe'
  laborHours: number
  partsNew: number
  partsUsed: number
  x: number
  y: number
  width: number
  height: number
  confidence: number
}

export default function Upload() {
  const [files, setFiles] = useState<File[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [detections, setDetections] = useState<DamageDetection[]>([])
  const [selectedFileIndex, setSelectedFileIndex] = useState(0)
  const [laborRate, setLaborRate] = useState(150)
  const [partsPreference, setPartsPreference] = useState<'oem' | 'used' | 'both'>('oem')
  const [fileIds, setFileIds] = useState<string[]>([])
  const [estimate, setEstimate] = useState<EstimateResponse | null>(null)
  const [includeIntact, setIncludeIntact] = useState<boolean>(false) // Hide intact by default
  const [imageDimensions, setImageDimensions] = useState<Record<string, { width: number, height: number }>>({})
  const { toast } = useToast()
  const selectedImage = files[selectedFileIndex] || null
  const selectedFileId = fileIds[selectedFileIndex] || ''
  const severityColors: Record<'minor' | 'moderate' | 'severe', string> = {
    minor: '#FFD166',
    moderate: '#FB8500',
    severe: '#D90429'
  }
  const visibleDetections = selectedFileId
    ? detections.filter(det => det.imageId === selectedFileId)
    : detections
  const clampPercent = (value: number) => Math.min(100, Math.max(0, value))

  useEffect(() => {
    if (selectedFileIndex >= files.length && files.length > 0) {
      setSelectedFileIndex(files.length - 1)
    }
  }, [files.length, selectedFileIndex])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => {
      const newFiles = [...prev, ...acceptedFiles]
      if (prev.length === 0 && newFiles.length > 0) {
        setSelectedFileIndex(0)
      }
      return newFiles
    })
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: true
  })

  const removeFile = (index: number) => {
    setFiles(prev => {
      const newFiles = prev.filter((_, i) => i !== index)
      if (newFiles.length === 0) {
        setSelectedFileIndex(0)
      } else if (index === selectedFileIndex) {
        setSelectedFileIndex(0)
      } else if (index < selectedFileIndex) {
        setSelectedFileIndex(Math.max(0, selectedFileIndex - 1))
      }
      return newFiles
    })
  }

  const analyzeImages = async () => {
    if (files.length === 0) {
      toast({
        title: "No images selected",
        description: "Please upload at least one image to analyze.",
        variant: "destructive"
      })
      return
    }

    setIsAnalyzing(true)
    try {
      // Step 1: Upload images
      console.log('Uploading images...', files.length)
      const uploadedFileIds = await uploadImages(files)
      console.log('Uploaded file IDs:', uploadedFileIds)
      setFileIds(uploadedFileIds)
      
      if (!uploadedFileIds || uploadedFileIds.length === 0) {
        throw new Error('No file IDs returned from upload')
      }
      
      // Step 2: Run inference
      console.log('Running inference...', uploadedFileIds, 'includeIntact:', includeIntact)
      const inferenceResult = await runInference(uploadedFileIds, includeIntact)
      console.log('Inference result:', inferenceResult)
      
      if (!inferenceResult || !inferenceResult.results || inferenceResult.results.length === 0) {
        throw new Error('Invalid inference result received')
      }
      
      // Combine detections from all images
      const backendDetections: Detection[] = []
      const flattenedDetections: { det: Detection; imageId: string }[] = []
      inferenceResult.results.forEach((result) => {
        result.detections.forEach((det) => {
          backendDetections.push(det)
          flattenedDetections.push({ det, imageId: result.image_id })
        })
      })
      
      console.log(`Total detections across ${inferenceResult.results.length} image(s): ${backendDetections.length}`)
      if (inferenceResult.filtered_count > 0) {
        console.log(`Filtered out ${inferenceResult.filtered_count} intact detections`)
      }
      
      if (backendDetections.length === 0) {
        toast({
          title: "No damage detected",
          description: includeIntact 
            ? "No detections found in uploaded images." 
            : "No damaged parts detected. All parts appear intact. Try enabling 'Show Intact Parts' to see all detections.",
          variant: "default"
        })
        setDetections([])
        setIsAnalyzing(false)
        return
      }
      
      // Step 3: Get cost estimate
      // Backend only supports 'oem' or 'used', so use 'oem' for 'both' option
      const useOemParts = partsPreference === 'oem' || partsPreference === 'both'
      console.log('Getting estimate...', backendDetections.length, 'detections')
      const estimateResult = await getEstimate(
        backendDetections,
        laborRate,
        useOemParts
      )
      console.log('Estimate result:', estimateResult)
      setEstimate(estimateResult)
      
      if (!estimateResult || !estimateResult.line_items) {
        throw new Error('Invalid estimate result received')
      }
      
      // Step 4: Map backend detections to frontend format
      const selectedFileIdForFirstImage = uploadedFileIds[0]
      const mappedDetections: DamageDetection[] = flattenedDetections.map(({ det, imageId }, index) => {
        // Convert bbox [x1, y1, x2, y2] to x, y, width, height
        if (!det.bbox || det.bbox.length !== 4) {
          console.warn('Invalid bbox for detection:', det)
          // Use default bbox if invalid
          return {
            id: `${det.part}-${index}`,
            imageId: imageId || selectedFileIdForFirstImage,
            part: det.part,
            damage: det.damage_type,
            severity: (det.severity || 'moderate') as 'minor' | 'moderate' | 'severe',
            laborHours: 0,
            partsNew: 0,
            partsUsed: 0,
            x: 0,
            y: 0,
            width: 100,
            height: 100,
            confidence: det.confidence || 0
          }
        }
        
        const [x1, y1, x2, y2] = det.bbox
        const x = x1
        const y = y1
        const width = x2 - x1
        const height = y2 - y1
        
        // Get corresponding line item for cost data
        const lineItem = estimateResult.line_items[index] || estimateResult.line_items[0]
        
        return {
          id: `${det.part}-${index}`,
          imageId: imageId || selectedFileIdForFirstImage,
          part: det.part,
          damage: det.damage_type,
          severity: (det.severity || 'moderate') as 'minor' | 'moderate' | 'severe',
          laborHours: lineItem?.labor_hours || 0,
          partsNew: lineItem?.part_cost_new || 0,
          partsUsed: lineItem?.part_cost_used || 0,
          x,
          y,
          width,
          height,
          confidence: det.confidence || 0
        }
      })
      
      console.log('Mapped detections:', mappedDetections)
      setDetections(mappedDetections)
      toast({
        title: "Analysis complete",
        description: `Found ${mappedDetections.length} damage areas to review.`
      })
    } catch (error: any) {
      console.error('Analysis error:', error)
      toast({
        title: "Analysis failed", 
        description: error.message || "Please try again or contact support.",
        variant: "destructive"
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const updateDetection = (id: string, field: keyof DamageDetection, value: any, shouldRecalculate = false) => {
    setDetections(prev => {
      const updated = prev.map(det => 
        det.id === id ? { ...det, [field]: value } : det
      )
      if (shouldRecalculate) {
        updateEstimate(updated)
      }
      return updated
    })
  }

  // Re-fetch estimate when values change
  const updateEstimate = async (overrideDetections?: DamageDetection[]) => {
    const sourceDetections = overrideDetections ?? detections
    if (sourceDetections.length === 0 || !fileIds.length) return

    try {
      const backendDetections: Detection[] = sourceDetections.map(det => ({
        part: det.part,
        damage_type: det.damage,
        confidence: det.confidence ?? 0.85,
        bbox: [det.x, det.y, det.x + det.width, det.y + det.height],
        severity: det.severity
      }))

      const useOemParts = partsPreference === 'oem' || partsPreference === 'both'
      const estimateResult = await getEstimate(
        backendDetections,
        laborRate,
        useOemParts
      )
      setEstimate(estimateResult)

      const applyLineItems = (list: DamageDetection[]) =>
        list.map((det, index) => {
          const lineItem = estimateResult.line_items[index] || estimateResult.line_items[estimateResult.line_items.length - 1]
          return {
            ...det,
            laborHours: lineItem?.labor_hours ?? det.laborHours,
            partsNew: lineItem?.part_cost_new ?? det.partsNew,
            partsUsed: lineItem?.part_cost_used ?? det.partsUsed
          }
        })

      const updatedList = applyLineItems(sourceDetections)
      setDetections(updatedList)
    } catch (error: any) {
      toast({
        title: "Estimate update failed",
        description: error.message || "Please try again.",
        variant: "destructive"
      })
    }
  }

  // Update estimate when labor rate or parts preference changes
  const handleLaborRateChange = (value: number) => {
    setLaborRate(value)
    if (detections.length > 0) {
      updateEstimate()
    }
  }

  const handlePartsPreferenceChange = async (value: 'oem' | 'used' | 'both') => {
    setPartsPreference(value)
    if (detections.length > 0) {
      await updateEstimate()
    }
  }

  // Use estimate totals from backend, or calculate from detections if estimate not available
  const totals = estimate?.totals || null

  const generatePDF = async () => {
    if (!estimate || detections.length === 0) {
      toast({
        title: "No data available",
        description: "Please analyze images first.",
        variant: "destructive"
      })
      return
    }

    try {
      // Map detections back to backend format
      const backendDetections: Detection[] = detections.map(det => ({
        part: det.part,
        damage_type: det.damage,
        confidence: 0.85, // Default confidence
        bbox: [det.x, det.y, det.x + det.width, det.y + det.height],
        severity: det.severity
      }))

      const reportData = {
        report_id: `report-${Date.now()}`,
        image_ids: fileIds,
        detections: backendDetections,
        line_items: estimate.line_items,
        totals: estimate.totals,
        labor_rate: laborRate,
        use_oem_parts: partsPreference === 'oem' || partsPreference === 'both'
      }

      await downloadPDFReport(reportData, `damage-report-${Date.now()}.pdf`)
      toast({
        title: "Report ready",
        description: "Your damage assessment report has been downloaded."
      })
    } catch (error: any) {
      toast({
        title: "PDF generation failed",
        description: error.message || "Please try again.",
        variant: "destructive"
      })
    }
  }

  const saveDraft = () => {
    // Mock save to localStorage
    const draft = {
      files: files.map(f => f.name),
      detections,
      laborRate,
      partsPreference,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('apex-draft', JSON.stringify(draft))
    toast({
      title: "Draft saved",
      description: "Your progress has been saved locally."
    })
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-apex-text mb-4">
            Upload & Analyze
          </h1>
          <p className="text-xl text-apex-text-muted">
            Upload vehicle damage photos for instant AI-powered assessment
          </p>
        </div>

        {/* Upload Area */}
        <Card className="glass-card border-white/10 mb-8">
          <CardHeader>
            <CardTitle className="text-apex-text">Upload Images</CardTitle>
            <CardDescription className="text-apex-text-muted">
              Drag and drop multiple images or click to select files
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer smooth-transition ${
                isDragActive
                  ? 'border-apex-cyan bg-apex-cyan/5'
                  : 'border-white/20 hover:border-apex-cyan/50 hover:bg-apex-surface/50'
              }`}
            >
              <input {...getInputProps()} />
              <div className="h-12 w-12 text-apex-cyan mx-auto mb-4 flex items-center justify-center">
                <UploadIcon className="h-8 w-8" />
              </div>
              {isDragActive ? (
                <p className="text-apex-text">Drop the images here...</p>
              ) : (
                <div>
                  <p className="text-apex-text mb-2">Drop images here, or click to select</p>
                  <p className="text-apex-text-muted text-sm">Supports JPEG, PNG, WebP formats</p>
                </div>
              )}
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="mt-6">
                <h3 className="text-apex-text font-medium mb-3">Uploaded Files ({files.length})</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg bg-apex-surface border smooth-transition cursor-pointer ${
                        selectedFileIndex === index
                          ? 'border-apex-cyan glow-cyan'
                          : 'border-white/10 hover:border-white/20'
                      }`}
                      onClick={() => setSelectedFileIndex(index)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 min-w-0">
                          <Eye className="h-4 w-4 text-apex-cyan flex-shrink-0" />
                          <span className="text-sm text-apex-text truncate">{file.name}</span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            removeFile(index)
                          }}
                          className="text-red-400 hover:text-red-300 flex-shrink-0"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Analysis Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              <div>
                <Label htmlFor="labor-rate" className="text-apex-text">Labor Rate ($/hour)</Label>
                <Input
                  id="labor-rate"
                  type="number"
                  value={laborRate}
                  onChange={(e) => handleLaborRateChange(Number(e.target.value))}
                  className="bg-apex-surface border-white/10 text-apex-text"
                />
              </div>
              <div>
                <Label className="text-apex-text">Parts Preference</Label>
                <Select value={partsPreference} onValueChange={(value: 'oem' | 'used' | 'both') => handlePartsPreferenceChange(value)}>
                  <SelectTrigger className="bg-apex-surface border-white/10 text-apex-text">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-apex-surface border-white/10">
                    <SelectItem value="oem">OEM Parts</SelectItem>
                    <SelectItem value="used">Used Parts</SelectItem>
                    <SelectItem value="both">Both Options</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            {/* Show Intact Parts Toggle */}
            <div className="mt-4 flex items-center space-x-2">
              <Checkbox
                id="include-intact"
                checked={includeIntact}
                onCheckedChange={(checked) => setIncludeIntact(checked === true)}
                className="border-white/20"
              />
              <Label
                htmlFor="include-intact"
                className="text-apex-text cursor-pointer"
              >
                Show intact parts (parts with no damage)
              </Label>
            </div>

            <div className="flex justify-center mt-6">
              <Button
                onClick={analyzeImages}
                disabled={isAnalyzing || files.length === 0}
                variant="hero"
                size="lg"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  'Analyze Images'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Analysis Results */}
        {detections.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Image with Detection Boxes */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-apex-text">Damage Detection</CardTitle>
                <CardDescription className="text-apex-text-muted">
                  {selectedImage?.name || 'Select an image to view detections'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {selectedImage && (
                  <div className="relative">
                    <img
                      src={URL.createObjectURL(selectedImage)}
                      alt="Vehicle damage"
                      className="w-full h-auto rounded-lg"
                      onLoad={(e) => {
                        if (selectedFileId) {
                          setImageDimensions(prev => ({
                            ...prev,
                            [selectedFileId]: {
                              width: e.currentTarget.naturalWidth,
                              height: e.currentTarget.naturalHeight
                            }
                          }))
                        }
                      }}
                    />
                    {/* Detection boxes overlay */}
                    {visibleDetections.map((detection) => {
                      const dims = imageDimensions[detection.imageId || selectedFileId] || imageDimensions[selectedFileId] || { width: 1, height: 1 }
                      const left = clampPercent((detection.x / dims.width) * 100)
                      const top = clampPercent((detection.y / dims.height) * 100)
                      const width = clampPercent((detection.width / dims.width) * 100)
                      const height = clampPercent((detection.height / dims.height) * 100)
                      const severityColor = severityColors[detection.severity] || severityColors.moderate
                      return (
                      <div
                        key={detection.id}
                        className="absolute rounded-sm"
                        style={{
                          left: `${left}%`,
                          top: `${top}%`,
                          width: `${width}%`,
                          height: `${height}%`,
                          border: `2px solid ${severityColor}`,
                          backgroundColor: `${severityColor}20`
                        }}
                      >
                        <div
                          className="absolute -top-6 left-0 text-white text-xs px-1 rounded"
                          style={{ backgroundColor: severityColor }}
                        >
                          {detection.part} • {detection.severity}
                        </div>
                      </div>
                    )})}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Editable Detection Table */}
            <div className="space-y-6">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-apex-text">Damage Assessment</CardTitle>
                  <CardDescription className="text-apex-text-muted">
                    Review and edit the detected damage details
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow className="border-white/10">
                        <TableHead className="text-apex-text">Part</TableHead>
                        <TableHead className="text-apex-text">Damage</TableHead>
                        <TableHead className="text-apex-text">Severity</TableHead>
                        <TableHead className="text-apex-text">Labor (hrs)</TableHead>
                        <TableHead className="text-apex-text">Parts ($)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {detections.map((detection) => (
                        <TableRow key={detection.id} className="border-white/10">
                          <TableCell className="text-apex-text">{detection.part}</TableCell>
                          <TableCell className="text-apex-text">{detection.damage}</TableCell>
                          <TableCell>
                            <Select
                              value={detection.severity}
                              onValueChange={(value: 'minor' | 'moderate' | 'severe') => 
                                updateDetection(detection.id, 'severity', value, true)
                              }
                            >
                              <SelectTrigger className="bg-apex-surface border-white/10 text-apex-text">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-apex-surface border-white/10">
                                <SelectItem value="minor">Minor</SelectItem>
                                <SelectItem value="moderate">Moderate</SelectItem>
                                <SelectItem value="severe">Severe</SelectItem>
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              step="0.5"
                              value={detection.laborHours}
                              onChange={(e) => updateDetection(detection.id, 'laborHours', Number(e.target.value), true)}
                              className="bg-apex-surface border-white/10 text-apex-text w-20"
                            />
                          </TableCell>
                          <TableCell className="text-apex-text">
                            {partsPreference === 'both' ? (
                              <div className="text-xs">
                                <div>New: ${detection.partsNew.toLocaleString()}</div>
                                <div>Used: ${detection.partsUsed.toLocaleString()}</div>
                              </div>
                            ) : (
                              `$${partsPreference === 'oem' 
                                ? detection.partsNew.toLocaleString() 
                                : detection.partsUsed.toLocaleString()}`
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

              {/* Totals Card */}
              {totals && (
                <Card className="glass-card border-apex-cyan/20 glow-cyan">
                  <CardHeader>
                    <CardTitle className="text-apex-text">Cost Estimate</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-apex-text-muted">Minimum:</span>
                        <span className="text-apex-text font-semibold">${totals.min.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-apex-text-muted">Likely:</span>
                        <span className="text-apex-cyan font-bold text-lg">${totals.likely.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-apex-text-muted">Maximum:</span>
                        <span className="text-apex-text font-semibold">${totals.max.toLocaleString()}</span>
                      </div>
                    </div>

                    <div className="flex gap-2 mt-6">
                      <Button onClick={generatePDF} variant="hero" className="flex-1">
                        <Download className="mr-2 h-4 w-4" />
                        Download PDF
                      </Button>
                      <Button onClick={saveDraft} variant="glass" className="flex-1">
                        <Save className="mr-2 h-4 w-4" />
                        Save Draft
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
