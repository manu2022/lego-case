import type { ApiResponse } from '../types'

interface ChatAreaProps {
  response: ApiResponse | null
  loading: boolean
  error: string
}

export const ChatArea = ({ response, loading, error }: ChatAreaProps) => {
  return (
    <div className="chat-area">
      {response && (
        <>
          <div className="message user-message">
            <div className="user-content">
              {response.question}
            </div>
          </div>
          <div className="message assistant-message">
            <div className="message-content">
              <p>{response.answer}</p>
              <div className="token-info">
                {response.usage.total} tokens
              </div>
            </div>
          </div>
        </>
      )}

      {loading && (
        <div className="message assistant-message">
          <div className="typing">Analyzing...</div>
        </div>
      )}

      {error && (
        <div className="message error-message">
          {error}
        </div>
      )}
    </div>
  )
}

