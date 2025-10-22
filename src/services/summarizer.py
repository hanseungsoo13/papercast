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
            "max_output_tokens": 10000,
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
            prompt = f"""다음 논문을 팟캐스트 제작을 위한 핵심 내용 요약본으로 작성해주세요.

제목: {paper.title}
저자: {', '.join(paper.authors)}
초록: {paper.abstract}

요구사항:
1. 이 요약본은 나중에 팟캐스트 대본 작성에 활용될 자료입니다
2. 500-1000자 내외로 작성해주세요
3. 다음 내용을 포함해주세요:
   - 연구의 핵심 아이디어
   - 주요 기여점 및 혁신적인 부분
   - 중요한 실험 결과나 발견
   - 이 연구가 중요한 이유

작성 스타일:
- 사실 중심으로 명확하게 작성
- 마크다운 형식(**, ##) 사용하지 말 것
- AI/ML 분야 학생이나 연구자가 이해하기 쉽게
- 핵심만 간결하게 정리

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
    
    def generate_podcast_script(self, papers: list[Paper], date: str, language: str = "ko") -> str:
        """Generate complete podcast script with intro, content, and outro using Gemini.
        
        Args:
            papers: List of papers with summaries
            date: Date string (YYYY-MM-DD)
            language: Target language
            
        Returns:
            Complete podcast script
        """
        self.logger.info(f"Generating podcast script for {len(papers)} papers")
        
        try:
            # Prepare paper summaries for context
            papers_context = []
            for i, paper in enumerate(papers, 1):
                paper_info = f"""
논문 {i}:
- 제목: {paper.title}
- 저자: {', '.join(paper.authors[:3])}{'외 {}명'.format(len(paper.authors) - 3) if len(paper.authors) > 3 else ''}
- 요약: {paper.summary}
"""
                papers_context.append(paper_info)
            
            papers_text = "\n".join(papers_context)
            
            # Create prompt for podcast script
            prompt = f"""당신은 AI 논문을 소개하는 전문 팟캐스트 호스트입니다.
아래 제공된 논문 요약본들을 바탕으로, 청취자에게 전달할 완전한 팟캐스트 대본을 작성해주세요.

=== 기본 정보 ===
날짜: {date}
논문 수: {len(papers)}개

=== 논문 요약 자료 ===
{papers_text}

=== 팟캐스트 대본 작성 가이드 ===

**1단계: 전체 흐름 파악**
- 위 논문들의 공통 주제나 트렌드를 파악하세요
- 오늘의 에피소드를 관통하는 핵심 메시지를 정하세요

**2단계: 인트로 작성 (30-40초 분량)**
- 청취자를 환영하고 오늘 날짜 언급
- 오늘 다룰 논문들의 공통 주제나 특징을 흥미롭게 소개
- "오늘은 특히 [주제]에 관한 흥미로운 연구들이 많습니다" 같은 맥락 제공
- 청취자의 관심을 끄는 후킹 멘트

**3단계: 본론 작성 (각 논문당 2-3분 분량)**
각 논문마다 다음 구조로 작성:
- 자연스러운 도입: "첫 번째로 살펴볼 논문은..." 또는 "이번엔 조금 다른 접근을 한 연구인데요..." 등 
- 제목과 저자 소개: 자연스럽게 녹여서 언급
- 핵심 내용 설명: 요약본의 내용을 바탕으로 스토리텔링
  * 왜 이 연구가 중요한지
  * 어떤 문제를 해결하려 했는지
  * 핵심 아이디어와 방법
  * 주요 결과와 의미
- 논문 간 전환: 다음 논문과 관련이 있는 경우에는 연결고리 제시
  * "이 연구와 관련해서..." 
  * "비슷한 맥락에서..." 
  * "조금 다른 각도에서 접근한 다음 논문은..."

**4단계: 아웃트로 작성 (20-30초 분량)**
- 오늘 소개한 논문들의 공통점이나 전체적인 의미 요약
- AI 연구의 흐름이나 미래 전망 언급
- 청취자에게 감사 인사
- 다음 에피소드 예고 (일반적으로)

=== 작성 스타일 ===
- **톤**: 전문적이지만 친절하게, 대화하듯 자연스럽게
- **작성 스타일**: 작성 대상이 이해하기 쉽고 자세하게, 배경지식을 포함하여 설몀
- **대상**: AI/ML에 관심 있는 비전공자 학생
- **속도**: 음성으로 읽었을 때 띄어쓰기를 잘 지켜서 읽을 수 있도록 "," 등 문장 부호를 적극적으로 대본에 포함할 것
- **강조**: 중요한 부분은 반복하거나 "특히", "주목할 점은" 등으로 강조
- **금지**: 마크다운 형식(**, ##) 절대 사용 금지
- **자연스러움**: 로봇처럼 딱딱하게가 아니라 라디오 DJ처럼 편안하게

=== 출력 형식 ===
완성된 팟캐스트 대본만 출력하세요. 
"인트로:", "본론:" 같은 섹션 제목은 쓰지 말고, 
처음부터 끝까지 연결된 하나의 스크립트로 작성하세요.

팟캐스트 대본:"""

            # Generate script using Gemini
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
            
            # Get script text
            script = None
            if response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    if finish_reason == 1:  # Normal completion
                        script = response.text
                    else:
                        self.logger.warning(f"Non-normal finish reason {finish_reason} for podcast script")
                        script = self._create_fallback_script(papers, date)
                else:
                    script = response.text
            
            if not script or len(script) < 100:
                self.logger.warning("Generated script too short, using fallback")
                script = self._create_fallback_script(papers, date)
            
            self.logger.info(f"Successfully generated podcast script ({len(script)} chars)")
            return script
            
        except Exception as e:
            self.logger.error(f"Failed to generate podcast script: {e}")
            return self._create_fallback_script(papers, date)
    
    def _create_fallback_script(self, papers: list[Paper], date: str) -> str:
        """Create fallback podcast script when AI generation fails.
        
        Args:
            papers: List of papers
            date: Date string
            
        Returns:
            Fallback script
        """
        from datetime import datetime
        
        # Parse date
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_kr = date_obj.strftime("%Y년 %m월 %d일")
        
        # Create intro
        intro = f"안녕하세요. Daily AI Papers입니다. "
        intro += f"{date_kr} "
        intro += f"Hugging Face 트렌딩 논문 Top {len(papers)}를 소개합니다. "
        intro += "오늘도 흥미로운 AI 연구 결과들이 준비되어 있습니다. 시작하겠습니다.\n\n"
        
        # Create content
        content_parts = []
        for i, paper in enumerate(papers, 1):
            part = f"{i}번째 논문입니다. "
            part += f"제목은 {paper.title}입니다. "
            part += f"저자는 {', '.join(paper.authors[:3])}입니다. "
            if len(paper.authors) > 3:
                part += f"외 {len(paper.authors) - 3}명입니다. "
            part += f"\n\n{paper.summary}\n\n"
            content_parts.append(part)
        
        # Create outro
        outro = "오늘의 논문 소개를 마치겠습니다. "
        outro += "최신 AI 연구 동향을 계속 전해드리겠습니다. "
        outro += "감사합니다."
        
        return intro + "".join(content_parts) + outro

