//Displays the details of the selected document
//Shows the title, extracted abstract, prediction results (and fallback text when appropriate)
export default function DocumentViewer({
  activeDoc,
  abstract,
  fallbackText,
  prediction,
  fieldPrediction,
}) {
  if (!activeDoc) { 
    return <h3 className="viewer-title" >Select a document</h3>; //Placeholder message before selecting a document
  } 

  return (
    <div className="viewer">
      <h3 className="viewer-title">{activeDoc}</h3> {/*Display the name*/}
      
      {/*Display the predicted discipline*/}
      {prediction && ( 
        <div className="prediction">
          <strong>Computer science discipline prediction:</strong>
          {/*Predicted label*/}
          <p className="prediction-main">
            {prediction.prediction}
          </p> 

          {/*Display list of probability scores*/}
          <ul>
            {Object.entries(prediction.probabilities).map( 
              ([label, prob]) =>(
                <li key={label}>
                  {label}: {(prob * 100).toFixed(1)}%
                </li>
              )
            )}
          </ul>
        </div>
      )}

      {/*Display the predicted field*/}
      {fieldPrediction && (
        <div className="prediction">
          <strong>Computer science field prediction:</strong>
          {/*Predicted label*/}
          <p className="prediction-main">
            {fieldPrediction.prediction}
          </p>

          {/*Display list of probability scores*/}
          <ul>
            {Object.entries(fieldPrediction.probabilities).map(
              ([label, prob]) => (
                <li key={label}>
                  {label}: {(prob * 100).toFixed(1)}%
                </li>
              )
            )}
          </ul>
        </div>
      )}

      {/* Container for the abstract or the fallback text*/}
      <div className="abstract-scroll"> 
        <div className="abstract">
          <strong>Abstract</strong>
          <p>{abstract}</p>
        </div>

        {/*Show fallback text if abstract was not found*/}
        {fallbackText && <pre>{fallbackText}</pre>}
      </div>
    </div>
  );
}
