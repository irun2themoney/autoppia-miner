# Dynamic Zero Optimization Plan

## Overview
Based on [Dynamic Zero: The Overfitting Punisher](https://autoppia.substack.com/p/dynamic-zero-the-overfitting-punisher), we need to optimize our miner to win in the **Winner Takes It All (WTA)** system.

## Key Changes in Dynamic Zero

1. **Winner Takes It All** - Only top miner gets full reward
2. **Time Factor Removed** - No longer part of scoring (was 15%)
3. **Efficiency Rewards Removed** - No longer reward fewer actions
4. **Focus: Completion + Precision** - Reliability is everything
5. **Dynamic IWA** - Tasks are randomized and harder:
   - **D1**: Layout & Structure randomization
   - **D2**: Real-Time Data (fresh data every session)
   - **D3**: Text & Label Variation
   - **D4**: Interactive Pop-Ups

## Optimization Strategy

### 1. Fix Chutes API Integration
- Current issue: 404 errors on all endpoints
- Solution: Try alternative authentication/endpoint formats
- Fallback: Use template actions with better intelligence

### 2. Enhanced Action Generation
- **Robust Selectors**: Use multiple fallback selectors for dynamic HTML
- **Screenshot-Based Reasoning**: Take screenshots before/after actions to adapt
- **Pop-Up Handling**: Detect and handle modals/pop-ups (D4)
- **Text Variation Handling**: Use flexible text matching (D3)
- **Layout Adaptation**: Handle randomized structures (D1)

### 3. Task Classification Improvements
- Better pattern matching for dynamic variations
- Handle edge cases and variations
- Classify complex multi-step tasks

### 4. Action Templates Optimization
- More comprehensive action sequences
- Better wait times for dynamic content
- Multiple screenshot points for verification
- Robust error recovery

### 5. Focus on Completion + Precision
- Don't optimize for speed (time removed from scoring)
- Don't optimize for fewer actions (efficiency removed)
- Focus on: **Reliability, Accuracy, Completeness**

## Implementation Priority

1. ✅ Fix Chutes API endpoint issues
2. ✅ Enhance action templates for dynamic environments
3. ✅ Improve selectors with fallbacks
4. ✅ Add pop-up detection and handling
5. ✅ Optimize for completion over speed

