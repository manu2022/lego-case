import { useImageQuestion } from './hooks/useImageQuestion'
import { ChatArea, InputArea } from './components'
import './App.css'

function App() {
  const {
    image,
    imagePreview,
    question,
    response,
    loading,
    error,
    fileName,
    setQuestion,
    handleImageChange,
    removeImage,
    submitQuestion,
  } = useImageQuestion()

  return (
    <div className="container">
      <ChatArea 
        response={response} 
        loading={loading} 
        error={error} 
      />
      
      <InputArea
        imagePreview={imagePreview}
        question={question}
        loading={loading}
        fileName={fileName}
        onImageChange={handleImageChange}
        onRemoveImage={removeImage}
        onQuestionChange={setQuestion}
        onSubmit={submitQuestion}
      />
    </div>
  )
}

export default App
