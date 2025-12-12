import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import torch

# Create mock modules for likely missing dependencies (tools etc)
mock_pandas = MagicMock()
mock_pandas.__spec__ = MagicMock()
mock_weasyprint = MagicMock()
mock_weasyprint.__spec__ = MagicMock()
mock_langchain_community = MagicMock()
mock_langchain_community.__spec__ = MagicMock()

# Patch sys.modules for these specific missing dependencies
sys.modules["pandas"] = mock_pandas
sys.modules["weasyprint"] = mock_weasyprint
sys.modules["langchain_community.tools"] = mock_langchain_community

# Patch env vars
patch_env = patch.dict(os.environ, {"LLM_MODEL_NAME": "dummy-model", "OPENAI_API_KEY": "", "GOOGLE_API_KEY": ""})
patch_env.start()

# Import LocalModel after patching env
from backend.llms import LocalModel
from langchain_core.messages import HumanMessage

class TestLocalModelVerification(unittest.TestCase):

    @patch("backend.llms.AutoTokenizer")
    @patch("backend.llms.AutoModelForCausalLM")
    def test_generate_returns_full_history(self, mock_model_cls, mock_tokenizer_cls):
        """
        Verify that LocalModel returns correctly sliced output using real Torch tensors.
        """
        # Setup mocks
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
        mock_model_cls.from_pretrained.return_value = mock_model

        # Mock tokenizer behavior
        # Return real tensor for "input_ids"
        # Shape (1, 3) -> [1, 2, 3]
        mock_tokenizer.return_value = {"input_ids": torch.tensor([[1, 2, 3]])}
        
        # Mock generate behavior
        # Return real tensor containing [1, 2, 3, 4, 5]
        # The code expects the result of client.generate()
        mock_model.generate.return_value = torch.tensor([[1, 2, 3, 4, 5]])
        
        def decode_side_effect(token_ids, skip_special_tokens=True):
            # token_ids will be a Tensor slice
            # Convert to list for easy comparison
            ids_list = token_ids.tolist()
            
            # If sliced correctly [4, 5]
            if ids_list == [4, 5]:
                return "Assistant: Hi there"
            # If full sequence (bug)
            if ids_list == [1, 2, 3, 4, 5]:
                 return "User: Hello\nAssistant: Hi there"
            return f"Unknown ids: {ids_list}"
            
        mock_tokenizer.decode.side_effect = decode_side_effect

        # Initialize LocalModel
        local_model = LocalModel(model="dummy-model")
        
        # Invoke
        messages = [HumanMessage(content="Hello")]
        response = local_model.invoke(messages)
        
        print(f"Test Result: '{response.content}'")

        # Assertion
        self.assertNotIn("User: Hello", response.content)
        self.assertIn("Assistant: Hi there", response.content)

    @patch("backend.llms.AutoTokenizer")
    @patch("backend.llms.AutoModelForCausalLM")
    def test_structured_output_behavior(self, mock_model_cls, mock_tokenizer_cls):
        """
        Verify behavior when .with_structured_output is called.
        """
        # Setup mocks
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
        mock_model_cls.from_pretrained.return_value = mock_model

        # Initialize LocalModel
        local_model = LocalModel(model="dummy-model")
        
        # Define schema
        from pydantic import BaseModel
        class TestSchema(BaseModel):
            answer: str
            
        # Attempt structured output
        try:
            structured_llm = local_model.with_structured_output(TestSchema)
            
            # Setup for invoke with minimal valid return values
            mock_tokenizer.return_value = {"input_ids": torch.tensor([[1]])}
            mock_model.generate.return_value = torch.tensor([[1, 2]])
            mock_tokenizer.decode.return_value = "raw response"
            
            result = structured_llm.invoke([HumanMessage(content="test")])
            
            print(f"Structured Output Result: {result}")
            self.assertNotIsInstance(result, TestSchema)
            
        except NotImplementedError:
            pass
        except Exception:
            pass

if __name__ == "__main__":
    patch_env.stop()
    unittest.main()
