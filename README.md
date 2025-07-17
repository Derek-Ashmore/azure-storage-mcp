# azure-storage-mcp

A Python MCP (Model Context Protocol) server that provides read-only access to Azure Storage Account information. This server enables AI assistants to query and analyze Azure Storage infrastructure through a standardized interface.

## Overview

This MCP server connects to Azure using the Azure SDK for Python and provides tools to list and inspect storage accounts across subscriptions, returning comprehensive details including configuration, security settings, and network topology.

## Project Documentation

### [INITIAL.md](./INITIAL.md) - Initial Requirements Specification
The `INITIAL.md` file contains the complete specification for the initial revision of this MCP server, including:

- **Core Functionality**: Azure SDK integration and storage account inspection capabilities
- **Required Tools**: Five essential MCP tools for storage account management
- **Data Requirements**: Comprehensive storage account details to be returned
- **Authentication**: Support for Azure CLI, managed identity, and service principal authentication
- **Output Format**: Structured JSON data with metadata and human-readable summaries

### [COMMANDS.md](./COMMANDS.md) - Claude-Flow Instructions
The `COMMANDS.md` file contains the specific instructions being provided to Claude-Flow for the development process, including:

- Technical implementation planning using Test-Driven Development (TDD)
- Python development with pip installation and UV packaging manager
- Research and planning phase commands

## Key Features

- **Multi-subscription Support**: Access storage accounts across multiple Azure subscriptions
- **Comprehensive Data**: Retrieve detailed storage account information including security, network, and performance metrics
- **Production Ready**: Proper logging, error handling, and MCP protocol compliance
- **Flexible Authentication**: Support for various Azure authentication methods

## Development Status

This project is currently in the planning and research phase, with Claude-Flow working on the technical implementation plan based on the requirements specified in `INITIAL.md`.

## Getting Started

*Development setup instructions will be added once the implementation plan is complete.*

## License

[License information to be added]