# Service Components

<cite>
**Referenced Files in This Document**
- [capture_manager.py](file://opencontext/managers/capture_manager.py)
- [processor_manager.py](file://opencontext/managers/processor_manager.py)
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py)
- [component_initializer.py](file://opencontext/server/component_initializer.py)
- [screenshot.py](file://opencontext/context_capture/screenshot.py)
- [web_link_capture.py](file://opencontext/context_capture/web_link_capture.py)
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py)
- [document_processor.py](file://opencontext/context_processing/processor/document_processor.py)
- [context_merger.py](file://opencontext/context_processing/merger/context_merger.py)
- [capture_interface.py](file://opencontext/interfaces/capture_interface.py)
- [processor_interface.py](file://opencontext/interfaces/processor_interface.py)
- [base.py](file://opencontext/context_capture/base.py)
- [base_processor.py](file://opencontext/context_processing/processor/base_processor.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document describes the backend service components of MineContext with a focus on the three core managers: ContextCaptureManager, ContextProcessorManager, and ConsumptionManager. It explains how ContextCaptureManager registers, initializes, and controls lifecycle of capture components (screenshot and web link capture), how ContextProcessorManager routes raw context data to appropriate processors based on source type and manages periodic memory compression via the merger component, and how ConsumptionManager generates AI-powered insights through scheduled tasks for activity reports, smart tips, and todo generation. It also details how these managers are initialized and wired together in component_initializer.py, including the callback chain from capture to processing to consumption. Thread safety, statistics tracking, and shutdown procedures are covered for each manager.

## Project Structure
The MineContext backend is organized around three primary layers:
- Managers: orchestrate lifecycle and coordination of capture, processing, and consumption subsystems.
- Components: concrete implementations of capture and processing units.
- Interfaces and base classes: define contracts and reusable behavior.

```mermaid
graph TB
subgraph "Managers"
CM["ContextCaptureManager"]
PM["ContextProcessorManager"]
CSM["ConsumptionManager"]
end
subgraph "Components"
SC["ScreenshotCapture"]
WLC["WebLinkCapture"]
SP["ScreenshotProcessor"]
DP["DocumentProcessor"]
MERGE["ContextMerger"]
end
subgraph "Interfaces/Base"
ICap["ICaptureComponent"]
IProc["IContextProcessor"]
BaseCap["BaseCaptureComponent"]
BaseProc["BaseContextProcessor"]
end
CM --> ICap
PM --> IProc
CM --> BaseCap
PM --> BaseProc
CM --> SC
CM --> WLC
PM --> SP
PM --> DP
PM --> MERGE
```

**Diagram sources**
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L1-L391)
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L1-L213)
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L1-L524)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L1-L508)
- [web_link_capture.py](file://opencontext/context_capture/web_link_capture.py#L1-L351)
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py#L1-L590)
- [document_processor.py](file://opencontext/context_processing/processor/document_processor.py#L1-L653)
- [context_merger.py](file://opencontext/context_processing/merger/context_merger.py#L1-L200)
- [capture_interface.py](file://opencontext/interfaces/capture_interface.py#L1-L153)
- [processor_interface.py](file://opencontext/interfaces/processor_interface.py#L1-L136)
- [base.py](file://opencontext/context_capture/base.py#L1-L515)
- [base_processor.py](file://opencontext/context_processing/processor/base_processor.py#L1-L261)

**Section sources**
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L1-L391)
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L1-L213)
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L1-L524)
- [component_initializer.py](file://opencontext/server/component_initializer.py#L1-L229)

## Core Components
- ContextCaptureManager: central coordinator for capture components. Registers, initializes, starts/stops components, exposes callbacks, and tracks statistics.
- ContextProcessorManager: routes raw contexts to processors by source type, maintains processor instances, sets merger, and schedules periodic memory compression.
- ConsumptionManager: runs scheduled tasks for activity reports, smart tips, and todos; manages task timers and configuration.

Key responsibilities:
- Capture lifecycle: register_component, initialize_component, start_component, stop_component, start_all_components, stop_all_components, set_callback, get_statistics, shutdown.
- Processing routing: register_processor, set_merger, process, batch_process, get_statistics, shutdown, reset_statistics.
- Consumption scheduling: start_scheduled_tasks, stop_scheduled_tasks, get_scheduled_tasks_status, update_task_config, get_task_config, shutdown.

**Section sources**
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L1-L391)
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L1-L213)
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L1-L524)

## Architecture Overview
The system follows a producer-consumer pipeline:
- Capture components produce RawContextProperties and push them to the ContextCaptureManager via callbacks.
- ContextCaptureManager forwards captured data to ContextProcessorManager via a callback.
- ContextProcessorManager selects the appropriate processor based on source type, processes the data, and persists results.
- ConsumptionManager consumes processed data indirectly through scheduled tasks and storage queries to generate insights.

```mermaid
sequenceDiagram
participant Cap as "Capture Components"
participant CM as "ContextCaptureManager"
participant PM as "ContextProcessorManager"
participant Proc as "Processors"
participant Storage as "GlobalStorage"
participant CSM as "ConsumptionManager"
Cap->>CM : "capture() -> RawContextProperties[]"
CM->>PM : "callback(RawContextProperties[])"
PM->>Proc : "process()/batch_process()"
Proc->>Storage : "batch_upsert_processed_context()"
CSM->>Storage : "get_*() for scheduled tasks"
CSM-->>CSM : "generate insights (activity, tips, todos)"
```

**Diagram sources**
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L264-L311)
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L129-L179)
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py#L197-L235)
- [document_processor.py](file://opencontext/context_processing/processor/document_processor.py#L211-L222)
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L243-L356)

## Detailed Component Analysis

### ContextCaptureManager
Responsibilities:
- Registration and lifecycle management of capture components.
- Validation and initialization of component configurations.
- Starting/stopping components and maintaining a set of running components.
- Exposing a callback to receive captured data and forwarding it upstream.
- Statistics tracking per component and totals.
- Manual capture triggers and bulk capture operations.
- Graceful shutdown of all components.

Thread safety:
- Uses locks and sets to guard component registry and running state.
- Callback invocation is guarded by exception handling to avoid crashing the pipeline.

Statistics:
- Tracks total captures, total contexts captured, last capture time, and per-component counters.

Shutdown:
- Stops all running components gracefully and logs shutdown status.

```mermaid
classDiagram
class ContextCaptureManager {
- Dict~str, ICaptureComponent~ _components
- Dict~str, Dict~str, Any~~ _component_configs
- Set~str~ _running_components
- callable _callback
- Dict~str, Any~ _statistics
+ register_component(name, component) bool
+ initialize_component(name, config) bool
+ start_component(name) bool
+ stop_component(name, graceful) bool
+ start_all_components() Dict~str, bool~
+ stop_all_components(graceful) Dict~str, bool~
+ set_callback(callback) void
+ capture(component_name) RawContextProperties[]
+ capture_all() Dict~str, RawContextProperties[]~
+ get_statistics() Dict~str, Any~
+ shutdown(graceful) void
+ reset_statistics() void
- _on_component_capture(contexts) void
}
class ICaptureComponent {
<<interface>>
+ initialize(config) bool
+ start() bool
+ stop(graceful) bool
+ capture() RawContextProperties[]
+ validate_config(config) bool
+ set_callback(cb) bool
+ get_status() Dict~str, Any~
+ get_statistics() Dict~str, Any~
}
ContextCaptureManager --> ICaptureComponent : "manages"
```

**Diagram sources**
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L1-L391)
- [capture_interface.py](file://opencontext/interfaces/capture_interface.py#L1-L153)

**Section sources**
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L1-L391)
- [base.py](file://opencontext/context_capture/base.py#L1-L515)

### Capture Components
Two concrete capture components are used in this system:
- ScreenshotCapture: periodic screen capture with deduplication, configurable region, and optional saving to disk.
- WebLinkCapture: converts URLs to Markdown or PDF using external libraries, with concurrency control.

Both inherit from BaseCaptureComponent, which provides:
- Configuration validation and schema extension.
- Auto-capture loop with configurable intervals.
- Thread-safe lifecycle management and statistics.

```mermaid
classDiagram
class BaseCaptureComponent {
- str _name
- str _description
- ContextSource _source_type
- Dict~str, Any~ _config
- bool _running
- Thread _capture_thread
- Event _stop_event
- callable _callback
- float _capture_interval
- datetime _last_capture_time
- int _capture_count
- int _error_count
- str _last_error
+ initialize(config) bool
+ start() bool
+ stop(graceful) bool
+ capture() RawContextProperties[]
+ validate_config(config) bool
+ set_callback(cb) bool
+ get_status() Dict~str, Any~
+ get_statistics() Dict~str, Any~
+ reset_statistics() bool
- _capture_loop() void
# _initialize_impl(config) bool
# _start_impl() bool
# _stop_impl(graceful) bool
# _capture_impl() RawContextProperties[]
}
class ScreenshotCapture
class WebLinkCapture
BaseCaptureComponent <|-- ScreenshotCapture
BaseCaptureComponent <|-- WebLinkCapture
```

**Diagram sources**
- [base.py](file://opencontext/context_capture/base.py#L1-L515)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L1-L508)
- [web_link_capture.py](file://opencontext/context_capture/web_link_capture.py#L1-L351)

**Section sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L1-L508)
- [web_link_capture.py](file://opencontext/context_capture/web_link_capture.py#L1-L351)
- [base.py](file://opencontext/context_capture/base.py#L1-L515)

### ContextProcessorManager
Responsibilities:
- Routing raw contexts to processors based on source type via a routing table.
- Managing processor instances and their statistics.
- Setting a merger component and starting periodic memory compression.
- Batch processing with a thread pool and error handling.
- Providing statistics and shutdown routines.

Routing table:
- SCREENSHOT -> screenshot_processor
- LOCAL_FILE/Vault/WEB_LINK -> document_processor

Periodic compression:
- Starts a Timer to periodically call merger’s periodic_memory_compression.

```mermaid
flowchart TD
Start(["process(initial_input)"]) --> Lookup["Lookup processor by ContextSource in routing table"]
Lookup --> Found{"Processor found?"}
Found --> |No| LogErr["Log error and return False"]
Found --> |Yes| CanProc{"Processor.can_process()?"}
CanProc --> |No| LogErr
CanProc --> |Yes| DoProcess["processor.process()"]
DoProcess --> Done(["Return result"])
```

**Diagram sources**
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L87-L179)

**Section sources**
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L1-L213)

### Processor Components
- ScreenshotProcessor: deduplicates screenshots, batches processing, uses LLM for VLM analysis, merges results, and persists to storage.
- DocumentProcessor: handles structured and visual documents, page-by-page analysis, VLM for visual pages, chunking, and knowledge context creation.

Both inherit from BaseContextProcessor, which provides:
- Configuration management, statistics tracking, and callback invocation.
- Background processing loops for batched workloads.

```mermaid
classDiagram
class BaseContextProcessor {
- Dict~str, Any~ config
- bool _is_initialized
- callable _callback
- Dict~str, Any~ _processing_stats
+ initialize(config) bool
+ validate_config(config) bool
+ can_process(context) bool
+ process(context) ProcessedContext[]
+ batch_process(contexts) Dict~str, ProcessedContext[]~
+ get_statistics() Dict~str, Any~
+ reset_statistics() bool
+ set_callback(callback) bool
+ shutdown() bool
}
class ScreenshotProcessor
class DocumentProcessor
BaseContextProcessor <|-- ScreenshotProcessor
BaseContextProcessor <|-- DocumentProcessor
```

**Diagram sources**
- [base_processor.py](file://opencontext/context_processing/processor/base_processor.py#L1-L261)
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py#L1-L590)
- [document_processor.py](file://opencontext/context_processing/processor/document_processor.py#L1-L653)

**Section sources**
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py#L1-L590)
- [document_processor.py](file://opencontext/context_processing/processor/document_processor.py#L1-L653)
- [base_processor.py](file://opencontext/context_processing/processor/base_processor.py#L1-L261)

### ContextMerger
Role:
- Merges similar contexts using type-aware strategies and vector similarity.
- Supports intelligent merging and legacy associative/similarity strategies.
- Periodic memory compression is invoked via ContextProcessorManager’s timer.

Integration:
- Registered as merger in ContextProcessorManager and started via component_initializer.

**Section sources**
- [context_merger.py](file://opencontext/context_processing/merger/context_merger.py#L1-L200)
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L46-L79)

### ConsumptionManager
Responsibilities:
- Scheduled tasks for:
  - Daily report generation at a configured time-of-day.
  - Realtime activity summaries with configurable intervals.
  - Smart tips generation with configurable intervals.
  - Smart todo generation with configurable intervals.
- Dynamic configuration updates for intervals and enabling/disabling tasks.
- Thread-safe configuration updates with a lock.
- Shutdown cancels all timers.

```mermaid
sequenceDiagram
participant CSM as "ConsumptionManager"
participant Timer as "threading.Timer"
participant Gen as "Generators"
participant Storage as "GlobalStorage"
CSM->>Timer : "start_scheduled_tasks()"
Timer->>CSM : "check_and_generate_daily_report()"
CSM->>Gen : "ReportGenerator.generate_report(start, end)"
Gen->>Storage : "persist report"
Timer->>CSM : "generate_activity()/generate_tips()/generate_todos()"
CSM->>Gen : "monitor/ai generators"
Gen->>Storage : "persist insights"
```

**Diagram sources**
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L200-L356)

**Section sources**
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L1-L524)

### Component Initialization and Wiring
ComponentInitializer orchestrates:
- Capture components: reads configuration, creates instances, registers, initializes, and starts them.
- Processors: creates processors via factory, registers them, and sets callbacks.
- Merger: instantiates ContextMerger, sets it on processor manager, and starts periodic compression.
- Completion service: optional service initialization.
- Consumption components: constructs ConsumptionManager and starts scheduled tasks.

```mermaid
sequenceDiagram
participant CI as "ComponentInitializer"
participant CM as "ContextCaptureManager"
participant PM as "ContextProcessorManager"
participant CSM as "ConsumptionManager"
CI->>CM : "initialize_capture_components()"
CM->>CM : "register_component(), initialize_component()"
CI->>PM : "initialize_processors(processed_context_callback)"
PM->>PM : "register_processor(), set_merger()"
CI->>CSM : "initialize_consumption_components()"
CSM->>CSM : "start_scheduled_tasks()"
CM->>PM : "set_callback(processed_context_callback)"
```

**Diagram sources**
- [component_initializer.py](file://opencontext/server/component_initializer.py#L71-L207)

**Section sources**
- [component_initializer.py](file://opencontext/server/component_initializer.py#L1-L229)

## Dependency Analysis
- Capture components depend on BaseCaptureComponent and ICaptureComponent.
- Processor components depend on BaseContextProcessor and IContextProcessor.
- ContextProcessorManager depends on processors and merger.
- ContextCaptureManager depends on capture components and provides callbacks to ContextProcessorManager.
- ConsumptionManager depends on storage and generators for insights.

```mermaid
graph TB
CM["ContextCaptureManager"] --> SC["ScreenshotCapture"]
CM --> WLC["WebLinkCapture"]
CM --> PM["ContextProcessorManager"]
PM --> SP["ScreenshotProcessor"]
PM --> DP["DocumentProcessor"]
PM --> MERGE["ContextMerger"]
CSM["ConsumptionManager"] --> Storage["GlobalStorage"]
PM --> Storage
SP --> Storage
DP --> Storage
```

**Diagram sources**
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L1-L391)
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L1-L213)
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L1-L524)
- [screenshot_processor.py](file://opencontext/context_processing/processor/screenshot_processor.py#L1-L590)
- [document_processor.py](file://opencontext/context_processing/processor/document_processor.py#L1-L653)
- [context_merger.py](file://opencontext/context_processing/merger/context_merger.py#L1-L200)

**Section sources**
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L1-L391)
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L1-L213)
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L1-L524)

## Performance Considerations
- Concurrency:
  - ContextProcessorManager uses a ThreadPoolExecutor for batch processing.
  - ScreenshotProcessor and DocumentProcessor use background threads and queues to decouple capture from processing.
- Deduplication:
  - ScreenshotCapture performs image deduplication to reduce redundant processing.
  - ScreenshotProcessor uses perceptual hashing and caches to detect duplicates.
- Memory compression:
  - ContextProcessorManager starts a periodic timer to invoke merger’s memory compression routine.
- I/O and external dependencies:
  - WebLinkCapture uses concurrency to convert multiple URLs efficiently.
  - ScreenshotProcessor and DocumentProcessor rely on external LLM/VLM clients; batching reduces overhead.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and diagnostics:
- Capture component errors:
  - Validate configuration using validate_config and inspect get_status/get_statistics.
  - Check capture thread lifecycle and stop events.
- Processor failures:
  - Review batch_process exceptions and per-processor statistics.
  - Verify can_process checks and source type routing.
- Merger and compression:
  - Ensure merger is set and periodic timer is running.
  - Inspect merger statistics and strategy initialization.
- Consumption tasks:
  - Confirm scheduled timers are active and intervals are valid.
  - Use get_scheduled_tasks_status to verify active timers.

Operational controls:
- Reset statistics for managers and processors.
- Graceful shutdown sequences for capture and processors.
- ConsumptionManager shutdown cancels all timers.

**Section sources**
- [base.py](file://opencontext/context_capture/base.py#L1-L515)
- [base_processor.py](file://opencontext/context_processing/processor/base_processor.py#L1-L261)
- [processor_manager.py](file://opencontext/managers/processor_manager.py#L191-L213)
- [consumption_manager.py](file://opencontext/managers/consumption_manager.py#L101-L111)

## Conclusion
MineContext’s backend is structured around three cohesive managers that coordinate capture, processing, and consumption. ContextCaptureManager provides a robust, thread-safe interface for registering and controlling capture components. ContextProcessorManager routes raw contexts to specialized processors, aggregates statistics, and integrates a merger for memory compression. ConsumptionManager automates AI-driven insights through scheduled tasks. ComponentInitializer wires these managers together and establishes the callback chain from capture to processing to consumption. Thread safety, statistics tracking, and graceful shutdown are integral to each manager’s design, ensuring reliability and observability across the system.