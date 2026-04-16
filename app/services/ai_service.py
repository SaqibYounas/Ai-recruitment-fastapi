from openai import AsyncOpenAI
import os, json, asyncio

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyze_cv(cv_text: str, jd: str):
    prompt = f"""
    Compare CV with Job Description. Return JSON: {{"score": 0-100, "summary": "brief description"}}
    JD: {jd}
    CV: {cv_text}
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"score": 0, "summary": "Error in AI analysis"}