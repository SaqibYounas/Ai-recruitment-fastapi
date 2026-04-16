# from openai import OpenAI
# import os

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def analyze_candidate(job_description: str, cv_text: str):
#     prompt = f"""
#     Job Description: {job_description}
#     Candidate CV: {cv_text}
    
#     Task: Compare the CV with the job description. 
#     1. Give a matching score out of 100.
#     2. Provide a 2-line summary of why this candidate is a good or bad fit.
    
#     Return the response in JSON format like this:
#     {{"score": 85, "reason": "Candidate has strong FastAPI experience but lacks AWS knowledge."}}
#     """
    
#     response = client.chat.completions.create(
#         model="gpt-4o", # Ya gpt-3.5-turbo
#         messages=[{"role": "user", "content": prompt}],
#         response_format={ "type": "json_object" }
#     )
    
#     return response.choices[0].message.content