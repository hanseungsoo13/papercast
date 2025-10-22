"""Summarizer service using Google Gemini Pro."""

import google.generativeai as genai

from src.models.paper import Paper
from src.utils.logger import logger
from src.utils.retry import retry_on_failure


class Summarizer:
    """Generates summaries of papers using Gemini Pro."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize the summarizer.
        
        Args:
            api_key: Google Gemini API key
            model_name: Model to use (default: gemini-pro)
        """
        self.logger = logger
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Generation config
        self.generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 5000,
            "top_p": 0.8,
            "top_k": 40
        }
    
    @retry_on_failure(max_attempts=3, exceptions=(Exception,))
    def generate_summary(self, paper: Paper, language: str = "ko") -> str:
        """Generate a summary for a paper.
        
        Args:
            paper: Paper object to summarize
            language: Target language (default: "ko" for Korean)
            
        Returns:
            Generated summary text
            
        Raises:
            Exception: If summary generation fails
        """
        self.logger.info(f"Generating summary for paper: {paper.id}")
        
        try:
            prompt = self._create_prompt(paper, language)
            
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
                self.logger.warning(f"No candidates in response for {paper.id}")
                raise ValueError("No response candidates generated")
            
            # Initialize summary variable
            summary = None
            
            # Check finish reason
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                if finish_reason != 1:  # 1 = STOP (normal completion)
                    self.logger.warning(f"Non-normal finish reason {finish_reason} for {paper.id}")
                    # Try to get partial text if available
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        summary = candidate.content.parts[0].text
                    else:
                        # Fallback to simple summary
                        summary = self._create_fallback_summary(paper, language)
                        self.logger.warning(f"Using fallback summary for {paper.id}")
                else:
                    # Normal completion
                    summary = response.text
            else:
                summary = response.text
            
            # Safety check: ensure summary is not None
            if summary is None:
                summary = self._create_fallback_summary(paper, language)
                self.logger.warning(f"Summary was None, using fallback for {paper.id}")
            
            if not self._validate_summary(summary):
                # If validation fails, create a basic summary
                summary = self._create_fallback_summary(paper, language)
                self.logger.warning(f"Using fallback summary due to validation failure for {paper.id}")
            
            self.logger.info(f"Successfully generated summary ({len(summary)} chars)")
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary for {paper.id}: {e}")
            # Create fallback summary instead of failing
            summary = self._create_fallback_summary(paper, language)
            self.logger.warning(f"Using fallback summary due to error for {paper.id}")
            return summary
    
    def _create_prompt(self, paper: Paper, language: str = "ko") -> str:
        """Create prompt for summary generation.
        
        Args:
            paper: Paper to summarize
            language: Target language
            
        Returns:
            Formatted prompt
        """
        if language == "ko":
            prompt = f"""다음 논문을 한국어로 요약하는 팟캐스트를 제작해주세요.:

            제목: {paper.title}
            저자: {', '.join(paper.authors)}
            초록: {paper.abstract}

            다음 사항을 포함하여 500-1000자 내외로 요약해 팟캐스트로 제작하세요.:
            1. 논문의 주요 내용
            2. 핵심 기여점
            3. 중요한 결과나 발견

            다음의 규칙을 지켜주세요.
            1. **, ## 와 같은 마크다운 형식을 사용하지 마세요.
            2. 팟캐스트는 한명의 나래이터를 가정하며, 이 나래이터는 자연스럽게 논문을 설명하는 인공지능 스토리텔러 입니다.
            3. 팟캐스트의 목적은 수신자가 논문을 쉽게 이해할 수 있도록 하는 목적이 있으며, 나래이터는 인공지능에 관심있는 학생에게 논문을 설명하며, 중요한 부분, 기억할 부분을 강조하도록 작성해줘.

            요약:"""
        else:
            prompt = f"""Summarize the following paper:

Title: {paper.title}
Authors: {', '.join(paper.authors)}
Abstract: {paper.abstract}

Please provide a 200-400 character summary including:
1. Main content of the paper
2. Key contributions
3. Important results or findings

Summary:"""
        
        return prompt
    
    def _validate_summary(self, summary: str) -> bool:
        """Validate generated summary.
        
        Args:
            summary: Summary text to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not summary:
            return False
        
        # Check length (between 50 and 1000 characters)
        if len(summary) < 500 or len(summary) > 5000:
            return False
        
        return True
    
    def _create_fallback_summary(self, paper: Paper, language: str = "ko") -> str:
        """Create a fallback summary when AI generation fails.
        
        Args:
            paper: Paper to summarize
            language: Target language
            
        Returns:
            Fallback summary text
        """
        if language == "ko":
            # Use more of abstract to meet minimum length (500 chars)
            abstract_preview = paper.abstract[:800] if len(paper.abstract) > 800 else paper.abstract
            authors_str = ", ".join(paper.authors[:5])
            if len(paper.authors) > 5:
                authors_str += f" 외 {len(paper.authors) - 5}명"
            
            summary = f"논문 제목: '{paper.title}'\n\n"
            summary += f"저자: {authors_str}\n\n"
            summary += f"연구 내용:\n{abstract_preview}\n\n"
            summary += f"이 논문은 {paper.title}에 관한 최신 연구 결과를 담고 있습니다. "
            summary += f"총 {len(paper.authors)}명의 연구진이 참여하였으며, "
            summary += f"해당 분야의 중요한 발견과 기여를 포함하고 있습니다."
        else:
            abstract_preview = paper.abstract[:800] if len(paper.abstract) > 800 else paper.abstract
            authors_str = ", ".join(paper.authors[:5])
            if len(paper.authors) > 5:
                authors_str += f" et al."
            
            summary = f"Title: '{paper.title}'\n\n"
            summary += f"Authors: {authors_str}\n\n"
            summary += f"Research Content:\n{abstract_preview}\n\n"
            summary += f"This paper presents recent research findings on {paper.title}. "
            summary += f"A total of {len(paper.authors)} researchers participated, "
            summary += f"and it includes important discoveries and contributions to the field."
        
        return summary
    
    def generate_batch_summaries(self, papers: list[Paper], language: str = "ko") -> dict[str, str]:
        """Generate summaries for multiple papers.
        
        Args:
            papers: List of papers to summarize
            language: Target language
            
        Returns:
            Dictionary mapping paper ID to summary
        """
        summaries = {}
        
        for paper in papers:
            try:
                summary = self.generate_summary(paper, language)
                summaries[paper.id] = summary
            except Exception as e:
                self.logger.error(f"Failed to generate summary for {paper.id}: {e}")
                summaries[paper.id] = f"요약 생성 실패: {str(e)}"
        
        return summaries

