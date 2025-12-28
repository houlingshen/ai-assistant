# System Configuration (config.yaml)

<cite>
**Referenced Files in This Document**
- [config.yaml](file://config/config.yaml)
- [config_manager.py](file://opencontext/config/config_manager.py)
- [global_config.py](file://opencontext/config/global_config.py)
- [cli.py](file://opencontext/cli.py)
- [opencontext.py](file://opencontext/server/opencontext.py)
- [settings.py](file://opencontext/server/routes/settings.py)
- [llm_client.py](file://opencontext/llm/llm_client.py)
- [screenshot.py](file://opencontext/context_capture/screenshot.py)
- [ScreenshotService.ts](file://frontend/src/main/services/ScreenshotService.ts)
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
10. [Appendices](#appendices)

## Introduction
This document explains the system configuration file config.yaml and how it defines core application settings. It covers:
- How the configuration file specifies server settings, model parameters (VLM and embeddings), capture intervals, and storage paths
- The hierarchical configuration loading mechanism: defaults, config file, environment variables, and command-line arguments
- How ConfigManager parses and validates the file and propagates values to services like ScreenshotService and LLMClient
- Practical examples for modifying screenshot frequency, changing the LLM provider endpoint, and adjusting context retention policies
- Guidance for environment-specific configurations and best practices for securing sensitive values

## Project Structure
The configuration system centers around a YAML file and a Python configuration manager that loads, merges, and exposes settings across the backend. Frontend services read configuration indirectly via the backend’s API.

```mermaid
graph TB
subgraph "Configuration Layer"
CFG["config/config.yaml"]
CM["ConfigManager<br/>loads/merges/env vars"]
GC["GlobalConfig<br/>singleton accessor"]
end
subgraph "Backend Services"
OC["OpenContext<br/>initializes components"]
CAP["Capture Managers<br/>use capture config"]
PROC["Processing Managers<br/>use processing config"]
STOR["Storage Backends<br/>use storage config"]
LLM["LLM Clients<br/>use model config"]
end
subgraph "Frontend"
FE_SVC["ScreenshotService.ts<br/>reads backend API"]
end
CFG --> CM
CM --> GC
GC --> OC
OC --> CAP
OC --> PROC
OC --> STOR
OC --> LLM
FE_SVC --> OC
```

**Diagram sources**
- [config.yaml](file://config/config.yaml#L1-L253)
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [global_config.py](file://opencontext/config/global_config.py#L90-L113)
- [opencontext.py](file://opencontext/server/opencontext.py#L60-L83)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L106-L122)
- [llm_client.py](file://opencontext/llm/llm_client.py#L32-L46)
- [ScreenshotService.ts](file://frontend/src/main/services/ScreenshotService.ts#L1-L120)

**Section sources**
- [config.yaml](file://config/config.yaml#L1-L253)
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [global_config.py](file://opencontext/config/global_config.py#L90-L113)
- [opencontext.py](file://opencontext/server/opencontext.py#L60-L83)

## Core Components
- config/config.yaml: Central configuration file defining server, capture, processing, storage, prompts, content generation, tools, and completion settings.
- ConfigManager: Loads YAML, replaces ${ENV_VAR} placeholders, merges user settings, and exposes merged configuration.
- GlobalConfig: Singleton accessor that initializes ConfigManager and provides convenience methods to retrieve configuration and prompts.
- CLI: Parses command-line arguments and applies overrides to server host/port; passes config path to initialization.
- OpenContext: Initializes subsystems and uses configuration to configure capture, processing, storage, and LLM clients.
- LLMClient: Reads model parameters from configuration to connect to VLM and embedding providers.
- ScreenshotCapture: Uses capture configuration (interval, storage path, dedup thresholds) to drive periodic screenshot capture.
- ScreenshotService.ts: Frontend service that interacts with backend APIs; screenshots are stored on disk by backend services.

**Section sources**
- [config.yaml](file://config/config.yaml#L1-L253)
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [global_config.py](file://opencontext/config/global_config.py#L90-L113)
- [cli.py](file://opencontext/cli.py#L140-L167)
- [opencontext.py](file://opencontext/server/opencontext.py#L60-L83)
- [llm_client.py](file://opencontext/llm/llm_client.py#L32-L46)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L106-L122)
- [ScreenshotService.ts](file://frontend/src/main/services/ScreenshotService.ts#L1-L120)

## Architecture Overview
The configuration lifecycle:
- Defaults are implicit in component initialization and route handlers.
- config/config.yaml provides baseline values.
- Environment variables resolve placeholders in the YAML (e.g., ${CONTEXT_PATH}, ${LLM_BASE_URL}, ${EMBEDDING_API_KEY}).
- User settings (user_setting.yaml) are merged into the main configuration.
- Command-line arguments override web server host/port.
- GlobalConfig exposes configuration to all subsystems.

```mermaid
sequenceDiagram
participant CLI as "CLI"
participant GC as "GlobalConfig"
participant CM as "ConfigManager"
participant OC as "OpenContext"
participant CAP as "Capture/Processing/Storage"
participant LLM as "LLMClient"
CLI->>GC : initialize(config_path)
GC->>CM : load_config(config_path)
CM->>CM : _load_env_vars()
CM->>CM : _replace_env_vars(config)
CM->>CM : load_user_settings()
CM-->>GC : get_config()
GC-->>OC : get_config()
OC->>CAP : initialize with capture/processing/storage config
OC->>LLM : initialize with vlm_model/embedding_model config
CLI->>CLI : parse_args(--host/--port)
CLI->>OC : start_web_server(host, port)
```

**Diagram sources**
- [cli.py](file://opencontext/cli.py#L140-L167)
- [global_config.py](file://opencontext/config/global_config.py#L90-L113)
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [opencontext.py](file://opencontext/server/opencontext.py#L60-L83)
- [llm_client.py](file://opencontext/llm/llm_client.py#L32-L46)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L106-L122)

## Detailed Component Analysis

### Configuration File Roles and Sections
- General and logging: enables/disables features and sets log level and path.
- Document processing: batch sizes and image processing parameters for VLM.
- Model parameters:
  - vlm_model: base_url, api_key, model, provider
  - embedding_model: base_url, api_key, model, provider, output_dim
- Capture module:
  - screenshot.enabled/capture_interval/storage_path
  - folder_monitor/file_monitor/vault_document_monitor intervals and paths
- Processing module:
  - document_processor and screenshot_processor batch sizes/timeouts
  - context merger thresholds and retention policies per context type
- Storage module:
  - Vector database backends (ChromaDB or Qdrant) with modes and paths
  - Document database (SQLite) path
- Consumption module: enabled flag
- Web server: host and port
- API authentication: enable/disable and api_keys with excluded paths
- Prompts: language selection
- Content generation: debug output path and task intervals
- Tools: web search tool configuration
- Completion: enabled flag

Practical examples:
- Modify screenshot frequency: adjust capture.screenshot.capture_interval in config.yaml.
- Change LLM provider endpoint: set vlm_model.base_url and embedding_model.base_url.
- Adjust context retention: change retention_days and max_merge_count for specific context types under processing.context_merger.

**Section sources**
- [config.yaml](file://config/config.yaml#L1-L253)

### Hierarchical Configuration Loading Mechanism
- Defaults: Implicit defaults in component initialization and route handlers.
- Config file: Values loaded from config/config.yaml.
- Environment variables: Placeholders like ${VAR} and ${VAR:default} are replaced using ConfigManager.
- User settings: user_setting.yaml is merged into the main configuration.
- Command-line overrides: CLI allows overriding web server host/port; other overrides can be introduced similarly.

```mermaid
flowchart TD
Start(["Load Configuration"]) --> Defaults["Defaults"]
Defaults --> FileCfg["Load config/config.yaml"]
FileCfg --> EnvVars["Replace ${ENV_VAR} placeholders"]
EnvVars --> UserSettings["Merge user_setting.yaml"]
UserSettings --> Overrides["Apply CLI overrides (host/port)"]
Overrides --> Expose["Expose via GlobalConfig.get_config()"]
Expose --> Consumers["Components consume configuration"]
```

**Diagram sources**
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [global_config.py](file://opencontext/config/global_config.py#L236-L262)
- [cli.py](file://opencontext/cli.py#L222-L239)

**Section sources**
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [global_config.py](file://opencontext/config/global_config.py#L236-L262)
- [cli.py](file://opencontext/cli.py#L222-L239)

### ConfigManager Parsing and Validation
- Loads YAML safely and stores raw config.
- Replaces environment variable placeholders using regex patterns.
- Loads user_setting.yaml and deep-merges it into the main configuration.
- Exposes merged configuration via get_config().

```mermaid
classDiagram
class ConfigManager {
- _config : Dict
- _config_path : str
- _env_vars : Dict
+ load_config(config_path) bool
+ get_config() Dict
+ get_config_path() str
+ load_user_settings() bool
+ save_user_settings(settings) bool
+ reset_user_settings() bool
- _load_env_vars() void
- _replace_env_vars(config_data) Any
- deep_merge(base, override) Dict
}
```

**Diagram sources**
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L253)

**Section sources**
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [config_manager.py](file://opencontext/config/config_manager.py#L143-L224)

### GlobalConfig Accessor
- Ensures singleton access to configuration and prompts.
- Initializes ConfigManager and loads prompts based on configuration.
- Provides get_config(path) to retrieve nested values and is_enabled(module) helpers.

```mermaid
classDiagram
class GlobalConfig {
- _config_manager : ConfigManager
- _prompt_manager : PromptManager
- _config_path : str
- _prompt_path : str
+ get_instance() GlobalConfig
+ initialize(config_path) bool
+ get_config(path) Dict
+ get_prompt(name, default) str
+ get_prompt_group(name) Dict
+ is_enabled(module) bool
+ set_language(language) bool
}
```

**Diagram sources**
- [global_config.py](file://opencontext/config/global_config.py#L23-L113)
- [global_config.py](file://opencontext/config/global_config.py#L236-L331)

**Section sources**
- [global_config.py](file://opencontext/config/global_config.py#L23-L113)
- [global_config.py](file://opencontext/config/global_config.py#L236-L331)

### Propagation to Services

#### ScreenshotService (Frontend)
- The frontend ScreenshotService captures screenshots and writes them to disk under a structured path.
- Backend services (e.g., ScreenshotCapture) also write screenshots to storage_path defined in capture.screenshot.storage_path.

```mermaid
sequenceDiagram
participant FE as "ScreenshotService.ts"
participant BE as "Backend Capture/Storage"
participant FS as "Filesystem"
FE->>BE : Request screenshot capture
BE->>FS : Write PNG to storage_path
FS-->>BE : Success/Failure
BE-->>FE : Return screenshot URL/path
```

**Diagram sources**
- [ScreenshotService.ts](file://frontend/src/main/services/ScreenshotService.ts#L1-L120)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L106-L122)
- [config.yaml](file://config/config.yaml#L43-L47)

**Section sources**
- [ScreenshotService.ts](file://frontend/src/main/services/ScreenshotService.ts#L1-L120)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L106-L122)
- [config.yaml](file://config/config.yaml#L43-L47)

#### LLMClient (Backend)
- Reads vlm_model and embedding_model from configuration to construct OpenAI-compatible clients.
- Validates configuration by attempting API calls.

```mermaid
sequenceDiagram
participant GC as "GlobalConfig"
participant CM as "ConfigManager"
participant LLM as "LLMClient"
participant API as "LLM Provider"
GC->>CM : get_config()
CM-->>GC : {vlm_model, embedding_model}
GC->>LLM : initialize with vlm_model
LLM->>API : chat/completions
API-->>LLM : response
GC->>LLM : initialize with embedding_model
LLM->>API : embeddings
API-->>LLM : embedding
```

**Diagram sources**
- [global_config.py](file://opencontext/config/global_config.py#L236-L262)
- [config_manager.py](file://opencontext/config/config_manager.py#L102-L118)
- [llm_client.py](file://opencontext/llm/llm_client.py#L32-L46)
- [settings.py](file://opencontext/server/routes/settings.py#L108-L196)

**Section sources**
- [llm_client.py](file://opencontext/llm/llm_client.py#L32-L46)
- [settings.py](file://opencontext/server/routes/settings.py#L108-L196)

#### Capture Interval and Paths
- Screenshot capture interval and storage path are read by ScreenshotCapture.
- Other capture modules (folder_monitor, file_monitor, vault_document_monitor) use their respective intervals and paths.

```mermaid
flowchart TD
CFG["config.yaml capture.screenshot"] --> CAP["ScreenshotCapture.init"]
CAP --> INTERVAL["Set capture_interval"]
CAP --> PATH["Set storage_path"]
CAP --> RUN["Run periodic capture"]
```

**Diagram sources**
- [config.yaml](file://config/config.yaml#L43-L47)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L106-L122)

**Section sources**
- [config.yaml](file://config/config.yaml#L43-L47)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L106-L122)

### Practical Configuration Examples
- Modify screenshot frequency:
  - Edit capture.screenshot.capture_interval in config.yaml.
  - Restart backend or trigger a reload to apply changes.
- Change the LLM provider endpoint:
  - Update vlm_model.base_url and embedding_model.base_url in config.yaml.
  - Alternatively, use the model settings API to update and reinitialize clients.
- Adjust context retention policies:
  - Under processing.context_merger, modify retention_days and max_merge_count for specific context types (e.g., ENTITY_CONTEXT, ACTIVITY, INTENT, SEMANTIC, PROCEDURAL, STATE).

Security-sensitive values:
- vlm_model.api_key and embedding_model.api_key should be provided via environment variables or user_setting.yaml to avoid committing secrets to source control.
- Use user_setting.yaml to persist runtime updates without editing the main config file.

**Section sources**
- [config.yaml](file://config/config.yaml#L26-L37)
- [config.yaml](file://config/config.yaml#L112-L144)
- [settings.py](file://opencontext/server/routes/settings.py#L108-L196)
- [config_manager.py](file://opencontext/config/config_manager.py#L168-L224)

## Dependency Analysis
- ConfigManager depends on YAML parsing and environment variables.
- GlobalConfig depends on ConfigManager and prompt manager.
- CLI depends on GlobalConfig for logging setup and passes config path to initialization.
- OpenContext depends on GlobalConfig to initialize capture, processing, storage, and LLM clients.
- LLMClient depends on configuration for base_url, api_key, model, provider, and output_dim.

```mermaid
graph TB
CM["ConfigManager"] --> GC["GlobalConfig"]
GC --> OC["OpenContext"]
OC --> CAP["Capture Managers"]
OC --> PROC["Processing Managers"]
OC --> STOR["Storage Backends"]
OC --> LLM["LLMClient"]
CLI["CLI"] --> GC
CLI --> OC
```

**Diagram sources**
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [global_config.py](file://opencontext/config/global_config.py#L90-L113)
- [opencontext.py](file://opencontext/server/opencontext.py#L60-L83)
- [cli.py](file://opencontext/cli.py#L140-L167)
- [llm_client.py](file://opencontext/llm/llm_client.py#L32-L46)

**Section sources**
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [global_config.py](file://opencontext/config/global_config.py#L90-L113)
- [opencontext.py](file://opencontext/server/opencontext.py#L60-L83)
- [cli.py](file://opencontext/cli.py#L140-L167)
- [llm_client.py](file://opencontext/llm/llm_client.py#L32-L46)

## Performance Considerations
- Lower capture intervals increase CPU and I/O usage; tune capture.screenshot.capture_interval to balance frequency and resource usage.
- Larger max_image_size and higher resize_quality increase memory and processing time; adjust processing.screenshot_processor.max_image_size and resize_quality accordingly.
- Embedding output_dim affects downstream vector storage and similarity computations; align embedding_model.output_dim with chosen vector database configuration.
- Batch sizes in document_processor and screenshot_processor influence throughput; tune processing.document_processor.batch_size and processing.screenshot_processor.batch_size.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Configuration not found: Ensure config/config.yaml exists and is readable; CLI accepts a --config path.
- Environment variables not resolving: Confirm ${VAR} placeholders are present and environment variables are exported; ConfigManager replaces ${VAR} and ${VAR:default}.
- Model settings invalid: Use the model settings API to validate and update vlm_model and embedding_model; the API performs connectivity checks and persists user settings.
- Screenshots not saved: Verify capture.screenshot.storage_path exists and is writable; confirm capture.screenshot.enabled is true.
- Web server host/port override: Use CLI --host and --port to override web.host and web.port.

**Section sources**
- [config_manager.py](file://opencontext/config/config_manager.py#L37-L118)
- [settings.py](file://opencontext/server/routes/settings.py#L108-L196)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L106-L122)
- [cli.py](file://opencontext/cli.py#L222-L239)

## Conclusion
The config.yaml file centralizes application behavior across server, capture, processing, storage, and LLM settings. ConfigManager and GlobalConfig provide robust mechanisms to load, merge, and expose configuration, while CLI and API routes enable environment-specific overrides and runtime updates. Following the outlined examples and best practices ensures secure, maintainable, and performant deployments.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Environment Variables and Placeholders
- ${CONTEXT_PATH}: Resolves to the application context directory used for logs, screenshots, and persistent data.
- ${LLM_BASE_URL}, ${EMBEDDING_BASE_URL}, ${LLM_API_KEY}, ${EMBEDDING_API_KEY}, ${LLM_MODEL}, ${EMBEDDING_MODEL}, ${QDRANT_API_KEY}, ${CONTEXT_API_KEY}: Provide externalized configuration values.

**Section sources**
- [config.yaml](file://config/config.yaml#L10-L14)
- [config.yaml](file://config/config.yaml#L26-L37)
- [config.yaml](file://config/config.yaml#L150-L176)
- [config.yaml](file://config/config.yaml#L193-L211)
- [config_manager.py](file://opencontext/config/config_manager.py#L62-L101)