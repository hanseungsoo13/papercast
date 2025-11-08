'use client';

import { DayPicker } from 'react-day-picker';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

interface CalendarProps {
  selectedDate: Date | undefined;
  onDateSelect: (date: Date | undefined) => void;
  availableDates?: string[]; // 날짜 문자열 배열 (YYYY-MM-DD 형식)
}

export default function Calendar({ selectedDate, onDateSelect, availableDates = [] }: CalendarProps) {
  const today = new Date();
  
  // availableDates를 Date 객체로 변환
  const availableDatesSet = new Set(availableDates);
  
  // 날짜가 사용 가능한지 확인하는 함수
  const isDateAvailable = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    return availableDatesSet.has(dateStr);
  };

  // 날짜 스타일링을 위한 modifiers
  const modifiers = {
    available: (date: Date) => isDateAvailable(date),
    today: today,
  };

  const modifiersClassNames = {
    available: 'bg-blue-100 hover:bg-blue-200 text-blue-900 font-semibold',
    today: 'bg-blue-500 text-white font-bold',
    selected: 'bg-blue-600 text-white font-bold',
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">날짜 선택</h2>
      <DayPicker
        mode="single"
        selected={selectedDate}
        onSelect={onDateSelect}
        defaultMonth={selectedDate || today}
        locale={ko}
        modifiers={modifiers}
        modifiersClassNames={modifiersClassNames}
        disabled={(date) => date > today} // 미래 날짜 비활성화
        className="w-full"
        classNames={{
          months: 'flex flex-col sm:flex-row space-y-4 sm:space-x-4 sm:space-y-0',
          month: 'space-y-4',
          caption: 'flex justify-center pt-1 relative items-center mb-4',
          caption_label: 'text-lg font-semibold text-gray-900',
          nav: 'space-x-1 flex items-center',
          nav_button: 'h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100 border border-gray-300 rounded hover:bg-gray-100 flex items-center justify-center text-gray-700',
          nav_button_previous: 'absolute left-1',
          nav_button_next: 'absolute right-1',
          table: 'w-full border-collapse space-y-1',
          head_row: 'flex',
          head_cell: 'text-gray-500 rounded-md w-9 font-normal text-[0.8rem]',
          row: 'flex w-full mt-2',
          cell: 'text-center text-sm p-0 relative [&:has([aria-selected])]:bg-blue-50 first:[&:has([aria-selected])]:rounded-l-md last:[&:has([aria-selected])]:rounded-r-md focus-within:relative focus-within:z-20',
          day: 'h-9 w-9 p-0 font-normal aria-selected:opacity-100 hover:bg-blue-100 rounded-md transition-colors',
          day_selected: 'bg-blue-600 text-white hover:bg-blue-600 hover:text-white focus:bg-blue-600 focus:text-white',
          day_today: 'bg-blue-500 text-white font-bold',
          day_outside: 'opacity-50',
          day_disabled: 'opacity-30 cursor-not-allowed',
          day_range_middle: 'aria-selected:bg-blue-50 aria-selected:text-blue-900',
          day_hidden: 'invisible',
        }}
      />
      {selectedDate && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>선택된 날짜:</strong>{' '}
            {format(selectedDate, 'yyyy년 MM월 dd일 (EEEE)', { locale: ko })}
          </p>
        </div>
      )}
    </div>
  );
}
