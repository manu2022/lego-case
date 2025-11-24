export interface ApiResponse {
  question: string
  answer: string
  usage: {
    input: number
    output: number
    total: number
  }
}

