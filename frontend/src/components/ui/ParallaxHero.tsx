import { useRef, useState } from "react"

export function ParallaxHero({ children }: { children: React.ReactNode }) {
  const [rotate, setRotate] = useState({ x: 0, y: 0 })
  const ref = useRef<HTMLDivElement>(null)

  function onMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    if (!ref.current) return
    const box = ref.current.getBoundingClientRect()
    const x = e.clientX - box.left
    const y = e.clientY - box.top
    const centerX = box.width / 2
    const centerY = box.height / 2
    
    const rotateX = ((y - centerY) / centerY) * -5
    const rotateY = ((x - centerX) / centerX) * 5
    setRotate({ x: rotateX, y: rotateY })
  }

  function onMouseLeave() {
    setRotate({ x: 0, y: 0 })
  }

  return (
    <div
      ref={ref}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#070C18]"
      style={{ perspective: "1000px" }}
    >
      <div
        className="absolute inset-0 w-full h-full transition-transform duration-200 ease-out"
        style={{
          transform: `rotateX(${rotate.x}deg) rotateY(${rotate.y}deg) scale(1.05)`,
          transformStyle: "preserve-3d",
        }}
      >
        <img
          src="/wcip-bg.jpg"
          alt="WCIP 3D Background"
          className="absolute inset-0 w-full h-full object-cover object-center pointer-events-none"
        />
        <div className="absolute inset-0 bg-[#070C18]/50 backdrop-brightness-75" />
      </div>

      <div
        className="relative z-10 transition-transform duration-300 ease-out w-full px-4"
        style={{
          transform: `translateX(${rotate.y * 2}px) translateY(${rotate.x * 2}px)`,
          transformStyle: "preserve-3d",
        }}
      >
        {children}
      </div>
    </div>
  )
}