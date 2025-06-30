import React from 'react';

interface ClickUpIconProps {
  className?: string;
  size?: number;
}

const ClickUpIcon: React.FC<ClickUpIconProps> = ({ className = '', size = 24 }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* ClickUp Logo - Simplified version */}
      <path
        d="M12 2L6 8L12 14L18 8L12 2Z"
        fill="#7B68EE"
        stroke="currentColor"
        strokeWidth="0.5"
      />
      <path
        d="M12 10L6 16L12 22L18 16L12 10Z"
        fill="#FF6B6B"
        stroke="currentColor"
        strokeWidth="0.5"
      />
      <circle
        cx="12"
        cy="12"
        r="2"
        fill="currentColor"
      />
    </svg>
  );
};

export default ClickUpIcon;
