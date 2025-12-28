# Prompt Management (prompts_en.yaml, prompts_zh.yaml)

<cite>
**Referenced Files in This Document**   
- [prompts_en.yaml](file://config/prompts_en.yaml)
- [prompts_zh.yaml](file://config/prompts_zh.yaml)
- [prompt_manager.py](file://opencontext/config/prompt_manager.py)
- [global_config.py](file://opencontext/config/global_config.py)
- [document_text_chunker.py](file://opencontext/context_processing/chunker/document_text_chunker.py)
- [llm_client.py](file://opencontext/llm/llm_client.py)
- [enums.py](file://opencontext/models/enums.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prompt Configuration Schema](#prompt-configuration-schema)
3. [Prompt Types and Variables](#prompt-types-and-variables)
4. [PromptManager Implementation](#promptmanager-implementation)
5. [Integration with LLMClient](#integration-with-llmclient)
6. [Chunking Strategies and Semantic Context](#chunking-strategies-and-semantic-context)
7. [Customization and Language Variants](#customization-and-language-variants)
8. [Conclusion](#conclusion)

## Introduction
The OpenContext system utilizes structured prompt configuration files (`prompts_en.yaml` and `prompts_zh.yaml`) to define templates for various AI operations including context summarization, task generation, and insight extraction. These YAML files serve as the foundation for the system's intelligent context management capabilities, providing standardized templates that guide the behavior of different AI components throughout the workflow. The PromptManager class loads and interpolates these templates during agent workflows, integrating them with the LLMClient for dynamic content generation. This documentation provides a comprehensive analysis of the prompt configuration system, detailing its schema, implementation, and integration with other components.

**Section sources**
- [prompts_en.yaml](file://config/prompts_en.yaml#L1-L800)
- [prompts_zh.yaml](file://config/prompts_zh.yaml#L1-L800)

## Prompt Configuration Schema
The prompt configuration files follow a hierarchical YAML structure that organizes prompts by workflow phase and operation type. The schema is designed to support multiple languages with parallel files (`prompts_en.yaml` for English and `prompts_zh.yaml` for Chinese) that maintain identical structure but contain language-specific content. The root-level keys represent major workflow phases such as `chat_workflow`, `processing`, `merging`, and `generation`, each containing nested structures for specific operations.

Each prompt definition includes both `system` and `user` templates, which correspond to the system and user roles in the LLM conversation. The system prompts provide detailed instructions to the AI about its role, responsibilities, and operational principles, while user prompts define how user input and context variables should be formatted. The configuration supports variable interpolation through curly brace notation (e.g., `{query}`, `{current_time}`), allowing dynamic content injection based on runtime context.

The schema also includes specialized prompts for different AI operations such as intent analysis, context collection, execution, and merging. For example, the `chat_workflow` section contains prompts for `intent_analysis`, `query_classification`, and `executor` operations, each with their own system and user templates. Similarly, the `processing` section includes prompts for `extraction` operations, particularly for analyzing screenshots and extracting structured context.

**Section sources**
- [prompts_en.yaml](file://config/prompts_en.yaml#L6-L800)
- [prompts_zh.yaml](file://config/prompts_zh.yaml#L6-L800)

## Prompt Types and Variables
The prompt configuration system defines several types of prompts that serve different purposes in the AI workflow. The primary distinction is between `system` prompts, which define the AI's role and behavior, and `user` prompts, which format user input and context for processing. System prompts are typically longer and more detailed, providing comprehensive instructions about the AI's responsibilities, operational principles, and output requirements.

Key prompt types include:
- **Intent Analysis**: Guides the AI in understanding and optimizing user queries
- **Query Classification**: Determines whether a query requires information retrieval or is simple social interaction
- **Executor Operations**: Handles content generation, editing, and answering tasks
- **Context Collection**: Manages the intelligent selection and calling of retrieval tools
- **Processing and Extraction**: Analyzes screenshots and other inputs to extract structured context
- **Merging**: Combines multiple context items into comprehensive summaries

The system supports numerous variables that are dynamically replaced during prompt interpolation. Common variables include `{query}` (the user's original query), `{current_time}` (the current timestamp), `{chat_history}` (conversation context), `{enhancement_results}` (entity information), and `{selected_content}` (user-selected text). More specialized variables include `{collected_contexts}` (retrieved context information), `{current_document}` (the active document), and `{document_id}` (identifier for the current document).

These variables enable the creation of dynamic prompts that incorporate relevant context from the user's current session, allowing the AI to generate more accurate and contextually appropriate responses. The variable system supports complex workflows where information flows between different stages of processing, with each stage building upon the output of previous stages.

**Section sources**
- [prompts_en.yaml](file://config/prompts_en.yaml#L8-L221)
- [prompts_zh.yaml](file://config/prompts_zh.yaml#L8-L221)

## PromptManager Implementation
The PromptManager class is responsible for loading, managing, and retrieving prompt templates from the configuration files. Implemented in `prompt_manager.py`, this class provides a clean interface for accessing prompts throughout the application. The PromptManager is initialized with a path to a prompt configuration file, which it loads using PyYAML's `safe_load` method to parse the YAML content into a Python dictionary.

The core functionality of PromptManager includes:
- `get_prompt(name, default)`: Retrieves a specific prompt by dot-notation path (e.g., "chat_workflow.intent_analysis.system")
- `get_prompt_group(name)`: Returns all prompts within a specified group as a dictionary
- `load_user_prompts()`: Loads and merges user-customized prompts from a separate file
- `save_prompts(prompts_data)`: Saves user-defined prompts to a custom file
- `import_prompts(yaml_content)`: Imports prompts from YAML content
- `reset_user_prompts()`: Resets user prompts to default values

The class implements a deep merge strategy when loading user prompts, allowing users to override specific prompts without replacing the entire configuration. This enables customization while maintaining the integrity of the overall prompt structure. The PromptManager also handles multi-line string formatting in YAML output, using literal style (|) for prompts containing newlines or exceeding 80 characters to preserve formatting.

The PromptManager integrates with the GlobalConfig singleton, which manages the overall application configuration. GlobalConfig initializes the PromptManager based on the language setting in the main configuration file, automatically loading either `prompts_en.yaml` or `prompts_zh.yaml`. This integration ensures that the correct language-specific prompts are used throughout the application.

**Section sources**
- [prompt_manager.py](file://opencontext/config/prompt_manager.py#L17-L220)
- [global_config.py](file://opencontext/config/global_config.py#L114-L149)

## Integration with LLMClient
The prompt system integrates with the LLMClient class to enable dynamic content generation in agent workflows. The LLMClient, defined in `llm_client.py`, serves as an abstraction layer for interacting with different LLM providers (OpenAI, Doubao) and handles the actual API calls to generate responses. When an agent workflow requires AI processing, it retrieves the appropriate prompt templates through the GlobalConfig's convenience functions and formats them with the necessary context variables.

The integration follows a standard pattern:
1. Retrieve prompt templates using `get_prompt_group()` or `get_prompt()`
2. Format the prompts by replacing variables with actual values
3. Construct a messages array with system and user roles
4. Pass the messages to the LLMClient for processing
5. Handle the response and extract the generated content

For example, in the context agent's workflow, the `analyze_and_plan_tools` method retrieves the tool analysis prompts, formats them with the current query, enhanced query, and existing context, then passes them to the LLM for processing. The LLMClient handles the API call, including error handling, token usage recording, and response parsing.

The system supports both synchronous and asynchronous operations, with streaming capabilities for real-time response generation. The LLMClient also handles provider-specific features, such as Doubao's thinking parameter, through conditional logic in the request preparation phase. This integration enables seamless use of the prompt templates across different components and workflows within the OpenContext system.

**Section sources**
- [llm_client.py](file://opencontext/llm/llm_client.py#L32-L466)
- [global_config.py](file://opencontext/config/global_config.py#L273-L281)
- [llm_context_strategy.py](file://opencontext/context_consumption/context_agent/core/llm_context_strategy.py#L52-L75)

## Chunking Strategies and Semantic Context
The prompt system includes specialized templates for intelligent text chunking, which plays a crucial role in processing and analyzing document content. The `text_chunking` and `global_semantic_chunking` prompts in the configuration files define how the system should split text into semantically complete, independently understandable chunks. These prompts emphasize semantic completeness over strict length limits, prioritizing the preservation of context and meaning.

The chunking strategy implemented in `document_text_chunker.py` uses these prompts to guide the LLM in splitting text based on semantic boundaries. For shorter documents (<10,000 characters), the system uses global semantic chunking, where the LLM analyzes the entire document at once to identify optimal split points. For longer documents, it falls back to a paragraph-based accumulation strategy with LLM-assisted splitting of oversized buffers.

The chunking prompts include detailed principles and examples to guide the LLM:
- **Semantic Completeness First**: Each chunk must be a semantically complete unit
- **Preserve Context**: Add necessary context when splitting would cause loss of subject or topic
- **Structure Recognition**: Identify and maintain structural integrity of titles, lists, and paragraphs
- **Length Balance**: Only subdivide when content is very long, prioritizing completeness

The system also includes context type descriptions from `enums.py` that are injected into prompts to help the LLM understand the different types of context it may encounter. These descriptions cover entity context, activity context, intent context, semantic context, procedural context, and state context, each with specific identification indicators and examples. This semantic context enables the system to process and organize information more effectively, supporting advanced features like context merging and intelligent retrieval.

**Section sources**
- [prompts_en.yaml](file://config/prompts_en.yaml#L1571-L1690)
- [document_text_chunker.py](file://opencontext/context_processing/chunker/document_text_chunker.py#L25-L349)
- [enums.py](file://opencontext/models/enums.py#L293-L332)

## Customization and Language Variants
The prompt system supports extensive customization through user-defined prompts and multiple language variants. Users can create custom prompts by modifying the `user_prompts_en.yaml` or `user_prompts_zh.yaml` files, which are automatically loaded and merged with the base configuration. The PromptManager's `load_user_prompts()` method handles this process, performing a deep merge that allows users to override specific prompts without affecting others.

The system maintains parallel language variants through separate configuration files (`prompts_en.yaml` and `prompts_zh.yaml`) that mirror each other's structure. The GlobalConfig class determines which file to load based on the language setting in the main configuration. Users can switch between languages through the `set_language()` method, which reloads the appropriate prompt file and updates the PromptManager instance.

Customization options include:
- Creating new prompt templates for specialized use cases
- Modifying existing prompts to change AI behavior
- Adding new variables to support additional context
- Adjusting chunking strategies for specific document types
- Fine-tuning context type descriptions for domain-specific knowledge

The system also provides import and export functionality through the `import_prompts()` and `export_prompts()` methods, allowing users to share and backup their custom prompt configurations. This flexibility enables the OpenContext system to adapt to different use cases and user preferences while maintaining consistency across language variants.

**Section sources**
- [prompt_manager.py](file://opencontext/config/prompt_manager.py#L75-L148)
- [global_config.py](file://opencontext/config/global_config.py#L201-L234)

## Conclusion
The prompt configuration system in OpenContext provides a robust framework for defining and managing AI behavior across multiple languages and use cases. Through the structured YAML files (`prompts_en.yaml` and `prompts_zh.yaml`), the system establishes clear guidelines for AI operations including context summarization, task generation, and insight extraction. The PromptManager class enables efficient loading and interpolation of these templates, while integration with the LLMClient facilitates dynamic content generation in agent workflows.

The system's support for chunking strategies and semantic context injection enhances its ability to process complex documents and extract meaningful information. By leveraging context type descriptions and intelligent splitting algorithms, the system maintains the integrity of information while enabling efficient retrieval and analysis. The customization capabilities and language variant support make the system adaptable to diverse user needs and preferences.

This comprehensive prompt management system forms the foundation of OpenContext's intelligent context management capabilities, enabling sophisticated AI interactions that are both contextually aware and linguistically flexible.