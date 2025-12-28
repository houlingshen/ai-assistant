# API Reference

<cite>
**Referenced Files in This Document**   
- [IpcChannel.ts](file://frontend/packages/shared/IpcChannel.ts)
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py)
- [completions.py](file://opencontext/server/routes/completions.py)
- [context.py](file://opencontext/server/routes/context.py)
- [health.py](file://opencontext/server/routes/health.py)
- [conversation.py](file://opencontext/server/routes/conversation.py)
- [messages.py](file://opencontext/server/routes/messages.py)
- [auth.py](file://opencontext/server/middleware/auth.py)
- [context.py](file://opencontext/models/context.py)
- [enums.py](file://opencontext/models/enums.py)
- [config.yaml](file://config/config.yaml)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [RESTful API Endpoints](#restful-api-endpoints)
3. [IPC Communication Channels](#ipc-communication-channels)
4. [Data Structures](#data-structures)
5. [Authentication and Security](#authentication-and-security)
6. [Error Handling](#error-handling)
7. [Client Implementation Guidelines](#client-implementation-guidelines)
8. [Usage Examples](#usage-examples)

## Introduction
The MineContext application provides a comprehensive API for interacting with its intelligent context management system. This API reference documents the public interfaces for both RESTful HTTP endpoints and IPC (Inter-Process Communication) channels. The API enables clients to perform agent chat operations, content completions, context management, and health checks. The system is designed to support both frontend applications and external clients, with a focus on secure, efficient communication between components.

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L1-L367)
- [IpcChannel.ts](file://frontend/packages/shared/IpcChannel.ts#L1-L349)

## RESTful API Endpoints

### Agent Chat API
The Agent Chat API provides intelligent conversation capabilities through the Context Agent system. It supports both synchronous and streaming responses for interactive chat experiences.

#### Chat Endpoint
- **URL**: `/api/agent/chat`
- **Method**: `POST`
- **Description**: Process a user query and return a chat response
- **Request Body**:
  ```json
  {
    "query": "string",
    "context": "object",
    "session_id": "string",
    "user_id": "string",
    "conversation_id": "integer"
  }
  ```
- **Response**:
  ```json
  {
    "success": "boolean",
    "workflow_id": "string",
    "stage": "string",
    "query": "string",
    "intent": "object",
    "context": "object",
    "execution": "object",
    "reflection": "object",
    "errors": "array"
  }
  ```

#### Streaming Chat Endpoint
- **URL**: `/api/agent/chat/stream`
- **Method**: `POST`
- **Description**: Process a user query with streaming response for real-time updates
- **Request Body**: Same as Chat Endpoint
- **Response**: Server-Sent Events (SSE) stream with JSON events containing:
  - `session_start`: Initial event with session information
  - `thinking`: Intermediate reasoning steps
  - `stream_chunk`: Partial response content
  - `completed`: Final response with full result
  - `error`: Error information if processing fails

#### Workflow Management Endpoints
- **Resume Workflow**: `POST /api/agent/resume/{workflow_id}` - Resume a paused workflow with user input
- **Get Workflow State**: `GET /api/agent/state/{workflow_id}` - Retrieve the current state of a workflow
- **Cancel Workflow**: `DELETE /api/agent/cancel/{workflow_id}` - Cancel an active workflow
- **Test Agent**: `GET /api/agent/test` - Test if the Context Agent is functioning properly

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L79-L367)

### Completions API
The Completions API provides GitHub Copilot-like functionality for intelligent content completion in documents and notes.

#### Suggest Completions
- **URL**: `/api/completions/suggest`
- **Method**: `POST`
- **Description**: Get intelligent completion suggestions for current document content
- **Request Body**:
  ```json
  {
    "text": "string",
    "cursor_position": "integer",
    "document_id": "integer",
    "completion_types": "array",
    "max_suggestions": "integer",
    "context": "object"
  }
  ```
- **Response**:
  ```json
  {
    "success": "boolean",
    "suggestions": "array",
    "processing_time_ms": "number",
    "cache_hit": "boolean",
    "timestamp": "string"
  }
  ```

#### Stream Completions
- **URL**: `/api/completions/suggest/stream`
- **Method**: `POST`
- **Description**: Stream completion suggestions for real-time display
- **Response**: SSE stream with events for:
  - `start`: Stream initialization
  - `processing`: Status updates for different completion types
  - `suggestion`: Individual completion suggestions
  - `complete`: Stream completion with total count

#### Additional Completion Endpoints
- **Submit Feedback**: `POST /api/completions/feedback` - Submit user feedback on completion suggestions
- **Get Statistics**: `GET /api/completions/stats` - Retrieve completion service statistics
- **Cache Operations**: 
  - `GET /api/completions/cache/stats` - Get cache statistics
  - `POST /api/completions/cache/optimize` - Optimize cache performance
  - `POST /api/completions/cache/clear` - Clear the completion cache
- **Precompute Context**: `POST /api/completions/precompute/{document_id}` - Precompute context for a document

**Section sources**
- [completions.py](file://opencontext/server/routes/completions.py#L57-L329)

### Context Operations API
The Context API manages processed context data, including retrieval, search, and deletion operations.

#### Vector Search
- **URL**: `/api/vector_search`
- **Method**: `POST`
- **Description**: Search the vector database directly without LLM processing
- **Request Body**:
  ```json
  {
    "query": "string",
    "top_k": "integer",
    "context_types": "array",
    "filters": "object"
  }
  ```
- **Response**: Search results with processed context data and metadata

#### Context Management
- **Get Context Types**: `GET /api/context_types` - Retrieve all available context types
- **Get Context Detail**: `POST /contexts/detail` - Retrieve detailed information about a specific context
- **Delete Context**: `POST /contexts/delete` - Delete a processed context by ID and type

**Section sources**
- [context.py](file://opencontext/server/routes/context.py#L69-L146)

### Health Check API
The Health API provides endpoints for monitoring system status and authentication configuration.

#### Health Endpoints
- **Basic Health Check**: `GET /health` - Simple health check returning service status
- **Detailed Health Check**: `GET /api/health` - Comprehensive health check with component status
- **Authentication Status**: `GET /api/auth/status` - Check if API authentication is enabled

**Section sources**
- [health.py](file://opencontext/server/routes/health.py#L19-L47)

### Conversation Management API
The Conversation API handles CRUD operations for chat conversations and their messages.

#### Conversation Endpoints
- **Create Conversation**: `POST /api/agent/chat/conversations` - Create a new conversation
- **Get Conversation List**: `GET /api/agent/chat/conversations/list` - Retrieve a paginated list of conversations
- **Get Conversation Detail**: `GET /api/agent/chat/conversations/{cid}` - Retrieve details of a specific conversation
- **Update Conversation Title**: `PATCH /api/agent/chat/conversations/{cid}/update` - Update a conversation's title
- **Delete Conversation**: `DELETE /api/agent/chat/conversations/{cid}/update` - Soft delete a conversation

#### Message Endpoints
- **Create Message**: `POST /api/agent/chat/message/{mid}/create` - Create a new message in a conversation
- **Create Streaming Message**: `POST /api/agent/chat/message/stream/{mid}/create` - Create a placeholder for streaming messages
- **Update Message**: `POST /api/agent/chat/message/{mid}/update` - Update an existing message's content
- **Append Message Content**: `POST /api/agent/chat/message/{mid}/append` - Append content to a message (for streaming)
- **Mark Message Finished**: `POST /api/agent/chat/message/{mid}/finished` - Mark a message as complete
- **Get Conversation Messages**: `GET /api/agent/chat/conversations/{cid}/messages` - Retrieve all messages for a conversation
- **Interrupt Message**: `POST /api/agent/chat/messages/{mid}/interrupt` - Interrupt ongoing message generation

**Section sources**
- [conversation.py](file://opencontext/server/routes/conversation.py#L77-L234)
- [messages.py](file://opencontext/server/routes/messages.py#L102-L316)

## IPC Communication Channels
The IPC (Inter-Process Communication) system enables communication between the frontend and backend processes in the MineContext application. These channels are defined in the IpcChannel enum and support various request/response patterns and event types.

### Application Management Channels
- `app:get-cache-size`: Retrieve current cache size
- `app:clear-cache`: Clear application cache
- `app:set-launch-on-boot`: Configure launch on system boot
- `app:set-language`: Set application language
- `app:check-for-update`: Check for application updates
- `app:download-update`: Download available updates
- `app:quit-and-install`: Quit and install downloaded update
- `app:reload`: Reload the application

### System and UI Channels
- `tray:update-recording-status`: Update recording status in system tray
- `tray:show`: Show system tray icon
- `tray:hide`: Hide system tray icon
- `app:set-theme`: Set application theme
- `app:set-tray-on-close`: Configure tray behavior on close
- `window:resize`: Resize application window
- `window:get-size`: Get current window size

### File and Storage Channels
- `file:open`: Open a file
- `file:save`: Save a file
- `file:select`: Select a file
- `file:upload`: Upload a file
- `file:delete`: Delete a file
- `file:read`: Read file content
- `file-service:upload`: Upload file through file service
- `file-service:list`: List available files
- `file-service:delete`: Delete a file through file service
- `file-service:retrieve`: Retrieve a file

### Database Operations
- `database:get-all-vaults`: Retrieve all vaults
- `database:get-vaults-by-parent-id`: Get vaults by parent ID
- `database:get-vault-by-id`: Get vault by ID
- `database:insert-vault`: Insert a new vault
- `database:update-vault-by-id`: Update vault by ID
- `database:delete-vault-by-id`: Delete vault by ID
- `database:get-all-activities`: Retrieve all activities
- `database:get-new-activities`: Get new activities
- `database:get-latest-activity`: Get the latest activity
- `database:get-all-tasks`: Retrieve all tasks
- `database:add-task`: Add a new task
- `database:update-task`: Update a task
- `database:delete-task`: Delete a task

### Event Channels
- `backup-progress`: Backup progress updates
- `theme:updated`: Theme change notifications
- `update-available`: Update availability notifications
- `download-progress`: Download progress updates
- `redux-state-change`: Redux store state changes
- `store-sync:subscribe`: Subscribe to store synchronization
- `store-sync:unsubscribe`: Unsubscribe from store synchronization
- `store-sync:on-update`: Store update notifications

**Section sources**
- [IpcChannel.ts](file://frontend/packages/shared/IpcChannel.ts#L4-L348)

## Data Structures

### RawContextProperties
The RawContextProperties model represents the raw properties of context data captured from various sources.

**Properties**:
- `content_format`: Content format (text, image, file)
- `source`: Source of the context (screenshot, vault, local_file, web_link, input)
- `create_time`: Timestamp when the context was created
- `object_id`: Unique identifier for the context object
- `content_path`: File path for non-text content
- `content_type`: MIME type of the content
- `content_text`: Text content for text-based contexts
- `filter_path`: Path used for filtering
- `additional_info`: Additional metadata as key-value pairs
- `enable_merge`: Flag indicating if context can be merged

**Section sources**
- [context.py](file://opencontext/models/context.py#L35-L46)

### ProcessedContext
The ProcessedContext model represents context data after processing, enrichment, and vectorization.

**Properties**:
- `id`: Unique identifier for the processed context
- `properties`: ContextProperties object containing metadata and processing information
- `extracted_data`: ExtractedData object with title, summary, keywords, and entities
- `vectorize`: Vectorize object containing embedding vector and content information
- `metadata`: Additional structured metadata for the context

The ProcessedContext model includes methods for:
- Converting to dictionary format (`to_dict`)
- Converting to JSON string (`dump_json`)
- Creating from dictionary (`from_dict`)
- Creating from JSON string (`from_json`)
- Getting vectorization content (`get_vectorize_content`)
- Getting LLM context string (`get_llm_context_string`)

**Section sources**
- [context.py](file://opencontext/models/context.py#L131-L183)

### Context Types
The ContextType enumeration defines different types of knowledge and information that can be classified in the system:

- `ENTITY_CONTEXT`: Entity profile information management
- `ACTIVITY_CONTEXT`: Behavioral activity history records
- `INTENT_CONTEXT`: Intent planning and goal information
- `SEMANTIC_CONTEXT`: Semantic knowledge and conceptual information
- `PROCEDURAL_CONTEXT`: Procedural methods and operational guides
- `STATE_CONTEXT`: Status monitoring and progress information
- `KNOWLEDGE_CONTEXT`: File context and document knowledge

Each context type has associated descriptions, key indicators, and examples that help the system classify and process different types of information appropriately.

**Section sources**
- [enums.py](file://opencontext/models/enums.py#L84-L247)

## Authentication and Security

### API Authentication
The MineContext API supports API key-based authentication, which can be enabled or disabled in the configuration.

#### Authentication Configuration
Authentication settings are defined in the `config.yaml` file under the `api_auth` section:

```yaml
api_auth:
  enabled: false
  api_keys:
    - "${CONTEXT_API_KEY:test}"
  excluded_paths:
    - "/health"
    - "/api/health"
    - "/api/auth/status"
    - "/"
    - "/static/*"
    - "/contexts"
    - "/vector_search"
    - "/debug"
    - "/chat"
    - "/advanced_chat"
    - "/monitoring"
    - "/assistant"
    - "/vaults"
```

#### Authentication Mechanism
- **Enabled**: When `api_auth.enabled` is set to `true`, API key authentication is required
- **Disabled**: When set to `false`, authentication is disabled (default for development)
- **API Keys**: Valid API keys are specified in the `api_keys` list
- **Excluded Paths**: Certain paths are excluded from authentication requirements

#### Authentication Methods
Clients can provide the API key through:
- **Header**: `X-API-Key: <api_key_value>`
- **Query Parameter**: `?api_key=<api_key_value>`

The authentication middleware processes requests by:
1. Checking if authentication is enabled
2. Verifying if the requested path is excluded from authentication
3. Extracting the API key from header or query parameter
4. Validating the API key against the configured list
5. Rejecting requests with invalid or missing API keys

**Section sources**
- [auth.py](file://opencontext/server/middleware/auth.py#L1-L113)
- [config.yaml](file://config/config.yaml#L192-L211)

### Security Considerations
When implementing API clients, consider the following security best practices:

1. **API Key Management**: Store API keys securely and never expose them in client-side code
2. **HTTPS**: Always use HTTPS when communicating with the API in production environments
3. **Rate Limiting**: Implement rate limiting on client applications to prevent abuse
4. **Input Validation**: Validate all inputs before sending to the API to prevent injection attacks
5. **Error Handling**: Avoid exposing sensitive information in error messages
6. **Session Management**: Implement proper session management for authenticated sessions

**Section sources**
- [auth.py](file://opencontext/server/middleware/auth.py#L1-L113)

## Error Handling

### HTTP Error Responses
The API follows standard HTTP status codes for error responses:

- **400 Bad Request**: Invalid request parameters or malformed JSON
- **401 Unauthorized**: Authentication required or invalid credentials
- **404 Not Found**: Requested resource not found
- **500 Internal Server Error**: Server-side error during processing
- **503 Service Unavailable**: Service is temporarily unavailable

Error responses include a JSON body with error details:
```json
{
  "success": false,
  "error": "Error description",
  "code": "HTTP status code"
}
```

### Specific Error Scenarios
#### Authentication Errors
- **Missing API Key**: Returns 401 with message "API key required"
- **Invalid API Key**: Returns 401 with message "Invalid API key"
- **No Configured Keys**: Returns 500 with message "Server configuration error: No API keys configured"

#### Validation Errors
- **Invalid Parameters**: Returns 400 with specific validation error
- **Missing Required Fields**: Returns 400 with field-specific error
- **Invalid Enum Values**: Returns 400 with valid options

#### Processing Errors
- **Database Errors**: Returns 500 with database-specific error
- **LLM Processing Errors**: Returns 500 with processing error details
- **Vector Database Errors**: Returns 500 with search-specific error

### Client Error Handling Strategies
1. **Retry Logic**: Implement exponential backoff for transient errors (5xx)
2. **Graceful Degradation**: Provide fallback functionality when API is unavailable
3. **User Feedback**: Display meaningful error messages to users
4. **Logging**: Log errors for debugging and monitoring
5. **Circuit Breaker**: Implement circuit breaker pattern for repeated failures

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L113-L115)
- [completions.py](file://opencontext/server/routes/completions.py#L119-L131)
- [context.py](file://opencontext/server/routes/context.py#L77-L78)
- [health.py](file://opencontext/server/routes/health.py#L39-L40)

## Client Implementation Guidelines

### REST API Client
When implementing a REST API client for MineContext, follow these guidelines:

#### Base Configuration
- **Base URL**: `http://127.0.0.1:1733` (configurable in `config.yaml`)
- **Content-Type**: `application/json`
- **Accept**: `application/json`

#### Authentication
```javascript
// Using API key in header
headers: {
  'X-API-Key': 'your-api-key-here'
}

// Or using query parameter
url: '/api/agent/chat?api_key=your-api-key-here'
```

#### Streaming Response Handling
For endpoints that return Server-Sent Events (SSE):
1. Use `text/event-stream` as the response type
2. Parse each line prefixed with `data: `
3. Handle different event types appropriately
4. Implement reconnection logic for dropped connections

#### Rate Limiting Considerations
- Implement client-side rate limiting to avoid overwhelming the server
- Use exponential backoff for retrying failed requests
- Cache responses when appropriate to reduce API calls

### IPC Client Implementation
For Electron-based applications using IPC channels:

#### Request/Response Pattern
```typescript
// Send request and await response
const result = await ipcRenderer.invoke(channel, data);

// Handle the response
if (result.success) {
  // Process successful response
} else {
  // Handle error
}
```

#### Event Subscription Pattern
```typescript
// Subscribe to events
ipcRenderer.on(channel, (event, data) => {
  // Handle incoming event
});

// Unsubscribe when no longer needed
ipcRenderer.removeListener(channel, listener);
```

#### Error Handling
- Wrap IPC calls in try-catch blocks
- Handle cases where the main process is not available
- Implement timeout mechanisms for long-running operations

### Best Practices
1. **Connection Management**: Maintain persistent connections where possible
2. **Error Recovery**: Implement robust error recovery mechanisms
3. **Performance Monitoring**: Monitor API response times and throughput
4. **Security**: Follow security best practices for API key management
5. **Version Compatibility**: Handle API version changes gracefully

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L119-L290)
- [IpcChannel.ts](file://frontend/packages/shared/IpcChannel.ts#L4-L348)

## Usage Examples

### Agent Chat with Streaming
```javascript
// Example of streaming chat implementation
async function chatWithStreaming(query, sessionId) {
  const response = await fetch('/api/agent/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify({
      query: query,
      session_id: sessionId
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const eventData = line.slice(6);
        if (eventData === '[DONE]') continue;
        
        try {
          const event = JSON.parse(eventData);
          // Handle different event types
          switch (event.type) {
            case 'session_start':
              console.log('Session started:', event.session_id);
              break;
            case 'thinking':
              console.log('Thinking:', event.content);
              break;
            case 'stream_chunk':
              process.stdout.write(event.content);
              break;
            case 'completed':
              console.log('\nResponse completed');
              return event;
            case 'error':
              console.error('Error:', event.content);
              return null;
          }
        } catch (e) {
          console.error('Failed to parse event:', e);
        }
      }
    }
  }
}
```

### Vector Search Implementation
```javascript
// Example of vector search implementation
async function performVectorSearch(query, topK = 10) {
  const response = await fetch('/api/vector_search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify({
      query: query,
      top_k: topK,
      context_types: ['ACTIVITY_CONTEXT', 'SEMANTIC_CONTEXT']
    })
  });

  const result = await response.json();
  if (result.success) {
    return result.data.results;
  } else {
    throw new Error(result.message);
  }
}

// Usage
const results = await performVectorSearch('recent project activities');
console.log(`Found ${results.length} relevant contexts`);
```

### Completion Suggestions
```javascript
// Example of getting completion suggestions
async function getSuggestions(text, cursorPosition) {
  const response = await fetch('/api/completions/suggest', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify({
      text: text,
      cursor_position: cursorPosition,
      max_suggestions: 3
    })
  });

  const result = await response.json();
  if (result.success) {
    return result.suggestions;
  } else {
    console.error('Failed to get suggestions:', result.error);
    return [];
  }
}

// Usage
const suggestions = await getSuggestions('function calculate', 18);
suggestions.forEach(suggestion => {
  console.log(`- ${suggestion.text} (type: ${suggestion.completion_type})`);
});
```

### IPC Communication
```typescript
// Example of IPC communication in frontend
import { ipcRenderer } from 'electron';
import { IpcChannel } from '../packages/shared/IpcChannel';

// Get application information
async function getAppInfo() {
  try {
    const info = await ipcRenderer.invoke(IpcChannel.App_Info);
    return info;
  } catch (error) {
    console.error('Failed to get app info:', error);
    return null;
  }
}

// Subscribe to theme changes
function subscribeToThemeChanges(callback) {
  ipcRenderer.on('theme:updated', (event, theme) => {
    callback(theme);
  });
}

// Cleanup subscription
function unsubscribeFromThemeChanges(callback) {
  ipcRenderer.removeListener('theme:updated', callback);
}
```

**Section sources**
- [agent_chat.py](file://opencontext/server/routes/agent_chat.py#L119-L290)
- [completions.py](file://opencontext/server/routes/completions.py#L134-L202)
- [context.py](file://opencontext/server/routes/context.py#L117-L146)
- [IpcChannel.ts](file://frontend/packages/shared/IpcChannel.ts#L4-L348)