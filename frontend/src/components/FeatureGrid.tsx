/**
 * Feature Grid Component
 * Displays key features and benefits of the Daily Paper Cast service
 */

import React from 'react';
import { 
  Clock, 
  Download, 
  Globe, 
  Headphones, 
  BookOpen, 
  Zap,
  Shield,
  Users
} from 'lucide-react';

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}

const features: Feature[] = [
  {
    icon: <Clock className="w-6 h-6" />,
    title: "매일 자동 업데이트",
    description: "매일 아침 6시, 최신 AI 논문을 자동으로 수집하고 요약합니다",
    color: "from-blue-500 to-blue-600"
  },
  {
    icon: <Headphones className="w-6 h-6" />,
    title: "고품질 음성",
    description: "Google TTS로 생성된 자연스러운 한국어 음성을 제공합니다",
    color: "from-purple-500 to-purple-600"
  },
  {
    icon: <BookOpen className="w-6 h-6" />,
    title: "논문 원문 링크",
    description: "각 논문의 원문을 바로 확인할 수 있는 링크를 제공합니다",
    color: "from-green-500 to-green-600"
  },
  {
    icon: <Globe className="w-6 h-6" />,
    title: "언제 어디서나",
    description: "웹 브라우저에서 바로 재생하고 다운로드할 수 있습니다",
    color: "from-orange-500 to-orange-600"
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: "빠른 이해",
    description: "복잡한 논문을 쉽게 이해할 수 있도록 요약합니다",
    color: "from-yellow-500 to-yellow-600"
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: "신뢰할 수 있는 정보",
    description: "Hugging Face 트렌딩 논문을 기반으로 한 검증된 정보입니다",
    color: "from-red-500 to-red-600"
  }
];

export default function FeatureGrid() {
  return (
    <section className="py-16">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          왜 Daily Paper Cast인가요?
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          AI 연구의 최신 동향을 빠르고 쉽게 파악할 수 있는 
          혁신적인 팟캐스트 서비스입니다
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {features.map((feature, index) => (
          <div
            key={index}
            className="group relative bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:border-gray-200"
          >
            {/* Icon with gradient background */}
            <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-r ${feature.color} text-white mb-4 group-hover:scale-110 transition-transform duration-300`}>
              {feature.icon}
            </div>

            {/* Content */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>

            {/* Hover effect */}
            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10"></div>
          </div>
        ))}
      </div>

      {/* Call to Action */}
      <div className="text-center mt-12">
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8 border border-blue-100">
          <div className="flex items-center justify-center mb-4">
            <Users className="w-8 h-8 text-blue-600 mr-3" />
            <h3 className="text-2xl font-bold text-gray-900">
              지금 시작하세요
            </h3>
          </div>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            매일 아침, 최신 AI 연구 논문을 팟캐스트로 만나보세요. 
            복잡한 논문도 쉽게 이해할 수 있습니다.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="btn-primary">
              최신 에피소드 듣기
            </button>
            <button className="btn-secondary">
              아카이브 보기
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
