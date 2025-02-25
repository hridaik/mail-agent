import boto3
from dataclasses import dataclass

@dataclass
class ModelResponse:
    content: str

class BedrockChat:
    def __init__(self, model_id="amazon.nova-lite-v1:0", region="us-east-1", max_tokens=1024, history_size=5):
        """
        Args:
            model_id (str): The AWS Bedrock model identifier.
            region (str): The AWS region.
            max_tokens (int): Maximum tokens for the response.
            history_size (int): Number of conversation turns to retain 
                                (each turn includes one user and one assistant message).
        """
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.history_size = history_size
        self.history = []  # List to store messages as dicts

    def _add_to_history(self, role: str, text: str):
        """
        Append a message to the history, formatting the content as a list of dicts.
        """
        message = {"role": role, "content": [{"text": text}]}
        self.history.append(message)
        # Each conversation turn is two messages; keep only the last (history_size * 2) messages.
        if len(self.history) > self.history_size * 2:
            self.history = self.history[-(self.history_size * 2):]

    def run(self, user_message: str) -> str:
        """
        Send a prompt to AWS Bedrock and return the assistant's response.
        
        Args:
            user_message (str): The new prompt/message from the user.
            
        Returns:
            str: The assistant's generated text.
        """
        # Add the user's message to the history.
        self._add_to_history("user", user_message)
        
        # Construct the request payload using the conversation history.
        payload = {
            "modelId": self.model_id,
            # API expects messages as a list of dicts.
            "messages": self.history,
            # Use inferenceConfig to set generation parameters (e.g., maxTokens).
            "inferenceConfig": {
                "maxTokens": self.max_tokens,
            }
        }
        
        # Call the AWS Bedrock API.
        response = self.client.converse(**payload)
        
        # For debugging: print the full response.
        # print("Full API Response:", response)
        
        # Extract the assistant's reply.
        content_list = response.get("output", {}).get("message", {}).get("content", [])
        assistant_response = " ".join(item.get("text", "").strip() for item in content_list)
        
        # Save the assistant's reply in the history.
        self._add_to_history("assistant", assistant_response)
        
        return ModelResponse(content=assistant_response)