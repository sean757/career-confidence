from openai import OpenAI
from functions import extract_text
client = OpenAI(api_key='')

def reformat(cv, jobdesc):
    Resume_Content = extract_text(cv)
    Job_Description_Content = extract_text(jobdesc)

    reformat = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages = [
            {"role": "system", "content": "You are a highly knowledgeable assistant capable of comparing a resume with a job description and giving advice on how to improve the CV to better match the job requirements."},
            {"role": "user", "content": f"CV: \n{Resume_Content}"},
            {"role": "user", "content": f"Job Description: \n{Job_Description_Content}"},
            {"role": "user", "content": "Looking at resume and job description, please reformat the given resume to tailor it to the job description. Only respond with the reformat, no additional text."}
        ]
    )

    output = reformat.choices[0].message.content
    return output
