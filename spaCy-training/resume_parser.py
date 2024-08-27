import spacy
from spacy.matcher import Matcher
import functions


def parser(resume):
    nlp = spacy.load('en_core_web_sm')

    custom_nlp = spacy.load(r'spaCy-training/output/res_model')
    matcher = Matcher(nlp.vocab)
    details = {
        'name': None,
        'email': None,
        'mobile_number': None,
        'location': None,
        'skills': None,
        'college_name': None,
        'degree': None,
        'designation': None,
        'experience': None,
        'company_names': None,
        'total_experience': None,
        'linkedin': None,
    }

    text_raw = functions.extract_text(resume)
    text = ' '.join(text_raw.split())
    nlp_text = nlp(text)
    custom_nlp_text = custom_nlp(text_raw)
    noun_chunks = list(nlp_text.noun_chunks)
    cust_ent = functions.extract_entities_with_custom_model(custom_nlp_text)
    entities = functions.extract_entity_sections(text_raw)
    

    try:
        details['name'] = functions.extract_name(nlp_text, matcher=matcher)
    except (IndexError, KeyError):
        details['name'] = functions.extract_name(nlp_text, matcher=matcher)

    details['email'] = functions.extract_email(text)
    details['mobile_number'] = functions.extract_mobile_number(text)
    details['skills'] = functions.extract_skills(nlp_text, noun_chunks)

    try:
        details['college_name'] = functions.extract_education(text_raw)
    except KeyError:
        pass

    try:
        details['degree'] = cust_ent['Degree']
    except KeyError:
        pass

    try:
        details['designation'] = cust_ent['Designation']
    except KeyError:
        pass

    try:
        details['company_names'] = cust_ent['Companies worked at']
    except KeyError:
        pass

    try:
        details['experience'] = functions.extract_experience(text_raw)
        try:
            exp = functions.extract_years_of_experience(text_raw)
            details['total_experience'] = exp
        except KeyError:
            details['total_experience'] = 0
    except KeyError:
        details['total_experience'] = 0

    details['linkedin'] = functions.extract_linkedin(text)

    return details