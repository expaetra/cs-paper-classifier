import { useEffect, useState } from "react";
import "./App.css";

//API helpers, communication with the backend
import {
  fetchDocuments, 
  uploadDocuments, 
  fetchDocument,
} from "./api/documents";


//Reusable UI componentes
import FileUploader from "./components/FileUploader"; 
import DocumentList from "./components/DocumentList";
import DocumentViewer from "./components/DocumentViewer";


//Main application
export default function App() {
  //State variables, store app data
  const [documents, setDocuments] = useState([]); //List of uploaded PDFs
  const [activeDoc, setActiveDoc] = useState(null);//Current document
  const [abstract, setAbstract] = useState(""); //Extracted abstract
  const [fallbackText, setFallbackText] = useState("");//Fa;;back text if abstract not availabe
  const [prediction, setPrediction] = useState(null); //Discipline prediction
  const [fieldPrediction, setFieldPrediction] = useState(null); //Field prediction

  //Load the document list when the application starts
  useEffect(() => {
    loadDocuments();
  }, []);

  //Fetch list of documents from the backend
  async function loadDocuments() {
    const docs = await fetchDocuments();
    setDocuments(docs); 
  }
  
  //Handle PDF file upload from the FileUploader 
  async function handleUpload(files) {
    await uploadDocuments(files);
    await loadDocuments();
  }

  //Open a document and feth the extracted data
  async function openDocument(name) {
    setActiveDoc(name); 
    setAbstract("Loading abstract... ");
    setFallbackText("");
    setPrediction(null);
    setFieldPrediction(null);

    const data = await fetchDocument(name);

    //Update state with the returned data
    setAbstract(data.abstract || "Abstract not found.");
    setFallbackText(data.fallback_text || "");
    setPrediction(data.cs_discipline_prediction || null);
    setFieldPrediction(data.cs_field_prediction || null);
  }

  return (
    <div className="container">
      <h1>NLP Classifier
      </h1>

      {/*Upload PDF files*/}
      <FileUploader onUpload={handleUpload} />

       {/*Sidebar with the uploaded documents */}
      <div className="layout">
        <DocumentList
          documents={documents}
          activeDoc={activeDoc}
          onSelect={openDocument}
        />

        {/*Field that shows abstract and prediction*/}
        <DocumentViewer
          activeDoc={activeDoc}
          abstract={abstract} 
          fallbackText={fallbackText}
          prediction={prediction}
          fieldPrediction={fieldPrediction}
        /> 
      </div>
    </div>
  );
};
