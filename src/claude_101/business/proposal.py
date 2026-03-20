"""Proposal scaffolding tool — structured business proposal generator."""

from __future__ import annotations

import re

from .._utils import count_pattern_matches


# ---------------------------------------------------------------------------
# Section templates by proposal type
# ---------------------------------------------------------------------------

_SECTION_TEMPLATES: dict[str, list[dict]] = {
    "business": [
        {
            "name": "Executive Summary",
            "description": "High-level overview of the proposal, problem, and proposed solution",
            "word_pct": 10,
            "required": True,
            "template": (
                "## Executive Summary\n\n"
                "[Company Name] proposes [solution] to address [problem]. "
                "This initiative will [key benefit 1] and [key benefit 2], "
                "delivering an estimated [ROI/value] within [timeframe].\n\n"
                "**Investment Required:** [amount]\n"
                "**Expected Return:** [return]\n"
                "**Timeline:** [duration]"
            ),
            "aida": "Attention",
        },
        {
            "name": "Problem Statement",
            "description": "Clear articulation of the business problem or opportunity",
            "word_pct": 12,
            "required": True,
            "template": (
                "## Problem Statement\n\n"
                "### Current Situation\n[Describe the status quo and its limitations]\n\n"
                "### Impact\n[Quantify the cost of inaction: revenue loss, inefficiency, risk]\n\n"
                "### Root Causes\n- [Cause 1]\n- [Cause 2]\n- [Cause 3]"
            ),
            "aida": "Interest",
        },
        {
            "name": "Proposed Solution",
            "description": "Detailed description of what is being proposed",
            "word_pct": 25,
            "required": True,
            "template": (
                "## Proposed Solution\n\n"
                "### Overview\n[High-level description of the solution]\n\n"
                "### Key Components\n1. [Component 1]: [description]\n"
                "2. [Component 2]: [description]\n"
                "3. [Component 3]: [description]\n\n"
                "### How It Works\n[Step-by-step explanation]\n\n"
                "### Differentiators\n- [What makes this approach unique]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Benefits and ROI",
            "description": "Quantified benefits and return on investment analysis",
            "word_pct": 15,
            "required": True,
            "template": (
                "## Benefits and ROI\n\n"
                "### Quantitative Benefits\n"
                "| Benefit | Year 1 | Year 2 | Year 3 |\n"
                "|---------|--------|--------|--------|\n"
                "| [Benefit 1] | [value] | [value] | [value] |\n"
                "| [Benefit 2] | [value] | [value] | [value] |\n\n"
                "### Qualitative Benefits\n- [Benefit A]\n- [Benefit B]\n\n"
                "### ROI Calculation\n"
                "- Total Investment: [amount]\n"
                "- Total Return (3-year): [amount]\n"
                "- ROI: [percentage]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Implementation Plan",
            "description": "Timeline, phases, and resource requirements",
            "word_pct": 18,
            "required": True,
            "template": (
                "## Implementation Plan\n\n"
                "### Phase 1: [Name] (Weeks 1-N)\n- [Deliverable]\n- [Deliverable]\n\n"
                "### Phase 2: [Name] (Weeks N-M)\n- [Deliverable]\n- [Deliverable]\n\n"
                "### Resource Requirements\n"
                "- Team: [roles and headcount]\n"
                "- Budget: [breakdown]\n"
                "- Tools: [required tools/licenses]"
            ),
            "aida": "Action",
        },
        {
            "name": "Risk Analysis",
            "description": "Potential risks and mitigation strategies",
            "word_pct": 10,
            "required": True,
            "template": (
                "## Risk Analysis\n\n"
                "| Risk | Likelihood | Impact | Mitigation |\n"
                "|------|-----------|--------|------------|\n"
                "| [Risk 1] | [H/M/L] | [H/M/L] | [Strategy] |\n"
                "| [Risk 2] | [H/M/L] | [H/M/L] | [Strategy] |"
            ),
            "aida": "Action",
        },
        {
            "name": "Next Steps",
            "description": "Clear call to action and immediate next steps",
            "word_pct": 5,
            "required": True,
            "template": (
                "## Next Steps\n\n"
                "1. **[Action]** — [Owner] by [Date]\n"
                "2. **[Action]** — [Owner] by [Date]\n"
                "3. **[Action]** — [Owner] by [Date]\n\n"
                "**Decision Requested By:** [Date]"
            ),
            "aida": "Action",
        },
        {
            "name": "Appendix",
            "description": "Supporting data, references, and detailed calculations",
            "word_pct": 5,
            "required": False,
            "template": (
                "## Appendix\n\n"
                "### A. Detailed Cost Breakdown\n[Table]\n\n"
                "### B. Market Research Data\n[Data]\n\n"
                "### C. Technical Specifications\n[Specs]"
            ),
            "aida": "Desire",
        },
    ],
    "sales": [
        {
            "name": "Cover Letter",
            "description": "Personalized introduction establishing credibility",
            "word_pct": 8,
            "required": True,
            "template": (
                "## Cover Letter\n\n"
                "Dear [Client Name],\n\n"
                "Thank you for the opportunity to present this proposal. "
                "We understand that [client challenge] and believe "
                "[company] is uniquely positioned to help you [achieve goal]."
            ),
            "aida": "Attention",
        },
        {
            "name": "Understanding Your Needs",
            "description": "Demonstrate understanding of the client's situation",
            "word_pct": 12,
            "required": True,
            "template": (
                "## Understanding Your Needs\n\n"
                "Based on our conversations, we understand that:\n"
                "- [Need 1]: [detail]\n"
                "- [Need 2]: [detail]\n"
                "- [Need 3]: [detail]\n\n"
                "**Key Success Criteria:**\n[What the client defines as success]"
            ),
            "aida": "Interest",
        },
        {
            "name": "Our Solution",
            "description": "Tailored solution mapped to client needs",
            "word_pct": 25,
            "required": True,
            "template": (
                "## Our Solution\n\n"
                "### Approach\n[How we will solve each identified need]\n\n"
                "### Deliverables\n"
                "| Deliverable | Description | Timeline |\n"
                "|------------|-------------|----------|\n"
                "| [D1] | [desc] | [when] |\n\n"
                "### Why Us\n- [Differentiator 1]\n- [Differentiator 2]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Case Studies",
            "description": "Relevant success stories demonstrating capability",
            "word_pct": 12,
            "required": True,
            "template": (
                "## Case Studies\n\n"
                "### [Client A]\n"
                "**Challenge:** [problem]\n"
                "**Solution:** [what we did]\n"
                "**Result:** [measurable outcome]\n\n"
                "### [Client B]\n"
                "**Challenge:** [problem]\n"
                "**Solution:** [what we did]\n"
                "**Result:** [measurable outcome]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Pricing",
            "description": "Clear pricing structure with options",
            "word_pct": 10,
            "required": True,
            "template": (
                "## Pricing\n\n"
                "### Option A: [Name]\n- Scope: [what's included]\n- Investment: [amount]\n\n"
                "### Option B: [Name] (Recommended)\n- Scope: [what's included]\n- Investment: [amount]\n\n"
                "### Option C: [Name]\n- Scope: [what's included]\n- Investment: [amount]\n\n"
                "*All prices valid until [date].*"
            ),
            "aida": "Action",
        },
        {
            "name": "Timeline",
            "description": "Project timeline with key milestones",
            "word_pct": 8,
            "required": True,
            "template": (
                "## Timeline\n\n"
                "| Phase | Duration | Key Milestones |\n"
                "|-------|----------|---------------|\n"
                "| Kickoff | Week 1 | [milestones] |\n"
                "| Delivery | Weeks 2-N | [milestones] |\n"
                "| Launch | Week N | [milestones] |"
            ),
            "aida": "Action",
        },
        {
            "name": "Terms and Conditions",
            "description": "Payment terms, warranties, and legal considerations",
            "word_pct": 5,
            "required": True,
            "template": (
                "## Terms and Conditions\n\n"
                "- **Payment Terms:** [net 30, milestone-based, etc.]\n"
                "- **Warranty:** [guarantee period and scope]\n"
                "- **Confidentiality:** [NDA reference]\n"
                "- **Cancellation:** [policy]"
            ),
            "aida": "Action",
        },
        {
            "name": "Team",
            "description": "Key team members and their qualifications",
            "word_pct": 8,
            "required": False,
            "template": (
                "## Our Team\n\n"
                "### [Name], [Title]\n[Brief bio and relevant experience]\n\n"
                "### [Name], [Title]\n[Brief bio and relevant experience]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Next Steps",
            "description": "Clear call to action",
            "word_pct": 5,
            "required": True,
            "template": (
                "## Next Steps\n\n"
                "1. Review this proposal and share feedback by [date]\n"
                "2. Schedule a follow-up call to discuss questions\n"
                "3. Sign the agreement to begin [start date]\n\n"
                "**Contact:** [name] | [email] | [phone]"
            ),
            "aida": "Action",
        },
    ],
    "grant": [
        {
            "name": "Project Summary",
            "description": "Concise abstract of the project and funding request",
            "word_pct": 8,
            "required": True,
            "template": (
                "## Project Summary\n\n"
                "**Project Title:** [title]\n"
                "**Principal Investigator:** [name]\n"
                "**Organization:** [org]\n"
                "**Funding Requested:** [amount]\n"
                "**Duration:** [months/years]\n\n"
                "[2-3 sentence summary of goals and expected outcomes]"
            ),
            "aida": "Attention",
        },
        {
            "name": "Statement of Need",
            "description": "Evidence-based case for why this project matters",
            "word_pct": 15,
            "required": True,
            "template": (
                "## Statement of Need\n\n"
                "### The Problem\n[Describe the problem with supporting data and citations]\n\n"
                "### Gap Analysis\n[What existing solutions miss]\n\n"
                "### Significance\n[Why addressing this now is critical]"
            ),
            "aida": "Interest",
        },
        {
            "name": "Project Description",
            "description": "Detailed methodology and activities",
            "word_pct": 30,
            "required": True,
            "template": (
                "## Project Description\n\n"
                "### Goals and Objectives\n"
                "1. [Goal 1]: [measurable objective]\n"
                "2. [Goal 2]: [measurable objective]\n\n"
                "### Methodology\n[Detailed approach and activities]\n\n"
                "### Innovation\n[What is novel about this approach]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Evaluation Plan",
            "description": "How success will be measured",
            "word_pct": 10,
            "required": True,
            "template": (
                "## Evaluation Plan\n\n"
                "### Metrics\n"
                "| Outcome | Indicator | Target | Method |\n"
                "|---------|-----------|--------|--------|\n"
                "| [O1] | [indicator] | [target] | [method] |\n\n"
                "### Reporting\n[Frequency and format of progress reports]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Budget",
            "description": "Detailed budget with justification",
            "word_pct": 15,
            "required": True,
            "template": (
                "## Budget\n\n"
                "| Category | Year 1 | Year 2 | Total |\n"
                "|----------|--------|--------|-------|\n"
                "| Personnel | [amt] | [amt] | [amt] |\n"
                "| Equipment | [amt] | [amt] | [amt] |\n"
                "| Travel | [amt] | [amt] | [amt] |\n"
                "| Other | [amt] | [amt] | [amt] |\n"
                "| **Total** | [amt] | [amt] | [amt] |\n\n"
                "### Budget Justification\n[Explain each line item]"
            ),
            "aida": "Action",
        },
        {
            "name": "Organizational Capacity",
            "description": "Demonstrate ability to execute",
            "word_pct": 10,
            "required": True,
            "template": (
                "## Organizational Capacity\n\n"
                "### About [Organization]\n[Mission, history, relevant track record]\n\n"
                "### Key Personnel\n"
                "- **[Name]**, [Role]: [qualifications]\n"
                "- **[Name]**, [Role]: [qualifications]\n\n"
                "### Past Performance\n[Similar projects successfully completed]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Sustainability",
            "description": "Plan for continuing impact after grant period",
            "word_pct": 8,
            "required": True,
            "template": (
                "## Sustainability Plan\n\n"
                "### Post-Grant Funding\n[How the project will be sustained]\n\n"
                "### Scaling Strategy\n[How outcomes will be expanded]\n\n"
                "### Knowledge Sharing\n[How findings will be disseminated]"
            ),
            "aida": "Action",
        },
        {
            "name": "References",
            "description": "Citations and supporting documentation",
            "word_pct": 4,
            "required": False,
            "template": (
                "## References\n\n"
                "1. [Author]. [Title]. [Journal/Source], [Year].\n"
                "2. [Author]. [Title]. [Journal/Source], [Year]."
            ),
            "aida": "Desire",
        },
    ],
    "partnership": [
        {
            "name": "Introduction",
            "description": "Who we are and why we are reaching out",
            "word_pct": 10,
            "required": True,
            "template": (
                "## Introduction\n\n"
                "[Company A] is excited to propose a strategic partnership with "
                "[Company B]. Our complementary strengths in [area A] and [area B] "
                "create a unique opportunity to [shared goal]."
            ),
            "aida": "Attention",
        },
        {
            "name": "Strategic Alignment",
            "description": "How both organizations benefit from the partnership",
            "word_pct": 15,
            "required": True,
            "template": (
                "## Strategic Alignment\n\n"
                "### Shared Vision\n[Common goals and market opportunity]\n\n"
                "### Complementary Strengths\n"
                "| [Company A] Brings | [Company B] Brings |\n"
                "|-------------------|-------------------|\n"
                "| [Strength 1] | [Strength 1] |\n"
                "| [Strength 2] | [Strength 2] |"
            ),
            "aida": "Interest",
        },
        {
            "name": "Partnership Model",
            "description": "Structure, roles, and governance",
            "word_pct": 25,
            "required": True,
            "template": (
                "## Partnership Model\n\n"
                "### Structure\n[Type: co-marketing, technology, revenue share, etc.]\n\n"
                "### Roles and Responsibilities\n"
                "- **[Company A]:** [responsibilities]\n"
                "- **[Company B]:** [responsibilities]\n\n"
                "### Governance\n"
                "- Joint steering committee (quarterly)\n"
                "- Operational sync (bi-weekly)\n"
                "- Escalation path: [process]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Mutual Benefits",
            "description": "Specific benefits for each partner",
            "word_pct": 18,
            "required": True,
            "template": (
                "## Mutual Benefits\n\n"
                "### For [Company A]\n- [Benefit 1]: [quantified impact]\n- [Benefit 2]: [quantified impact]\n\n"
                "### For [Company B]\n- [Benefit 1]: [quantified impact]\n- [Benefit 2]: [quantified impact]\n\n"
                "### Combined Market Impact\n[Joint value proposition and market reach]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Implementation Roadmap",
            "description": "Phased plan for launching the partnership",
            "word_pct": 12,
            "required": True,
            "template": (
                "## Implementation Roadmap\n\n"
                "### Phase 1: Foundation (Month 1-2)\n- Sign partnership agreement\n- Establish governance structure\n\n"
                "### Phase 2: Pilot (Month 3-4)\n- Launch pilot program\n- Measure initial results\n\n"
                "### Phase 3: Scale (Month 5+)\n- Expand based on pilot learnings\n- Formalize long-term agreement"
            ),
            "aida": "Action",
        },
        {
            "name": "Investment and Terms",
            "description": "Resource commitments and key terms",
            "word_pct": 10,
            "required": True,
            "template": (
                "## Investment and Terms\n\n"
                "### Resource Commitment\n"
                "| Resource | [Company A] | [Company B] |\n"
                "|----------|------------|------------|\n"
                "| People | [N FTEs] | [N FTEs] |\n"
                "| Budget | [amount] | [amount] |\n\n"
                "### Key Terms\n- Duration: [initial term]\n"
                "- Exclusivity: [scope]\n"
                "- IP Ownership: [policy]\n"
                "- Exit Clause: [conditions]"
            ),
            "aida": "Action",
        },
        {
            "name": "Next Steps",
            "description": "Immediate actions to move forward",
            "word_pct": 5,
            "required": True,
            "template": (
                "## Next Steps\n\n"
                "1. Review and provide feedback on this proposal by [date]\n"
                "2. Schedule leadership meeting to discuss terms\n"
                "3. Draft and review partnership agreement\n"
                "4. Target partnership launch: [date]"
            ),
            "aida": "Action",
        },
    ],
    "internal": [
        {
            "name": "Summary",
            "description": "One-paragraph summary of the request",
            "word_pct": 8,
            "required": True,
            "template": (
                "## Summary\n\n"
                "**Request:** [What you need approved]\n"
                "**Impact:** [Expected outcome]\n"
                "**Investment:** [Resources/budget needed]\n"
                "**Timeline:** [When you need a decision]"
            ),
            "aida": "Attention",
        },
        {
            "name": "Background",
            "description": "Context and rationale",
            "word_pct": 15,
            "required": True,
            "template": (
                "## Background\n\n"
                "### Current State\n[Describe the current situation]\n\n"
                "### Why Now\n[What has changed or what opportunity exists]\n\n"
                "### Alignment\n[How this connects to company OKRs/strategy]"
            ),
            "aida": "Interest",
        },
        {
            "name": "Proposal",
            "description": "What you want to do",
            "word_pct": 25,
            "required": True,
            "template": (
                "## Proposal\n\n"
                "### What\n[Clear description of the initiative]\n\n"
                "### How\n[Approach and methodology]\n\n"
                "### Who\n[Team and resource requirements]\n\n"
                "### When\n[Timeline with milestones]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Options Considered",
            "description": "Alternatives evaluated and why this is the best choice",
            "word_pct": 15,
            "required": True,
            "template": (
                "## Options Considered\n\n"
                "| Option | Pros | Cons | Cost |\n"
                "|--------|------|------|------|\n"
                "| **Option A (Recommended)** | [pros] | [cons] | [cost] |\n"
                "| Option B | [pros] | [cons] | [cost] |\n"
                "| Do Nothing | [pros] | [cons] | [cost] |"
            ),
            "aida": "Desire",
        },
        {
            "name": "Impact and Metrics",
            "description": "Expected outcomes and how to measure success",
            "word_pct": 12,
            "required": True,
            "template": (
                "## Impact and Metrics\n\n"
                "### Expected Outcomes\n- [Outcome 1]: [measurable target]\n- [Outcome 2]: [measurable target]\n\n"
                "### Success Metrics\n"
                "| Metric | Baseline | Target | Timeline |\n"
                "|--------|----------|--------|----------|\n"
                "| [M1] | [current] | [target] | [when] |"
            ),
            "aida": "Desire",
        },
        {
            "name": "Risks",
            "description": "What could go wrong and mitigation plans",
            "word_pct": 10,
            "required": True,
            "template": (
                "## Risks\n\n"
                "| Risk | Probability | Impact | Mitigation |\n"
                "|------|------------|--------|------------|\n"
                "| [Risk 1] | [H/M/L] | [H/M/L] | [Plan] |\n"
                "| [Risk 2] | [H/M/L] | [H/M/L] | [Plan] |"
            ),
            "aida": "Action",
        },
        {
            "name": "Ask",
            "description": "Clear statement of what you need from the decision maker",
            "word_pct": 5,
            "required": True,
            "template": (
                "## The Ask\n\n"
                "**Approval needed for:**\n"
                "- [Specific approval 1]\n"
                "- [Specific approval 2]\n\n"
                "**Decision needed by:** [date]\n"
                "**Escalation if delayed:** [consequence of delay]"
            ),
            "aida": "Action",
        },
    ],
    "technical": [
        {
            "name": "Overview",
            "description": "Technical summary and scope",
            "word_pct": 8,
            "required": True,
            "template": (
                "## Technical Overview\n\n"
                "**Objective:** [What this proposal achieves technically]\n"
                "**Scope:** [Systems, services, or components affected]\n"
                "**Complexity:** [Low/Medium/High]\n"
                "**Estimated Effort:** [person-hours or sprints]"
            ),
            "aida": "Attention",
        },
        {
            "name": "Problem Analysis",
            "description": "Technical deep-dive into the problem",
            "word_pct": 15,
            "required": True,
            "template": (
                "## Problem Analysis\n\n"
                "### Current Architecture\n[Diagram or description of current state]\n\n"
                "### Pain Points\n1. [Technical issue 1]: [evidence/metrics]\n"
                "2. [Technical issue 2]: [evidence/metrics]\n\n"
                "### Root Cause\n[Analysis of why these issues exist]"
            ),
            "aida": "Interest",
        },
        {
            "name": "Proposed Design",
            "description": "Detailed technical design",
            "word_pct": 30,
            "required": True,
            "template": (
                "## Proposed Design\n\n"
                "### Architecture\n[Diagram and description]\n\n"
                "### Components\n"
                "| Component | Responsibility | Technology |\n"
                "|-----------|---------------|------------|\n"
                "| [C1] | [what it does] | [tech] |\n\n"
                "### Data Flow\n[How data moves through the system]\n\n"
                "### API Design\n[Key endpoints or interfaces]"
            ),
            "aida": "Desire",
        },
        {
            "name": "Alternatives Considered",
            "description": "Other approaches evaluated",
            "word_pct": 12,
            "required": True,
            "template": (
                "## Alternatives Considered\n\n"
                "### Option A: [Name]\n"
                "- **Approach:** [description]\n- **Pros:** [list]\n- **Cons:** [list]\n- **Why not:** [reason]\n\n"
                "### Option B: [Name]\n"
                "- **Approach:** [description]\n- **Pros:** [list]\n- **Cons:** [list]\n- **Why not:** [reason]"
            ),
            "aida": "Interest",
        },
        {
            "name": "Implementation Plan",
            "description": "Phased rollout with milestones",
            "word_pct": 15,
            "required": True,
            "template": (
                "## Implementation Plan\n\n"
                "### Phase 1: [Name]\n"
                "- Duration: [weeks]\n- Tasks: [list]\n- Milestone: [deliverable]\n\n"
                "### Phase 2: [Name]\n"
                "- Duration: [weeks]\n- Tasks: [list]\n- Milestone: [deliverable]\n\n"
                "### Migration Strategy\n[How to move from current to new state]\n\n"
                "### Rollback Plan\n[How to revert if issues arise]"
            ),
            "aida": "Action",
        },
        {
            "name": "Testing Strategy",
            "description": "How the solution will be validated",
            "word_pct": 8,
            "required": True,
            "template": (
                "## Testing Strategy\n\n"
                "- **Unit Tests:** [coverage targets]\n"
                "- **Integration Tests:** [key scenarios]\n"
                "- **Load Tests:** [performance targets]\n"
                "- **Canary Deployment:** [rollout percentage and duration]"
            ),
            "aida": "Action",
        },
        {
            "name": "Operational Considerations",
            "description": "Monitoring, alerting, and maintenance",
            "word_pct": 8,
            "required": True,
            "template": (
                "## Operational Considerations\n\n"
                "### Monitoring\n- [Key metrics to track]\n- [Alerting thresholds]\n\n"
                "### On-Call Impact\n[Changes to runbooks or on-call procedures]\n\n"
                "### Maintenance\n[Ongoing maintenance requirements]"
            ),
            "aida": "Action",
        },
        {
            "name": "Open Questions",
            "description": "Unresolved items needing discussion",
            "word_pct": 4,
            "required": False,
            "template": (
                "## Open Questions\n\n"
                "1. [Question needing team input]\n"
                "2. [Decision that affects the design]\n"
                "3. [Dependency that needs confirmation]"
            ),
            "aida": "Interest",
        },
    ],
}

# ---------------------------------------------------------------------------
# Objection templates by proposal type
# ---------------------------------------------------------------------------

_OBJECTION_TEMPLATES: dict[str, list[dict]] = {
    "business": [
        {
            "objection": "The cost is too high",
            "response_framework": "Reframe as investment: compare cost of inaction vs. cost of action. Show ROI timeline and break-even point.",
        },
        {
            "objection": "We do not have the resources",
            "response_framework": "Present a phased approach that starts small. Show how existing resources can be reallocated, or propose a pilot with minimal commitment.",
        },
        {
            "objection": "The timing is not right",
            "response_framework": "Quantify the cost of delay per month. Show competitive pressure or market window that makes now the optimal time.",
        },
        {
            "objection": "This has been tried before and failed",
            "response_framework": "Acknowledge the past attempt, then highlight what is different now: new technology, team, market conditions, or lessons learned.",
        },
    ],
    "sales": [
        {
            "objection": "Your price is higher than competitors",
            "response_framework": "Shift from price to total cost of ownership. Highlight unique value, support quality, and hidden costs of cheaper alternatives.",
        },
        {
            "objection": "We need to think about it",
            "response_framework": "Agree that it is an important decision. Offer a specific follow-up date and ask what information would help them decide.",
        },
        {
            "objection": "We are happy with our current vendor",
            "response_framework": "Respect the relationship. Ask what they would improve if they could, then show how your solution addresses those gaps.",
        },
        {
            "objection": "Can you do a pilot first?",
            "response_framework": "Embrace the pilot: define success criteria, timeline, and commitment from both sides. Make the pilot compelling enough to convert.",
        },
    ],
    "grant": [
        {
            "objection": "The methodology is not rigorous enough",
            "response_framework": "Strengthen with peer-reviewed references, established frameworks, and a detailed evaluation plan with measurable indicators.",
        },
        {
            "objection": "The budget is not justified",
            "response_framework": "Provide line-item justification with market-rate references. Show that each expense directly supports a project objective.",
        },
        {
            "objection": "The team lacks relevant experience",
            "response_framework": "Highlight transferable skills, advisory board strength, and plans for skill-building. Reference successful adjacent projects.",
        },
    ],
    "partnership": [
        {
            "objection": "We do not see enough value for our side",
            "response_framework": "Quantify the specific benefits: market access, technology, revenue. Offer to adjust the partnership model to increase their share.",
        },
        {
            "objection": "The exclusivity terms are too restrictive",
            "response_framework": "Propose tiered exclusivity: full exclusivity in a narrow segment, non-exclusive in adjacent markets. Time-bound the terms.",
        },
        {
            "objection": "Our cultures may not be compatible",
            "response_framework": "Propose a cultural compatibility assessment in the pilot phase. Define shared values and working agreements upfront.",
        },
    ],
    "internal": [
        {
            "objection": "This is not a priority right now",
            "response_framework": "Map the proposal to current OKRs. Show how delaying increases cost or risk. Propose a minimal viable version that fits current priorities.",
        },
        {
            "objection": "The ROI is uncertain",
            "response_framework": "Propose a time-boxed pilot with clear go/no-go criteria. Define the minimum success threshold for continuing.",
        },
        {
            "objection": "Other teams should own this",
            "response_framework": "Clarify ownership boundaries. Propose a cross-functional working group or show why your team is best positioned to lead.",
        },
    ],
    "technical": [
        {
            "objection": "This adds too much complexity",
            "response_framework": "Show the complexity comparison: current state vs. proposed. Highlight how the new design reduces accidental complexity even if it adds essential complexity.",
        },
        {
            "objection": "The migration risk is too high",
            "response_framework": "Present the detailed rollback plan. Show how feature flags, canary deployments, and incremental rollout minimize risk.",
        },
        {
            "objection": "Why not use an existing solution?",
            "response_framework": "Present the build-vs-buy analysis. Show the specific gaps in existing solutions and the long-term cost of working around them.",
        },
    ],
}

# ---------------------------------------------------------------------------
# Audience configuration
# ---------------------------------------------------------------------------

_AUDIENCE_PROFILES: dict[str, dict] = {
    "executive": {
        "tone": "Concise and results-oriented. Lead with outcomes and ROI. Use data to support claims. Minimize technical jargon.",
        "word_multiplier": 0.7,
    },
    "technical": {
        "tone": "Detailed and precise. Include specifications, architecture diagrams, and code examples where relevant. Assume technical literacy.",
        "word_multiplier": 1.3,
    },
    "general": {
        "tone": "Clear and accessible. Balance detail with readability. Define technical terms when first used. Use analogies to explain complex concepts.",
        "word_multiplier": 1.0,
    },
}


def _score_argument_strength(text: str) -> dict:
    """Score argument strength by comparing claims vs evidence."""
    if not text.strip():
        return {"claims": 0, "evidence": 0, "ratio": 0.0, "strength": "none"}

    # Claims: declarative assertions
    claim_markers = [
        "will",
        "should",
        "must",
        "need to",
        "is essential",
        "is critical",
        "is important",
        "clearly",
        "obviously",
        "without doubt",
        "certainly",
        "undeniably",
    ]
    # Evidence: data references, numbers, citations
    evidence_markers = [
        "%",
        "$",
        "million",
        "billion",
        "study",
        "research",
        "according to",
        "data shows",
        "survey",
        "report",
        "statistics",
        "analysis",
        "evidence",
        "proven",
    ]

    claims = count_pattern_matches(text, claim_markers)
    evidence = count_pattern_matches(text, evidence_markers)

    # Also count raw numbers as evidence
    number_count = len(re.findall(r"\b\d+(?:\.\d+)?(?:%|x|X)?\b", text))
    evidence += number_count

    ratio = (
        round(evidence / claims, 2) if claims > 0 else (1.0 if evidence > 0 else 0.0)
    )

    if ratio >= 1.0:
        strength = "strong"
    elif ratio >= 0.5:
        strength = "moderate"
    elif ratio > 0:
        strength = "weak"
    else:
        strength = "unsupported"

    return {
        "claims": claims,
        "evidence": evidence,
        "ratio": ratio,
        "strength": strength,
    }


def _compute_roi(investment: float, annual_return: float, years: int = 3) -> dict:
    """Compute ROI metrics: ROI%, payback period, NPV at 10% discount rate."""
    if investment <= 0:
        return {"error": "Investment must be positive"}

    total_return = annual_return * years
    roi_pct = round((total_return - investment) / investment * 100, 1)

    # Payback period
    if annual_return > 0:
        payback = round(investment / annual_return, 1)
    else:
        payback = float("inf")

    # NPV at 10% discount rate
    discount_rate = 0.10
    npv = -investment
    for year in range(1, years + 1):
        npv += annual_return / ((1 + discount_rate) ** year)
    npv = round(npv, 2)

    return {
        "investment": investment,
        "annual_return": annual_return,
        "years": years,
        "total_return": round(total_return, 2),
        "roi_percent": roi_pct,
        "payback_years": payback,
        "npv_at_10pct": npv,
        "recommendation": "positive" if npv > 0 else "negative",
    }


def _score_aida_coverage(sections: list[dict], aida_mapping: dict[str, str]) -> dict:
    """Score word allocation across AIDA phases vs ideal distribution."""
    phase_words: dict[str, int] = {
        "Attention": 0,
        "Interest": 0,
        "Desire": 0,
        "Action": 0,
    }
    for sec in sections:
        phase = aida_mapping.get(sec["name"], "")
        if phase in phase_words:
            phase_words[phase] += sec.get("target_words", 0)

    total = sum(phase_words.values()) or 1
    actual_dist = {k: round(v / total * 100, 1) for k, v in phase_words.items()}

    # Ideal distribution
    ideal_dist = {"Attention": 10, "Interest": 20, "Desire": 40, "Action": 30}

    deviation = sum(abs(actual_dist.get(k, 0) - v) for k, v in ideal_dist.items())
    balance_score = round(max(0, 100 - deviation), 1)

    return {
        "actual_distribution": actual_dist,
        "ideal_distribution": ideal_dist,
        "balance_score": balance_score,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scaffold_proposal(
    type: str,
    title: str,
    audience: str = "executive",
    content: str = "",
    investment: float = 0,
    annual_return: float = 0,
) -> dict:
    """Generate a structured proposal scaffold with section templates.

    Args:
        type: Proposal type — business, sales, grant, partnership,
              internal, or technical.
        title: Title of the proposal.
        audience: Target audience — executive (concise), technical
                  (detailed), or general (balanced).
        content: Optional proposal text to analyze for argument strength.
        investment: Optional investment amount for ROI calculation.
        annual_return: Optional annual return for ROI calculation.

    Returns:
        Dictionary with sections, persuasion framework, objection
        templates, word targets, and tone guide.
    """
    type_key = type.lower().strip()
    if type_key not in _SECTION_TEMPLATES:
        type_key = "business"

    audience_key = audience.lower().strip()
    if audience_key not in _AUDIENCE_PROFILES:
        audience_key = "executive"

    audience_profile = _AUDIENCE_PROFILES[audience_key]
    base_word_count = 2000  # base target for a standard proposal
    word_multiplier = audience_profile["word_multiplier"]
    total_target_words = round(base_word_count * word_multiplier)

    # ── Build sections ───────────────────────────────────────────
    raw_sections = _SECTION_TEMPLATES[type_key]
    sections: list[dict] = []
    aida_mapping: dict[str, str] = {}

    for sec in raw_sections:
        target_words = round(total_target_words * sec["word_pct"] / 100)
        sections.append(
            {
                "name": sec["name"],
                "description": sec["description"],
                "target_words": target_words,
                "required": sec["required"],
                "template": sec["template"],
            }
        )
        aida_mapping[sec["name"]] = sec["aida"]

    # ── Persuasion framework ─────────────────────────────────────
    persuasion_framework = {
        "model": "AIDA",
        "mapping": aida_mapping,
    }

    # ── Objection templates ──────────────────────────────────────
    objection_templates = _OBJECTION_TEMPLATES.get(
        type_key, _OBJECTION_TEMPLATES["business"]
    )

    result = {
        "type": type_key,
        "title": title,
        "audience": audience_key,
        "sections": sections,
        "persuasion_framework": persuasion_framework,
        "objection_templates": objection_templates,
        "total_target_words": total_target_words,
        "tone_guide": audience_profile["tone"],
        "aida_coverage": _score_aida_coverage(sections, aida_mapping),
    }

    if content.strip():
        result["argument_analysis"] = _score_argument_strength(content)

    if investment > 0:
        result["roi_analysis"] = _compute_roi(investment, annual_return)

    return result
