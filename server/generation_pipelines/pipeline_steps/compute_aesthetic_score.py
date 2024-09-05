from abc import ABC
import json
from typing import Dict, Any
from dataclasses import dataclass

from server.pipeline_step import PipelineStep
from server.shared.llm import LlmClient, ModelType, parse_markdown_output


@dataclass
class AestheticScoreResult:
    score: float


class ComputeAestheticScoreStep(PipelineStep):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_type() -> str:
        return "compute_aesthetic_score"

    @staticmethod
    def get_name() -> str:
        return "Compute Aesthetic Score"

    @staticmethod
    def get_description() -> str:
        return "Compute the aesthetic score of a website from a screenshot."

    async def process(self, screenshot: bytes, **kwargs) -> AestheticScoreResult:
        self.push_update("Starting aesthetic score computation...")

        # Formulate the prompt for LLM
        self.push_update("Preparing prompt for LLM...")
        prompt = """
        Analyze the visual features of a website from the provided screenshot and compute the following aesthetic metrics. Exclude any analysis related to animations or accessibility features.
        
        Provide the output in the following JSON format:

        ```json
        {
          "color_scheme": {
            "color_harmony": int,
            "color_contrast": int,
            "color_consistency": int,
            "color_balance": int
          },
          "typography": {
            "font_pairing": int,
            "font_size_and_hierarchy": int,
            "readability": int,
            "line_spacing_and_alignment": int
          },
          "layout_and_composition": {
            "visual_balance": int,
            "alignment_and_spacing": int,
            "whitespace_usage": int,
            "grid_structure": int,
            "element_proportion_and_size": int
          },
          "imagery_and_media": {
            "image_quality": int,
            "image_relevance": int,
            "media_balance": int
          },
          "consistency_and_cohesion": {
            "design_consistency": int,
            "visual_cohesion": int
          },
          "visual_hierarchy": {
            "cta_visibility": int,
            "focal_points": int,
            "content_prioritization": int
          },
          "aesthetic_appeal": {
            "modern_design_elements": int,
            "visual_novelty": int,
            "overall_attractiveness": int
          },
          "consistency_with_branding": {
            "logo_placement_and_size": int,
            "brand_color_usage": int,
            "unique_brand_elements": int
          },
          "iconography": {
            "icon_consistency": int,
            "icon_relevance": int
          }
        }
        ```

        Each metric should be rated on a scale from 0 to 10.
        """

        # Call the LLM with the prompt
        self.push_update("Querying LLM for aesthetic score analysis...")
        llm = LlmClient(model=ModelType.GPT_4_OMNI)
        llm_response = llm.get_completions(prompt, temperature=0.0, image_list=[screenshot])

        # Parse the JSON output from LLM
        self.push_update("Parsing LLM response...")
        aesthetic_scores = json.loads(parse_markdown_output(llm_response, lang='json'))
        print(aesthetic_scores)

        # Define weights for each category
        weights = {
            "color_scheme": 0.15,
            "typography": 0.15,
            "layout_and_composition": 0.20,
            "imagery_and_media": 0.10,
            "consistency_and_cohesion": 0.10,
            "visual_hierarchy": 0.10,
            "aesthetic_appeal": 0.15,
            "consistency_with_branding": 0.05,
            "iconography": 0.05,
        }

        # Compute the weighted sum
        self.push_update("Computing overall aesthetic score...")
        weighted_sum = sum(
            weights[category] * sum(metrics.values()) / len(metrics)
            for category, metrics in aesthetic_scores.items()
        )
        print(weighted_sum)

        self.push_update("Aesthetic score computation completed.")
        return AestheticScoreResult(score=weighted_sum)
