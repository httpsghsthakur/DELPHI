import pytest
from delphi.research.schemas import ResearchDossier, DossierSource, DossierClaim
from delphi.research.composer import GroundedReportComposer
from delphi.research.engine import LiveResearchEngine

def test_grounded_report_composer():
    composer = GroundedReportComposer()
    dossier = ResearchDossier(
        research_question="What are the global economic implications of the latest semiconductor trade restrictions?",
        search_queries=[
            "semiconductor trade restrictions latest developments",
            "semiconductor export controls official statement",
            "semiconductor supply chain economic impact"
        ],
        research_cutoff="2026-10-13T00:00:00Z",
        sources=[
            DossierSource(
                document_id="doc_1",
                url="https://csis.org/analysis/semiconductor-supply-chain",
                title="Mapping the Semiconductor Supply Chain",
                source_name="CSIS",
                source_domain="csis.org",
                published_at="2026-09-15T00:00:00Z",
                retrieved_at="2026-10-13T00:00:00Z",
                credibility_score=0.92,
                word_count=1450,
                summary_snippet="Analysis of global advanced chip manufacturing and trade corridors.",
                status="extracted"
            ),
            DossierSource(
                document_id="doc_2",
                url="https://investopedia.com/semiconductors-supply-chain",
                title="Semiconductor Supply Chain and Global Trade",
                source_name="Investopedia",
                source_domain="investopedia.com",
                published_at="2026-09-20T00:00:00Z",
                retrieved_at="2026-10-13T00:00:00Z",
                credibility_score=0.85,
                word_count=980,
                summary_snippet="Global trade impacts of advanced lithography restrictions.",
                status="extracted"
            )
        ],
        extracted_claims=[
            DossierClaim(
                claim_id="claim_1",
                claim_text="The United States announced expanded restrictions on advanced computing chip equipment exports.",
                document_id="doc_1",
                source_url="https://csis.org/analysis/semiconductor-supply-chain",
                source_domain="csis.org",
                source_name="CSIS",
                published_at="2026-09-15T00:00:00Z",
                claim_type="official_statement",
                direction="supporting",
                credibility_score=0.92
            ),
            DossierClaim(
                claim_id="claim_2",
                claim_text="Industry representatives warned that licensing delays could reduce capital expenditures by 15 percent.",
                document_id="doc_2",
                source_url="https://investopedia.com/semiconductors-supply-chain",
                source_domain="investopedia.com",
                source_name="Investopedia",
                published_at="2026-09-20T00:00:00Z",
                claim_type="expert_analysis",
                direction="supporting",
                credibility_score=0.85
            ),
            DossierClaim(
                claim_id="claim_3",
                claim_text="Trade officials refuted claims that consumer electronics supply lines would be immediately disrupted.",
                document_id="doc_1",
                source_url="https://csis.org/analysis/semiconductor-supply-chain",
                source_domain="csis.org",
                source_name="CSIS",
                published_at="2026-09-15T00:00:00Z",
                claim_type="competing_account",
                direction="conflicting",
                credibility_score=0.92
            )
        ],
        quantitative_findings=["$50 billion in domestic manufacturing subsidies allocated across three fiscal years."],
        unresolved_questions=["Unclear whether third-party distributor exemptions will be extended."]
    )
    
    report = composer.compose_report(
        dossier=dossier,
        event_context={"event_type_code": "042_TRADE_POLICY_RESTRICTION"},
        credibility_assessment={"credibility_score": 0.88}
    )
    
    assert report.title.startswith("DELPHI Strategic Intelligence Briefing")
    assert len(report.executive_summary) > 100
    assert len(report.background_and_context) > 100
    assert len(report.current_developments) > 100
    assert len(report.evidence_and_sources) > 100
    assert len(report.historical_comparisons) > 100
    assert len(report.causal_analysis) > 100
    assert len(report.future_scenarios) > 100
    assert len(report.risks_and_uncertainties) > 100
    assert len(report.conclusion) > 100
    assert len(report.sources_and_reading) == 2
    # Check citations exist
    assert "[1]" in report.executive_summary or "[1]" in report.current_developments

def test_live_research_engine_workflow():
    engine = LiveResearchEngine()
    event = {
        "event_id": "test_ev_1",
        "event_type_code": "042_MAKE_A_VISIT",
        "source_text": "The Prime Minister of India visited the United States to discuss bilateral trade agreements."
    }
    report = engine.run_research(event, cutoff="2026-10-13T00:00:00Z")
    assert report.run_id is not None
    assert len(report.queries_executed) >= 1
    assert report.dossier is not None
    assert report.intelligence_report is not None
