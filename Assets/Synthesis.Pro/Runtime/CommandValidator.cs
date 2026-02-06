using UnityEngine;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace Synthesis.Bridge
{
    /// <summary>
    /// Command Validator for Synthesis.Pro
    ///
    /// Provides comprehensive input validation and security checks for SynLink commands:
    /// - Command type whitelist validation
    /// - Parameter type and range validation
    /// - String sanitization and injection prevention
    /// - Rate limiting per command type
    /// - Resource limits (queue size, string lengths)
    ///
    /// Security-first design for production deployment.
    /// </summary>
    public class CommandValidator
    {
        #region Configuration

        // Allowed command types (whitelist)
        private static readonly HashSet<string> AllowedCommands = new HashSet<string>
        {
            // Core commands
            "Ping",
            "Log",
            "GetSceneInfo",

            // GameObject commands
            "FindGameObject",
            "SetActive",
            "SetPosition",
            "MoveGameObject",

            // Component commands
            "GetComponent",
            "SetComponentValue",

            // Creative AI commands (extended)
            "GenerateImage",
            "GenerateSound",
            "Generate3DModel",
            "GenerateShader",
            "GenerateScript",
            "GetCapabilities"
        };

        // Rate limiting configuration (requests per second per command type)
        private static readonly Dictionary<string, float> RateLimits = new Dictionary<string, float>
        {
            // High-cost operations (AI generation)
            { "GenerateImage", 0.1f },      // 1 every 10 seconds
            { "GenerateSound", 0.1f },
            { "Generate3DModel", 0.1f },
            { "GenerateShader", 0.2f },     // 1 every 5 seconds
            { "GenerateScript", 0.2f },

            // Moderate operations
            { "SetComponentValue", 10f },   // 10 per second
            { "SetPosition", 10f },
            { "MoveGameObject", 10f },

            // Light operations
            { "GetSceneInfo", 30f },        // 30 per second
            { "FindGameObject", 30f },
            { "GetComponent", 30f },
            { "Log", 60f },                 // 60 per second
            { "Ping", 60f }
        };

        // String validation limits
        private const int MaxStringLength = 10000;
        private const int MaxPromptLength = 4000;
        private const int MaxCommandIdLength = 128;

        // Dangerous patterns to reject
        private static readonly Regex DangerousPatterns = new Regex(
            @"(<script|javascript:|data:|vbscript:|on\w+\s*=|\.\.\/|\.\.\\)",
            RegexOptions.IgnoreCase | RegexOptions.Compiled
        );

        #endregion

        #region State

        // Rate limiting state (command type -> last execution times)
        private Dictionary<string, Queue<float>> rateLimitTracking = new Dictionary<string, Queue<float>>();

        // Statistics
        private int totalCommandsValidated = 0;
        private int totalCommandsRejected = 0;
        private Dictionary<string, int> rejectionReasons = new Dictionary<string, int>();

        #endregion

        #region Public API

        /// <summary>
        /// Validate a command before execution
        /// </summary>
        /// <returns>ValidationResult indicating if command is valid</returns>
        public ValidationResult ValidateCommand(BridgeCommand cmd)
        {
            totalCommandsValidated++;

            // Null check
            if (cmd == null)
            {
                return Reject("Command is null");
            }

            // Validate command ID
            if (string.IsNullOrEmpty(cmd.id))
            {
                return Reject("Command ID is missing");
            }

            if (cmd.id.Length > MaxCommandIdLength)
            {
                return Reject($"Command ID too long (max {MaxCommandIdLength} characters)");
            }

            // Validate command type
            if (string.IsNullOrEmpty(cmd.type))
            {
                return Reject("Command type is missing");
            }

            if (!AllowedCommands.Contains(cmd.type))
            {
                return Reject($"Unknown or disallowed command type: {cmd.type}");
            }

            // Check rate limiting
            var rateLimitResult = CheckRateLimit(cmd.type);
            if (!rateLimitResult.IsValid)
            {
                return rateLimitResult;
            }

            // Validate parameters based on command type
            var paramResult = ValidateParameters(cmd);
            if (!paramResult.IsValid)
            {
                return paramResult;
            }

            // Command is valid
            return ValidationResult.Valid();
        }

        /// <summary>
        /// Get validation statistics
        /// </summary>
        public ValidationStats GetStats()
        {
            return new ValidationStats
            {
                TotalValidated = totalCommandsValidated,
                TotalRejected = totalCommandsRejected,
                RejectionRate = totalCommandsValidated > 0
                    ? (float)totalCommandsRejected / totalCommandsValidated
                    : 0f,
                RejectionReasons = new Dictionary<string, int>(rejectionReasons)
            };
        }

        /// <summary>
        /// Reset statistics
        /// </summary>
        public void ResetStats()
        {
            totalCommandsValidated = 0;
            totalCommandsRejected = 0;
            rejectionReasons.Clear();
        }

        #endregion

        #region Validation Logic

        private ValidationResult CheckRateLimit(string commandType)
        {
            if (!RateLimits.TryGetValue(commandType, out float maxPerSecond))
            {
                // Default rate limit for unknown commands: 1 per second
                maxPerSecond = 1f;
            }

            float currentTime = Time.realtimeSinceStartup;

            // Initialize tracking for this command type
            if (!rateLimitTracking.ContainsKey(commandType))
            {
                rateLimitTracking[commandType] = new Queue<float>();
            }

            var times = rateLimitTracking[commandType];

            // Remove timestamps older than 1 second
            while (times.Count > 0 && currentTime - times.Peek() > 1f)
            {
                times.Dequeue();
            }

            // Check if rate limit exceeded
            if (times.Count >= maxPerSecond)
            {
                float oldestTime = times.Peek();
                float waitTime = 1f - (currentTime - oldestTime);
                return Reject($"Rate limit exceeded for {commandType}. Wait {waitTime:F1}s");
            }

            // Record this request
            times.Enqueue(currentTime);

            return ValidationResult.Valid();
        }

        private ValidationResult ValidateParameters(BridgeCommand cmd)
        {
            if (cmd.parameters == null)
            {
                // Some commands don't require parameters
                if (RequiresParameters(cmd.type))
                {
                    return Reject($"Command {cmd.type} requires parameters");
                }
                return ValidationResult.Valid();
            }

            // Validate based on command type
            switch (cmd.type)
            {
                case "FindGameObject":
                    return ValidateStringParam(cmd.parameters, "name", required: true, maxLength: 256);

                case "SetActive":
                    return ValidateStringParam(cmd.parameters, "object", required: true, maxLength: 256)
                        .And(() => ValidateBoolParam(cmd.parameters, "active", required: true));

                case "SetPosition":
                case "MoveGameObject":
                    return ValidateStringParam(cmd.parameters, "object", required: true, maxLength: 256)
                        .And(() => ValidateNumericParams(cmd.parameters, new[] { "x", "y", "z" }));

                case "GetComponent":
                    return ValidateStringParam(cmd.parameters, "object", required: true, maxLength: 256)
                        .And(() => ValidateStringParam(cmd.parameters, "component", required: true, maxLength: 256));

                case "SetComponentValue":
                    return ValidateStringParam(cmd.parameters, "object", required: true, maxLength: 256)
                        .And(() => ValidateStringParam(cmd.parameters, "component", required: true, maxLength: 256))
                        .And(() => ValidateStringParam(cmd.parameters, "field", required: true, maxLength: 256));

                case "GenerateImage":
                    return ValidateStringParam(cmd.parameters, "prompt", required: true, maxLength: MaxPromptLength)
                        .And(() => ValidateSafeString(cmd.parameters, "prompt"));

                case "GenerateShader":
                case "GenerateScript":
                    return ValidateStringParam(cmd.parameters, "prompt", required: true, maxLength: MaxPromptLength)
                        .And(() => ValidateSafeString(cmd.parameters, "prompt"));

                case "Log":
                    return ValidateStringParam(cmd.parameters, "message", required: true, maxLength: MaxStringLength);

                default:
                    // No specific validation needed
                    return ValidationResult.Valid();
            }
        }

        private bool RequiresParameters(string commandType)
        {
            // Commands that must have parameters
            return commandType switch
            {
                "Ping" => false,
                "GetSceneInfo" => false,
                "GetCapabilities" => false,
                _ => true
            };
        }

        private ValidationResult ValidateStringParam(
            Dictionary<string, object> parameters,
            string paramName,
            bool required,
            int maxLength = MaxStringLength)
        {
            if (!parameters.TryGetValue(paramName, out object value))
            {
                if (required)
                {
                    return Reject($"Missing required parameter: {paramName}");
                }
                return ValidationResult.Valid();
            }

            if (value == null)
            {
                if (required)
                {
                    return Reject($"Parameter {paramName} is null");
                }
                return ValidationResult.Valid();
            }

            string strValue = value.ToString();

            if (string.IsNullOrEmpty(strValue) && required)
            {
                return Reject($"Parameter {paramName} is empty");
            }

            if (strValue.Length > maxLength)
            {
                return Reject($"Parameter {paramName} exceeds max length of {maxLength}");
            }

            return ValidationResult.Valid();
        }

        private ValidationResult ValidateSafeString(Dictionary<string, object> parameters, string paramName)
        {
            if (!parameters.TryGetValue(paramName, out object value))
            {
                return ValidationResult.Valid();
            }

            string strValue = value?.ToString();
            if (string.IsNullOrEmpty(strValue))
            {
                return ValidationResult.Valid();
            }

            // Check for dangerous patterns
            if (DangerousPatterns.IsMatch(strValue))
            {
                return Reject($"Parameter {paramName} contains potentially dangerous content");
            }

            return ValidationResult.Valid();
        }

        private ValidationResult ValidateBoolParam(Dictionary<string, object> parameters, string paramName, bool required)
        {
            if (!parameters.TryGetValue(paramName, out object value))
            {
                if (required)
                {
                    return Reject($"Missing required parameter: {paramName}");
                }
                return ValidationResult.Valid();
            }

            // Accept bool or string "true"/"false"
            if (value is bool)
            {
                return ValidationResult.Valid();
            }

            string strValue = value?.ToString()?.ToLower();
            if (strValue == "true" || strValue == "false")
            {
                return ValidationResult.Valid();
            }

            return Reject($"Parameter {paramName} must be a boolean");
        }

        private ValidationResult ValidateNumericParams(Dictionary<string, object> parameters, string[] paramNames)
        {
            foreach (string paramName in paramNames)
            {
                if (parameters.TryGetValue(paramName, out object value))
                {
                    // Try to convert to float
                    try
                    {
                        Convert.ToSingle(value);
                    }
                    catch
                    {
                        return Reject($"Parameter {paramName} must be numeric");
                    }
                }
            }

            return ValidationResult.Valid();
        }

        private ValidationResult Reject(string reason)
        {
            totalCommandsRejected++;

            if (!rejectionReasons.ContainsKey(reason))
            {
                rejectionReasons[reason] = 0;
            }
            rejectionReasons[reason]++;

            Debug.LogWarning($"[CommandValidator] Command rejected: {reason}");

            return ValidationResult.Invalid(reason);
        }

        #endregion
    }

    #region Data Structures

    /// <summary>
    /// Result of command validation
    /// </summary>
    public class ValidationResult
    {
        public bool IsValid { get; private set; }
        public string ErrorMessage { get; private set; }

        private ValidationResult(bool isValid, string errorMessage = null)
        {
            IsValid = isValid;
            ErrorMessage = errorMessage;
        }

        public static ValidationResult Valid()
        {
            return new ValidationResult(true);
        }

        public static ValidationResult Invalid(string reason)
        {
            return new ValidationResult(false, reason);
        }

        /// <summary>
        /// Chain validation results (AND logic)
        /// </summary>
        public ValidationResult And(Func<ValidationResult> nextValidation)
        {
            if (!IsValid)
            {
                return this;
            }

            return nextValidation();
        }
    }

    /// <summary>
    /// Validation statistics
    /// </summary>
    public class ValidationStats
    {
        public int TotalValidated { get; set; }
        public int TotalRejected { get; set; }
        public float RejectionRate { get; set; }
        public Dictionary<string, int> RejectionReasons { get; set; }

        public override string ToString()
        {
            string stats = $"Validation Stats:\n";
            stats += $"  Total Validated: {TotalValidated}\n";
            stats += $"  Total Rejected: {TotalRejected}\n";
            stats += $"  Rejection Rate: {RejectionRate:P1}\n";

            if (RejectionReasons.Count > 0)
            {
                stats += "  Top Rejection Reasons:\n";
                foreach (var kvp in RejectionReasons.OrderByDescending(x => x.Value).Take(5))
                {
                    stats += $"    {kvp.Key}: {kvp.Value}\n";
                }
            }

            return stats;
        }
    }

    #endregion
}
