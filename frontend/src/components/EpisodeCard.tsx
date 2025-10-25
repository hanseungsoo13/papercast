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
      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer">
        <div className="p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
              {episode.title}
            </h3>
            <Play className="w-5 h-5 text-blue-600" />
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
