"""
Seeded question bank + skill domain bootstrap.

Used for offline demos and as the primary content source when the LLM
is not configured (or as a fallback when LLM generation fails).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.models import Difficulty, Question, SkillDomain

DOMAINS = [
    {
        "slug": "argument_analysis",
        "name": "Argument Analysis",
        "description": "Identify claims, reasons, and the structure of arguments.",
    },
    {
        "slug": "fallacy_detection",
        "name": "Fallacy Detection",
        "description": "Spot common logical fallacies and explain why they weaken an argument.",
    },
    {
        "slug": "evidence_evaluation",
        "name": "Evidence Evaluation",
        "description": "Judge the quality, relevance, and sufficiency of evidence.",
    },
    {
        "slug": "assumptions",
        "name": "Assumptions",
        "description": "Surface hidden assumptions and test whether they hold.",
    },
    {
        "slug": "causal_reasoning",
        "name": "Causal Reasoning",
        "description": "Distinguish correlation from causation and evaluate causal claims.",
    },
]

# Seed questions: (domain_slug, difficulty, title, scenario, prompt, expected_signals)
SEED_QUESTIONS: list[tuple] = [
    (
        "argument_analysis",
        "beginner",
        "Campus Coffee Ban",
        (
            "A student newspaper editorial argues: 'The campus should ban disposable coffee cups. "
            "Single-use cups create waste, and our university claims to care about sustainability. "
            "Therefore, a ban is the only responsible policy.'"
        ),
        "Identify the main claim and the supporting reasons. What is missing from this argument?",
        {"good_keywords": ["claim", "reason", "alternative", "assumption"], "fallacy_traps": ["false_dilemma"]},
    ),
    (
        "argument_analysis",
        "intermediate",
        "Remote Work Productivity",
        (
            "A manager writes: 'Since we switched to remote work, customer tickets have increased by 12%. "
            "Remote work clearly reduces productivity. We must return to the office five days a week "
            "or accept declining service quality.'"
        ),
        "Map the argument's structure. Which premises would you challenge, and why?",
        {"good_keywords": ["premise", "causal", "alternative", "confound"], "fallacy_traps": ["false_dilemma", "post_hoc"]},
    ),
    (
        "argument_analysis",
        "advanced",
        "AI Hiring Screens",
        (
            "A tech firm claims its résumé-screening AI is fair because 'it ignores names and photos, "
            "so it cannot be biased.' Critics note the model was trained on a decade of past hiring "
            "decisions that favored graduates from a small set of schools."
        ),
        "Reconstruct both sides as structured arguments. Where does the company's argument fail?",
        {"good_keywords": ["proxy", "training data", "fairness", "warrant"], "fallacy_traps": []},
    ),
    (
        "fallacy_detection",
        "beginner",
        "Group Chat Debate",
        (
            "Alex: 'We should try a four-day work week; trials in other companies show similar output.'\n"
            "Jordan: 'Of course you'd say that — you just want more days off. Typical lazy take.'"
        ),
        "Name any fallacies you see and explain how they affect the discussion.",
        {"good_keywords": ["ad_hominem", "attack", "person"], "fallacy_traps": ["ad_hominem"]},
    ),
    (
        "fallacy_detection",
        "intermediate",
        "City Bike Lanes",
        (
            "'If we add protected bike lanes downtown, cars will be slower, businesses will close, "
            "tourism will collapse, and the city will go bankrupt. We cannot risk that.'"
        ),
        "Which fallacy (or fallacies) appear here? Rewrite the concern as a non-fallacious argument.",
        {"good_keywords": ["slippery_slope", "evidence", "probability"], "fallacy_traps": ["slippery_slope"]},
    ),
    (
        "fallacy_detection",
        "advanced",
        "Nutrition Influencer",
        (
            "An influencer says: 'Millions of my followers swear by this detox tea. Doctors who "
            "criticize it are just protecting Big Pharma. Either you cleanse or you stay toxic.'"
        ),
        "Identify multiple fallacies and explain how they interact to persuade the audience.",
        {"good_keywords": ["bandwagon", "false_dilemma", "ad_hominem"], "fallacy_traps": ["bandwagon", "false_dilemma"]},
    ),
    (
        "evidence_evaluation",
        "beginner",
        "Sleep Survey",
        (
            "A blog cites a poll of 40 readers: 80% who took a new supplement 'felt more energized.' "
            "The author concludes the supplement works."
        ),
        "Evaluate the quality of this evidence. What would stronger evidence look like?",
        {"good_keywords": ["sample", "control", "placebo", "bias"], "fallacy_traps": ["hasty_generalization"]},
    ),
    (
        "evidence_evaluation",
        "intermediate",
        "Crime and Ice Cream",
        (
            "A city dashboard shows ice cream sales and reported assaults both rise in summer months. "
            "A council member proposes restricting ice cream vendors to reduce violence."
        ),
        "What is wrong with using this correlation as policy evidence? What data would you request?",
        {"good_keywords": ["confound", "temperature", "correlation", "causation"], "fallacy_traps": ["post_hoc"]},
    ),
    (
        "evidence_evaluation",
        "advanced",
        "EdTech RCT Snippet",
        (
            "A vendor reports: 'In a randomized trial across 12 schools (n=3,400), students using our "
            "app gained +0.08 SD on a standardized math test (p=0.04). We conclude it transforms learning.'"
        ),
        "Critique the evidence and the leap to the conclusion. What additional details matter?",
        {"good_keywords": ["effect size", "multiple testing", "implementation", "generalizability"], "fallacy_traps": []},
    ),
    (
        "assumptions",
        "beginner",
        "Library Quiet Hours",
        (
            "'Extending quiet hours will help students study better, so exam scores will improve.'"
        ),
        "List the hidden assumptions in this argument. Which is most questionable?",
        {"good_keywords": ["assumption", "study", "scores", "causation"], "fallacy_traps": []},
    ),
    (
        "assumptions",
        "intermediate",
        "Mandatory Internships",
        (
            "A university proposes requiring every major to complete a paid internship, arguing that "
            "'career readiness requires workplace experience, and employers only hire interns who already know the ropes.'"
        ),
        "Surface the key assumptions. How would you test one of them empirically?",
        {"good_keywords": ["assumption", "employer", "access", "equity"], "fallacy_traps": []},
    ),
    (
        "assumptions",
        "advanced",
        "Predictive Policing",
        (
            "A city adopts a predictive policing model because 'deploying officers where crime is predicted "
            "will prevent crime, and historical crime data is an objective record of where risk lies.'"
        ),
        "Identify load-bearing assumptions about data, feedback loops, and fairness. Which is most dangerous if false?",
        {"good_keywords": ["feedback loop", "bias", "objectivity", "assumption"], "fallacy_traps": []},
    ),
    (
        "causal_reasoning",
        "beginner",
        "New Desk Chairs",
        (
            "After a company bought ergonomic chairs, sick days fell 10% the next quarter. "
            "Leadership credits the chairs."
        ),
        "Give two non-causal explanations for the drop in sick days. How would you test the chair hypothesis?",
        {"good_keywords": ["confound", "regression", "season", "experiment"], "fallacy_traps": ["post_hoc"]},
    ),
    (
        "causal_reasoning",
        "intermediate",
        "Homework Ban Pilot",
        (
            "School A bans homework for a semester; average well-being scores rise. School B keeps homework; "
            "scores stay flat. Advocates say the ban caused the improvement."
        ),
        "What causal inferences are justified? What threats to validity remain?",
        {"good_keywords": ["selection", "confound", "history", "comparison"], "fallacy_traps": []},
    ),
    (
        "causal_reasoning",
        "advanced",
        "Social Media & Attention",
        (
            "A longitudinal study finds teens who spend more time on short-video apps later score lower on "
            "sustained-attention tasks. The authors carefully control for baseline attention, SES, and sleep."
        ),
        "Even with controls, what causal challenges remain? Design a stronger study in outline form.",
        {"good_keywords": ["residual confounding", "reverse causality", "instrument", "experiment"], "fallacy_traps": []},
    ),
]


def seed_domains_and_questions(db: Session) -> None:
    """Idempotently insert skill domains and seed questions."""
    slug_to_domain: dict[str, SkillDomain] = {}
    for d in DOMAINS:
        existing = db.query(SkillDomain).filter_by(slug=d["slug"]).one_or_none()
        if existing:
            slug_to_domain[d["slug"]] = existing
        else:
            domain = SkillDomain(**d)
            db.add(domain)
            db.flush()
            slug_to_domain[d["slug"]] = domain

    existing_titles = {q.title for q in db.query(Question).all()}
    for slug, diff, title, scenario, prompt, signals in SEED_QUESTIONS:
        if title in existing_titles:
            continue
        db.add(
            Question(
                domain_id=slug_to_domain[slug].id,
                difficulty=Difficulty(diff),
                title=title,
                scenario=scenario,
                prompt=prompt,
                expected_signals=signals,
                source="seed",
            )
        )
    db.commit()
