import React, { useEffect, useRef } from 'react';
import styled from 'styled-components';

const Pattern = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    let mouseX = 0;
    let mouseY = 0;
    let currentX = 0;
    let currentY = 0;
    let time = 0;

    const handleMouseMove = (e) => {
      // Inverse mouse tracking for depth parallax
      mouseX = (e.clientX / window.innerWidth - 0.5) * 40; 
      mouseY = (e.clientY / window.innerHeight - 0.5) * 40;
    };

    window.addEventListener('mousemove', handleMouseMove);
    let animationId;

    const loop = () => {
      currentX += (mouseX - currentX) * 0.05;
      currentY += (mouseY - currentY) * 0.05;
      time += 1;

      // Organic continuous drift
      const driftX = Math.sin(time * 0.005) * 20;
      const driftY = Math.cos(time * 0.004) * 20;

      if (containerRef.current) {
        // Integer snapping to prevent SVG texture flickering
        const x = Math.round(currentX + driftX);
        const y = Math.round(currentY + driftY);
        containerRef.current.style.transform = `translate3d(${x}px, ${y}px, 0)`;
      }

      animationId = window.requestAnimationFrame(loop);
    };

    loop();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <StyledWrapper>
      <div className="moving-container" ref={containerRef}>
        <div className="topography-layer" />
      </div>
      
      <svg width="0" height="0" aria-hidden="true" focusable="false">
        <filter id="topographic-filter">
          {/* Base fractal noise for the terrain topology */}
          <feTurbulence 
            type="fractalNoise" 
            baseFrequency="0.001" 
            numOctaves="3" 
            result="noise" 
            seed="42"
          />
          {/* Posterize to discrete height levels to isolate contours */}
          <feComponentTransfer in="noise" result="posterized">
            <feFuncR type="discrete" tableValues="0 0.5 1" />
            <feFuncG type="discrete" tableValues="0 0.5 1" />
            <feFuncB type="discrete" tableValues="0 0.5 1" />
          </feComponentTransfer>
          {/* Edge detection to selectively extract only the contour lines (everything else transparent) */}
          <feConvolveMatrix 
            order="3" 
            kernelMatrix="
              1 1 1 
              1 -8 1 
              1 1 1" 
            in="posterized" 
            result="edges" 
          />
          {/* Colorize extracted lines exactly to #59121e and drop everything else to pure black/transparent */}
          <feColorMatrix 
            type="matrix" 
            values="
              0 0 0 0 0.349 
              0 0 0 0 0.070 
              0 0 0 0 0.117 
              8 8 8 0 0" 
            in="edges" 
            result="redLines" 
          />
        </filter>
      </svg>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  position: absolute;
  inset: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  background-color: #000000; /* Pure black background */

  .moving-container {
    position: absolute;
    top: -10%;
    left: -10%;
    width: 120%;
    height: 120%;
    will-change: transform;
  }

  .topography-layer {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    background: transparent;
    filter: url(#topographic-filter);
    opacity: 1; 
  }
`;

export default Pattern;