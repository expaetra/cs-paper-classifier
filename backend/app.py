#Backend API of the application using FastAPI
#Imports
from fastapi import FastAPI, UploadFile, File #Creates application & handles file uploads
from fastapi.middleware.cors import CORSMiddleware #Allows frontend communication with the backend
from fastapi.responses import Response #HTTP responses
from pathlib import Path
import shutil #Copy uploaded fiels to disk
import logging 

#Connect the API to the text & abstract extrraction logis and the classification model
from extraction import extract_text_from_pdf, extract_abstract
from model.classifier import CSClassifier 

#Logging to track uploaded files 
logging.basicConfig(
    level = logging.INFO,
    format= "%(asctime)s | %(levelname)s | %(message)s",  
)
logger = logging.getLogger(__name__)

#App and storage setup
app = FastAPI() 

UPLOAD_DIR = Path("uploads") #Store uploaded PDFs in the uploads/ folder
UPLOAD_DIR.mkdir(exist_ok=True) #Create if doesn't exist

#Load the model at startup
classifier = CSClassifier()
print("app.py loaded")
print("classifier instance created")

#---------- ROUTING ----------#
#Accept one or multipole PDFs, delete previously uplodaded PDFs and save new ones to disk
@app.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    for existing in UPLOAD_DIR.glob("*.pdf"): 
        existing.unlink() 

    saved=[] 
    for file in files:
        dest = UPLOAD_DIR / file.filename
        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved.append(file.filename) 

    logger.info(f"Uploaded files: {saved}")
    return {"uploaded": saved}


#Return the list of all uploaded PDF files
@app.get("/documents")
def documents():
    return {"documents": [f.name for f in UPLOAD_DIR.glob("*.pdf")]} 

#Extracts text, abstract, discipline prediction, & field prediction
@app.get("/document/{filename}")
def document(filename: str):
    print(f"Processing file: {filename}")
    path = UPLOAD_DIR / filename
    if not path.exists():
        return {"error": "not found"}

    full_text = extract_text_from_pdf(path) #Extract full text 

    abstract = extract_abstract(full_text[:6000]) #Extract abstract

    text_for_prediction = abstract or full_text[:2000] #Choose prediction: abstract or the fallback
    print("Text used for prediction:", text_for_prediction[:200])

    discipline_prediction = classifier.predict_discipline(text_for_prediction) #Predict the compSci discipline
    field_prediction = classifier.predict_field(text_for_prediction) #Predict the compSci field
    discipline_prediction = classifier.rerank_discipline_with_taxonomy(discipline_prediction, field_prediction)
    print("Discipline:", discipline_prediction)
    print("Field:", field_prediction)

    #Return results asn JSON
    return {
        "filename": filename,
        "abstract": abstract if abstract else "Abstract not found.",
        "abstract_source": "extraction.abstract" if abstract else "not_found", 
        "cs_discipline_prediction": discipline_prediction,
        "cs_field_prediction": field_prediction,
        "fallback_text": None if abstract else full_text[:6000], 
    } 

#Prevents favicon erors
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204) 

#---------- CORS --------#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)