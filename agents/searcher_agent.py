"""
Searcher Agent
--------------
Collects information from web sources and academic resources based on the plan.
Returns relevant research data and source links.
"""

import time
import random
import copy


# --- Sample research data pools ---

TOPIC_DATA = {
    "default": {
        "abstract": (
            "This research explores the intersection of advanced computational methods "
            "and real-world applications. Through systematic analysis of existing literature "
            "and empirical studies, we identify core patterns, challenges, and emerging "
            "opportunities. The findings suggest significant potential for cross-disciplinary "
            "innovation and scalable solutions."
        ),

        "key_findings": [
            "Existing models achieve 87–94% accuracy on benchmark datasets, with transformer-based architectures consistently outperforming traditional baselines.",
            "Data scarcity remains the primary bottleneck; federated learning approaches reduce dependency on centralized datasets by up to 60%.",
            "Computational cost has dropped by 3× over the past two years due to hardware acceleration and model distillation techniques.",
            "Explainability tools (SHAP, LIME) are now integrated into 70% of production deployments, addressing regulatory compliance needs.",
            "Emerging hybrid approaches combining symbolic reasoning with neural networks show promise for edge-case robustness.",
        ],

        "methodology": (
            "A systematic literature review was conducted across IEEE Xplore, arXiv, and Google Scholar "
            "covering publications from 2019–2024. Inclusion criteria required empirical validation and "
            "peer review. Meta-analysis was applied to quantitative results, and thematic coding was "
            "used for qualitative synthesis."
        ),

        "analysis": (
            "The landscape is shifting from monolithic model development toward modular, composable "
            "systems. Researchers increasingly prioritize reproducibility and open-source tooling. "
            "Industry adoption lags academia by roughly 18 months, indicating a healthy pipeline. "
            "Ethical considerations—bias, fairness, and transparency—are transitioning from footnotes "
            "to first-class design constraints in leading research groups."
        ),

        "conclusion": (
            "This field is at an inflection point. The convergence of better hardware, open datasets, "
            "and mature tooling is accelerating progress. Key priorities for the next research cycle "
            "include robustness under distribution shift, multi-modal integration, and low-resource "
            "deployment. Interdisciplinary collaboration will be the defining factor in translating "
            "research advances into societal impact."
        ),

        "sources": [
            {
                "title": "Attention Is All You Need",
                "url": "https://arxiv.org/abs/1706.03762",
                "year": 2017,
                "venue": "NeurIPS"
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "url": "https://arxiv.org/abs/1810.04805",
                "year": 2018,
                "venue": "NAACL"
            },
            {
                "title": "A Survey on Transfer Learning",
                "url": "https://ieeexplore.ieee.org/document/5288526",
                "year": 2021,
                "venue": "IEEE TKDE"
            },
            {
                "title": "Federated Learning: Challenges, Methods, and Future Directions",
                "url": "https://arxiv.org/abs/1908.07873",
                "year": 2020,
                "venue": "IEEE Signal Processing"
            },
            {
                "title": "Explainable AI: A Review of Machine Learning Interpretability Methods",
                "url": "https://www.mdpi.com/1099-4300/23/1/18",
                "year": 2022,
                "venue": "Entropy"
            },
            {
                "title": "Deep Learning for Natural Language Processing",
                "url": "https://arxiv.org/abs/2003.08271",
                "year": 2023,
                "venue": "ACL Anthology"
            },
            {
                "title": "Model Compression and Efficient Inference",
                "url": "https://arxiv.org/abs/2106.08962",
                "year": 2023,
                "venue": "arXiv"
            },
            {
                "title": "Ethical AI: Frameworks and Case Studies",
                "url": "https://dl.acm.org/doi/10.1145/3442188.3445922",
                "year": 2024,
                "venue": "FAccT"
            },
        ],
    }
}


URL_DATA = {
    "abstract": (
        "This paper presents a novel framework addressing a critical gap in current methodology. "
        "The authors propose a three-stage pipeline combining preprocessing, representation learning, "
        "and task-specific fine-tuning. Extensive experiments on five benchmark datasets demonstrate "
        "state-of-the-art performance, with a 12.3% improvement over the previous best baseline."
    ),

    "key_findings": [
        "The proposed architecture achieves a new SOTA on all five benchmarks, with gains of 8–15% over prior work.",
        "Ablation studies confirm each module contributes independently; removing any single component degrades performance by at least 4%.",
        "The model generalizes well to out-of-distribution data, a significant improvement over specialized prior methods.",
        "Training converges 2× faster than the closest competitor due to a novel loss formulation.",
        "The approach is parameter-efficient: comparable performance to larger models at 40% of the parameter count.",
    ],

    "methodology": (
        "The authors employ a mixed-methods approach: quantitative experiments on standard benchmarks "
        "plus qualitative analysis via expert evaluation. The model is trained on a curated dataset "
        "of 2.4M examples with rigorous train/validation/test splits. Hyperparameter tuning uses "
        "Bayesian optimization. Statistical significance is reported for all comparisons (p < 0.05)."
    ),

    "analysis": (
        "The paper makes a strong contribution to its subfield. The ablation design is thorough "
        "and the claims are well-supported. The primary limitation is dataset scope—all benchmarks "
        "are English-language, and multilingual generalization is left as future work. The efficiency "
        "gains are meaningful for real-world deployment, particularly on resource-constrained devices. "
        "The open-sourced code and pretrained weights significantly increase reproducibility."
    ),

    "conclusion": (
        "This work advances the state of the art in a meaningful and reproducible way. The proposed "
        "method is both effective and efficient, addressing practical deployment constraints that prior "
        "methods ignored. Future work should focus on multilingual extension, robustness to adversarial "
        "inputs, and integration with retrieval-augmented systems. The released artifacts will likely "
        "serve as a strong baseline for subsequent research."
    ),

    "sources": [
        {
            "title": "Referenced paper – Section 2.1",
            "url": "https://arxiv.org/abs/2301.00303",
            "year": 2023,
            "venue": "arXiv"
        },
        {
            "title": "Baseline model comparison",
            "url": "https://arxiv.org/abs/2204.02311",
            "year": 2022,
            "venue": "ACL"
        },
        {
            "title": "Dataset origin paper",
            "url": "https://huggingface.co/datasets",
            "year": 2023,
            "venue": "HuggingFace"
        },
    ],
}


def searcher_agent(plan: dict) -> dict:
    """
    Searcher Agent: Collects research information based on the planner's output.

    Args:
        plan: dict produced by planner_agent

    Returns:
        dict containing abstract, findings, methodology, analysis,
        conclusion, and sources.
    """

    # Simulate web/database search
    time.sleep(0.8)

    input_type = plan.get("input_type", "topic")
    subject = plan.get("subject", "")
    mode = plan.get("mode", "Short Summary")

    if input_type == "url":
        # Deep copy so original URL_DATA is never modified
        data = copy.deepcopy(URL_DATA)

        data["title"] = (
            f"Analysis of Research Paper: "
            f"{subject[:60]}{'...' if len(subject) > 60 else ''}"
        )

    else:
        # Deep copy so the original TOPIC_DATA is never modified
        data = copy.deepcopy(TOPIC_DATA["default"])

        data["title"] = f"Research Report: {subject}"

        # Shuffle only the copied list
        random.shuffle(data["key_findings"])

    # Common information
    data["source_count"] = len(data["sources"])
    data["mode"] = mode
    data["input_type"] = input_type
    data["subject"] = subject
    data["status"] = "Research data collected successfully"

    return data
