
import traceback
import google.generativeai as genai
from dotenv import load_dotenv
from libs.logger import logger
import streamlit as st

class GeminiAI:
    def __init__(self, api_key, model="gemini-pro", temperature=0.1, max_output_tokens=2048,mode="balanced"):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.mode = mode
        self.top_k = 20
        self.top_p = 0.85
        self._configure()

        # Dynamically construct guidelines based on session state
        self.guidelines_list = []

        if st.session_state["coding_guidelines"]["modular_code"]:
            self.guidelines_list.append("- Ensure the method is modular in its approach.")
        if st.session_state["coding_guidelines"]["exception_handling"]:
            self.guidelines_list.append("- Integrate robust exception handling.")
        if st.session_state["coding_guidelines"]["error_handling"]:
            self.guidelines_list.append("- Add error handling to each module.")
        if st.session_state["coding_guidelines"]["efficient_code"]:
            self.guidelines_list.append("- Optimize the code to ensure it runs efficiently.")
        if st.session_state["coding_guidelines"]["robust_code"]:
            self.guidelines_list.append("- Ensure the code is robust against potential issues.")
        if st.session_state["coding_guidelines"]["naming_conventions"]:
            self.guidelines_list.append("- Follow standard naming conventions.")

        # Convert the list to a string
        self.guidelines = "\n".join(self.guidelines_list)
        
        
    def _configure(self):
        try:
            logger.info("Configuring Gemini AI Pro...")
            genai.configure(api_key=self.api_key)
            self.generation_config = {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "max_output_tokens": self.max_output_tokens
            }
            self.model = genai.GenerativeModel(model_name=self.model,generation_config=self.generation_config)
            logger.info("Gemini AI Pro configured successfully.")
        except Exception as exception:
            logger.error(f"Error configuring Gemini AI Pro: {str(exception)}")
            traceback.print_exc()

    def _extract_code(self, code):
        """
        Extracts the code from the provided string.
        If the string contains '```', it extracts the code between them.
        Otherwise, it returns the original string.
        """
        try:
            if '```' in code:
                start = code.find('```') + len('```\n')
                end = code.find('```', start)
                # Skip the first line after ```
                start = code.find('\n', start) + 1
                extracted_code = code[start:end]
                logger.info("Code extracted successfully.")
                return extracted_code
            else:
                logger.info("No special characters found in the code. Returning the original code.")
                return code
        except Exception as exception:
            logger.error(f"Error occurred while extracting code: {exception}")
            return None
        
    def generate_code(self, code_prompt,code_language):
        """
        Function to generate text using the Gemini API.
        """
        try:
            # Define top_k and top_p based on the mode
            if self.mode == "precise":
                top_k = 40
                top_p = 0.95
                self.temprature = 0
            elif self.mode == "balanced":
                top_k = 20
                top_p = 0.85
                self.temprature = 0.3
            elif self.mode == "creative":
                top_k = 10
                top_p = 0.75
                self.temprature = 1
            else:
                raise ValueError("Invalid mode. Choose from 'precise', 'balanced', 'creative'.")

            logger.info(f"Generating code with mode: {self.mode}, top_k: {top_k}, top_p: {top_p}")

            
            # check for valid prompt and language
            if not code_prompt or len(code_prompt) == 0:
                st.toast("Error in code generation: Please enter a valid prompt.", icon="❌")
                logger.error("Error in code generation: Please enter a valid prompt.")
                return
            
            logger.info(f"Generating code for prompt: {code_prompt} in language: {code_language}")
            if code_prompt and len(code_prompt) > 0 and code_language and len(code_language) > 0:
                logger.info(f"Generating code for prompt: {code_prompt} in language: {code_language}")
                
            # Plain and Simple Coding Task Prompt
            prompt = f"""
            Task: You're an experienced developer. Your mission is to create a program for {code_prompt} in {code_language} that takes {st.session_state.code_input} as input.

            Your goal is clear: Craft a solution that showcases your expertise as a coder and problem solver.

            Ensure that the program's output contains only the code you've written, with no extraneous information.

            Show your skills and solve this challenge with confidence!
            
            And follow the proper coding guidelines and dont add comment unless instructed to do so.
            {self.guidelines}
            """
            
            gemini_completion = self.model.generate_content(prompt)
            logger.info("Text generation completed successfully.")
            
            code = None
            if gemini_completion:
                # extract the code from the gemini completion
                code = gemini_completion.text
                logger.info(f"GeminiAI coder is initialized.")
                logger.info(f"Generated code: {code[:100]}...")
            
            if gemini_completion:
                # Extracted code from the gemini completion
                extracted_code = self._extract_code(code)
                
                # Check if the code or extracted code is not empty or null
                if not code or not extracted_code:
                    raise Exception("Error: Generated code or extracted code is empty or null.")
                
                return extracted_code
            else:
                raise Exception("Error in code generation: Please enter a valid code.")
            
        except Exception as exception:
            st.toast(f"Error in code generation: {exception}", icon="❌")
            logger.error(f"Error in code generation: {traceback.format_exc()}")
