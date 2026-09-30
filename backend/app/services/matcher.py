import re
from typing import List, Dict, Any, Optional, Tuple
from backend.app.schemas import (
    ClaimVerification,
    ClaimStatus,
    ClaimItemBreakdown,
    EvidenceSnippet,
    DiscoveredUrl,
    UrlStatus,
    UrlPlatform
)

class ClaimEvidenceMatcher:
    """
    Matches extracted claims against gathered public evidence from GitHub, Portfolio, LinkedIn, and Web sources.
    Strictly outputs:
    - Supported
    - Partially Supported
    - Unverified
    - Broken Link
    - Restricted
    """
    def match_claims(
        self,
        claims: List[Dict[str, Any]],
        discovered_urls: List[DiscoveredUrl]
    ) -> List[ClaimVerification]:
        verified_claims: List[ClaimVerification] = []
        
        # Build lookup maps for URLs
        url_map: Dict[str, DiscoveredUrl] = {u.normalized_url: u for u in discovered_urls}
        # Also map raw URLs
        for u in discovered_urls:
            url_map[u.raw_url] = u
            
        # Collect all accessible GitHub repos and Web pages for cross-reference
        github_repos = [u for u in discovered_urls if u.github_data is not None and u.status == UrlStatus.ACCESSIBLE]
        web_pages = [u for u in discovered_urls if u.web_data is not None and u.status == UrlStatus.ACCESSIBLE]

        for claim in claims:
            cid = claim.get("id", "")
            category = claim.get("category", "general")
            section = claim.get("section", "Resume")
            claim_text = claim.get("claim_text", "")
            claimed_items = claim.get("claimed_items", [])
            assoc_url_str = claim.get("associated_url")
            
            # Find the associated DiscoveredUrl object if any
            assoc_url_obj: Optional[DiscoveredUrl] = None
            if assoc_url_str:
                assoc_url_obj = url_map.get(assoc_url_str)
                if not assoc_url_obj:
                    for u in discovered_urls:
                        if assoc_url_str in u.normalized_url or u.normalized_url in assoc_url_str:
                            assoc_url_obj = u
                            break

            # 1. Handle Direct Repository Link Claims
            if category == "repository_link" and assoc_url_obj:
                res = self._evaluate_repo_link_claim(claim, assoc_url_obj)
                verified_claims.append(res)
                continue

            # 2. Handle Broken Associated URLs
            if assoc_url_obj and assoc_url_obj.status in (UrlStatus.BROKEN, UrlStatus.INVALID, UrlStatus.TIMEOUT):
                verified_claims.append(ClaimVerification(
                    id=cid,
                    category=category,
                    section=section,
                    claim_text=claim_text,
                    claimed_items=claimed_items,
                    status=ClaimStatus.BROKEN_LINK,
                    confidence=0.0,
                    associated_url=assoc_url_str,
                    items_breakdown=[ClaimItemBreakdown(item_name=item, status=ClaimStatus.BROKEN_LINK) for item in claimed_items],
                    evidence_snippets=[],
                    explanation=f"The associated URL ({assoc_url_obj.normalized_url}) is inaccessible or returned 404 / broken status."
                ))
                continue

            # 3. Handle Restricted Associated URLs (e.g. Private Repos or Auth-walled LinkedIn)
            if assoc_url_obj and assoc_url_obj.status == UrlStatus.RESTRICTED:
                verified_claims.append(ClaimVerification(
                    id=cid,
                    category=category,
                    section=section,
                    claim_text=claim_text,
                    claimed_items=claimed_items,
                    status=ClaimStatus.RESTRICTED,
                    confidence=0.0,
                    associated_url=assoc_url_str,
                    items_breakdown=[ClaimItemBreakdown(item_name=item, status=ClaimStatus.RESTRICTED) for item in claimed_items],
                    evidence_snippets=[],
                    explanation=f"The associated resource ({assoc_url_obj.normalized_url}) is restricted (private repository or requires sign-in)."
                ))
                continue

            # 4. Check Claimed Items against Target Scope (Associated Repo first, then All Repos/Web)
            target_repos = [assoc_url_obj] if (assoc_url_obj and assoc_url_obj.github_data) else github_repos
            target_web = [assoc_url_obj] if (assoc_url_obj and assoc_url_obj.web_data) else web_pages
            
            items_breakdown: List[ClaimItemBreakdown] = []
            all_evidence: List[EvidenceSnippet] = []
            
            # If there are no specific tech items extracted, match against full sentence keywords
            eval_items = claimed_items if claimed_items else [claim_text[:40]]
            
            supported_count = 0
            
            for item in eval_items:
                item_evidence = self._find_evidence_for_item(item, target_repos, target_web)
                if item_evidence:
                    supported_count += 1
                    best_ev = item_evidence[0]
                    items_breakdown.append(ClaimItemBreakdown(
                        item_name=item,
                        status=ClaimStatus.SUPPORTED,
                        evidence_source=best_ev.source_type,
                        evidence_snippet=best_ev.snippet
                    ))
                    all_evidence.extend(item_evidence)
                else:
                    items_breakdown.append(ClaimItemBreakdown(
                        item_name=item,
                        status=ClaimStatus.UNVERIFIED,
                        evidence_source=None,
                        evidence_snippet=None
                    ))

            # Determine Claim Status
            total_items = len(eval_items)
            if total_items == 0:
                claim_status = ClaimStatus.UNVERIFIED
                confidence = 0.0
                explanation = "No verifiable public entities or public repositories found for this claim."
            elif supported_count == total_items:
                claim_status = ClaimStatus.SUPPORTED
                confidence = round(sum(e.confidence for e in all_evidence) / max(1, len(all_evidence)), 2)
                sources_str = ", ".join(list(set(e.source_type for e in all_evidence))[:3])
                explanation = f"All claimed items verified in public evidence ({sources_str})."
            elif supported_count > 0:
                claim_status = ClaimStatus.PARTIALLY_SUPPORTED
                confidence = round((supported_count / total_items) * 0.8, 2)
                supp_names = [b.item_name for b in items_breakdown if b.status == ClaimStatus.SUPPORTED]
                unv_names = [b.item_name for b in items_breakdown if b.status == ClaimStatus.UNVERIFIED]
                explanation = f"Partially supported: Found public evidence for {', '.join(supp_names)}. No public evidence found for {', '.join(unv_names)}."
            else:
                claim_status = ClaimStatus.UNVERIFIED
                confidence = 0.0
                explanation = "No public supporting evidence was found in reachable URLs. (Not verified publicly; evidence may reside in private/internal systems)."

            verified_claims.append(ClaimVerification(
                id=cid,
                category=category,
                section=section,
                claim_text=claim_text,
                claimed_items=claimed_items,
                status=claim_status,
                confidence=confidence,
                associated_url=assoc_url_str,
                items_breakdown=items_breakdown,
                evidence_snippets=all_evidence[:10], # Top 10 evidence snippets
                explanation=explanation
            ))

        return verified_claims

    def _evaluate_repo_link_claim(self, claim: Dict[str, Any], url_obj: DiscoveredUrl) -> ClaimVerification:
        cid = claim.get("id", "")
        if url_obj.status == UrlStatus.ACCESSIBLE and url_obj.github_data:
            data = url_obj.github_data
            top_langs = ", ".join(list(data.language_percentages.keys())[:3]) or "Code"
            snippet = f"Repo: {data.full_name} | Stars: {data.stars} | Primary: {top_langs} | Commits: {len(data.recent_commits)}"
            return ClaimVerification(
                id=cid,
                category="repository_link",
                section="Links / Portfolio",
                claim_text=claim.get("claim_text", ""),
                claimed_items=[url_obj.normalized_url],
                status=ClaimStatus.SUPPORTED,
                confidence=1.0,
                associated_url=url_obj.normalized_url,
                items_breakdown=[ClaimItemBreakdown(
                    item_name=url_obj.normalized_url,
                    status=ClaimStatus.SUPPORTED,
                    evidence_source="GitHub REST API",
                    evidence_snippet=snippet
                )],
                evidence_snippets=[EvidenceSnippet(
                    source_type="GitHub Repository",
                    source_url=url_obj.normalized_url,
                    snippet=snippet,
                    matched_term=data.name,
                    confidence=1.0,
                    location_detail=f"Active GitHub repository with {data.stars} stars"
                )],
                explanation=f"Public GitHub repository verified: {data.full_name} with {len(data.dependencies)} dependencies and {len(data.recent_commits)} recent commits."
            )
        elif url_obj.status == UrlStatus.RESTRICTED:
            return ClaimVerification(
                id=cid,
                category="repository_link",
                section="Links / Portfolio",
                claim_text=claim.get("claim_text", ""),
                claimed_items=[url_obj.normalized_url],
                status=ClaimStatus.RESTRICTED,
                confidence=0.0,
                associated_url=url_obj.normalized_url,
                items_breakdown=[ClaimItemBreakdown(item_name=url_obj.normalized_url, status=ClaimStatus.RESTRICTED)],
                evidence_snippets=[],
                explanation="Repository is private or restricted."
            )
        else:
            return ClaimVerification(
                id=cid,
                category="repository_link",
                section="Links / Portfolio",
                claim_text=claim.get("claim_text", ""),
                claimed_items=[url_obj.normalized_url],
                status=ClaimStatus.BROKEN_LINK,
                confidence=0.0,
                associated_url=url_obj.normalized_url,
                items_breakdown=[ClaimItemBreakdown(item_name=url_obj.normalized_url, status=ClaimStatus.BROKEN_LINK)],
                evidence_snippets=[],
                explanation=f"Repository URL returned 404 or broken: {url_obj.error_message or 'Inaccessible'}"
            )

    def _find_evidence_for_item(
        self,
        item_name: str,
        repos: List[DiscoveredUrl],
        web_pages: List[DiscoveredUrl]
    ) -> List[EvidenceSnippet]:
        evidence: List[EvidenceSnippet] = []
        low_item = item_name.lower().strip()
        if not low_item:
            return evidence

        # 1. Search GitHub Repositories
        for r_url in repos:
            if not r_url.github_data:
                continue
            gdata = r_url.github_data
            
            # A. Check Dependencies Manifest (requirements.txt, package.json, etc.)
            for dep in gdata.dependencies:
                if low_item == dep.package_name or low_item in dep.package_name:
                    evidence.append(EvidenceSnippet(
                        source_type=f"GitHub Manifest ({dep.file})",
                        source_url=r_url.normalized_url,
                        snippet=f"Found dependency '{dep.package_name}' {dep.version_spec or ''} in {dep.file}",
                        matched_term=item_name,
                        confidence=1.0,
                        location_detail=f"Repo: {gdata.full_name} -> {dep.file}"
                    ))
                    
            # B. Check Languages breakdown
            for lang, pct in gdata.language_percentages.items():
                if low_item == lang.lower():
                    evidence.append(EvidenceSnippet(
                        source_type="GitHub Languages",
                        source_url=r_url.normalized_url,
                        snippet=f"{lang} constitutes {pct}% of repository codebase",
                        matched_term=item_name,
                        confidence=0.95,
                        location_detail=f"Repo: {gdata.full_name}"
                    ))
                    
            # C. Check README content
            if gdata.readme_content:
                # Look for matching line in README
                for line in gdata.readme_content.splitlines():
                    if re.search(rf'\b{re.escape(low_item)}\b', line.lower()):
                        clean_line = line.strip().lstrip("#-* ").strip()
                        if len(clean_line) > 10:
                            evidence.append(EvidenceSnippet(
                                source_type="GitHub README",
                                source_url=r_url.normalized_url,
                                snippet=f"README excerpt: \"{clean_line[:180]}\"",
                                matched_term=item_name,
                                confidence=0.9,
                                location_detail=f"Repo: {gdata.full_name} -> README.md"
                            ))
                            break # One good line from README is enough

            # D. Check File Tree
            for fpath in gdata.file_tree_summary:
                if low_item in fpath.lower():
                    evidence.append(EvidenceSnippet(
                        source_type="GitHub Source File Tree",
                        source_url=r_url.normalized_url,
                        snippet=f"Found matching source file: {fpath}",
                        matched_term=item_name,
                        confidence=0.85,
                        location_detail=f"Repo: {gdata.full_name}"
                    ))
                    break

        # 2. Search Web & Portfolio Pages
        for w_url in web_pages:
            if not w_url.web_data:
                continue
            wdata = w_url.web_data
            
            # Check discovered techs
            if any(low_item == t.lower() for t in wdata.discovered_techs):
                evidence.append(EvidenceSnippet(
                    source_type="Portfolio Technology Stack",
                    source_url=w_url.normalized_url,
                    snippet=f"Listed in technical skills on portfolio ({wdata.title})",
                    matched_term=item_name,
                    confidence=0.85,
                    location_detail=w_url.normalized_url
                ))
                
            # Check headings & text
            if wdata.raw_text_snippet and re.search(rf'\b{re.escape(low_item)}\b', wdata.raw_text_snippet.lower()):
                # Find matching sentence
                sentences = re.split(r'[\.\n]', wdata.raw_text_snippet)
                for s in sentences:
                    if low_item in s.lower() and len(s.strip()) > 15:
                        evidence.append(EvidenceSnippet(
                            source_type="Web Page Content",
                            source_url=w_url.normalized_url,
                            snippet=f"Found mention: \"{s.strip()[:180]}\"",
                            matched_term=item_name,
                            confidence=0.8,
                            location_detail=w_url.normalized_url
                        ))
                        break

        return evidence
