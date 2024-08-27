import io
import os
import re

from collections import defaultdict 
import nltk
import pandas as pd
from datetime import datetime
from dateutil import relativedelta
import stopwords as st
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

def extract_pdf_text(pdf_path):
    if not isinstance(pdf_path, io.BytesIO):
        with open(pdf_path, 'rb') as f:
            try:
                for page in PDFPage.get_pages(f,caching=True,check_extractable=True):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()
                    converter = TextConverter(resource_manager,fake_file_handle,laparams=LAParams())
                    page_interpreter = PDFPageInterpreter(resource_manager,converter)
                    page_interpreter.process_page(page)

                    text = fake_file_handle.getvalue()
                    yield text

                    converter.close()
                    fake_file_handle.close()
            except PDFSyntaxError:
                return
    else:
        try:
            for page in PDFPage.get_pages(pdf_path,caching=True,check_extractable=True):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager,fake_file_handle,laparams=LAParams())
                page_interpreter = PDFPageInterpreter(resource_manager,converter)
                page_interpreter.process_page(page)

                text = fake_file_handle.getvalue()
                yield text

                converter.close()
                fake_file_handle.close()
        except PDFSyntaxError:
            return


def extract_text(file_path):
    extension = os.path.splitext(file_path)[1]
    text = ''
    if extension == '.pdf':
        for page in extract_pdf_text(file_path):
            text += ' ' + page
        def prune_text(text):
            def replace_cid(match):
                ascii_num = int(match.group(1))
                try:
                    return chr(ascii_num)
                except:
                    return ''
                
            cid_pattern = re.compile(r'\(cid:(\d+)\)')
            pruned_text = re.sub(cid_pattern, replace_cid, text)
            return pruned_text
        text = prune_text(text)
    else:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            text = file.read()
    return text


def extract_entity_sections(text):
    text_split = [i.strip() for i in text.split('\n')]
    entities = {}
    key = None
    for phrase in text_split:
        if phrase.lower() in st.RESUME_SECTIONS:
            key = phrase.lower()
            entities[key] = []
        elif key and phrase.strip():
            entities[key].append(phrase)
    return entities

def remove_non_readable_chars(input_string):
    non_readable_regex = r'[\x00-\x1F\x7F]'
    cleaned_string = re.sub(non_readable_regex, '', input_string)

    return cleaned_string


def is_readable(word):
    allowed_chars_regex = r'^[a-zA-Z0-9\s.,;:!?\'\"-]+$'

    return re.match(allowed_chars_regex, word) is not None


def extract_tags_with_custom_model(custom_nlp_text):
    entities = defaultdict(list)
    current_entity = []
    current_tag = ""

    for token in custom_nlp_text:
        tag_type = token.tag_.split('-')[-1] if '-' in token.tag_ else token.tag_

        if is_readable(token.text):
            if token.tag_.startswith('B-'):
                if current_entity:
                    entities[current_tag].append(' '.join(current_entity))
                current_tag = tag_type
                current_entity = [token.text]
            elif token.tag_.startswith('I-'):
                if not current_entity:
                    current_tag = tag_type
                if tag_type == current_tag:
                    current_entity.append(token.text)
                else:
                    if current_entity:
                        entities[current_tag].append(' '.join(current_entity))
                        current_entity = [token.text]
                    current_tag = tag_type
            else:
                if current_entity:
                    entities[current_tag].append(' '.join(current_entity))
                    current_entity = []
                current_tag = ""
        else:
            if current_entity:
                entities[current_tag].append(' '.join(current_entity))
                current_entity = []
            current_tag = ""

    if current_entity:
        entities[current_tag].append(' '.join(current_entity))

    return dict(entities)

def extract_entities_with_custom_model(doc):
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities.keys():
            entities[ent.label_] = [ent.text]
        else:
            entities[ent.label_].append(ent.text)
    for key in entities.keys():
        entities[key] = list(set(entities[key]))
    return entities


def get_total_experience(experience_list):
    exp_ = []
    for line in experience_list:
        experience = re.search(r'(?P<fmonth>\w+.\d+)\s*(\D|to)\s*(?P<smonth>\w+.\d+|present)',line,re.I)
        if experience:
            exp_.append(experience.groups())
    total_exp = sum([get_number_of_months_from_dates(i[0], i[2]) for i in exp_])
    total_experience_in_months = total_exp
    return total_experience_in_months


def get_number_of_months_from_dates(date1, date2):
    if date2.lower() == 'present':
        date2 = datetime.now().strftime('%b %Y')
    try:
        if len(date1.split()[0]) > 3:
            date1 = date1.split()
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = date2.split()
            date2 = date2[0][:3] + ' ' + date2[1]
    except IndexError:
        return 0
    try:
        date1 = datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.strptime(str(date2), '%b %Y')
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience


def extract_entity_sections_professional(text):
    text_split = [i.strip() for i in text.split('\n')]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            key = phrase
        else:
            key = set(phrase.lower().split()) \
                    & set(st.RESUME_SECTIONS)
        try:
            key = list(key)[0]
        except IndexError:
            pass
        if key in st.RESUME_SECTIONS:
            entities[key] = []
            key = key
        elif key and phrase.strip():
            entities[key].append(phrase)
    return entities


def extract_email(text):
    email = re.findall(r'([^@|\s]+@[^@]+\.[^@|\s]+)', text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None


def extract_name(nlp_text, matcher):
    pattern = [st.NAME_PATTERN]

    matcher.add('NAME', pattern)

    matches = matcher(nlp_text)

    for _, start, end in matches:
        span = nlp_text[start:end]
        if 'name' not in span.text.lower():
            return span.text


def extract_mobile_number(text):
    mob_num_regex = r'(\(?\d{3}\)?[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)[-\.\s]*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
    phone = re.findall(re.compile(mob_num_regex), text)
    if phone:
        number = ''.join(phone[0])
        return number


def clean_skills(skills):
    skillset = []
    for skill in skills:
        skill = remove_non_readable_chars(skill.strip())
        if len(skill) > 0:
            skillset.append(skill)
    return skillset


def extract_skills_from_all(all_skills, noun_chunks):
    data = pd.read_csv(r'spaCy-training/skills.csv')
    skills = list(data.columns.values)
    skillset = []

    for skill in all_skills:
        tokens = skill.lower().split()
        for token in tokens:
            if token.lower() in skills:
                skillset.append(token)

    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)

    return [i.capitalize() for i in set([i.lower() for i in skillset])]


def extract_skills(nlp_text, noun_chunks):
    tokens = [token.text for token in nlp_text if not token.is_stop]
    data = pd.read_csv(r'spaCy-training/skills.csv')
    skills = list(data.columns.values)
    skillset = []
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]


def cleanup(token, lower=True):
    if lower:
        token = token.lower()
    return token.strip()


def extract_education(nlp_text):
    edu = {}
    try:
        for index, text in enumerate(nlp_text):
            for tex in text.split():
                tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                if tex.upper() in st.EDUCATION and tex not in st.STOPWORDS:
                    edu[tex] = text + nlp_text[index + 1]
    except IndexError:
        pass

    education = []
    for key in edu.keys():
        year = re.search(re.compile(st.YEAR), edu[key])
        if year:
            education.append((key, ''.join(year.group(0))))
        else:
            education.append(key)
    return education


def extract_experience(resume_text):
    wordnet_lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    word_tokens = nltk.word_tokenize(resume_text)

    filtered_sentence = [w for w in word_tokens if w not in stop_words and wordnet_lemmatizer.lemmatize(w) not in stop_words]
    sent = nltk.pos_tag(filtered_sentence)

    cp = nltk.RegexpParser('P: {<NNP>+}')
    parsed_sent = cp.parse(sent)
    test = []

    for i in list(parsed_sent.subtrees(filter=lambda x: x.label() == 'P')):
        if isinstance(i, nltk.Tree) and len(i) > 1:
            test.append(" ".join([leaf[0] for leaf in i.leaves() if len(i.leaves()) >= 2]))

    x = [x[x.lower().index('experience') + 10:] for x in test if x and 'experience' in x.lower()]
    return x


def extract_linkedin(text):
    linkedin_regex = r'(https?://[a-zA-Z0-9.-]+linkedin.com/in/[^ \s]+)'

    linkedin = re.findall(linkedin_regex, text)
    if linkedin:
        return linkedin[0]
    else:
        return None


def extract_years_of_experience(text):
    patterns = [
        r'(\d+)\s+years',
        r'(\d+)\s*-\s*(\d+)\s+years',
        r'minimum of\s*(\d+)', 
        r'at least\s*(\d+)',
        r'(\d+)\s+to\s+(\d+)\s+years',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) > 1:
                return f"{match.group(1)} to {match.group(2)} years"
            return f"{match.group(1)} years"
        
    return None