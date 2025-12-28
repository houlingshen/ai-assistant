# Common Issues and Solutions

<cite>
**Referenced Files in This Document**   
- [regenerate_debug_file.py](file://examples/regenerate_debug_file.py)
- [screenshot.py](file://opencontext/context_capture/screenshot.py)
- [folder_monitor.py](file://opencontext/context_capture/folder_monitor.py)
- [vault_document_monitor.py](file://opencontext/context_capture/vault_document_monitor.py)
- [web_link_capture.py](file://opencontext/context_capture/web_link_capture.py)
- [llm_client.py](file://opencontext/llm/llm_client.py)
- [config.yaml](file://config/config.yaml)
- [global_config.py](file://opencontext/config/global_config.py)
- [capture_manager.py](file://opencontext/managers/capture_manager.py)
- [unified_storage.py](file://opencontext/storage/unified_storage.py)
- [axiosConfig.ts](file://frontend/src/renderer/src/services/axiosConfig.ts)
- [health.py](file://opencontext/server/routes/health.py)
- [auth.py](file://opencontext/server/middleware/auth.py)
</cite>

## Table of Contents
1. [Context Capture Failures](#context-capture-failures)
2. [AI Connectivity Issues](#ai-connectivity-issues)
3. [Performance Problems](#performance-problems)
4. [Platform-Specific Bugs](#platform-specific-bugs)
5. [Database and Configuration Recovery](#database-and-configuration-recovery)
6. [Troubleshooting Workflows](#troubleshooting-workflows)

## Context Capture Failures

### Screenshots Not Recording
**Symptoms**: No screenshots are being captured despite the capture component being enabled in the configuration.

**Root Causes**:
- Screenshot capture component is disabled in the configuration file
- Missing or incompatible screenshot library (mss)
- Invalid configuration parameters such as capture interval or storage path
- Permission issues on macOS preventing screen recording

**Diagnostic Steps**:
1. Check the configuration file to ensure screenshot capture is enabled:
```yaml
capture:
  screenshot:
    enabled: true
    capture_interval: 5
    storage_path: "${CONTEXT_PATH:.}/screenshots"
```
2. Verify the mss library is installed and accessible
3. Check application logs for initialization errors related to screenshot capture
4. On macOS, verify that MineContext has screen recording permissions in System Settings > Privacy & Security

**Solutions**:
- Enable the screenshot component in config.yaml by setting `capture.screenshot.enabled` to `true`
- Install the mss library using pip: `pip install mss`
- Ensure the storage path exists and is writable
- Grant screen recording permission to MineContext in macOS System Settings

**Section sources**
- [config.yaml](file://config/config.yaml#L39-L47)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L28-L58)
- [capture_manager.py](file://opencontext/managers/capture_manager.py#L23-L391)

### Document Changes Not Detected
**Symptoms**: File modifications in monitored folders are not being captured or processed.

**Root Causes**:
- Folder monitoring component is disabled in configuration
- Watched folder paths are incorrectly specified or do not exist
- File size exceeds the maximum configured limit (default 100MB)
- Initial scan is disabled and new files are not being detected

**Diagnostic Steps**:
1. Verify folder monitoring is enabled in config.yaml:
```yaml
capture:
  folder_monitor:
    enabled: true
    monitor_interval: 30
    watch_folder_paths:
      - "${CONTEXT_PATH:.}/persist/Documents"
```
2. Check that the specified folder paths exist and are accessible
3. Verify file sizes are within the configured limits
4. Examine logs for file monitoring activity and error messages

**Solutions**:
- Enable folder_monitor in the configuration file
- Ensure watch_folder_paths point to valid, existing directories
- Adjust max_file_size parameter if large files need to be processed
- Set initial_scan to true to ensure existing files are processed

**Section sources**
- [config.yaml](file://config/config.yaml#L48-L58)
- [folder_monitor.py](file://opencontext/context_capture/folder_monitor.py#L29-L54)
- [folder_monitor.py](file://opencontext/context_capture/folder_monitor.py#L147-L164)

## AI Connectivity Issues

### LLM Timeouts
**Symptoms**: AI requests are failing with timeout errors, particularly during content generation or processing.

**Root Causes**:
- Network connectivity issues between client and LLM provider
- LLM provider server overload or rate limiting
- Insufficient timeout configuration for long-running requests
- Invalid API keys or authentication credentials

**Diagnostic Steps**:
1. Check network connectivity to the LLM provider endpoint
2. Verify API keys and base URLs are correctly configured in config.yaml:
```yaml
vlm_model:
  base_url: "${LLM_BASE_URL}"
  api_key: "${LLM_API_KEY}"
  model: "${LLM_MODEL}"
```
3. Examine logs for specific timeout error messages
4. Test connectivity using the LLM validation feature

**Solutions**:
- Verify network connectivity and firewall settings
- Check API key validity and ensure the model is accessible
- Increase timeout values in the LLM client configuration
- Implement retry logic with exponential backoff for transient failures

**Section sources**
- [config.yaml](file://config/config.yaml#L26-L30)
- [llm_client.py](file://opencontext/llm/llm_client.py#L33-L466)
- [llm_client.py](file://opencontext/llm/llm_client.py#L344-L466)

### Authentication Errors
**Symptoms**: API requests are failing with authentication errors such as "Invalid API key" or "Access denied."

**Root Causes**:
- Incorrect or expired API keys in configuration
- Authentication enabled in production but no valid API keys configured
- Environment variables for API keys not properly set
- Provider-specific authentication requirements not met

**Diagnostic Steps**:
1. Verify API key configuration in config.yaml:
```yaml
api_auth:
  enabled: false
  api_keys:
    - "${CONTEXT_API_KEY:test}"
```
2. Check that environment variables (LLM_API_KEY, EMBEDDING_API_KEY) are properly set
3. Examine logs for specific authentication error messages
4. Test API key validity using provider's authentication test tools

**Solutions**:
- Update API keys in configuration or environment variables
- Ensure authentication is properly configured for the deployment environment
- For Volcengine/Doubao, verify the model is enabled in the console
- Check account quota and billing status if receiving quota exceeded errors

**Section sources**
- [config.yaml](file://config/config.yaml#L192-L209)
- [auth.py](file://opencontext/server/middleware/auth.py#L1-L113)
- [llm_client.py](file://opencontext/llm/llm_client.py#L344-L466)

## Performance Problems

### High CPU/Memory Usage
**Symptoms**: MineContext process consumes excessive CPU or memory resources, potentially affecting system performance.

**Root Causes**:
- High screenshot capture frequency (short capture_interval)
- Large batch sizes for document processing
- Memory leaks in long-running processes
- Inefficient image processing or VLM calls

**Diagnostic Steps**:
1. Monitor resource usage through system monitoring tools
2. Check configuration for aggressive capture intervals:
```yaml
capture:
  screenshot:
    capture_interval: 5  # Lower values increase CPU usage
```
3. Review document processing batch sizes:
```yaml
processing:
  document_processor:
    batch_size: 3
  screenshot_processor:
    batch_size: 20
```
4. Analyze memory usage patterns over time to detect leaks

**Solutions**:
- Increase capture_interval to reduce screenshot frequency
- Optimize batch sizes based on system capabilities
- Implement proper resource cleanup in processing components
- Limit maximum image size for processing to reduce memory footprint

**Section sources**
- [config.yaml](file://config/config.yaml#L43-L47)
- [config.yaml](file://config/config.yaml#L79-L93)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L46-L57)
- [base_processor.py](file://opencontext/context_processing/processor/base_processor.py#L23-L261)

### Slow UI Response
**Symptoms**: User interface is unresponsive or slow to update, particularly during intensive operations.

**Root Causes**:
- Blocking operations on the main thread
- High-frequency updates from backend components
- Large data transfers between frontend and backend
- Inefficient rendering of UI components

**Diagnostic Steps**:
1. Check network traffic between frontend and backend
2. Monitor backend API response times
3. Examine frontend performance using browser developer tools
4. Review configuration for update frequencies

**Solutions**:
- Optimize data transfer between frontend and backend
- Implement debouncing for high-frequency updates
- Use pagination for large data sets in the UI
- Ensure long-running operations are performed asynchronously

**Section sources**
- [axiosConfig.ts](file://frontend/src/renderer/src/services/axiosConfig.ts#L1-L63)
- [config.yaml](file://config/config.yaml#L188-L191)
- [health.py](file://opencontext/server/routes/health.py#L1-L47)

## Platform-Specific Bugs

### Capture Permissions on macOS
**Symptoms**: Screen capture fails on macOS with permission errors despite correct configuration.

**Root Causes**:
- MineContext lacks screen recording permission in macOS Privacy settings
- Accessibility permissions not granted
- Application not properly signed or notarized

**Diagnostic Steps**:
1. Check System Settings > Privacy & Security > Screen Recording
2. Verify MineContext is listed and enabled
3. Check Accessibility permissions if window information is needed
4. Examine console logs for permission-related errors

**Solutions**:
1. Open System Settings > Privacy & Security
2. Scroll to Screen Recording and click the lock to make changes
3. Add MineContext to the allowed applications list
4. Restart MineContext after granting permissions
5. If issues persist, also grant Accessibility permissions

**Section sources**
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L72-L77)
- [config.yaml](file://config/config.yaml#L43-L47)

### Display Scaling Issues Affecting Screenshot Quality
**Symptoms**: Screenshots appear blurry or pixelated, particularly on high-DPI displays.

**Root Causes**:
- Display scaling settings not accounted for in screenshot capture
- Image resizing with inappropriate quality settings
- Maximum image size limits too restrictive

**Diagnostic Steps**:
1. Check display scaling settings in system preferences
2. Verify screenshot quality and resizing configuration:
```yaml
processing:
  screenshot_processor:
    max_image_size: 1920
    resize_quality: 85
```
3. Compare original screen content with captured images

**Solutions**:
- Adjust max_image_size to accommodate high-resolution displays
- Increase resize_quality for better image fidelity
- Consider disabling automatic resizing for high-DPI displays
- Ensure the screenshot library properly handles display scaling

**Section sources**
- [config.yaml](file://config/config.yaml#L88-L91)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L56-L57)
- [screenshot.py](file://opencontext/context_capture/screenshot.py#L277-L287)

### Network Configuration Problems Affecting AI Services
**Symptoms**: AI services are unreachable despite correct API configuration.

**Root Causes**:
- Corporate firewalls or proxy servers blocking outbound connections
- DNS resolution issues
- Incorrect proxy configuration
- Network isolation in containerized environments

**Diagnostic Steps**:
1. Test connectivity to LLM provider endpoints using command line tools
2. Check for proxy settings in the environment
3. Verify DNS resolution for provider domains
4. Examine network traffic for blocked connections

**Solutions**:
- Configure proxy settings if operating behind a corporate firewall
- Ensure DNS resolution is working properly
- Whitelist LLM provider domains in firewalls
- For containerized deployments, ensure proper network configuration

**Section sources**
- [config.yaml](file://config/config.yaml#L27-L28)
- [llm_client.py](file://opencontext/llm/llm_client.py#L38-L46)
- [axiosConfig.ts](file://frontend/src/renderer/src/services/axiosConfig.ts#L8-L16)

## Database and Configuration Recovery

### Database Corruption Recovery
**Symptoms**: Application fails to start or crashes with database-related errors.

**Root Causes**:
- SQLite database file corruption
- Incomplete writes due to unexpected shutdowns
- Version incompatibilities after updates

**Diagnostic Steps**:
1. Check logs for database connection errors
2. Verify database file integrity
3. Attempt to open the database file with a SQLite browser
4. Look for error messages indicating corruption

**Solutions**:
1. Stop MineContext if running
2. Locate the database file (typically in persist/sqlite/app.db)
3. Create a backup of the corrupted database
4. Use SQLite repair tools or restore from backup
5. If using ChromaDB, consider reinitializing the vector database

**Section sources**
- [unified_storage.py](file://opencontext/storage/unified_storage.py#L90-L800)
- [config.yaml](file://config/config.yaml#L146-L182)

### Configuration Reset Procedures
**Symptoms**: Application behaves unexpectedly due to corrupted or misconfigured settings.

**Root Causes**:
- Invalid YAML syntax in configuration files
- Missing required configuration parameters
- Environment variable conflicts

**Diagnostic Steps**:
1. Validate config.yaml syntax using a YAML validator
2. Compare current configuration with default template
3. Check for missing required fields
4. Verify environment variable substitution

**Solutions**:
1. Backup current configuration file
2. Replace with default config.yaml from installation
3. Gradually reintroduce custom settings
4. Validate configuration after each change
5. Use the global_config.py validation methods to test configuration

**Section sources**
- [config.yaml](file://config/config.yaml#L1-L253)
- [global_config.py](file://opencontext/config/global_config.py#L23-L331)
- [config.yaml](file://config/config.yaml#L14-L15)

## Troubleshooting Workflows

### Using regenerate_debug_file.py to Repair Data Issues
The regenerate_debug_file.py utility allows users to regenerate content from debug files and compare outputs, which is useful for diagnosing and repairing data issues.

**Usage**:
```bash
python examples/regenerate_debug_file.py --debug-file debug/generation/activity/2025-10-20_18-01-26.json
```

**Workflow**:
1. Locate the debug file containing the problematic generation
2. Run the regeneration script with the debug file path
3. Compare original and regenerated responses
4. Analyze differences to identify processing issues
5. Use insights to adjust prompts or processing parameters

**Example Output**:
```
================================================================================
TASK TYPE: activity
METADATA: {"timestamp": "2025-10-20T18:01:26", "model": "gpt-4"}
================================================================================

--------------------------------------------------------------------------------
ORIGINAL RESPONSE:
...
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
REGENERATED RESPONSE:
...
--------------------------------------------------------------------------------
```

The script saves a comparison file with the original and regenerated responses, enabling detailed analysis of generation differences.

**Section sources**
- [regenerate_debug_file.py](file://examples/regenerate_debug_file.py#L1-L180)
- [config.yaml](file://config/config.yaml#L219-L221)
- [llm_client.py](file://opencontext/llm/llm_client.py#L58-L62)