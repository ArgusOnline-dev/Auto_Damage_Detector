import { type RefObject } from 'react'
import LiquidGlass from 'liquid-glass-react'

type LiquidGlassButtonProps = {
  children: React.ReactNode
  onClick?: () => void
  className?: string
  mouseContainer?: RefObject<HTMLElement | null>
}

function LiquidGlassButton({ children, onClick, className, mouseContainer }: LiquidGlassButtonProps) {
  return (
    <LiquidGlass
      displacementScale={64}
      blurAmount={0.08}
      saturation={120}
      aberrationIntensity={1.5}
      elasticity={0.28}
      cornerRadius={999}
      padding="12px 20px"
      className={className}
      mouseContainer={mouseContainer as any}
      style={{ display: 'inline-block', position: 'relative' }}
      onClick={onClick}
    >
      <div className="text-white font-medium flex items-center gap-2">
        {children}
      </div>
    </LiquidGlass>
  )
}

export default LiquidGlassButton


