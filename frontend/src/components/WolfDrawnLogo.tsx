import React from 'react';

/**
 * Geometric Hand-Drawn Circular Wolf Badge
 * Matches the circular crest with warm amber/gold geometric line-art contours (Image 3).
 */
export const WolfDrawnIcon: React.FC<{
  className?: string;
  size?: number;
  strokeColor?: string;
  hasCircle?: boolean;
}> = ({
  className = '',
  size = 32,
  strokeColor = '#D97736',
  hasCircle = true,
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`transition-transform duration-300 ${className}`}
      aria-label="Lenny Growth Drawn Wolf Badge"
    >
      {/* Optional Outer Circular Rings */}
      {hasCircle && (
        <>
          <circle cx="32" cy="32" r="29" stroke={strokeColor} strokeWidth="2.5" />
          <circle cx="32" cy="32" r="26.5" stroke={strokeColor} strokeWidth="0.75" strokeOpacity="0.45" />
        </>
      )}

      {/* Outer Faceted Head & Ears Perimeter */}
      <path
        d="M 19 16 L 26 21 L 32 18 L 38 21 L 45 16 L 43 26 L 48 31 L 43 35 L 47 41 L 39 44 L 32 50 L 25 44 L 17 41 L 21 35 L 16 31 L 21 26 Z"
        stroke={strokeColor}
        strokeWidth="2"
        strokeLinejoin="round"
        strokeLinecap="round"
      />

      {/* Forehead Crest & Brow Diamond */}
      <path
        d="M 32 18 L 28 25 L 32 30 L 36 25 Z"
        stroke={strokeColor}
        strokeWidth="1.6"
        strokeLinejoin="round"
        strokeLinecap="round"
      />

      {/* Inner Ear Facets */}
      <path
        d="M 22 19 L 26 25 M 42 19 L 38 25"
        stroke={strokeColor}
        strokeWidth="1.4"
        strokeLinecap="round"
      />

      {/* Stylized Keen Eyes / Brow Angles */}
      <path
        d="M 22 28 L 28 32 M 42 28 L 36 32"
        stroke={strokeColor}
        strokeWidth="1.6"
        strokeLinecap="round"
      />

      {/* Central Snout & Muzzle Lines */}
      <path
        d="M 32 30 L 32 35 M 28 35 L 32 41 L 36 35 L 32 35 Z"
        stroke={strokeColor}
        strokeWidth="1.8"
        strokeLinejoin="round"
        strokeLinecap="round"
      />

      {/* Cheek Facet Angles & Chin Stroke */}
      <path
        d="M 28 35 L 21 35 M 36 35 L 43 35 M 32 41 L 32 50"
        stroke={strokeColor}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
};

/**
 * Brand Title Component
 * Clean typography matching the chat font, properly named "Lenny Growth Assistant",
 * without hover effects, animations, or underline strokes.
 */
export const DrawnBrandTitle: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`flex items-center min-w-0 ${className}`}>
      <span className="font-sans font-semibold text-[13.5px] leading-tight text-[#FAF5EE] tracking-normal select-none whitespace-nowrap">
        Lenny Growth Assistant
      </span>
    </div>
  );
};
