import threading
import time
import unittest
from unittest.mock import patch

from server.pipeline import Pipeline


class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Prepare the pipeline with the correct steps folder path
        self.pipeline = Pipeline(steps_folder="pipeline_steps", runtime_dependencies={})

        # Inline JSON configuration for the test
        self.config = {
            "steps": [
                {
                    "id": "data_collection_step",
                    "inputs": {},
                    "config": {
                        "source": "test_source"
                    }
                },
                {
                    "id": "data_processing_step",
                    "inputs": {
                        "raw_data": "data_collection_step.raw_data"
                    },
                    "config": {
                        "processing_mode": "test_mode"
                    }
                },
                {
                    "id": "final_aggregation_step",
                    "inputs": {
                        "summary": "data_processing_step.summary"
                    },
                    "config": {
                        "aggregation_strategy": "test_strategy"
                    }
                }
            ]
        }

    def test_discovery_of_steps(self):
        # Test that the pipeline discovers the steps correctly
        expected_steps = {"data_collection_step", "data_processing_step", "final_aggregation_step"}
        discovered_steps = set(self.pipeline.steps.keys())
        self.assertEqual(discovered_steps, expected_steps, "Pipeline did not discover steps correctly")

    def test_pipeline_execution(self):
        # Load the pipeline configuration
        self.pipeline.load_pipeline_from_json(self.config)

        # Run the pipeline
        self.pipeline.run(initial_params={"source": "inline_test_source"})

        # Check the final result
        result = self.pipeline.get_step_result("final_aggregation_step")
        self.assertIsNotNone(result, "Final result should not be None")

        # Handle both object and dictionary returns for final aggregation
        if isinstance(result, dict):
            self.assertIn("final_report", result, "Final result should contain 'final_report'")
            self.assertEqual(result["final_report"], "Final Report (Strategy: test_strategy):\nProcessed (test_mode): data point 1, data point 2, data point 3")
        else:
            # Assuming result is an object with a 'final_report' attribute
            self.assertTrue(hasattr(result, "final_report"), "Final result object should have 'final_report' attribute")
            self.assertEqual(result.final_report, "Final Report (Strategy: test_strategy):\nProcessed (test_mode): data point 1, data point 2, data point 3")


if __name__ == '__main__':
    unittest.main()
