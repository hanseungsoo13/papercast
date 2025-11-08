'use client';

import { useState } from 'react';
import Calendar from './Calendar';
import PaperList from './PaperList';

interface HomePageClientProps {
  availableDates: string[];
  apiUrl: string;
}

export default function HomePageClient({ availableDates, apiUrl }: HomePageClientProps) {
  const today = new Date();
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(today);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-900 mb-3">
            📚 PaperCast
          </h1>
          <p className="text-xl text-gray-600">
            AI 논문 요약 및 팟캐스트
          </p>
        </div>

        {/* 메인 컨텐츠 영역 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 캘린더 섹션 */}
          <div className="lg:sticky lg:top-8 lg:h-fit">
            <Calendar
              selectedDate={selectedDate}
              onDateSelect={setSelectedDate}
              availableDates={availableDates}
            />
          </div>

          {/* 논문 목록 섹션 */}
          <div>
            <PaperList selectedDate={selectedDate} apiUrl={apiUrl} />
          </div>
        </div>
      </div>
    </div>
  );
}
