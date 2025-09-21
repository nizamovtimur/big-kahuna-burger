/**
 * Basic text sanitization utilities
 */

/**
 * Basic HTML sanitization - remove control characters
 * @param {string} html - HTML content to sanitize
 * @returns {string} - Sanitized HTML content
 */
export function sanitizeHtml(html) {
  if (!html || typeof html !== 'string') {
    return ''
  }
  
  // Remove control characters
  return html.replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '')
}

/**
 * Basic text sanitization - remove control characters
 * @param {string} text - Text content to sanitize
 * @returns {string} - Sanitized text content
 */
export function sanitizeText(text) {
  if (!text || typeof text !== 'string') {
    return ''
  }
  
  // Remove control characters and normalize whitespace
  return text
    .replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

/**
 * Basic user input sanitization
 * @param {string} input - User input to sanitize
 * @returns {string} - Sanitized input
 */
export function sanitizeInput(input) {
  if (!input || typeof input !== 'string') {
    return ''
  }
  
  // Basic sanitization - remove control characters and normalize
  return sanitizeText(input)
}

/**
 * Basic file upload validation
 * @param {File} file - File to validate
 * @returns {Object} - Validation result
 */
export function validateFileUpload(file) {
  const result = {
    isValid: false,
    error: null,
    sanitizedName: ''
  }
  
  if (!file) {
    result.error = 'No file provided'
    return result
  }
  
  // Check file size (10MB limit)
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    result.error = 'File size exceeds 10MB limit'
    return result
  }
  
  // Basic filename sanitization
  result.sanitizedName = sanitizeInput(file.name)
  if (!result.sanitizedName) {
    result.error = 'Invalid filename'
    return result
  }
  
  result.isValid = true
  return result
}

/**
 * Basic markdown rendering with sanitization
 * @param {string} markdown - Markdown content to render
 * @returns {string} - Sanitized HTML content
 */
export function safeMarkdownRender(markdown) {
  if (!markdown || typeof markdown !== 'string') {
    return ''
  }
  
  try {
    // First sanitize the markdown content
    const sanitizedMarkdown = sanitizeInput(markdown)
    
    // Then render as markdown and sanitize the result
    const { marked } = require('marked')
    const html = marked.parse(sanitizedMarkdown)
    
    return sanitizeHtml(html)
  } catch (error) {
    console.warn('Markdown rendering failed:', error)
    return sanitizeText(markdown)
  }
}
