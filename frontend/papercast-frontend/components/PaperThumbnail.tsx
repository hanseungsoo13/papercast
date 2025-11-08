'use client';

import { useState } from 'react';

interface PaperThumbnailProps {
  src: string;
  alt: string;
  className?: string;
}

export default function PaperThumbnail({
  src,
  alt,
  className = '',
}: PaperThumbnailProps) {
  const [imgSrc, setImgSrc] = useState(src);
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    if (!hasError) {
      setHasError(true);
      setImgSrc('https://via.placeholder.com/400x300?text=No+Image');
    }
  };

  return (
    <img
      src={imgSrc}
      alt={alt}
      className={className}
      onError={handleError}
    />
  );
}

