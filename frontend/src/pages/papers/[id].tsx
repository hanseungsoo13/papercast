/**
 * Paper Detail Page
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { ArrowLeft, ExternalLink, Star, Users, Calendar, MessageCircle, Download, Share2, ChevronDown, ChevronUp } from 'lucide-react';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

interface Paper {
  id: string;
  title: string;
  authors: string[];
  url: string;
  upvotes: number;
  summary: string;
  abstract?: string;
  tags?: string[];
  published_date?: string;
  venue?: string;
}

export default function PaperDetail() {
  const router = useRouter();
  const { id } = router.query;
  
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(false);
  const [isAbstractExpanded, setIsAbstractExpanded] = useState(false);

  useEffect(() => {
    if (!id) return;

    const fetchPaper = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('논문 상세 정보 요청:', id);
        
        // 실제 API에서 논문 데이터 가져오기
        const response = await fetch(`http://localhost:8001/api/papers/${id}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('논문을 찾을 수 없습니다');
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const paperData = await response.json();
        console.log('논문 데이터 받음:', paperData);
        
        // API 응답을 Paper 인터페이스에 맞게 변환
        const paper: Paper = {
          id: paperData.id,
          title: paperData.title,
          authors: paperData.authors,
          url: paperData.url,
          upvotes: paperData.upvotes,
          summary: paperData.summary || '',
          abstract: paperData.abstract,
          tags: paperData.categories || [],
          published_date: paperData.published_date,
          venue: paperData.venue
        };
        
        setPaper(paper);
      } catch (err) {
        console.error('Error fetching paper:', err);
        setError(err instanceof Error ? err.message : 'Failed to load paper details');
      } finally {
        setLoading(false);
      }
    };

    fetchPaper();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ErrorMessage message={error} />
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ErrorMessage message="Paper not found" />
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{paper.title} - Daily Paper Cast</title>
        <meta name="description" content={paper.summary} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
          <div className="container-custom">
            <div className="flex items-center justify-between py-4">
              <div className="flex items-center space-x-4">
                <Link 
                  href="/"
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5" />
                  <span>뒤로가기</span>
                </Link>
                <div className="h-6 w-px bg-gray-300"></div>
                <h1 className="text-lg font-semibold text-gray-900 truncate">
                  논문 상세정보
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <Link href="/archive" className="btn-ghost">
                  아카이브
                </Link>
                <button className="btn-primary">
                  구독하기
                </button>
              </div>
            </div>
          </div>
        </header>

        <div className="container-custom py-8">
          {/* Paper Header */}
          <div className="card-gradient mb-8">
            <div className="p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    논문 상세정보
                  </h2>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500 bg-white/80 backdrop-blur-sm px-3 py-1 rounded-full border border-white/20">
                    <Calendar className="w-4 h-4 mr-1 inline" />
                    {paper.published_date}
                  </span>
                  {paper.venue && (
                    <span className="text-sm text-gray-500 bg-white/80 backdrop-blur-sm px-3 py-1 rounded-full border border-white/20">
                      {paper.venue}
                    </span>
                  )}
                </div>
              </div>

              <h3 className="text-3xl font-bold text-gray-800 mb-6 leading-tight">
                {paper.title}
              </h3>

              {/* Paper Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="flex items-center text-sm text-gray-600 bg-white/50 rounded-lg p-3">
                  <Users className="w-5 h-5 mr-2 text-blue-500" />
                  <span className="font-medium">{paper.authors.length}명 저자</span>
                </div>
                <div className="flex items-center text-sm text-gray-600 bg-white/50 rounded-lg p-3">
                  <Star className="w-5 h-5 mr-2 text-yellow-500" />
                  <span className="font-medium">{paper.upvotes} upvotes</span>
                </div>
                <div className="flex items-center text-sm text-gray-600 bg-white/50 rounded-lg p-3">
                  <ExternalLink className="w-5 h-5 mr-2 text-green-500" />
                  <span className="font-medium">원문 링크</span>
                </div>
              </div>

              {/* Authors */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-800 mb-3">저자</h4>
                <div className="flex flex-wrap gap-2">
                  {paper.authors.map((author, index) => (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {author}
                    </span>
                  ))}
                </div>
              </div>

              {/* Tags */}
              {paper.tags && paper.tags.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-3">태그</h4>
                  <div className="flex flex-wrap gap-2">
                    {paper.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-4">
                <a
                  href={paper.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary flex items-center space-x-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>논문 원문 보기</span>
                </a>
                <button className="btn-secondary flex items-center space-x-2">
                  <Download className="w-4 h-4" />
                  <span>PDF 다운로드</span>
                </button>
                <button className="btn-secondary flex items-center space-x-2">
                  <Share2 className="w-4 h-4" />
                  <span>공유하기</span>
                </button>
                <button className="btn-secondary flex items-center space-x-2">
                  <MessageCircle className="w-4 h-4" />
                  <span>논평 보기</span>
                </button>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="card mb-8">
            <div className="p-6">
              <h4 className="text-xl font-bold text-gray-900 mb-4">요약</h4>
              <div className="text-gray-700 leading-relaxed">
                <p className={isSummaryExpanded ? '' : 'line-clamp-4'}>
                  {paper.summary}
                </p>
                  {paper.summary.length > 300 && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        setIsSummaryExpanded(!isSummaryExpanded);
                      }}
                      className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm font-medium mt-3 transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-2 rounded-lg border border-blue-200 hover:border-blue-300"
                    >
                      <span>
                        {isSummaryExpanded ? '간략히 보기' : '더보기'}
                      </span>
                      {isSummaryExpanded ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  )}
              </div>
            </div>
          </div>

          {/* Abstract */}
          {paper.abstract && (
            <div className="card mb-8">
              <div className="p-6">
                <h4 className="text-xl font-bold text-gray-900 mb-4">초록</h4>
                <div className="text-gray-700 leading-relaxed">
                  <p className={isAbstractExpanded ? '' : 'line-clamp-6'}>
                    {paper.abstract}
                  </p>
                  {paper.abstract.length > 500 && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        setIsAbstractExpanded(!isAbstractExpanded);
                      }}
                      className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm font-medium mt-3 transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-2 rounded-lg border border-blue-200 hover:border-blue-300"
                    >
                      <span>
                        {isAbstractExpanded ? '간략히 보기' : '더보기'}
                      </span>
                      {isAbstractExpanded ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Related Papers */}
          <div className="card mb-8">
            <div className="p-6">
              <h4 className="text-xl font-bold text-gray-900 mb-4">관련 논문</h4>
              <div className="space-y-4">
                <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <h5 className="font-medium text-gray-900 mb-2">Attention Is All You Need</h5>
                  <p className="text-sm text-gray-600 mb-2">Vaswani et al., 2017</p>
                  <p className="text-sm text-gray-700">The original transformer paper that introduced the attention mechanism.</p>
                </div>
                <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <h5 className="font-medium text-gray-900 mb-2">BERT: Pre-training of Deep Bidirectional Transformers</h5>
                  <p className="text-sm text-gray-600 mb-2">Devlin et al., 2018</p>
                  <p className="text-sm text-gray-700">A bidirectional transformer model for language understanding.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex justify-between items-center">
            <Link href="/" className="btn-secondary">
              홈으로 돌아가기
            </Link>
            <Link href="/archive" className="btn-primary">
              다른 논문 보기
            </Link>
          </div>
        </div>
      </main>
    </>
  );
}
