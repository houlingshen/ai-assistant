# Context Management Endpoints

<cite>
**Referenced Files in This Document**   
- [context.py](file://opencontext/server/routes/context.py)
- [context_operations.py](file://opencontext/server/context_operations.py)
- [opencontext.py](file://opencontext/server/opencontext.py)
- [context.py](file://opencontext/models/context.py)
- [enums.py](file://opencontext/models/enums.py)
- [global_storage.py](file://opencontext/storage/global_storage.py)
- [screen-monitor.tsx](file://frontend/src/renderer/src/pages/screen-monitor/screen-monitor.tsx)
- [home-page.tsx](file://frontend/src/renderer/src/pages/home/home-page.tsx)
- [use-screen.tsx](file://frontend/src/renderer/src/hooks/use-screen.tsx)
- [use-home-info.ts](file://frontend/src/renderer/src/hooks/use-home-info.ts)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Endpoints](#core-endpoints)
3. [Request/Response Schemas](#requestresponse-schemas)
4. [Context Data Model](#context-data-model)
5. [Source Type Filtering](#source-type-filtering)
6. [Integration with Processing Modules](#integration-with-processing-modules)
7. [Frontend Consumption](#frontend-consumption)
8. [Performance Considerations](#performance-considerations)

## Introduction
The Context Management API provides endpoints for retrieving, filtering, and managing captured user context data. This documentation details the endpoints that handle context data captured from various sources such as screenshots, documents, and web links. The API enables clients to retrieve context by time range, filter by source type, and manage context metadata. The system integrates with context_capture and context_processing modules to provide processed context data to the frontend components, particularly the ScreenMonitor and Home pages.

## Core Endpoints

The context management endpoints are implemented in the FastAPI application and provide comprehensive functionality for managing user context data. The primary endpoints include vector search, context type retrieval, and context deletion operations.

```mermaid
flowchart TD
A["Client Request"] --> B["Authentication"]
B --> C{"Endpoint Type"}
C --> |Vector Search| D["/api/vector_search"]
C --> |Context Types| E["/api/context_types"]
C --> |Context Detail| F["/contexts/detail"]
C --> |Context Delete| G["/contexts/delete"]
D --> H["Search Processing"]
E --> I["Type Retrieval"]
F --> J["Detail Retrieval"]
G --> K["Deletion Processing"]
H --> L["Return Results"]
I --> L
J --> L
K --> L
L --> M["Client Response"]
```

**Diagram sources**
- [context.py](file://opencontext/server/routes/context.py#L1-L146)

**Section sources**
- [context.py](file://opencontext/server/routes/context.py#L1-L146)

## Request/Response Schemas

The API endpoints use Pydantic models to define request and response schemas, ensuring type safety and proper validation. The schemas define the structure of data exchanged between the client and server.

```mermaid
classDiagram
class VectorSearchRequest {
+query : str
+top_k : int = 10
+context_types : Optional[List[str]]
+filters : Optional[Dict[str, Any]]
}
class ContextDetailRequest {
+id : str
+context_type : str
}
class QueryIn {
+query : str
}
class ConsumeIn {
+query : str
+context_ids : List[str]
}
class UpdateContextIn {
+title : Optional[str]
+summary : Optional[str]
+keywords : Optional[List[str]]
}
class ContextIn {
+source : ContextSource
+content_format : ContentFormat
+data : Any
+metadata : Optional[dict]
}
VectorSearchRequest --> QueryIn : "inherits"
ContextDetailRequest --> QueryIn : "inherits"
ConsumeIn --> QueryIn : "inherits"
UpdateContextIn --> QueryIn : "inherits"
ContextIn --> QueryIn : "inherits"
```

**Diagram sources**
- [context.py](file://opencontext/server/routes/context.py#L48-L67)

**Section sources**
- [context.py](file://opencontext/server/routes/context.py#L48-L67)

## Context Data Model

The context data model defines the structure of processed context data, including properties, extracted data, and vectorization information. The model supports various context types and metadata storage.

```mermaid
classDiagram
class ProcessedContext {
+id : str
+properties : ContextProperties
+extracted_data : ExtractedData
+vectorize : Vectorize
+metadata : Optional[Dict[str, Any]]
+get_vectorize_content() : str
+get_llm_context_string() : str
+to_dict() : Dict[str, Any]
+dump_json() : str
}
class ContextProperties {
+raw_properties : list[RawContextProperties]
+create_time : datetime.datetime
+event_time : datetime.datetime
+is_processed : bool
+has_compression : bool
+update_time : datetime.datetime
+call_count : int
+merge_count : int
+duration_count : int
+enable_merge : bool
+is_happend : bool
+last_call_time : Optional[datetime.datetime]
+file_path : Optional[str]
+raw_type : Optional[str]
+raw_id : Optional[str]
}
class ExtractedData {
+title : Optional[str]
+summary : Optional[str]
+keywords : List[str]
+entities : List[str]
+context_type : ContextType
+confidence : int
+importance : int
}
class Vectorize {
+content_format : ContentFormat
+image_path : Optional[str]
+text : Optional[str]
+vector : Optional[List[float]]
+get_vectorize_content() : str
}
class RawContextProperties {
+content_format : ContentFormat
+source : ContextSource
+create_time : datetime.datetime
+object_id : str
+content_path : Optional[str]
+content_type : Optional[str]
+content_text : Optional[str]
+filter_path : Optional[str]
+additional_info : Optional[Dict[str, Any]]
+enable_merge : bool
+to_dict() : Dict[str, Any]
}
ProcessedContext --> ContextProperties
ProcessedContext --> ExtractedData
ProcessedContext --> Vectorize
ProcessedContext --> RawContextProperties
ContextProperties --> RawContextProperties
```

**Diagram sources**
- [context.py](file://opencontext/models/context.py#L131-L343)

**Section sources**
- [context.py](file://opencontext/models/context.py#L131-L343)

## Source Type Filtering

The system supports filtering context data by source type, including screenshot, document, web link, and other sources. The ContextSource enumeration defines the available source types.

```mermaid
classDiagram
class ContextSource {
<<enumeration>>
SCREENSHOT
VAULT
LOCAL_FILE
WEB_LINK
INPUT
}
class ContentFormat {
<<enumeration>>
TEXT
IMAGE
FILE
}
class ContextType {
<<enumeration>>
ENTITY_CONTEXT
ACTIVITY_CONTEXT
INTENT_CONTEXT
SEMANTIC_CONTEXT
PROCEDURAL_CONTEXT
STATE_CONTEXT
KNOWLEDGE_CONTEXT
}
ContextSource --> ContentFormat
ContextSource --> ContextType
```

**Diagram sources**
- [enums.py](file://opencontext/models/enums.py#L15-L101)

**Section sources**
- [enums.py](file://opencontext/models/enums.py#L15-L101)

## Integration with Processing Modules

The context management endpoints integrate with the context_capture and context_processing modules to retrieve and process context data. The OpenContext class serves as the main entry point, coordinating between capture, processing, and storage components.

```mermaid
flowchart TD
A["Frontend Request"] --> B["API Endpoint"]
B --> C["OpenContext"]
C --> D["ContextCaptureManager"]
C --> E["ContextProcessorManager"]
C --> F["ContextOperations"]
C --> G["GlobalStorage"]
D --> H["Capture Components"]
E --> I["Processor Components"]
F --> J["Storage Operations"]
G --> K["UnifiedStorage"]
H --> L["RawContextProperties"]
I --> M["ProcessedContext"]
J --> N["Database"]
K --> N
M --> B
N --> B
```

**Diagram sources**
- [opencontext.py](file://opencontext/server/opencontext.py#L31-L300)
- [context_operations.py](file://opencontext/server/context_operations.py#L24-L224)

**Section sources**
- [opencontext.py](file://opencontext/server/opencontext.py#L31-L300)
- [context_operations.py](file://opencontext/server/context_operations.py#L24-L224)

## Frontend Consumption

The frontend components consume the context management API endpoints to display context data in the ScreenMonitor and Home pages. The React components use hooks to fetch and manage context data.

```mermaid
sequenceDiagram
participant ScreenMonitor as ScreenMonitor.tsx
participant UseScreen as use-screen.tsx
participant DBAPI as window.dbAPI
participant API as Context API
ScreenMonitor->>UseScreen : getActivitiesByDate(date)
UseScreen->>DBAPI : getNewActivities(start, end)
DBAPI->>API : GET /api/activities?start=...&end=...
API-->>DBAPI : Return activities
DBAPI-->>UseScreen : Return activities
UseScreen-->>ScreenMonitor : Return activities
ScreenMonitor->>ScreenMonitor : Update UI
Note over ScreenMonitor,DBAPI : Real-time activity polling for current day
ScreenMonitor->>UseScreen : getNewActivities(lastTime)
UseScreen->>DBAPI : getNewActivities(lastTime)
DBAPI->>API : GET /api/activities?since=...
API-->>DBAPI : Return new activities
DBAPI-->>UseScreen : Return new activities
UseScreen-->>ScreenMonitor : Add new activities
ScreenMonitor->>ScreenMonitor : Update UI
```

**Diagram sources**
- [screen-monitor.tsx](file://frontend/src/renderer/src/pages/screen-monitor/screen-monitor.tsx#L1-L575)
- [use-screen.tsx](file://frontend/src/renderer/src/hooks/use-screen.tsx#L1-L261)

**Section sources**
- [screen-monitor.tsx](file://frontend/src/renderer/src/pages/screen-monitor/screen-monitor.tsx#L1-L575)
- [use-screen.tsx](file://frontend/src/renderer/src/hooks/use-screen.tsx#L1-L261)

## Performance Considerations

The context management system implements several performance optimizations for handling large context datasets, including pagination, filtering, and efficient storage operations.

```mermaid
flowchart TD
A["Large Context Dataset"] --> B["Pagination"]
A --> C["Filtering"]
A --> D["Indexing"]
A --> E["Caching"]
B --> F["limit: int = 10"]
B --> G["offset: int = 0"]
C --> H["context_types: List[str]"]
C --> I["filters: Dict[str, Any]"]
D --> J["Vector Database Index"]
D --> K["Timestamp Index"]
E --> L["Processed Context Cache"]
E --> M["Query Result Cache"]
F --> N["API Response"]
G --> N
H --> N
I --> N
J --> N
K --> N
L --> N
M --> N
N --> O["Client"]
P["Performance Metrics"] --> Q["Response Time"]
P --> R["Memory Usage"]
P --> S["Database Load"]
Q --> T["Optimization Feedback"]
R --> T
S --> T
T --> U["System Tuning"]
```

**Diagram sources**
- [context_operations.py](file://opencontext/server/context_operations.py#L30-L44)
- [global_storage.py](file://opencontext/storage/global_storage.py#L1-L196)

**Section sources**
- [context_operations.py](file://opencontext/server/context_operations.py#L30-L44)
- [global_storage.py](file://opencontext/storage/global_storage.py#L1-L196)