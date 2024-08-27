import spacy
import functions


def job_desc_details(jd):
    nlp = spacy.load('en_core_web_sm')
    custom_nlp = spacy.load(r'spaCy-training/output/jd_model')

    details = {
        'domain': None,
        'all_skills': None,
        'skills': None,
        'occupation': None,
        'location': None,
    }
    text_raw = functions.extract_text(jd)
    text = ' '.join(text_raw.split())
    nlp_text = nlp(text)
    custom_nlp_text = custom_nlp(text_raw)
    noun_chunks = list(nlp_text.noun_chunks)

    cust_tags = functions.extract_tags_with_custom_model(custom_nlp_text)
    all_skills = functions.clean_skills(cust_tags['SKILL'])
    skills = functions.extract_skills_from_all(all_skills, noun_chunks)
    
    if 'EXPERIENCE' in cust_tags and len(cust_tags['EXPERIENCE']) > 0:
        experience = functions.extract_years_of_experience(cust_tags['EXPERIENCE'][0])
    else:
        experience = None

    try:
        details['occupation'] = cust_tags['OCCUPATION'][0]
    except (IndexError, KeyError):
        details['occupation'] = None

    try:
        details['all_skills'] = all_skills
    except (IndexError, KeyError):
        details['all_skills'] = None

    details['experience'] = experience
    details['skills'] = skills
    details['domain'] = cust_tags['DOMAIN']

    return details