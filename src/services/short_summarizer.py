"""Short summary service for generating 3-line summaries using Gemini."""

import os
import google.generativeai as genai
from typing import Optional
from src.utils.logger import logger


class ShortSummarizer:
    """Generates short 3-line summaries for papers using Gemini Pro."""
    
    def __init__(self):
        """Initialize the short summarizer with Gemini API."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.logger = logger
    
    def generate_short_summary(self, title: str, abstract: str, full_summary: str) -> str:
        """Generate a 3-line summary for a paper.
        
        Args:
            title: Paper title
            abstract: Paper abstract
            full_summary: Full AI-generated summary
            
        Returns:
            3-line summary string
        """
        try:
            prompt = f"""
다음 논문에 대해 3줄로 간단하게 요약해주세요. 각 줄은 핵심 내용을 담고 있어야 합니다.

논문 제목: {title}

논문 초록: {abstract}

상세 요약: {full_summary}

요구사항:
1. 정확히 3줄로 요약
2. 각 줄은 50자 이내
3. 핵심 내용만 포함
4. 한국어로 작성
5. 기술적 용어는 쉽게 설명

3줄 요약:
"""
            
            response = self.model.generate_content(prompt)
            short_summary = response.text.strip()
            
            # 3줄로 제한
            lines = short_summary.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if len(lines) > 3:
                short_summary = '\n'.join(lines[:3])
            elif len(lines) < 3:
                # 부족한 줄 수만큼 빈 줄 추가
                while len(lines) < 3:
                    lines.append('')
                short_summary = '\n'.join(lines)
            
            self.logger.info(f"Generated short summary for paper: {title[:50]}...")
            return short_summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate short summary: {e}")
            # Fallback: 간단한 요약 생성
            return self._create_fallback_summary(title, full_summary)
    
    def _create_fallback_summary(self, title: str, full_summary: str) -> str:
        """Create a fallback summary when Gemini fails.
        
        Args:
            title: Paper title
            full_summary: Full summary text
            
        Returns:
            Fallback 3-line summary
        """
        # 첫 번째 줄: 제목에서 핵심 키워드 추출
        title_words = title.split()[:5]  # 처음 5개 단어
        line1 = f"{' '.join(title_words)}에 대한 연구"
        
        # 두 번째 줄: 요약에서 첫 번째 문장
        first_sentence = full_summary.split('.')[0] if full_summary else "논문의 주요 내용"
        line2 = first_sentence[:50] + "..." if len(first_sentence) > 50 else first_sentence
        
        # 세 번째 줄: 간단한 설명
        line3 = "AI 및 머신러닝 분야의 혁신적인 접근 방식을 제시합니다."
        
        return f"{line1}\n{line2}\n{line3}"
    
    def batch_generate_summaries(self, papers: list) -> list:
        """Generate short summaries for multiple papers.
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            List of papers with short_summary field added
        """
        results = []
        
        for paper in papers:
            try:
                if not paper.get('short_summary'):
                    short_summary = self.generate_short_summary(
                        paper.get('title', ''),
                        paper.get('abstract', ''),
                        paper.get('summary', '')
                    )
                    paper['short_summary'] = short_summary
                    self.logger.info(f"Added short summary for paper: {paper.get('id', 'unknown')}")
                else:
                    self.logger.info(f"Paper {paper.get('id', 'unknown')} already has short summary")
                
                results.append(paper)
                
            except Exception as e:
                self.logger.error(f"Failed to process paper {paper.get('id', 'unknown')}: {e}")
                # 원본 논문 정보 유지
                results.append(paper)
        
        return results
