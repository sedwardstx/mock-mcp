# Introduction

This document outlines the overall project architecture for the **Contoso Support Ticketing MCP Server**, including backend systems, the mock data layer, and non-UI concerns. Its primary goal is to serve as the guiding architectural blueprint for AI-driven development, ensuring consistency and adherence to chosen patterns and technologies.

**Relationship to Frontend Architecture:** N/A. This is a headless MCP server with no user interface. Students connect their own AI agents/Skills via the MCP protocol.

## Starter Template or Existing Project

**N/A — greenfield.** No starter template is used. The project is built from scratch on the official Python MCP SDK. The repository already exists (containing BMAD tooling and docs); application code will be added under `src/`. Manual setup of tooling and configuration is expected and documented in the Source Tree and Infrastructure sections.

## Change Log

| Date       | Version | Description                          | Author         |
|------------|---------|--------------------------------------|----------------|
| 2026-07-23 | 1.0     | Initial architecture from PRD        | Winston (Arch) |
