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
      <div className="card-primary hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300 cursor-pointer group">
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-lg font-bold text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors">
                {episode.title}
              </h3>
              <div className="flex items-center space-x-2 mt-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-500">최신</span>
              </div>
            </div>
            <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-100 to-purple-100 rounded-xl group-hover:from-blue-200 group-hover:to-purple-200 transition-all duration-200">
              <Play className="w-5 h-5 text-blue-600" />
            </div>
          </div>

          <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {formatDate(episode.publication_date)}
            </div>
            {episode.duration_seconds && (
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {formatDuration(episode.duration_seconds)}
              </div>
            )}
            <div className="flex items-center">
              <Users className="w-4 h-4 mr-1" />
              {episode.papers_count} papers
            </div>
          </div>

          <div className="text-sm text-gray-600">
            Listen to the latest AI research papers
          </div>
        </div>
      </div>
    </Link>
  );
}
