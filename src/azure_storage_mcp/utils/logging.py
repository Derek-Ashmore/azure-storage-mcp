"""Structured logging configuration for Azure Storage MCP server."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredLogger:
    """Structured logger for Azure Storage MCP server."""
    
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create handler if it doesn't exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_tool_execution(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        result: Any, 
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """Log tool execution with structured data."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool_name": tool_name,
            "parameters": self._sanitize_parameters(parameters),
            "result_type": type(result).__name__ if result is not None else "None",
            "success": success,
            "error": error
        }
        
        if success:
            self.logger.info(json.dumps(log_entry))
        else:
            self.logger.error(json.dumps(log_entry))
    
    def log_authentication(
        self, 
        auth_method: str, 
        success: bool, 
        error: Optional[str] = None
    ) -> None:
        """Log authentication attempts."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "authentication",
            "auth_method": auth_method,
            "success": success,
            "error": error
        }
        
        if success:
            self.logger.info(json.dumps(log_entry))
        else:
            self.logger.warning(json.dumps(log_entry))
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log errors with context."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        self.logger.error(json.dumps(log_entry))
    
    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from parameters."""
        sanitized = {}
        sensitive_keys = {'password', 'secret', 'key', 'token', 'credential'}
        
        for key, value in parameters.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized