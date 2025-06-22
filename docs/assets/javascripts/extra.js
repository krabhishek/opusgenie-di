/**
 * Extra JavaScript for OpusGenie DI Documentation
 * Enhances user experience with interactive features
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize OgPgy Bank documentation features
    initBankingFeatures();
    
    // Initialize code example interactions
    initCodeExamples();
    
    // Initialize team member interactions
    initTeamMemberFeatures();
    
    // Initialize performance metrics
    initMetrics();
});

/**
 * Initialize banking-specific features
 */
function initBankingFeatures() {
    // Add banking context indicators
    addContextIndicators();
    
    // Initialize banking flow animations
    initBankingFlowAnimations();
}

/**
 * Add visual indicators for different banking contexts
 */
function addContextIndicators() {
    const contextMappings = {
        'customer': { icon: '👥', color: '#1565C0', name: 'Customer Context' },
        'account': { icon: '💳', color: '#2E7D32', name: 'Account Context' },
        'payment': { icon: '💰', color: '#F57C00', name: 'Payment Context' },
        'compliance': { icon: '📋', color: '#C2185B', name: 'Compliance Context' },
        'infrastructure': { icon: '🏗️', color: '#00695C', name: 'Infrastructure Context' }
    };
    
    // Find code blocks with context indicators
    document.querySelectorAll('pre code').forEach(function(codeBlock) {
        const content = codeBlock.textContent;
        
        // Check for context patterns
        Object.keys(contextMappings).forEach(function(context) {
            const pattern = new RegExp(`@og_context\\([^)]*name=["']${context}[^"']*["']`, 'i');
            if (pattern.test(content)) {
                const mapping = contextMappings[context];
                const indicator = document.createElement('div');
                indicator.className = 'context-indicator';
                indicator.innerHTML = `
                    <span class="context-icon">${mapping.icon}</span>
                    <span class="context-name">${mapping.name}</span>
                `;
                indicator.style.cssText = `
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    background: ${mapping.color};
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                    z-index: 10;
                `;
                
                const pre = codeBlock.closest('pre');
                if (pre) {
                    pre.style.position = 'relative';
                    pre.appendChild(indicator);
                }
            }
        });
    });
}

/**
 * Initialize banking flow animations
 */
function initBankingFlowAnimations() {
    // Animate sequence diagrams when they come into view
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const mermaid = entry.target.querySelector('.mermaid');
                if (mermaid) {
                    mermaid.style.animation = 'slideInUp 0.6s ease-out';
                }
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.mermaid').forEach(function(element) {
        observer.observe(element.parentElement);
    });
}

/**
 * Initialize code example interactions
 */
function initCodeExamples() {
    // Add copy buttons to code blocks
    addCopyButtons();
    
    // Add example runners for simple examples
    addExampleRunners();
    
    // Initialize code comparison features
    initCodeComparisons();
}

/**
 * Add copy buttons to code blocks
 */
function addCopyButtons() {
    document.querySelectorAll('pre code').forEach(function(codeBlock) {
        const pre = codeBlock.closest('pre');
        if (!pre || pre.querySelector('.copy-button')) return;
        
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.innerHTML = '📋';
        button.title = 'Copy code';
        button.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0,0,0,0.1);
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            opacity: 0;
            transition: opacity 0.2s;
        `;
        
        pre.style.position = 'relative';
        pre.appendChild(button);
        
        pre.addEventListener('mouseenter', function() {
            button.style.opacity = '1';
        });
        
        pre.addEventListener('mouseleave', function() {
            button.style.opacity = '0';
        });
        
        button.addEventListener('click', function() {
            navigator.clipboard.writeText(codeBlock.textContent).then(function() {
                button.innerHTML = '✅';
                setTimeout(function() {
                    button.innerHTML = '📋';
                }, 1000);
            });
        });
    });
}

/**
 * Add example runners for simple code examples
 */
function addExampleRunners() {
    // This would be implemented to provide interactive code execution
    // For now, we'll just mark runnable examples
    document.querySelectorAll('pre code').forEach(function(codeBlock) {
        const content = codeBlock.textContent;
        
        // Simple heuristic for runnable examples
        if (content.includes('from opusgenie_di import') && 
            content.includes('def main()') && 
            content.length < 2000) {
            
            const runButton = document.createElement('button');
            runButton.className = 'run-example';
            runButton.innerHTML = '▶️ Run Example';
            runButton.style.cssText = `
                margin-top: 8px;
                padding: 6px 12px;
                background: #2E7D32;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            `;
            
            runButton.addEventListener('click', function() {
                // In a real implementation, this would execute the code
                runButton.innerHTML = '✅ Example would run here';
                setTimeout(function() {
                    runButton.innerHTML = '▶️ Run Example';
                }, 2000);
            });
            
            codeBlock.closest('pre').parentNode.insertBefore(runButton, codeBlock.closest('pre').nextSibling);
        }
    });
}

/**
 * Initialize code comparison features
 */
function initCodeComparisons() {
    // Enhance tabbed code comparisons
    document.querySelectorAll('.tabbed-set').forEach(function(tabbedSet) {
        const labels = tabbedSet.querySelectorAll('.tabbed-label');
        
        labels.forEach(function(label) {
            if (label.textContent.includes('✅')) {
                label.style.color = '#2E7D32';
                label.style.fontWeight = 'bold';
            } else if (label.textContent.includes('❌')) {
                label.style.color = '#C62828';
                label.style.fontWeight = 'bold';
            }
        });
    });
}

/**
 * Initialize team member features
 */
function initTeamMemberFeatures() {
    // Add team member profile photos (placeholder)
    document.querySelectorAll('.admonition-title').forEach(function(title) {
        const teamMembers = {
            'Elena Korvas': '👩‍💼',
            'Marcus Chen': '👨‍💼',
            'Priya Nakamura': '👩‍💻',
            'Sofia Ramos': '👩‍🎨',
            'Jake Morrison': '👨‍🔧',
            'Maria Santos': '👩‍🎨',
            'David Kim': '👨‍🍳',
            'Inspector Torres': '👮‍♀️'
        };
        
        Object.keys(teamMembers).forEach(function(name) {
            if (title.textContent.includes(name)) {
                const avatar = document.createElement('span');
                avatar.innerHTML = teamMembers[name];
                avatar.style.marginRight = '8px';
                title.insertBefore(avatar, title.firstChild);
            }
        });
    });
}

/**
 * Initialize performance metrics display
 */
function initMetrics() {
    // Animate metric cards when they come into view
    const metricObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const metricValue = entry.target.querySelector('.metric-value');
                if (metricValue) {
                    animateCountUp(metricValue);
                }
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('.metric-card').forEach(function(card) {
        metricObserver.observe(card);
    });
}

/**
 * Animate count-up for metric values
 */
function animateCountUp(element) {
    const targetText = element.textContent;
    const targetValue = parseFloat(targetText.replace(/[^0-9.]/g, ''));
    
    if (isNaN(targetValue)) return;
    
    const duration = 1000; // 1 second
    const steps = 30;
    const increment = targetValue / steps;
    let current = 0;
    
    const timer = setInterval(function() {
        current += increment;
        if (current >= targetValue) {
            current = targetValue;
            clearInterval(timer);
        }
        
        const suffix = targetText.replace(/[0-9.]/g, '');
        element.textContent = Math.round(current * 10) / 10 + suffix;
    }, duration / steps);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .context-indicator {
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .metric-card {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .run-example:hover {
        background: #388E3C !important;
        transform: scale(1.05);
        transition: all 0.2s ease;
    }
`;
document.head.appendChild(style);