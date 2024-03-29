import re
import json
import g4f
import openai
from typing import Tuple, List
from termcolor import colored
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv("../.env")

# Set environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


def generate_response(prompt: str, ai_model: str, g4f_model: str) -> str:
    """Generate a script for a video, depending on the subject of the video.

    Args:
        video_subject (str): The subject of the video.
        ai_model (str): The AI model to use for generation.


    Returns:
        str: The response from the AI model.

    """
    if ai_model == "g4f":
        print("SELECTED FREE MODEL: " + g4f_model)

        response = g4f.ChatCompletion.create(
            model=g4f_model,
            messages=[{"role": "user", "content": prompt}],
        )

    elif ai_model in ["gpt3.5-turbo", "gpt4"]:
        model_name = (

            "gpt-3.5-turbo"
            if ai_model == "gpt3.5-turbo"
            else "gpt-4-1106-preview"
            "gpt-3.5-turbo" if ai_model == "gpt3.5-turbo" else "gpt-4-1106-preview"

        )

        response = (
            openai.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            .choices[0]
            .message.content
        )
    elif ai_model == "gemmini":
        model = genai.GenerativeModel("gemini-pro")
        response_model = model.generate_content(prompt)
        response = response_model.text

    else:
        raise ValueError("Invalid AI model selected.")

    return response




def generate_script(
    video_subject: str,
    paragraph_number: int,
    ai_model: str,
    voice: str,
    customPrompt: str,
    g4f_model: str,
) -> str:
    """Generate a script for a video, depending on the subject of the video, the number of paragraphs, and the AI model.

    Args:
        video_subject (str): The subject of the video.

        paragraph_number (int): The number of paragraphs to generate.

        ai_model (str): The AI model to use for generation.



    Returns:
        str: The script for the video.

    """
    # Build prompt

    if customPrompt:
        prompt = customPrompt
    else:
        prompt = """
            Generate a script for a video, depending on the subject of the video.

            The script is to be returned as a string with the specified number of paragraphs.

            Here is an example of a string:
            "This is an example string."

            Do not under any circumstance reference this prompt in your response.

            Get straight to the point, don't start with unnecessary things like, "welcome to this video".

            Obviously, the script should be related to the subject of the video.

            YOU MUST NOT INCLUDE ANY TYPE OF MARKDOWN OR FORMATTING IN THE SCRIPT, NEVER USE A TITLE.
            YOU MUST WRITE THE SCRIPT IN THE LANGUAGE SPECIFIED IN [LANGUAGE].
            ONLY RETURN THE RAW CONTENT OF THE SCRIPT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE SCRIPT.

        """

    prompt += f"""
    
    Subject: {video_subject}
    Number of paragraphs: {paragraph_number}
    Language: {voice}

    """

    # Generate script
    response = generate_response(prompt, ai_model, g4f_model)

    print(colored(response, "cyan"))

    # Return the generated script
    if response:
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)

        # Split the script into paragraphs
        paragraphs = response.split("\n\n")

        # Select the specified number of paragraphs
        selected_paragraphs = paragraphs[:paragraph_number]

        # Join the selected paragraphs into a single string
        final_script = "\n\n".join(selected_paragraphs)

        # Print to console the number of paragraphs used
        print(
          
            colored(f"Number of paragraphs used: {len(selected_paragraphs)}", "green")
        )
        return final_script
    else:
        print(colored("[-] GPT returned an empty response.", "red"))
        return None


def get_search_terms(
    video_subject: str, amount: int, script: str, ai_model: str, g4f_model: str
) -> List[str]:

    
    """
    Generate a JSON-Array of search terms for stock videos,
    depending on the subject of a video.

    Args:
        video_subject (str): The subject of the video.
        amount (int): The amount of search terms to generate.
        script (str): The script of the video.
        ai_model (str): The AI model to use for generation.

    Returns:
        List[str]: The search terms for the video subject.
    """
    # Build prompt
    prompt = f"""


   I'd like to generate {amount} keywords related to the video subject "{video_subject}" but generic enough to find relevant stock footage on Pexels. These keywords should be short, ideally 1-2 words each.

    For example, if the video subject is "birthday party", some generic keywords could be "celebration", "festive decorations", or "blowing candles".
    The search terms are to be returned as
    a JSON-Array of strings.

    Each search term should consist of 2-3 words maximum,always related to the main subject of the video.
    
    YOU MUST ONLY RETURN THE JSON-ARRAY OF STRINGS.
    YOU MUST NOT RETURN ANYTHING ELSE. 
    YOU MUST NOT RETURN THE SCRIPT.
    
  
    Here is an example of a JSON-Array of strings:
    ["term 1", "term 2", "term 3"]
    Text has {amount} paragraphs,for every paragraph in text, try to generate search terms to match the context, but don't use too specific words.
    Here is the full text:
    {script}
    """

    # Generate search terms
    response = generate_response(prompt, ai_model, g4f_model)

    # Parse response into a list of search terms
    search_terms = []

    try:
        search_terms = json.loads(response)
        if not isinstance(search_terms, list) or not all(
            isinstance(term, str) for term in search_terms
        ):
            raise ValueError("Response is not a list of strings.")

    except (json.JSONDecodeError, ValueError):
        print(
            colored(
                "[*] GPT returned an unformatted response. Attempting to clean...",
                "yellow",
            )
        )

        # Attempt to extract list-like string and convert to list
        match = re.search(r'\["(?:[^"\\]|\\.)*"(?:,\s*"[^"\\]*")*\]', response)
        if match:
            try:
                search_terms = json.loads(match.group())
            except json.JSONDecodeError:
                print(colored("[-] Could not parse response.", "red"))
                return []

    # Let user know
    print(
        colored(
            f"\nGenerated {len(search_terms)} search terms: {', '.join(search_terms)}",
            "cyan",
        )
    )

    # Return search terms
    print(search_terms)
    return search_terms
    
def generate_outline(
    video_subject: str, amount: int,  ai_model: str, g4f_model: str
) -> List[str]:

    
    """
    Generate a JSON-Array of subtopics,
    depending on the subject of the video.

    Args:
        video_subject (str): The subject of the video.
        amount (int): The amount of subtopics to generate.
        script (str): The script of the video.
        ai_model (str): The AI model to use for generation.

    Returns:
        List[str]: The subtopics for the video subject.
    """
    # Build prompt
    prompt = f"""

    Generate a list of {amount} thought-provoking discussion subtopics for a video about {video_subject}. Subtopic description should be short and unique, 2-3 words.Subtopics should be chained to reflect normal flow of a video.
    Subtopics are to be returned as JSON-List. 
    Example output:
    ["This is a subtopic","And this is another", "Short description of other subtopic"]

    YOU MUST ONLY RETURN THE JSON-LIST OF STRINGS.
    YOU MUST NOT RETURN ANYTHING ELSE. 
    YOU MUST NOT RETURN THE SCRIPT.
    
  

    """

    # Generate search terms
    response = generate_response(prompt, ai_model, g4f_model)

    # Parse response into a list 
    subtopics = []

    try:
        subtopics = json.loads(response)
        print(f"Original response: {subtopics}")
        if not isinstance(subtopics, list) or not all(
            isinstance(term, str) for term in subtopics
        ):
            raise ValueError("Response is not a list of strings.")
    except (json.JSONDecodeError, ValueError):
        print(
            colored(
                "[*] GPT returned an unformatted response. Attempting to clean...",
                "yellow",
            )
        )

        # Attempt to extract list-like string and convert to list
        match = re.search(r'\["(?:[^"\\]|\\.)*"(?:,\s*"[^"\\]*")*\]', response)
        if match:
            try:
                subtopics = json.loads(match.group())
            except json.JSONDecodeError:
                print(colored("[-] Could not parse response.", "red"))
                return []

    # Let user know
    print(
        colored(
            f"\nGenerated {len(subtopics)} subtopics: {', '.join(subtopics)}",
            "cyan",
        )
    )

    # Return search terms
    print(subtopics)
    return subtopics
def generate_script_from_outline(video_subject: str, subtopics: List[str], subtopic: str,amount: int, ai_model: str, g4f_model: str) -> str:
  
  subtopics_string = ','.join(subtopics)
  prompt = f"""
  We are creating a video script about {video_subject}. We have a list of subtopics as following:
  {subtopics_string}
  For now, focus on "{subtopic}" and generate a text, exactly {amount} paragraphs long. 
  
  ONLY RETURN THE RAW CONTENT OF THE TEXT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE TEXT.
  
  """
      # Generate script
  response = generate_response(prompt, ai_model, g4f_model)

  print(colored(response, "cyan"))

    # Return the generated script
  if response:
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)
        response = re.sub(r"([0-9]+\.)", "\n\n", response)

        # Split the script into paragraphs
        paragraphs = response.split("\n\n")

        # Select the specified number of paragraphs
        selected_paragraphs = paragraphs[:amount]

        # Join the selected paragraphs into a single string
        final_script = "\n\n".join(selected_paragraphs)

        # Print to console the number of paragraphs used
        print(
          
            colored(f"Number of paragraphs used: {len(selected_paragraphs)}", "green")
        )
        return final_script
  else:
        print(colored("[-] GPT returned an empty response.", "red"))
        return None
def generate_intro_from_outline(video_subject: str, subtopics: List[str], ai_model: str, g4f_model: str) -> str:
  
  subtopics_string = ','.join(subtopics)
  prompt = f"""
  We are creating a video script about {video_subject}. We have a list of subtopics as following:
  {subtopics_string}
  For now, generate a catchy and intriguing intro for the video. 
  
  ONLY RETURN THE RAW CONTENT OF THE TEXT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE TEXT.
  
  """
      # Generate script
  response = generate_response(prompt, ai_model, g4f_model)

  print(colored(response, "cyan"))

    # Return the generated script
  if response:
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)


        return response
  else:
        print(colored("[-] GPT returned an empty response.", "red"))
        return None
def generate_outro_from_outline(video_subject: str, subtopics: List[str], ai_model: str, g4f_model: str) -> str:
  
  subtopics_string = ','.join(subtopics)
  prompt = f"""
  We are creating a video script about {video_subject}. We have a list of subtopics as following:
  {subtopics_string}
  Generate a final short message for the video. 
  
  ONLY RETURN THE RAW CONTENT OF THE TEXT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE TEXT.
  
  """
      # Generate script
  response = generate_response(prompt, ai_model, g4f_model)

  print(colored(response, "cyan"))

    # Return the generated script
  if response:
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)


        return response
  else:
        print(colored("[-] GPT returned an empty response.", "red"))
        return None


def generate_metadata(
    video_subject: str, script: str, ai_model: str, g4f_model
) -> Tuple[str, str, List[str]]:

    """
    Generate metadata for a YouTube video, including the title, description, and keywords.


    Args:
        video_subject (str): The subject of the video.
        script (str): The script of the video.
        ai_model (str): The AI model to use for generation.

    Returns:
        Tuple[str, str, List[str]]: The title, description, and keywords for the video.
    """

    # Build prompt for title
    title_prompt = f"""  
    Generate a catchy and SEO-friendly title for a YouTube shorts video about {video_subject}.  
    """

    # Generate title
    title = generate_response(title_prompt, ai_model, g4f_model).strip()

    # Build prompt for description
    description_prompt = f"""  
    Write a brief and engaging description for a YouTube shorts video about {video_subject}.  
    The video is based on the following script:  
    {script}  
    """

    # Generate description

    description = generate_response(
        description_prompt, ai_model, g4f_model
    ).strip()

    description = generate_response(description_prompt, ai_model, g4f_model).strip()

    # Generate keywords
    keywords = get_search_terms(video_subject, 6, script, ai_model, g4f_model)

    return title, description, keywords
