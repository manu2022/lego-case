import { useState } from 'react'
import type { ApiResponse } from '../types'
import { API_URL } from '../config'

export const useImageQuestion = () => {
  const [image, setImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string>('')
  const [question, setQuestion] = useState<string>('')
  const [response, setResponse] = useState<ApiResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const handleImageChange = (file: File | null) => {
    if (file) {
      setImage(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
      setError('')
    }
  }

  const removeImage = () => {
    setImage(null)
    setImagePreview('')
  }

  const submitQuestion = async () => {
    if (!image || !question.trim()) {
      setError('Please select an image and enter a question')
      return
    }

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      const formData = new FormData()
      formData.append('image', image)
      formData.append('question', question)

      const res = await fetch(`${API_URL}/multimodal/ask-with-image`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        throw new Error(`API error: ${res.status} ${res.statusText}`)
      }

      const data: ApiResponse = await res.json()
      setResponse(data)
      
      // Clear form after successful submission
      setQuestion('')
      setImage(null)
      setImagePreview('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer')
    } finally {
      setLoading(false)
    }
  }

  return {
    image,
    imagePreview,
    question,
    response,
    loading,
    error,
    setQuestion,
    handleImageChange,
    removeImage,
    submitQuestion,
  }
}

