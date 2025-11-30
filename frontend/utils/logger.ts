/**
 * Configurable logging system for the piano roll component.
 * Replaces scattered console.log calls with a structured, level-based logger.
 */

/**
 * Log levels in order of verbosity (most verbose to least verbose)
 */
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  SILENT = 4,
}

/**
 * Map of log level names for display
 */
const LOG_LEVEL_NAMES: Record<LogLevel, string> = {
  [LogLevel.DEBUG]: 'DEBUG',
  [LogLevel.INFO]: 'INFO',
  [LogLevel.WARN]: 'WARN',
  [LogLevel.ERROR]: 'ERROR',
  [LogLevel.SILENT]: 'SILENT',
};

/**
 * Map of log level prefixes with emojis for visual distinction
 */
const LOG_LEVEL_PREFIXES: Record<LogLevel, string> = {
  [LogLevel.DEBUG]: '🔍',
  [LogLevel.INFO]: 'ℹ️',
  [LogLevel.WARN]: '⚠️',
  [LogLevel.ERROR]: '❌',
  [LogLevel.SILENT]: '',
};

/**
 * Global configuration for the logging system
 */
interface LoggerConfig {
  /** Current global log level */
  level: LogLevel;
  /** Whether to include timestamps in log messages */
  includeTimestamp: boolean;
  /** Whether to include the logger name in log messages */
  includeLoggerName: boolean;
  /** Custom log handler (for testing or custom output) */
  customHandler?: (level: LogLevel, name: string, message: string, ...args: unknown[]) => void;
}

/**
 * Global logger configuration
 */
const globalConfig: LoggerConfig = {
  level: LogLevel.WARN, // Default to WARN in production
  includeTimestamp: false,
  includeLoggerName: true,
};

/**
 * Set the global log level
 * @param level - The log level to set
 */
export function setLogLevel(level: LogLevel): void {
  globalConfig.level = level;
}

/**
 * Get the current global log level
 * @returns The current log level
 */
export function getLogLevel(): LogLevel {
  return globalConfig.level;
}

/**
 * Enable debug mode (sets log level to DEBUG)
 */
export function enableDebugMode(): void {
  globalConfig.level = LogLevel.DEBUG;
}

/**
 * Disable all logging (sets log level to SILENT)
 */
export function disableLogging(): void {
  globalConfig.level = LogLevel.SILENT;
}

/**
 * Configure the logger
 * @param config - Partial configuration to apply
 */
export function configureLogger(config: Partial<LoggerConfig>): void {
  Object.assign(globalConfig, config);
}

/**
 * Logger class for structured logging
 */
export class Logger {
  private name: string;

  /**
   * Create a new logger instance
   * @param name - The name of this logger (typically the component/module name)
   */
  constructor(name: string) {
    this.name = name;
  }

  /**
   * Format a log message with optional metadata
   */
  private formatMessage(level: LogLevel, message: string): string {
    const parts: string[] = [];

    if (globalConfig.includeTimestamp) {
      parts.push(`[${new Date().toISOString()}]`);
    }

    parts.push(LOG_LEVEL_PREFIXES[level]);

    if (globalConfig.includeLoggerName) {
      parts.push(`[${this.name}]`);
    }

    parts.push(message);

    return parts.join(' ');
  }

  /**
   * Check if a log level should be output
   */
  private shouldLog(level: LogLevel): boolean {
    return level >= globalConfig.level;
  }

  /**
   * Log at DEBUG level
   * @param message - The message to log
   * @param args - Additional arguments to log
   */
  debug(message: string, ...args: unknown[]): void {
    if (!this.shouldLog(LogLevel.DEBUG)) return;

    if (globalConfig.customHandler) {
      globalConfig.customHandler(LogLevel.DEBUG, this.name, message, ...args);
      return;
    }

    console.log(this.formatMessage(LogLevel.DEBUG, message), ...args);
  }

  /**
   * Log at INFO level
   * @param message - The message to log
   * @param args - Additional arguments to log
   */
  info(message: string, ...args: unknown[]): void {
    if (!this.shouldLog(LogLevel.INFO)) return;

    if (globalConfig.customHandler) {
      globalConfig.customHandler(LogLevel.INFO, this.name, message, ...args);
      return;
    }

    console.info(this.formatMessage(LogLevel.INFO, message), ...args);
  }

  /**
   * Log at WARN level
   * @param message - The message to log
   * @param args - Additional arguments to log
   */
  warn(message: string, ...args: unknown[]): void {
    if (!this.shouldLog(LogLevel.WARN)) return;

    if (globalConfig.customHandler) {
      globalConfig.customHandler(LogLevel.WARN, this.name, message, ...args);
      return;
    }

    console.warn(this.formatMessage(LogLevel.WARN, message), ...args);
  }

  /**
   * Log at ERROR level
   * @param message - The message to log
   * @param args - Additional arguments to log
   */
  error(message: string, ...args: unknown[]): void {
    if (!this.shouldLog(LogLevel.ERROR)) return;

    if (globalConfig.customHandler) {
      globalConfig.customHandler(LogLevel.ERROR, this.name, message, ...args);
      return;
    }

    console.error(this.formatMessage(LogLevel.ERROR, message), ...args);
  }

  /**
   * Create a child logger with a prefixed name
   * @param childName - The child logger name
   * @returns A new Logger instance
   */
  child(childName: string): Logger {
    return new Logger(`${this.name}:${childName}`);
  }
}

/**
 * Create a logger for a specific component/module
 * @param name - The name of the component/module
 * @returns A Logger instance
 *
 * @example
 * const log = createLogger('PianoRoll');
 * log.debug('Initializing component');
 * log.info('Component mounted');
 * log.warn('Deprecated API used');
 * log.error('Failed to load audio data');
 */
export function createLogger(name: string): Logger {
  return new Logger(name);
}

/**
 * Default logger instance for quick usage
 */
export const defaultLogger = new Logger('PianoRoll');

// Auto-detect development mode and enable debug logging
if (typeof window !== 'undefined') {
  // Check for debug flag in URL or localStorage
  const urlParams = new URLSearchParams(window.location?.search || '');
  const debugEnabled =
    urlParams.get('debug') === 'true' ||
    localStorage?.getItem('pianoroll_debug') === 'true';

  if (debugEnabled) {
    enableDebugMode();
    defaultLogger.info('Debug mode enabled via URL/localStorage');
  }
}
