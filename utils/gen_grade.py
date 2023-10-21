from PyPDF2 import PdfReader
import os
import openai
import ast
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


class data_extraction:
    def __init__(self, path):
        self.reader = PdfReader(path)
        self.num_pages = len(self.reader.pages)
        self.context = self.reader.pages[0].extract_text() # 1 page resume 
        self.grades = ['Very Bad', 'Bad', 'Moderate', 'Good', 'Very Good', 'Excellent']
        self.total_score = {'Education':0, 'Experience':self.grades[0], 'Skills':self.grades[0], 'Projects':self.grades[0], 'Achievements':self.grades[0], 'Coding Profile(s)':0, 'Test Score':0}  
        self.comp_dict = None
        self.links = self.extract_links()
    def extract_links(self):
        key = '/Annots'
        uri = '/URI'
        ank = '/A'
        links = []
        for page in self.reader.pages:
            pageObject = page.get_object()
            if pageObject[key]:
                ann = pageObject[key]
                for a in ann:
                    u = a.get_object()
                    if u[ank][uri]:
                        links.append(u[ank][uri])     
        gfg = cf = cc = lc = None
        for link in links:
            if 'geeksforgeeks' in link:
                gfg = link
            elif 'codeforces' in link:
                cf = link
            elif 'codechef' in link:
                cc = link  
            elif 'leetcode' in link:
                lc = link                          
        return gfg, cf, cc, lc                
    def education_grade(self):
        #Education Section
        college_score = self.comp_dict['Education']['Score']
        if float(college_score)<6.5:  ##Assuming CGPA
            self.total_score['Education'] = 0
            return
        college_name = self.comp_dict['Education']['Name'].lower()
        if 'iit' in college_name or 'nit' in college_name \
                or 'indian institute of technology' in college_name  or 'national institute of technology' in college_name:
            if float(college_score) >9.0:
                education_grade = 5
            else:
                education_grade = 4
        else:
            if float(college_score) >8.5:
                education_grade = 4
            else:
                education_grade = 3
        self.total_score['Education'] = education_grade
    def jd_comparator(self, jd):
        if not self.context:
            return
        model = 'gpt-3.5-turbo'
        prompt = f"Be unbiased. Given resume and job description, return a python dictionary conaining only College in resume and section-wise only grades(Very Bad, Bad, Moderate, Good, Very Good, Excellent) in resume according to requirements and qualifications of job description. Strictly follow this format 'Education: (Name:, Degree:, Score:Numeric value from resume), Experience:Grade, Projects:Grade, Skills:Grade, Achievements:Grade'. Return grade 'Very Bad' if None.Resume\n{self.context}. Job Description\n{jd}"
        try:
            response = openai.ChatCompletion.create(model=model,
                            messages=[{"role": "user", "content": prompt}])
        except Exception as e:  
            return e
        self.comp_dict = ast.literal_eval(response.choices[0].message.content)
    def output_grade(self):        
        self.education_grade()
        self.total_score['Experience'] = self.comp_dict['Experience']
        self.total_score['Projects'] = self.comp_dict['Projects']
        self.total_score['Skills'] = self.comp_dict['Skills']
        self.total_score['Achievements'] = self.comp_dict['Achievements']
        print(self.total_score)
        return self.total_score


if __name__ == '__main__':
    dt = data_extraction('Ayush_Modi_Resume_G.pdf')
    jd = '''Selected intern's day-to-day responsibilities include:

    1. Writing algorithms in Python (at an advanced level) for predictive healthcare
    2. Working on pre-processing data
    3. Testing various hypotheses using statistical measures
    4. Conducting scientific research
    5. Developing mathematical algorithms

    Additional Information:

    We are looking for exceptional interns with advanced programming skills and a good understanding of data science. In addition to the minimum assured stipend, the interns may also receive additional incentives of up to Rs. 2000 on the basis of their performance.'''
    print(dt.jd_comparator(jd))
    print(dt.output_grade())