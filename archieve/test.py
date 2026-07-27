#Bug -1 : JavaScript is idetified as java
#Bug -2 : R language might be identifiend in any section 
#Bug -3 : C# is identified as c
#Bug -4 : C++ is identified as c
#Bug -5 : deeplearning is not identified as deep learning
#Bug -6 : Increase the skill set to include more skills and their variations
#Bug -7 : Language Go is identified everywhere
from extractor.processor import Processor

processor = Processor()

text = """
Skills:
Python
ReactJS
Docker

Projects:
Developed a REST API using Django and PostgreSQL.
Used Git and Docker for deployment.
"""

print("Resume Skills")
print("----------------")

skills = processor.get_resume_skills(text)

print(skills)

print("\nContext Skills")
print("----------------")

context = processor.get_skills_from_context(text)

print(context)