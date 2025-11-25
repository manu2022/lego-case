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
    if (!question.trim()) {
      setError('Please enter a question')
      return
    }

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      // Step 1: Call router for classification and PII redaction
      const routerFormData = new FormData()
      routerFormData.append('question', question)
      if (image) {
        routerFormData.append('image', image)
      }

      const routerRes = await fetch(`${API_URL}/router/ask`, {
        method: 'POST',
        body: routerFormData,
      })

      if (!routerRes.ok) {
        throw new Error(`Router error: ${routerRes.status} ${routerRes.statusText}`)
      }

      const routerData = await routerRes.json()
      const { sanitized_query, agent } = routerData

      // Step 2: Handle irrelevant queries
      if (agent === 'irrelevant') {
        setError('Sorry, I cannot assist with that query. Please ask work-related questions.')
        setLoading(false)
        return
      }

      // Step 3: Route to appropriate agent based on response
      let finalData: ApiResponse

      if (agent === 'multimodal_agent' && image) {
        // Call multimodal endpoint
        const multimodalFormData = new FormData()
        multimodalFormData.append('question', sanitized_query)
        multimodalFormData.append('image', image)

        const multimodalRes = await fetch(`${API_URL}/multimodal/ask-with-image`, {
          method: 'POST',
          body: multimodalFormData,
        })

        if (!multimodalRes.ok) {
          throw new Error(`Multimodal API error: ${multimodalRes.status}`)
        }

        finalData = await multimodalRes.json()
      } else {
        // Call text chat endpoint
        const chatRes = await fetch(`${API_URL}/chat/ask`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: sanitized_query }),
        })

        if (!chatRes.ok) {
          throw new Error(`Chat API error: ${chatRes.status}`)
        }

        finalData = await chatRes.json()
      }

      setResponse(finalData)
      
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

