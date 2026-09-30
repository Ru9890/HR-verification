from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLLMProvider(ABC):
    @abstractmethod
    async def extract_claims_and_entities(self, text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    async def match_claim_with_evidence(self, claim_text: str, claimed_items: List[str], evidence_summary: str) -> Dict[str, Any]:
        pass
