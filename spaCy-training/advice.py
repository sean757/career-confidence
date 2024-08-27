from openai import OpenAI
from functions import extract_text
client = OpenAI(api_key='')

def is_text_file(path):
    return path.endswith('.txt')

def safe_extract_text(path):
    if is_text_file(path):
        return extract_text(path)
    else:
        return path

def advice(Resume, Job_Description):
    Resume_Content = safe_extract_text(Resume)
    Job_Description_Content = safe_extract_text(Job_Description)

    upload_files = [path for path in [Resume, Job_Description] if is_text_file(path)]

    file_ids = []
    for file_name in upload_files:
        with open(file_name, "rb") as file_data:
            file_response = client.files.create(file=file_data, purpose='assistants')
            file_ids.append(file_response.id)

    advice = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages = [
            {"role": "system", "content": "You are a highly knowledgeable assistant capable of comparing a resume with a job description and giving advice on how to improve the CV to better match the job requirements."},
            {"role": "user", "content": f"CV: \n{Resume_Content}"},
            {"role": "user", "content": f"Job Description: \n{Job_Description_Content}"},
            {"role": "user", "content": "Looking at resume and job description, give some advice on how the resume can be altered to more accurately match the job description."}
        ]
    )

    output = advice.choices[0].message.content
    return output