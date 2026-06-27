import os
from typing import List
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from graph.state import ResearchPlan, SubQuery


class PlannerAgent:
    """Breaks a research question into focused sub-queries."""
    
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "groq")
        model = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
        
        if provider == "groq":
            self.llm = ChatGroq(
                model=model,
                temperature=0.3,
                api_key=os.getenv("GROQ_API_KEY")
            )
        else:
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.3,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        
        self.parser = PydanticOutputParser(pydantic_object=ResearchPlan)
    
    def _build_prompt(self) -> ChatPromptTemplate:
        template = """You are a research planning agent. Your job is to break a research question into 3-5 focused sub-queries.

Given a research question, produce a structured plan with:
1. Sub-queries: Each should be specific, non-overlapping, and cover a different angle of the question
2. Output format: What structure the final report should take
3. Quality threshold: A score from 0.0 to 1.0 indicating how thorough the answer must be
4. Domain hints: What domains this question relates to (e.g., "technical", "business", "academic")

{format_instructions}

Research Question: {question}

Respond with ONLY the JSON matching the format above. No extra text."""

        return ChatPromptTemplate.from_template(template)
    
    def run(self, question: str) -> ResearchPlan:
        prompt = self._build_prompt()
        chain = prompt | self.llm | self.parser
        
        # Try up to 3 times if parsing fails
        for attempt in range(3):
            try:
                result = chain.invoke({
                    "question": question,
                    "format_instructions": self.parser.get_format_instructions()
                })
                # Ensure at least one sub-query
                if not result.sub_queries:
                    result.sub_queries = [SubQuery(query=question, intent="Direct search")]
                return result
            except Exception as e:
                if attempt == 2:
                    # Final fallback: return a simple plan with the original question
                    return ResearchPlan(
                        sub_queries=[SubQuery(query=question, intent="Direct search")],
                        output_format="report",
                        quality_threshold=0.75
                    )
                continue
        
        return ResearchPlan(
            sub_queries=[SubQuery(query=question, intent="Direct search")],
            output_format="report",
            quality_threshold=0.75
        )