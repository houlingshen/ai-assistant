# Screenshot Capture

<cite>
**Referenced Files in This Document**   
- [screenshot.py](file://opencontext/context_capture/screenshot.py)
- [base.py](file://opencontext/context_capture/base.py)
- [capture_interface.py](file://opencontext/interfaces/capture_interface.py)
- [context.py](file://opencontext/models/context.py)
- [image.py](file://opencontext/utils/image.py)
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py)
- [config.yaml](file://config/config.yaml)
- [get-capture-sources.ts](file://frontend/src/main/utils/get-capture-sources.ts)
- [ScreenshotService.ts](file://frontend/src/main/services/ScreenshotService.ts)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Components](#core-components)
3. [Architecture Overview](#architecture-overview)
4. [Detailed Component Analysis](#detailed-component-analysis)
5. [Configuration Options](#configuration-options)
6. [Metadata Population](#metadata-population)
7. [Common Issues and Solutions](#common-issues-and-solutions)
8. [Conclusion](#conclusion)

## Introduction
The Screenshot Capture component is a critical part of the OpenContext system, responsible for periodic and event-triggered capture of user screen activity. This component implements a robust screenshot capture system that handles multi-monitor environments, provides flexible configuration options, and integrates with downstream processing components to extract meaningful context from visual data. The system is designed to balance performance, privacy, and resource usage while providing comprehensive screen monitoring capabilities.

## Core Components

The screenshot capture functionality is implemented through several interconnected components that work together to capture, process, and analyze screen activity. The core of the system is the `ScreenshotCapture` class, which implements the `ICaptureComponent` interface and handles the actual screen capture operations. This component works in conjunction with the `ScreenshotProcessor` which analyzes captured images and extracts contextual information. The capture manager coordinates multiple capture components and ensures proper lifecycle management.

**Section sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L28-L508)
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py#L47-L590)
- [capture_interface.py](file://opencontext/interfaces/capture_interface.py#L18-L153)

## Architecture Overview

The screenshot capture system follows a modular architecture with clear separation of concerns between capture, processing, and storage components. The system is designed to be extensible and maintainable, with well-defined interfaces between components.

```mermaid
graph TD
A[ScreenshotCapture] --> |Captures| B[RawContextProperties]
B --> |Provides| C[ScreenshotProcessor]
C --> |Processes| D[ProcessedContext]
D --> |Stores| E[Storage Backend]
F[CaptureManager] --> |Controls| A
G[Configuration] --> |Configures| A
H[Frontend] --> |Triggers| A
A --> |Saves| I[Screenshot Files]
class A,B,C,D,E,F,G,H,I component;
style A fill:#4CAF50,stroke:#388E3C
style B fill:#2196F3,stroke:#1976D2
style C fill:#FF9800,stroke:#F57C00
style D fill:#9C27B0,stroke:#7B1FA2
style E fill:#607D8B,stroke:#455A64
style F fill:#00BCD4,stroke:#0097A7
style G fill:#8BC34A,stroke:#689F38
style H fill:#E91E63,stroke:#C2185B
style I fill:#FFEB3B,stroke:#FBC02D
```

**Diagram sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L28-L508)
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py#L47-L590)
- [context.py](file://opencontext/models/context.py#L35-L143)

## Detailed Component Analysis

### ScreenshotCapture Implementation

The `ScreenshotCapture` class implements the `ICaptureComponent` interface, providing a standardized way to manage the lifecycle and configuration of the screenshot capture functionality. The component follows a well-defined initialization, start/stop lifecycle, and capture execution pattern.

#### Initialization and Configuration
The component is initialized with default values and then configured through the `initialize` method, which validates and applies configuration parameters. The initialization process sets up the screenshot library (mss), configures image format and quality settings, and prepares the storage directory for saved screenshots.

```mermaid
classDiagram
class ICaptureComponent {
<<interface>>
+initialize(config) bool
+start() bool
+stop(graceful) bool
+is_running() bool
+capture() List[RawContextProperties]
+get_name() str
+get_description() str
+get_config_schema() Dict[str, Any]
+validate_config(config) bool
+get_status() Dict[str, Any]
+get_statistics() Dict[str, Any]
+reset_statistics() bool
+set_callback(callback) bool
}
class BaseCaptureComponent {
-_name str
-_description str
-_source_type ContextSource
-_config Dict[str, Any]
-_running bool
-_capture_thread Thread
-_stop_event Event
-_callback callable
-_capture_interval float
-_last_capture_time datetime
-_capture_count int
-_error_count int
-_last_error str
-_lock RLock
+initialize(config) bool
+start() bool
+stop(graceful) bool
+is_running() bool
+capture() List[RawContextProperties]
+get_name() str
+get_description() str
+get_config_schema() Dict[str, Any]
+validate_config(config) bool
+get_status() Dict[str, Any]
+get_statistics() Dict[str, Any]
+reset_statistics() bool
+set_callback(callback) bool
-_capture_loop() void
-_initialize_impl(config) bool
-_start_impl() bool
-_stop_impl(graceful) bool
-_capture_impl() List[RawContextProperties]
-_get_config_schema_impl() Dict[str, Any]
-_validate_config_impl(config) bool
-_get_status_impl() Dict[str, Any]
-_get_statistics_impl() Dict[str, Any]
-_reset_statistics_impl() void
}
class ScreenshotCapture {
-_screenshot_lib str
-_screenshot_count int
-_last_screenshot_path str
-_last_screenshot_time datetime
-_screenshot_format str
-_screenshot_quality int
-_screenshot_region tuple
-_save_screenshots bool
-_screenshot_dir str
-_dedup_enabled bool
-_last_screenshots Dict[str, tuple[Image, RawContextProperties]]
-_similarity_threshold int
-_max_image_size int
-_resize_quality int
-_lock RLock
+_initialize_impl(config) bool
+_start_impl() bool
+_stop_impl(graceful) bool
+_capture_impl() List[RawContextProperties]
+_get_config_schema_impl() Dict[str, Any]
+_validate_config_impl(config) bool
+_get_status_impl() Dict[str, Any]
+_get_statistics_impl() Dict[str, Any]
+_reset_statistics_impl() void
}
ICaptureComponent <|-- BaseCaptureComponent
BaseCaptureComponent <|-- ScreenshotCapture
```

**Diagram sources**
- [capture_interface.py](file://opencontext/interfaces/capture_interface.py#L18-L153)
- [base.py](file://opencontext/context_capture/base.py#L26-L515)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L28-L508)

#### Capture Execution
The capture process is executed through the `_capture_impl` method, which orchestrates the screenshot capture workflow. This method coordinates with the underlying screenshot library (mss) to capture screen regions, processes the captured images according to configuration settings, and creates `RawContextProperties` objects containing the captured data and metadata.

```mermaid
flowchart TD
Start([Start Capture]) --> CheckRunning{"Component Running?"}
CheckRunning --> |No| ReturnEmpty["Return Empty List"]
CheckRunning --> |Yes| TakeScreenshot["Take Screenshot"]
TakeScreenshot --> ProcessImage["Process Image Data"]
ProcessImage --> CreateContext["Create RawContextProperties"]
CreateContext --> UpdateCount["Increment Capture Count"]
UpdateCount --> UpdateTimestamp["Update Last Capture Time"]
UpdateTimestamp --> CheckCallback{"Callback Set?"}
CheckCallback --> |No| ReturnContexts["Return Contexts"]
CheckCallback --> |Yes| ExecuteCallback["Execute Callback"]
ExecuteCallback --> ReturnContexts
style Start fill:#4CAF50,stroke:#388E3C
style ReturnEmpty fill:#F44336,stroke:#D32F2F
style TakeScreenshot fill:#2196F3,stroke:#1976D2
style ProcessImage fill:#2196F3,stroke:#1976D2
style CreateContext fill:#2196F3,stroke:#1976D2
style UpdateCount fill:#2196F3,stroke:#1976D2
style UpdateTimestamp fill:#2196F3,stroke:#1976D2
style CheckCallback fill:#FF9800,stroke:#F57C00
style ExecuteCallback fill:#2196F3,stroke:#1976D2
style ReturnContexts fill:#4CAF50,stroke:#388E3C
```

**Diagram sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L217-L245)
- [base.py](file://opencontext/context_capture/base.py#L176-L220)

### Multi-Monitor and Region Handling

The screenshot capture component supports both full-screen capture across multiple monitors and selective region capture. When no specific region is configured, the component captures each monitor individually, allowing for proper handling of multi-monitor setups. The region selection is implemented through the `_screenshot_region` parameter, which defines the rectangular area to capture in terms of left, top, width, and height coordinates.

```mermaid
flowchart TD
Start["Start Screenshot Capture"] --> CheckRegion{"Region Configured?"}
CheckRegion --> |Yes| ConfigureRegion["Configure Capture Region"]
CheckRegion --> |No| GetMonitors["Get All Monitors"]
ConfigureRegion --> DefineMonitors["Define Single Monitor Region"]
GetMonitors --> DefineMonitors
DefineMonitors --> LoopMonitors["For Each Monitor"]
LoopMonitors --> CaptureMonitor["Capture Monitor"]
CaptureMonitor --> ConvertImage["Convert to PIL Image"]
ConvertImage --> CompressImage["Compress Image"]
CompressImage --> StoreDetails["Store Monitor Details"]
StoreDetails --> NextMonitor["Next Monitor?"]
NextMonitor --> |Yes| LoopMonitors
NextMonitor --> |No| Complete["Capture Complete"]
style Start fill:#4CAF50,stroke:#388E3C
style CheckRegion fill:#FF9800,stroke:#F57C00
style ConfigureRegion fill:#2196F3,stroke:#1976D2
style GetMonitors fill:#2196F3,stroke:#1976D2
style DefineMonitors fill:#2196F3,stroke:#1976D2
style LoopMonitors fill:#FF9800,stroke:#F57C00
style CaptureMonitor fill:#2196F3,stroke:#1976D2
style ConvertImage fill:#2196F3,stroke:#1976D2
style CompressImage fill:#2196F3,stroke:#1976D2
style StoreDetails fill:#2196F3,stroke:#1976D2
style NextMonitor fill:#FF9800,stroke:#F57C00
style Complete fill:#4CAF50,stroke:#388E3C
```

**Diagram sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L246-L295)
- [get-capture-sources.ts](file://frontend/src/main/utils/get-capture-sources.ts#L561-L579)

### Image Compression and Quality Settings

The component implements flexible image compression strategies to balance image quality with storage and performance requirements. The compression settings are configurable through the `screenshot_format`, `screenshot_quality`, `max_image_size`, and `resize_quality` parameters. The system supports PNG and JPEG/JPG formats, with quality settings specifically applicable to JPEG compression.

```mermaid
flowchart TD
Start["Start Image Processing"] --> CheckFormat{"Format is JPG/JPEG?"}
CheckFormat --> |Yes| SetJPEG["Set JPEG Compression"]
CheckFormat --> |No| SetPNG["Set PNG Compression"]
SetJPEG --> ApplyQuality["Apply Quality Setting"]
SetPNG --> OptimizePNG["Apply PNG Optimization"]
ApplyQuality --> ResizeCheck{"Resize Needed?"}
OptimizePNG --> ResizeCheck
ResizeCheck --> |Yes| ResizeImage["Resize Image"]
ResizeCheck --> |No| SaveImage["Save Image"]
ResizeImage --> SaveImage
SaveImage --> Complete["Processing Complete"]
style Start fill:#4CAF50,stroke:#388E3C
style CheckFormat fill:#FF9800,stroke:#F57C00
style SetJPEG fill:#2196F3,stroke:#1976D2
style SetPNG fill:#2196F3,stroke:#1976D2
style ApplyQuality fill:#2196F3,stroke:#1976D2
style OptimizePNG fill:#2196F3,stroke:#1976D2
style ResizeCheck fill:#FF9800,stroke:#F57C00
style ResizeImage fill:#2196F3,stroke:#1976D2
style SaveImage fill:#2196F3,stroke:#1976D2
style Complete fill:#4CAF50,stroke:#388E3C
```

**Diagram sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L280-L287)
- [image.py](file://opencontext/utils/image.py#L46-L62)

## Configuration Options

The screenshot capture component provides a comprehensive set of configuration options that allow users to customize its behavior according to their specific needs. These options are defined in the component's configuration schema and can be set through the system configuration file.

### Core Configuration Parameters

The following table outlines the key configuration options available for the screenshot capture component:

| Configuration Parameter | Type | Default Value | Description | Constraints |
|------------------------|------|---------------|-------------|-------------|
| capture_interval | number | 5.0 | Screenshot capture interval in seconds | Minimum: 0.1 |
| screenshot_format | string | "png" | Image format for captured screenshots | Enum: ["png", "jpg", "jpeg"] |
| screenshot_quality | integer | 80 | Image quality for JPEG/JPG format (1-100) | Range: 1-100 |
| screenshot_region | object | null | Specific screen region to capture | Must contain left, top, width, height |
| storage_path | string | "./screenshots" | Directory path for saving screenshots | Must be valid directory path |
| dedup_enabled | boolean | true | Enable screenshot deduplication | true/false |
| similarity_threshold | number | 98 | Image similarity threshold for deduplication (0-100) | Range: 0-100 |

**Section sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L300-L353)
- [config.yaml](file://config/config.yaml#L43-L47)

### Configuration Validation

The component implements robust configuration validation to ensure that all settings are valid before initialization. The validation process checks data types, value ranges, and required fields, providing clear error messages when invalid configurations are detected.

```mermaid
flowchart TD
Start["Validate Configuration"] --> CheckInterval{"capture_interval Present?"}
CheckInterval --> |Yes| ValidateInterval["Validate Interval Value"]
CheckInterval --> |No| SkipInterval["Use Default"]
ValidateInterval --> CheckFormat{"screenshot_format Present?"}
SkipInterval --> CheckFormat
CheckFormat --> |Yes| ValidateFormat["Validate Format Value"]
CheckFormat --> |No| SkipFormat["Use Default"]
ValidateFormat --> CheckQuality{"screenshot_quality Present?"}
SkipFormat --> CheckQuality
CheckQuality --> |Yes| ValidateQuality["Validate Quality Value"]
CheckQuality --> |No| SkipQuality["Use Default"]
ValidateQuality --> CheckRegion{"screenshot_region Present?"}
SkipQuality --> CheckRegion
CheckRegion --> |Yes| ValidateRegion["Validate Region Structure"]
CheckRegion --> |No| SkipRegion["Capture Full Screen"]
ValidateRegion --> CheckThreshold{"similarity_threshold Present?"}
SkipRegion --> CheckThreshold
CheckThreshold --> |Yes| ValidateThreshold["Validate Threshold Value"]
CheckThreshold --> |No| SkipThreshold["Use Default"]
ValidateThreshold --> Complete["Validation Complete"]
SkipThreshold --> Complete
style Start fill:#4CAF50,stroke:#388E3C
style CheckInterval fill:#FF9800,stroke:#F57C00
style ValidateInterval fill:#2196F3,stroke:#1976D2
style SkipInterval fill:#2196F3,stroke:#1976D2
style CheckFormat fill:#FF9800,stroke:#F57C00
style ValidateFormat fill:#2196F3,stroke:#1976D2
style SkipFormat fill:#2196F3,stroke:#1976D2
style CheckQuality fill:#FF9800,stroke:#F57C00
style ValidateQuality fill:#2196F3,stroke:#1976D2
style SkipQuality fill:#2196F3,stroke:#1976D2
style CheckRegion fill:#FF9800,stroke:#F57C00
style ValidateRegion fill:#2196F3,stroke:#1976D2
style SkipRegion fill:#2196F3,stroke:#1976D2
style CheckThreshold fill:#FF9800,stroke:#F57C00
style ValidateThreshold fill:#2196F3,stroke:#1976D2
style SkipThreshold fill:#2196F3,stroke:#1976D2
style Complete fill:#4CAF50,stroke:#388E3C
```

**Diagram sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L355-L454)

## Metadata Population

The screenshot capture component enriches each captured screenshot with comprehensive metadata that provides context about the capture event. This metadata is stored in the `additional_info` field of the `RawContextProperties` object and includes various details about the capture environment and settings.

### RawContextProperties Structure

The `RawContextProperties` class is used to encapsulate all information related to a captured screenshot. This includes the content format, source type, creation time, file path, and additional metadata specific to the screenshot capture.

```mermaid
classDiagram
class RawContextProperties {
+content_format ContentFormat
+source ContextSource
+create_time datetime
+object_id str
+content_path str
+content_type str
+content_text str
+filter_path str
+additional_info Dict[str, Any]
+enable_merge bool
+to_dict() Dict[str, Any]
+from_dict(data) RawContextProperties
}
class ContentFormat {
<<enumeration>>
TEXT
IMAGE
VIDEO
AUDIO
}
class ContextSource {
<<enumeration>>
SCREENSHOT
DOCUMENT
WEB_LINK
FOLDER_MONITOR
VAULT_DOCUMENT_MONITOR
}
RawContextProperties --> ContentFormat : "uses"
RawContextProperties --> ContextSource : "uses"
```

**Diagram sources**
- [context.py](file://opencontext/models/context.py#L35-L55)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L176-L216)

### Metadata Fields

The following metadata fields are populated for each captured screenshot:

| Metadata Field | Description | Example Value |
|---------------|-------------|---------------|
| format | Image format of the captured screenshot | "png" |
| timestamp | ISO formatted timestamp of capture | "2025-01-15T10:30:45.123456" |
| last_seen_timestamp | ISO formatted timestamp of last capture | "2025-01-15T10:30:45.123456" |
| lib | Screenshot library used for capture | "mss" |
| region | Capture region coordinates (if applicable) | {"left": 0, "top": 0, "width": 1920, "height": 1080} |
| screenshot_format | Configured screenshot format | "png" |
| screenshot_path | Absolute path to saved screenshot file | "/Users/username/screenshots/screenshot_monitor_1_20250115_103045_123456.png" |
| duration_count | Number of times this context has been captured | 1 |
| monitor | Monitor identifier for multi-monitor setups | "monitor_1" |
| coordinates | Monitor coordinates used for capture | {"left": 0, "top": 0, "width": 1920, "height": 1080} |

**Section sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L191-L207)
- [context.py](file://opencontext/models/context.py#L35-L55)

## Common Issues and Solutions

### Permission Errors on macOS

macOS implements strict privacy controls that require explicit user permission for screen recording. The system must handle these permissions gracefully and guide users through the process of granting the necessary access.

```mermaid
flowchart TD
Start["Attempt Screenshot"] --> CheckPermissions{"Has Screen Permission?"}
CheckPermissions --> |Yes| CaptureScreen["Capture Screen"]
CheckPermissions --> |No| RequestPermission["Request Permission"]
RequestPermission --> UserGrants{"User Grants Permission?"}
UserGrants --> |Yes| CaptureScreen
UserGrants --> |No| ShowInstructions["Show Instructions"]
ShowInstructions --> UserEnables["User Enables in Settings?"]
UserEnables --> |Yes| CheckPermissions
UserEnables --> |No| ReturnError["Return Permission Error"]
CaptureScreen --> Complete["Capture Complete"]
ReturnError --> Complete
style Start fill:#4CAF50,stroke:#388E3C
style CheckPermissions fill:#FF9800,stroke:#F57C00
style CaptureScreen fill:#2196F3,stroke:#1976D2
style RequestPermission fill:#2196F3,stroke:#1976D2
style UserGrants fill:#FF9800,stroke:#F57C00
style ShowInstructions fill:#2196F3,stroke:#1976D2
style UserEnables fill:#FF9800,stroke:#F57C00
style ReturnError fill:#F44336,stroke:#D32F2F
style Complete fill:#4CAF50,stroke:#388E3C
```

**Diagram sources**
- [get-capture-sources.ts](file://frontend/src/main/utils/get-capture-sources.ts#L336-L345)
- [ScreenshotService.ts](file://frontend/src/main/services/ScreenshotService.ts#L28-L34)

### Screen Capture Failures in Secure Contexts

Certain applications and system interfaces may prevent screen capture for security reasons. The system handles these cases by implementing fallback mechanisms and providing clear error reporting.

**Section sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L296-L298)
- [get-capture-sources.ts](file://frontend/src/main/utils/get-capture-sources.ts#L615-L620)

### Memory Usage Optimization

High-frequency screenshot capture can lead to significant memory usage. The system implements several optimization strategies to mitigate this issue, including image resizing, compression, and efficient memory management.

```mermaid
flowchart TD
Start["Start Capture"] --> CheckMemory{"High Memory Usage?"}
CheckMemory --> |Yes| ResizeImage["Resize Image to Max Size"]
CheckMemory --> |No| ProcessImage["Process Image Normally"]
ResizeImage --> CompressImage["Compress with High Quality"]
ProcessImage --> CompressImage
CompressImage --> StoreImage["Store Image"]
StoreImage --> Complete["Capture Complete"]
style Start fill:#4CAF50,stroke:#388E3C
style CheckMemory fill:#FF9800,stroke:#F57C00
style ResizeImage fill:#2196F3,stroke:#1976D2
style ProcessImage fill:#2196F3,stroke:#1976D2
style CompressImage fill:#2196F3,stroke:#1976D2
style StoreImage fill:#2196F3,stroke:#1976D2
style Complete fill:#4CAF50,stroke:#388E3C
```

**Diagram sources**
- [image.py](file://opencontext/utils/image.py#L46-L62)
- [config.yaml](file://config/config.yaml#L89-L91)

## Conclusion

The Screenshot Capture component provides a comprehensive solution for capturing and processing user screen activity. By implementing a modular architecture with clear separation of concerns, the system offers flexible configuration options, robust error handling, and efficient resource management. The integration with the `RawContextProperties` model ensures that captured screenshots are enriched with meaningful metadata, enabling downstream processing components to extract valuable context from visual data. The system's design addresses common challenges such as permission management on macOS, secure context limitations, and memory optimization for high-frequency capture scenarios.