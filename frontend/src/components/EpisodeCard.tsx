/**
 * Episode Card Component
 */

import Link from 'next/link';
import { Calendar, Clock, Users, Play } from 'lucide-react';
import { Episode } from '../services/types';
import { formatDate, formatDuration } from '../services/api';

interface EpisodeCardProps {
  episode: Episode;
}

export default function EpisodeCard({ episode }: EpisodeCardProps) {
  return (
    <Link href={`/episodes/${episode.id}`}>
      <div className="episode-card group relative overflow-hidden">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        {/* Card Content */}
        <div className="relative p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
                  최신 에피소드
                </span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors">
                {episode.title}
              </h3>
            </div>
            <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl group-hover:scale-110 transition-all duration-300 shadow-lg">
              <Play className="w-5 h-5" />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 gap-2 mb-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Calendar className="w-4 h-4 text-blue-500" />
              <span className="font-medium">{formatDate(episode.publication_date)}</span>
            </div>
            
            {episode.duration_seconds && (
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Clock className="w-4 h-4 text-purple-500" />
                <span>{formatDuration(episode.duration_seconds)}</span>
              </div>
            )}
            
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Users className="w-4 h-4 text-green-500" />
              <span>{episode.papers_count} 논문</span>
            </div>
          </div>

          {/* Description */}
          <div className="text-sm text-gray-600 mb-4 line-clamp-2">
            최신 AI 연구 논문을 한국어로 요약한 팟캐스트를 들어보세요
          </div>

          {/* Play Button */}
          <div className="flex items-center justify-between">
            <button className="btn-primary text-sm px-4 py-2 flex items-center space-x-2 group-hover:shadow-glow transition-all duration-300">
              <Play className="w-4 h-4" />
              <span>재생하기</span>
            </button>
            <div className="text-xs text-gray-500">
              클릭하여 자세히 보기
            </div>
          </div>
        </div>

        {/* Hover Effect */}
        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
      </div>
    </Link>
  );
}

