"""Short summary service for generating 3-line summaries using Gemini."""

import google.generativeai as genai
from typing import Optional
from src.utils.logger import logger
from src.utils.config import config
from src.utils.retry import retry_on_failure


class ShortSummarizer:
    """Generates short 3-line summaries for papers using Gemini Pro."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initialize the short summarizer with Gemini API."""
        self.logger = logger
        self.api_key = config.gemini_api_key
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Generation config
        self.generation_config = {
            "temperature": 0.4,
            "top_p": 0.8,
            "top_k": 40
        }
    
    @retry_on_failure(max_attempts=3, exceptions=(Exception,))
    def generate_short_summary(self, title: str, abstract: str, full_summary: str) -> str:
        """Generate a 3-line summary for a paper.
        
        Args:
            title: Paper title
            abstract: Paper abstract
            full_summary: Full AI-generated summary
            
        Returns:
            3-line summary string
        """
        self.logger.info(f"Generating short summary for: {title}")
        
        try:
            prompt = self._create_prompt(title, abstract, full_summary)
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
            
            # Check if response has valid content
            if not response.candidates:
                self.logger.warning(f"No candidates in response for short summary of {title}")
                return self._fallback_summary(full_summary)
            
            # Initialize summary variable
            short_summary = None
            
            # Check finish reason
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                if finish_reason != 1:  # 1 = STOP (normal completion)
                    self.logger.warning(f"Non-normal finish reason {finish_reason} for short summary of {title}")
                    # Try to get partial text if available
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        short_summary = candidate.content.parts[0].text
                    else:
                        short_summary = self._fallback_summary(full_summary)
                else:
                    # Normal completion
                    short_summary = response.text
            else:
                short_summary = response.text
            
            # Safety check: ensure summary is not None
            if short_summary is None:
                short_summary = self._fallback_summary(full_summary)
                self.logger.warning(f"Short summary was None, using fallback for {title}")
            
            # Process and validate the summary
            short_summary = self._process_summary(short_summary)
            
            if not self._validate_short_summary(short_summary):
                short_summary = self._fallback_summary(full_summary)
                self.logger.warning(f"Using fallback short summary due to validation failure for {title}")
            
            self.logger.info(f"Successfully generated short summary for {title}")
            return short_summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate short summary for {title}: {e}")
            return self._fallback_summary(full_summary)
    
    def _create_prompt(self, title: str, abstract: str, full_summary: str) -> str:
        """Create prompt for short summary generation."""
        return f"""
다음 AI 논문에 대해 3줄로 간단하게 요약해주세요. 각 줄은 핵심 내용을 담고 있어야 합니다.

논문 제목: {title}
논문 초록: {abstract}
상세 요약: {full_summary}

요구사항:
1. 정확히 3줄로 요약
2. 각 줄은 50자 이내
3. 핵심 내용만 포함
4. 한국어로 작성
5. 기술적 용어는 쉽게 설명
"""
    
    def _process_summary(self, summary: str) -> str:
        """Process and format the generated summary."""
        if not summary:
            return ""
        
        # Clean up the summary
        summary = summary.strip()
        
        # Split into lines and clean
        lines = summary.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Ensure exactly 3 lines
        if len(lines) > 3:
            lines = lines[:3]
        elif len(lines) < 3:
            # Add empty lines if needed
            while len(lines) < 3:
                lines.append('')
        
        return '\n'.join(lines)
    
    def _validate_short_summary(self, summary: str) -> bool:
        """Validate the generated short summary."""
        if not summary:
            return False
        
        lines = summary.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Should have at least 1 non-empty line
        if len(lines) < 1:
            return False
        
        # Each line should be reasonable length
        for line in lines:
            if len(line) > 100:  # Too long for a short summary line
                return False
        
        return True
    
    def _fallback_summary(self, full_summary: str) -> str:
        """Create a fallback summary from the full summary."""
        self.logger.info("Using fallback for short summary.")
        lines = full_summary.split('\n')
        return '\n'.join(lines[:3]) if len(lines) > 3 else full_summary
    
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
            papers: List of paper dictionaries or Paper objects
            
        Returns:
            List of papers with short_summary field added
        """
        results = []
        
        for paper in papers:
            try:
                # Handle both dict and Paper object
                if hasattr(paper, 'short_summary'):
                    # Paper object
                    if not paper.short_summary:
                        short_summary = self.generate_short_summary(
                            paper.title,
                            paper.abstract,
                            paper.summary
                        )
                        paper.short_summary = short_summary
                        self.logger.info(f"Added short summary for paper: {paper.id}")
                    else:
                        self.logger.info(f"Paper {paper.id} already has short summary")
                else:
                    # Dict object
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
                self.logger.error(f"Failed to process paper {paper.get('id', 'unknown') if isinstance(paper, dict) else getattr(paper, 'id', 'unknown')}: {e}")
                # 원본 논문 정보 유지
                results.append(paper)
        
        return results
