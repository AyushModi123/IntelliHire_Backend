from PyPDF2 import PdfReader
from prompts import parse_resume_prompt, ResumeSchema
from utils.prompter import exec_prompt


class ResumeParser:
    def __init__(self, path):        
        self.reader = PdfReader(path)
        self.num_pages = len(self.reader.pages)
        self.context = self.reader.pages[0].extract_text() # 1 page resume current
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
        return links
    
    def get_profile_links(self):        
        linkedin = codeforces = codechef = leetcode = github = None
        for link in self.links:
            if 'linkedin' in link:
                linkedin = link
            elif 'github' in link:
                if github and len(github) > len(link):
                    github = link
                elif not github:
                    github = link
            elif 'codeforces' in link:
                codeforces = link
            elif 'codechef' in link:
                codechef = link  
            elif 'leetcode' in link:
                leetcode = link   
        return linkedin, github, leetcode, codechef, codeforces
    
    def parse_resume(self):
        if not self.context:
            return
        try:
            document = exec_prompt(output_schema=ResumeSchema, parse_prompt=parse_resume_prompt, input_data={'resume_text': self.context})
        except Exception as e:  
            print("ERROR:", e)
            return None
        return document