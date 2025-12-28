# Debugging Tools and Utilities

<cite>
**Referenced Files in This Document**   
- [debug_helper.py](file://opencontext/context_consumption/generation/debug_helper.py)
- [debug.py](file://opencontext/server/routes/debug.py)
- [debug.html](file://opencontext/web/templates/debug.html)
- [config.yaml](file://config/config.yaml)
- [global_config.py](file://opencontext/config/global_config.py)
- [regenerate_debug_file.py](file://examples/regenerate_debug_file.py)
- [settings.html](file://opencontext/web/templates/settings.html)
- [settings.js](file://opencontext/web/static/js/settings.js)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [DebugHelper Class](#debughelper-class)
3. /debug API Endpoints
4. [Debug HTML Template](#debug-html-template)
5. [Enabling Debug Mode](#enabling-debug-mode)
6. [Using Debug Tools](#using-debug-tools)
7. [Troubleshooting Guide](#troubleshooting-guide)

## Introduction
MineContext provides a comprehensive suite of debugging tools and utilities to assist developers and users in verifying system functionality, reproducing issues, and troubleshooting problems. These tools include the DebugHelper class for generating diagnostic reports and test data, a set of /debug API endpoints for introspection into the application state, and a debug HTML template for manual testing and troubleshooting. This document explains how to use these tools to inspect captured contexts, test AI completions, and validate data processing workflows.

## DebugHelper Class
The DebugHelper class is a utility designed to save generation messages and responses for debugging prompts. It is located in the `opencontext/context_consumption/generation/debug_helper.py` file and provides methods to check if debug mode is enabled, get the debug output path, serialize messages, and save generation debug information.

### Purpose and Functionality
The DebugHelper class serves several key purposes:
- **Check Debug Mode**: The `is_debug_enabled` method checks if debug mode is enabled by looking at the configuration.
- **Get Debug Output Path**: The `get_debug_output_path` method retrieves the debug output path from the configuration, expanding environment variables if necessary.
- **Serialize Messages**: The `_serialize_messages` method converts messages to a JSON-serializable format, handling both dictionary messages and ChatCompletionMessage objects.
- **Save Generation Debug**: The `save_generation_debug` method saves generation debug information to a file, including messages, responses, and metadata.

### Usage
To use the DebugHelper class, you need to ensure that debug mode is enabled in the configuration. Once enabled, the class will automatically save generation messages and responses to the specified output path. This can be particularly useful for debugging prompts and understanding the AI's decision-making process.

**Section sources**
- [debug_helper.py](file://opencontext/context_consumption/generation/debug_helper.py#L23-L156)

## /debug API Endpoints
The /debug API endpoints provide introspection into the application state, including context data, configuration, and processing pipelines. These endpoints are defined in the `opencontext/server/routes/debug.py` file and can be used to verify system functionality and reproduce issues.

### Available Endpoints
- **GET /api/debug/reports**: Retrieves SQLite report table data for debugging.
- **GET /api/debug/todos**: Retrieves SQLite todo table data for debugging.
- **GET /api/debug/activities**: Retrieves SQLite activity record table data for debugging.
- **GET /api/debug/tips**: Retrieves SQLite tips table data for debugging.
- **PATCH /api/debug/todos/{todo_id}**: Updates the status of a todo item for debugging.
- **POST /api/debug/generate/report**: Manually generates a daily report for debugging.
- **POST /api/debug/generate/activity**: Manually generates an activity record for debugging.
- **POST /api/debug/generate/tips**: Manually generates tips for debugging.
- **POST /api/debug/generate/todos**: Manually generates todos for debugging.
- **GET /api/debug/prompts/export**: Exports all generation prompts for debugging.
- **POST /api/debug/prompts/restore**: Restores prompts to a specified version for debugging.
- **GET /api/debug/prompts/{category}**: Retrieves prompts for a specified category for debugging.
- **POST /api/debug/prompts/{category}**: Updates prompts for a specified category for debugging.
- **POST /api/debug/generate/{category}/custom**: Generates content with custom prompts for debugging.

### Usage
These endpoints can be used to inspect the current state of the application, manually trigger generation tasks, and modify prompts for testing. For example, you can use the `GET /api/debug/reports` endpoint to retrieve a list of generated reports and their details, or use the `POST /api/debug/generate/report` endpoint to manually generate a daily report.

**Section sources**
- [debug.py](file://opencontext/server/routes/debug.py#L28-L691)

## Debug HTML Template
The debug HTML template, located in the `opencontext/web/templates/debug.html` file, provides a user-friendly interface for manual testing and troubleshooting. It includes tabs for viewing reports, todos, activities, and tips, as well as buttons for refreshing data and toggling todo statuses.

### Features
- **Data Display Tabs**: The template includes tabs for viewing reports, todos, activities, and tips, each with a count of items.
- **Refresh Buttons**: Each tab has a refresh button to reload the data.
- **Todo Status Toggle**: The todos tab includes a dropdown to filter by status and a button to toggle the status of individual todos.
- **Image Modal**: The activities tab includes a modal to view images in full size.
- **Alert Messages**: The template displays alert messages for successful and failed operations.

### Usage
To use the debug HTML template, navigate to the `/debug` endpoint in your browser. You can then use the tabs to view different types of data, refresh the data, and toggle todo statuses. This can be particularly useful for verifying that data is being captured and processed correctly.

**Section sources**
- [debug.html](file://opencontext/web/templates/debug.html#L1-L461)

## Enabling Debug Mode
Debug mode can be enabled through configuration and environment variables. This allows you to control whether debug information is saved and where it is stored.

### Configuration
To enable debug mode, you need to modify the `config.yaml` file. Specifically, you need to set the `content_generation.debug.enabled` flag to `true` and specify the `content_generation.debug.output_path` where debug files will be saved.

```yaml
content_generation:
  debug:
    enabled: true
    output_path: "${CONTEXT_PATH:.}/debug/generation"
```

### Environment Variables
The `CONTEXT_PATH` environment variable can be used to specify the base path for the debug output directory. If not set, the default value is the current directory (`.`).

### Usage
To enable debug mode, you can either modify the `config.yaml` file directly or set the `CONTEXT_PATH` environment variable. Once enabled, the DebugHelper class will save generation messages and responses to the specified output path.

**Section sources**
- [config.yaml](file://config/config.yaml#L219-L222)
- [global_config.py](file://opencontext/config/global_config.py#L44-L56)

## Using Debug Tools
The debug tools in MineContext can be used to inspect captured contexts, test AI completions, and validate data processing workflows. Here are some step-by-step examples of how to use these tools.

### Inspecting Captured Contexts
1. Navigate to the `/debug` endpoint in your browser.
2. Use the tabs to view reports, todos, activities, and tips.
3. Click the refresh button to reload the data.
4. Use the todo status toggle to mark todos as complete or incomplete.

### Testing AI Completions
1. Use the `POST /api/debug/generate/report` endpoint to manually generate a daily report.
2. Use the `POST /api/debug/generate/activity` endpoint to manually generate an activity record.
3. Use the `POST /api/debug/generate/tips` endpoint to manually generate tips.
4. Use the `POST /api/debug/generate/todos` endpoint to manually generate todos.

### Validating Data Processing Workflows
1. Use the `GET /api/debug/reports` endpoint to retrieve a list of generated reports.
2. Use the `GET /api/debug/todos` endpoint to retrieve a list of todos.
3. Use the `GET /api/debug/activities` endpoint to retrieve a list of activity records.
4. Use the `GET /api/debug/tips` endpoint to retrieve a list of tips.

### Example: Regenerating Content from a Debug File
1. Use the `regenerate_debug_file.py` script to regenerate content from a debug file.
2. Run the script with the `--debug-file` argument to specify the path to the debug file.
3. The script will load the debug file, regenerate the content using the same messages, and print a comparison of the original and regenerated responses.

```bash
python regenerate_debug_file.py --debug-file debug/generation/activity/2025-10-20_18-01-26.json
```

**Section sources**
- [regenerate_debug_file.py](file://examples/regenerate_debug_file.py#L1-L180)
- [debug.py](file://opencontext/server/routes/debug.py#L145-L691)

## Troubleshooting Guide
The debugging tools in MineContext can assist in identifying issues with context capture, AI integration, and data storage. Here are some common issues and how to troubleshoot them.

### Context Capture Issues
- **No Data Captured**: Check the `capture` section in the `config.yaml` file to ensure that the relevant capture modules (e.g., screenshot, folder_monitor) are enabled.
- **Incorrect Data**: Use the `/debug` endpoint to inspect the captured data and verify that it is correct.

### AI Integration Issues
- **Incorrect Prompts**: Use the `GET /api/debug/prompts/{category}` endpoint to retrieve the current prompts and verify that they are correct.
- **Failed Generation**: Use the `POST /api/debug/generate/{category}/custom` endpoint to test generation with custom prompts.

### Data Storage Issues
- **Missing Data**: Use the `/debug` endpoint to inspect the data in the SQLite tables and verify that it is being stored correctly.
- **Corrupted Data**: Use the `GET /api/debug/reports`, `GET /api/debug/todos`, `GET /api/debug/activities`, and `GET /api/debug/tips` endpoints to retrieve the data and verify its integrity.

By using these tools and following the steps outlined in this document, you can effectively debug and troubleshoot issues in MineContext.

**Section sources**
- [debug_helper.py](file://opencontext/context_consumption/generation/debug_helper.py#L23-L156)
- [debug.py](file://opencontext/server/routes/debug.py#L28-L691)
- [debug.html](file://opencontext/web/templates/debug.html#L1-L461)
- [config.yaml](file://config/config.yaml#L219-L222)
- [global_config.py](file://opencontext/config/global_config.py#L44-L56)
- [regenerate_debug_file.py](file://examples/regenerate_debug_file.py#L1-L180)