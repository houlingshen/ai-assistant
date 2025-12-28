# Agent Chat API

<cite>
**Referenced Files in This Document**   
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py)
- [schemas.py](file://opencontext/context_consumption/context_agent/models/schemas.py)
- [enums.py](file://opencontext/context_consumption/context_agent/models/enums.py)
- [events.py](file://opencontext/context_consumption/context_agent/models/events.py)
- [auth.py](file://opencontext/server/middleware/auth.py)
- [config.yaml](file://config/config.yaml)
- [ChatStreamService.ts](file://frontend/src/renderer/src/services/ChatStreamService.ts)
- [messages-service.ts](file://frontend/src/renderer/src/services/messages-service.ts)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [API Endpoint](#api-endpoint)
3. [Request Schema](#request-schema)
4. [Streaming Response Format](#streaming-response-format)
5. [Context Agent Integration](#context-agent-integration)
6. [Request Examples](#request-examples)
7. [Error Handling](#error-handling)
8. [Client Implementation Examples](#client-implementation-examples)
9. [Authentication and Rate Limiting](#authentication-and-rate-limiting)
10. [Conclusion](#conclusion)

## Introduction

The Agent Chat API provides an intelligent conversation interface that leverages the Context Agent system to deliver AI-powered responses with real-time streaming capabilities. This API enables applications to initiate AI conversations with users, incorporating rich context data to enhance response quality and relevance. The system supports both standard and streaming endpoints, with the streaming interface using Server-Sent Events (SSE) to deliver real-time chat updates as the AI generates responses.

The core functionality revolves around the Context Agent, which processes user queries through a multi-stage workflow that includes intent analysis, context gathering, execution, and reflection. This sophisticated processing pipeline allows the system to provide contextually aware responses that incorporate information from various sources, including document libraries, web searches, agent memory, and chat history.

This documentation focuses on the POST /api/agent/chat endpoint, detailing its request schema, streaming response format, integration with the context agent system, and practical implementation examples for client applications.

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L29-L367)
- [config.yaml](file://config/config.yaml#L192-L211)

## API Endpoint

The Agent Chat API provides a streaming endpoint for initiating AI conversations with real-time updates. The primary endpoint is:

**POST /api/agent/chat/stream**

This endpoint accepts a JSON payload containing the user query, context data, and configuration parameters, and returns a streaming response using the text/event-stream content type. The streaming nature of this endpoint allows clients to receive AI responses incrementally as they are generated, providing a more responsive and interactive user experience.

The endpoint is part of a FastAPI router with the prefix "/api/agent" and is tagged as "agent_chat". It requires authentication via API key, which can be provided in the X-API-Key header or as an api_key query parameter. The authentication middleware validates the provided key against a list of valid keys configured in the system.

In addition to the streaming endpoint, the API also provides several related endpoints for managing chat workflows:
- **POST /api/agent/chat**: Non-streaming version that returns a complete response
- **POST /api/agent/resume/{workflow_id}**: Resume a previously interrupted workflow
- **GET /api/agent/state/{workflow_id}**: Retrieve the current state of a workflow
- **DELETE /api/agent/cancel/{workflow_id}**: Cancel an active workflow

These endpoints work together to provide a comprehensive interface for managing AI conversations and their associated workflows.

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L80-L367)
- [auth.py](file://opencontext/server/middleware/auth.py#L68-L112)

## Request Schema

The POST /api/agent/chat/stream endpoint accepts a JSON request body that follows the ChatRequest schema defined in the agent_chat.py file. The request schema includes several key parameters that control the conversation flow and provide context for the AI response.

### Core Parameters

**query** (string, required): The user's input message or question. This is the primary content that the AI will respond to.

**context** (object, optional): A dictionary containing additional context information that should be incorporated into the AI's response. This can include various types of contextual data such as:
- Chat history
- Current document information
- Selected content
- Collected contexts from various sources

**session_id** (string, optional): A unique identifier for the conversation session. If not provided, the system will generate a UUID automatically.

**user_id** (string, optional): Identifier for the user initiating the conversation. This can be used for personalization and tracking user-specific context.

**conversation_id** (integer, optional): Identifier for the conversation thread. When provided, the system will save the user message and create a streaming assistant message in the conversation storage.

### Context Structure

The context object can contain several nested structures that provide rich information to the AI:

**chat_history**: An array of previous conversation messages, each with a role (user or assistant) and content.

**current_document**: Information about the currently active document, including ID, title, content, summary, and tags.

**selected_content**: Text that the user has selected or highlighted, which may be relevant to their query.

**collected_contexts**: An array of context items from various sources, each with a source identifier, content, relevance score, and metadata.

The request schema is defined using Pydantic's BaseModel, ensuring type safety and automatic validation of incoming requests. Invalid requests will result in appropriate HTTP error responses, typically 422 Unprocessable Entity for validation errors.

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L49-L57)
- [schemas.py](file://opencontext/context_consumption/context_agent/models/schemas.py#L120-L177)

## Streaming Response Format

The POST /api/agent/chat/stream endpoint returns responses using the text/event-stream media type, implementing the Server-Sent Events (SSE) protocol for real-time communication. This streaming format allows clients to receive AI responses incrementally as they are generated, providing immediate feedback and a more responsive user experience.

### Response Headers

The streaming response includes specific headers to ensure proper handling by clients:
- **Content-Type**: text/event-stream
- **Cache-Control**: no-cache
- **Connection**: keep-alive
- **X-Accel-Buffering**: no

These headers prevent caching and ensure the connection remains open for the duration of the streaming response.

### Event Structure

Each event in the stream is formatted as an SSE message with the following structure:
```
data: {"type": "event_type", "content": "event_content", ...}\n\n
```

The JSON payload contains various fields depending on the event type:
- **type**: The event type (e.g., "thinking", "stream_chunk", "completed")
- **content**: The main content of the event
- **stage**: The current workflow stage
- **progress**: A float value from 0.0 to 1.0 indicating progress
- **timestamp**: ISO format timestamp of the event
- **metadata**: Additional data specific to the event type

### Event Types

The streaming response includes several types of events that represent different stages of the AI processing workflow:

**session_start**: Sent at the beginning of the stream, containing the session_id and assistant_message_id.

**thinking**: Represents internal reasoning or processing steps, providing transparency into the AI's thought process.

**stream_chunk**: Contains a portion of the final response text, allowing incremental display to the user.

**completed**: Indicates the workflow has finished successfully, with the final response.

**failed**: Indicates the workflow encountered an error.

**interrupted**: Sent when the stream has been interrupted by the client.

The stream continues until a terminal event (completed, failed, or interrupted) is sent, at which point the connection is closed.

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L122-L290)
- [events.py](file://opencontext/context_consumption/context_agent/models/events.py#L16-L57)

## Context Agent Integration

The Agent Chat API is tightly integrated with the Context Agent system, which provides the underlying intelligence for processing user queries and generating responses. This integration enables the AI to leverage various types of contextual information to produce more relevant and personalized responses.

### Context Types

The Context Agent system supports multiple types of context, each serving a specific purpose in understanding and responding to user queries:

**Entity Context**: Manages profile information for various entities such as people, projects, teams, and organizations. This allows the AI to understand and reference specific entities in its responses.

**Activity Context**: Records behavioral activity history, including specific actions, completed tasks, and participated activities. This provides temporal context for understanding user behavior patterns.

**Intent Context**: Tracks forward-looking information such as future plans, goal setting, and action intentions. This helps the AI understand user objectives and provide goal-oriented responses.

**Semantic Context**: Contains knowledge concepts and technical principles, focusing on what the knowledge is rather than how it was obtained. This provides factual grounding for responses.

**Procedural Context**: Records user operation flows and task procedures based on temporal sequences, enabling the AI to understand and suggest workflows.

**State Context**: Monitors current status, progress tracking, and performance indicators, allowing the AI to provide status updates and progress reports.

### Workflow Stages

The Context Agent processes queries through a multi-stage workflow:

**Intent Analysis**: The system first analyzes the user's query to determine its type and intent, potentially enhancing or rewriting the query for better understanding.

**Context Gathering**: Relevant context is collected from various sources based on the identified intent, ensuring the AI has sufficient information to respond appropriately.

**Execution**: The AI generates its response, potentially performing actions like answering questions, editing documents, or creating new content.

**Reflection**: The system evaluates its own performance, assessing the success rate and identifying potential improvements for future interactions.

This staged approach ensures thorough processing of user queries while maintaining transparency about the AI's reasoning process.

**Section sources**
- [agent.py](file://opencontext/context_consumption/context_agent/agent.py#L24-L125)
- [enums.py](file://opencontext/context_consumption/context_agent/models/enums.py#L111-L142)
- [schemas.py](file://opencontext/context_consumption/context_agent/models/schemas.py#L120-L177)

## Request Examples

This section provides practical examples of request payloads for the Agent Chat API, demonstrating how to structure requests with conversation history, context data, and configuration parameters.

### Basic Chat Request

```json
{
  "query": "Hello, how are you today?",
  "session_id": "session_12345",
  "user_id": "user_67890"
}
```

This simple request initiates a conversation with a greeting. The system will generate a session_id if not provided and return a friendly response.

### Request with Conversation History

```json
{
  "query": "Can you summarize what we discussed earlier?",
  "context": {
    "chat_history": [
      {
        "role": "user",
        "content": "I'm working on a project about renewable energy"
      },
      {
        "role": "assistant",
        "content": "That sounds interesting. Renewable energy is an important field with solar, wind, and hydroelectric power being major components."
      },
      {
        "role": "user",
        "content": "Specifically, I'm focused on solar panel efficiency improvements"
      }
    ]
  },
  "session_id": "session_12345"
}
```

This request includes conversation history, allowing the AI to understand the context of the discussion and provide a relevant summary.

### Request with Document Context

```json
{
  "query": "What are the key points in this document?",
  "context": {
    "current_document": {
      "id": "doc_001",
      "title": "Solar Panel Efficiency Research",
      "content": "Recent advances in photovoltaic technology have significantly improved solar panel efficiency. Key developments include...",
      "summary": "Overview of recent advancements in solar panel efficiency with focus on photovoltaic technology improvements.",
      "tags": ["renewable energy", "solar power", "technology"]
    },
    "selected_content": "The new multi-junction cells have achieved 47.1% efficiency in laboratory conditions"
  },
  "session_id": "session_12345",
  "conversation_id": 1001
}
```

This request provides information about the current document and selected content, enabling the AI to focus its response on the relevant information.

### Request with Multiple Context Sources

```json
{
  "query": "Based on my recent activities and goals, what should I focus on next?",
  "context": {
    "chat_history": [
      {
        "role": "user",
        "content": "I want to improve my solar panel project"
      }
    ],
    "collected_contexts": [
      {
        "source": "document",
        "content": "Research paper on perovskite solar cells showing 25.5% efficiency",
        "relevance_score": 0.95
      },
      {
        "source": "web_search",
        "content": "Market report indicating growing demand for flexible solar panels",
        "relevance_score": 0.85
      },
      {
        "source": "activity_context",
        "content": "User spent 3 hours this week researching solar panel materials",
        "relevance_score": 0.9
      },
      {
        "source": "intent_context",
        "content": "User's goal: Increase solar panel efficiency by 15% in the next 6 months",
        "relevance_score": 1.0
      }
    ]
  },
  "session_id": "session_12345",
  "user_id": "user_67890",
  "conversation_id": 1001
}
```

This comprehensive request combines multiple context sources, allowing the AI to provide a well-informed recommendation based on the user's goals, recent activities, and relevant research.

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L49-L57)
- [schemas.py](file://opencontext/context_consumption/context_agent/models/schemas.py#L120-L177)

## Error Handling

The Agent Chat API implements comprehensive error handling to manage various failure scenarios and provide meaningful feedback to clients. Errors are communicated through appropriate HTTP status codes and descriptive error messages in the response body.

### HTTP Status Codes

The API uses standard HTTP status codes to indicate the result of requests:

**200 OK**: Successful response for non-streaming requests.

**206 Partial Content**: Used for streaming responses, indicating the stream is active.

**400 Bad Request**: The request was malformed or contained invalid parameters.

**401 Unauthorized**: Authentication failed due to missing or invalid API key.

**422 Unprocessable Entity**: The request was well-formed but contained semantic errors, such as invalid context data.

**500 Internal Server Error**: An unexpected error occurred on the server side.

### Error Response Format

For non-streaming requests, errors are returned as JSON objects:
```json
{
  "detail": "Error description"
}
```

For streaming requests, errors are sent as SSE events:
```
data: {"type": "error", "content": "Error description"}\n\n
```

### Common Error Scenarios

**Invalid Context Data**: When the context object contains malformed or unsupported data structures, the API returns a 422 Unprocessable Entity error with details about the specific validation failure.

**LLM Service Failures**: If the underlying language model service is unavailable or returns an error, the API captures this and returns a 500 Internal Server Error with details from the LLM service.

**Authentication Errors**: When authentication is enabled and the request lacks a valid API key, the API returns a 401 Unauthorized error with instructions for providing the key.

**Stream Interruption**: When a client interrupts a streaming request, the API sends an "interrupted" event and closes the connection gracefully.

The system also logs detailed error information for debugging purposes, while ensuring that sensitive information is not exposed in error responses.

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L113-L115)
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L260-L274)
- [auth.py](file://opencontext/server/middleware/auth.py#L89-L106)

## Client Implementation Examples

This section provides client implementation examples in JavaScript and Python, demonstrating how to establish and handle streaming responses from the Agent Chat API.

### JavaScript Implementation

```javascript
// ChatStreamService class for handling streaming chat requests
export class ChatStreamService {
  private abortController?: AbortController

  async sendStreamMessage(
    request: ChatStreamRequest,
    onEvent: (event: StreamEvent) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<void> {
    // Cancel any previous request
    this.abortStream()

    this.abortController = new AbortController()

    try {
      const baseUrl = axiosInstance.defaults.baseURL || 'http://127.0.0.1:1733'
      const response = await fetch(`${baseUrl}/api/agent/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request),
        signal: this.abortController.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Response body is not readable')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })

        // Handle multi-line data
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep the potentially incomplete last line

        for (const line of lines) {
          if (line.trim() === '') continue

          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6) // Remove 'data: ' prefix
              const eventData = JSON.parse(jsonStr)
              onEvent(eventData as StreamEvent)
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', line, parseError)
            }
          }
        }
      }

      onComplete?.()
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Stream request was aborted')
        return
      }

      console.error('Stream request failed:', error)
      onError?.(error as Error)
    } finally {
      this.abortController = undefined
    }
  }

  // Cancel the current streaming request
  abortStream(): void {
    if (this.abortController) {
      this.abortController.abort()
      this.abortController = undefined
    }
  }
}
```

### Python Implementation

```python
import asyncio
import json
from typing import Dict, Any, AsyncIterator
import aiohttp

class AgentChatClient:
    """Client for interacting with the Agent Chat API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1733", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
    
    async def _ensure_session(self):
        """Ensure the HTTP session is initialized"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def chat_stream(self, query: str, context: Dict[str, Any] = None, 
                         session_id: str = None, user_id: str = None) -> AsyncIterator[Dict[str, Any]]:
        """
        Send a streaming chat request and yield events as they arrive
        """
        await self._ensure_session()
        
        url = f"{self.base_url}/api/agent/chat/stream"
        
        payload = {
            "query": query,
            "context": context or {},
            "session_id": session_id,
            "user_id": user_id
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                
                # Process the streaming response
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data_json = line[6:]  # Remove 'data: ' prefix
                        if data_json != '[DONE]':
                            try:
                                event_data = json.loads(data_json)
                                yield event_data
                            except json.JSONDecodeError:
                                print(f"Failed to parse JSON: {data_json}")
                                
        except Exception as e:
            print(f"Stream request failed: {e}")
            raise
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# Example usage
async def main():
    async with AgentChatClient(api_key="your-api-key") as client:
        async for event in client.chat_stream(
            query="What are the benefits of solar energy?",
            context={
                "chat_history": [
                    {"role": "user", "content": "I'm researching renewable energy sources"}
                ]
            }
        ):
            print(f"Event: {event['type']}")
            if event['type'] == 'stream_chunk':
                print(f"Response chunk: {event['content']}")
            elif event['type'] == 'completed':
                print("Chat completed")

# Run the example
# asyncio.run(main())
```

These implementations demonstrate how to handle the streaming nature of the API, including proper connection management, event parsing, and error handling. The JavaScript example uses the Fetch API with a ReadableStream, while the Python example uses aiohttp for asynchronous HTTP requests.

**Section sources**
- [ChatStreamService.ts](file://frontend/src/renderer/src/services/ChatStreamService.ts#L91-L191)
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L122-L290)

## Authentication and Rate Limiting

The Agent Chat API implements authentication and rate limiting to ensure secure and fair usage of the service.

### Authentication

Authentication is controlled through the api_auth configuration in config.yaml. By default, authentication is disabled for development purposes, but it should be enabled in production environments.

When enabled, the API requires a valid API key for access, which can be provided in two ways:
- **Header**: X-API-Key: your_api_key_here
- **Query Parameter**: ?api_key=your_api_key_here

The valid API keys are configured in the api_auth.api_keys list in the configuration file. The system supports environment variable substitution, allowing keys to be set via environment variables for better security.

Certain paths are excluded from authentication, including health checks and static resources. These excluded paths are defined in the api_auth.excluded_paths list and support wildcard matching using fnmatch.

### Rate Limiting

While the provided code does not explicitly implement rate limiting, the architecture supports adding rate limiting middleware. Rate limiting would typically be implemented at the API gateway or reverse proxy level, or through additional middleware in the FastAPI application.

Recommended rate limiting strategies include:
- **Token Bucket Algorithm**: Allows bursts of requests while maintaining an average rate limit
- **Sliding Window Counter**: Provides more accurate rate limiting over time windows
- **Leaky Bucket Algorithm**: Smooths out request bursts

Rate limits should be configured based on the capacity of the underlying LLM services and the expected usage patterns of the application. Different limits may be applied to different user tiers or based on API key permissions.

The system logs authentication attempts and failures, which can be used for monitoring and detecting potential abuse. In production environments, these logs should be monitored and alerts configured for suspicious activity.

**Section sources**
- [auth.py](file://opencontext/server/middleware/auth.py#L68-L112)
- [config.yaml](file://config/config.yaml#L193-L211)

## Conclusion

The Agent Chat API provides a robust and flexible interface for integrating AI-powered conversations into applications. By leveraging the Context Agent system, the API delivers intelligent responses that incorporate rich contextual information from various sources, including conversation history, document content, user activities, and goals.

The streaming endpoint using Server-Sent Events enables real-time interaction, allowing clients to display responses incrementally as they are generated. This creates a more responsive and engaging user experience compared to traditional request-response patterns.

The API's comprehensive request schema supports complex use cases by allowing the inclusion of detailed context data, while the structured event format provides transparency into the AI's processing workflow. Error handling is robust, with appropriate HTTP status codes and descriptive messages for various failure scenarios.

Authentication is implemented through API keys, with configuration options for enabling or disabling authentication and specifying excluded paths. While rate limiting is not explicitly implemented in the provided code, the architecture supports adding such functionality as needed.

Client implementations in JavaScript and Python demonstrate how to establish and handle streaming connections, parse events, and manage connection lifecycle. These examples provide a solid foundation for integrating the Agent Chat API into various types of applications.

Overall, the Agent Chat API represents a sophisticated solution for AI-powered conversations, balancing advanced functionality with practical implementation considerations.

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L29-L367)
- [config.yaml](file://config/config.yaml#L192-L211)
- [auth.py](file://opencontext/server/middleware/auth.py#L68-L112)