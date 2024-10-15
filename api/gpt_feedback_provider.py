import openai
import time

class GPTFeedbackProvider:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def get_feedback(self, directory_structure, java_files_content):
        model = self.model

        """
        Sends the directory structure and Java file content to the GPT model for feedback.
        Returns the feedback from GPT.
        """
        # Combine the directory structure and Java content
        combined_content = "Directory Structure:\n" + directory_structure + "\n\nJava File Contents:\n" + java_files_content

        system_content = """
        You are a helpful assistant and an expert Java mentor for beginner programmers. Your task is to review the Java code and the directory structure of a repository. Please provide detailed feedback on:

        - Code quality and organization, including potential improvements.
        - Any mistakes or issues that may be present in the code.
        - Best practices that are not being followed and how to implement them.
        - Suggestions for refactoring the code for clarity or efficiency.
        - Explanations of key Java concepts for a beginner to learn from.
        - Overall feedback.

        Be encouraging and constructive, providing helpful advice that a beginner can understand and act on.
        """

        print(">>> Hold tight! GPT is reviewing your work... (May take up to a minute)\n")

        start_time = time.time()
        # Use OpenAI API to send the content to GPT
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": combined_content}
            ]
        )

        end_time = time.time()  # End time measurement
        duration = end_time - start_time  # Calculate the time taken
        
        # Extract and return GPT's feedback
        feedback = response.choices[0].message.content
        return feedback, model, duration
