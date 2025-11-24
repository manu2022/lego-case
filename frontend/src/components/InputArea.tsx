import type { FormEvent } from 'react'

interface InputAreaProps {
  imagePreview: string
  question: string
  loading: boolean
  hasImage: boolean
  onImageChange: (file: File | null) => void
  onRemoveImage: () => void
  onQuestionChange: (value: string) => void
  onSubmit: () => void
}

export const InputArea = ({
  imagePreview,
  question,
  loading,
  hasImage,
  onImageChange,
  onRemoveImage,
  onQuestionChange,
  onSubmit,
}: InputAreaProps) => {
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onSubmit()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    onImageChange(file || null)
  }

  return (
    <form onSubmit={handleSubmit} className="input-area">
      {imagePreview && (
        <div className="image-thumb">
          <img src={imagePreview} alt="Uploaded" />
          <button 
            type="button" 
            className="remove-image"
            onClick={onRemoveImage}
          >
            ×
          </button>
        </div>
      )}

      <div className="input-controls">
        <input
          id="image-upload"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        <label htmlFor="image-upload" className="attach-btn" title="Attach image">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
          </svg>
        </label>

        <input
          type="text"
          placeholder="Ask a question about your image..."
          value={question}
          onChange={(e) => onQuestionChange(e.target.value)}
          disabled={loading}
          className="text-input"
        />

        <button 
          type="submit" 
          disabled={loading || !hasImage || !question.trim()}
          className="send-btn"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </form>
  )
}

