/**
 * AI-Powered Code Optimizer
 * Uses OpenAI to intelligently apply Maximo best practices while preserving functionality
 */

const OpenAI = require('openai');

class AIOptimizer {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }

  /**
   * Intelligently optimize Maximo script using AI
   * Preserves functionality while applying best practices
   */
  async optimizeScript(source, scriptLanguage, analysis) {
    const improvements = [];
    
    // Identify what needs to be optimized
    const optimizationNeeds = this.identifyOptimizationNeeds(source, analysis);
    
    if (optimizationNeeds.length === 0) {
      // No optimizations needed, return original with header
      return {
        optimizedCode: this.addOptimizationHeader(source, ['No optimizations needed']),
        improvements: ['Script already follows best practices']
      };
    }

    // Use AI to apply optimizations intelligently
    const optimizedCode = await this.applyAIOptimizations(
      source,
      scriptLanguage,
      optimizationNeeds,
      improvements
    );

    return {
      optimizedCode,
      improvements
    };
  }

  /**
   * Identify what optimizations are needed
   */
  identifyOptimizationNeeds(source, analysis) {
    const needs = [];

    // Check for multiple count() calls
    if ((source.match(/\.count\(\)/g) || []).length > 1) {
      needs.push('cache_count_calls');
    }

    // Check for missing MboSet cleanup
    if (source.includes('getMboSet') && !source.includes('close()')) {
      needs.push('add_mboset_cleanup');
    }

    // Check for missing error handling
    if (!source.includes('try') && !source.includes('except') && !source.includes('catch')) {
      needs.push('add_error_handling');
    }

    // Check for logging without level check
    if (source.includes('service.log(') && !source.includes('isLoggingEnabled')) {
      needs.push('add_logging_check');
    }

    // Check for UIContext optimization opportunity
    if (analysis.metrics.lineCount > 30 && !source.includes('UIContext')) {
      needs.push('add_uicontext_check');
    }

    // Check for transaction management
    if (source.includes('MXServer.getMXServer().getMboSet') && !source.includes('getMXTransaction')) {
      needs.push('add_transaction_management');
    }

    return needs;
  }

  /**
   * Use OpenAI to intelligently apply optimizations
   */
  async applyAIOptimizations(source, scriptLanguage, optimizationNeeds, improvements) {
    const prompt = this.buildOptimizationPrompt(source, scriptLanguage, optimizationNeeds);

    try {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are an expert IBM Maximo automation script optimizer. Your task is to apply best practices while preserving the exact functionality of the original code. You must generate syntactically valid, production-ready code.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.3, // Lower temperature for more consistent, reliable output
        max_tokens: 4000
      });

      const optimizedCode = response.choices[0].message.content;
      
      // Extract the code from markdown if present
      const codeMatch = optimizedCode.match(/```(?:python|javascript)?\n([\s\S]*?)\n```/);
      const cleanCode = codeMatch ? codeMatch[1] : optimizedCode;

      // Add improvements based on what was optimized
      optimizationNeeds.forEach(need => {
        improvements.push(this.getImprovementDescription(need));
      });

      // Add header
      return this.addOptimizationHeader(cleanCode, improvements);

    } catch (error) {
      console.error('AI optimization error:', error);
      // Fallback to original code with header
      improvements.push('AI optimization unavailable, returning original code');
      return this.addOptimizationHeader(source, improvements);
    }
  }

  /**
   * Build optimization prompt for AI
   */
  buildOptimizationPrompt(source, scriptLanguage, optimizationNeeds) {
    const needsDescription = optimizationNeeds.map(need => {
      switch (need) {
        case 'cache_count_calls':
          return '- Cache MboSet.count() results to avoid multiple SQL queries';
        case 'add_mboset_cleanup':
          return '- Add proper MboSet cleanup in finally block to prevent memory leaks';
        case 'add_error_handling':
          return '- Add comprehensive error handling with try-catch/try-except';
        case 'add_logging_check':
          return '- Add logging level check before logging calls';
        case 'add_uicontext_check':
          return '- Add UIContext check to skip expensive operations in List tab';
        case 'add_transaction_management':
          return '- Add MboSets to encompassing transaction';
        default:
          return `- Apply ${need}`;
      }
    }).join('\n');

    return `Optimize this IBM Maximo ${scriptLanguage} automation script by applying the following best practices:

${needsDescription}

CRITICAL REQUIREMENTS:
1. Preserve the EXACT functionality of the original code
2. Generate syntactically valid ${scriptLanguage} code
3. Maintain proper indentation (4 spaces for Python, 2 for JavaScript)
4. Do NOT add explanatory comments about the optimizations
5. Do NOT add TODO comments
6. Keep the code clean and production-ready
7. Ensure all variables are properly scoped
8. Maintain the original code structure as much as possible

ORIGINAL CODE:
\`\`\`${scriptLanguage}
${source}
\`\`\`

Return ONLY the optimized code without any explanations or markdown formatting.`;
  }

  /**
   * Get improvement description for a specific optimization
   */
  getImprovementDescription(need) {
    const descriptions = {
      'cache_count_calls': 'Cached count() results',
      'add_mboset_cleanup': 'Added MboSet cleanup',
      'add_error_handling': 'Added error handling',
      'add_logging_check': 'Added logging level check',
      'add_uicontext_check': 'Added UIContext check',
      'add_transaction_management': 'Added transaction management'
    };
    return descriptions[need] || need;
  }

  /**
   * Add optimization header to code
   */
  addOptimizationHeader(code, improvements) {
    const isPython = code.includes('def ') || code.includes('import ');
    const commentChar = isPython ? '#' : '//';
    
    const header = [
      `${commentChar} Optimized by IBM Bob`,
      `${commentChar} Optimizations: ${improvements.join(', ')}`,
      ''
    ].join('\n');

    return header + code;
  }
}

module.exports = new AIOptimizer();

// Made with Bob
