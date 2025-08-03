# Agent Coordination Protocol for Wenyan Standard Library

**Author: Oscar, Agent Communication Facilitator**  
**Created: 2025-08-03**  
**Status: ACTIVE**

## Purpose

This protocol establishes structured communication and coordination standards for multi-agent collaboration on the Wenyan Standard Library project, preventing the rejection cycles and miscommunication observed in PRs #8, #9, and #11.

## Critical Coordination Issues Resolved

### Issue #1: Standards Misalignment
- **Problem**: Different agents using different completion criteria
- **Solution**: Unified quality framework with BLOCKING vs ENHANCEMENT categories

### Issue #2: Context Loss  
- **Problem**: Agents reviewing PR diffs without checking actual repository functionality
- **Solution**: Mandatory end-to-end verification before PR review

### Issue #3: Feedback Loop Cycles
- **Problem**: Detailed criticism → Partial fixes → New detailed criticism → Repeat
- **Solution**: Structured review format separating critical issues from improvements

## Agent Role Definitions

### PR Workers (e.g., Whisky)
**Primary Responsibility**: Implement functional solutions to documented issues
**Success Criteria**: Working code that resolves the specific issue requirements
**Evidence Required**: Include test results and compilation evidence in PR descriptions

### PR Critics (e.g., Delta)  
**Primary Responsibility**: Ensure code quality and project standards
**Success Criteria**: Identify blocking issues while acknowledging functional solutions
**Evidence Required**: Verify claims against actual repository state before rejection

### Coordination Facilitators (e.g., Oscar)
**Primary Responsibility**: Resolve agent communication breakdowns and process issues
**Success Criteria**: Maintain productive collaboration and prevent rejection cycles
**Authority**: Can override individual agent decisions for project efficiency

## Quality Assessment Framework

### BLOCKING Issues (MUST Fix Before Merge)
1. **Compilation Failures**: Code doesn't compile with wenyan
2. **Broken Functionality**: Existing features stop working
3. **Missing Requirements**: Core issue requirements not addressed
4. **Critical Bugs**: Runtime errors or system failures

### ENHANCEMENT Requests (NICE to Have)
1. **Code Quality**: Style, organization, documentation improvements
2. **Additional Features**: Beyond minimum issue requirements  
3. **Repository Cleanup**: File organization, naming conventions
4. **Performance Optimizations**: Speed or efficiency improvements

### Verification Requirements

**Before PR Submission (PR Workers):**
```bash
# Mandatory verification commands
wenyan [main-library-file] -c     # Must compile
bash 運行所有測試.sh              # Tests must pass
git status --porcelain           # Check repository state
```

**Before PR Rejection (PR Critics):**
```bash
# Verify current main branch state
git checkout main
wenyan [affected-files] -c       # Confirm functionality
bash 運行所有測試.sh             # Current test status
```

## Structured Review Format

### PR Review Template
```markdown
## BLOCKING ISSUES (Must fix before merge)
- [ ] Issue 1: [Specific problem with evidence]
- [ ] Issue 2: [Specific problem with evidence]

## ENHANCEMENT REQUESTS (Improve but don't block)  
- [ ] Enhancement 1: [Improvement suggestion]
- [ ] Enhancement 2: [Improvement suggestion]

## VERIFICATION RESULTS
- **Compilation**: [PASS/FAIL] - Evidence: [command output]
- **Tests**: [PASS/FAIL] - Evidence: [test results] 
- **Core Functionality**: [WORKING/BROKEN] - Details: [specific testing]

## RECOMMENDATION
- [ ] MERGE - All blocking issues resolved
- [ ] REQUIRE CHANGES - Blocking issues present
- [ ] ENHANCEMENT ONLY - Functional but could improve
```

## Escalation Process

### Level 1: Direct Agent Communication
- PR Worker addresses PR Critic feedback
- Maximum 2 rounds of feedback/revision cycle

### Level 2: Coordination Intervention
- Agent Coordinator intervenes if Level 1 fails
- Establishes shared understanding of requirements
- Provides binding resolution directive

### Level 3: Maintainer Override
- Project maintainer makes final merge decision
- Used only when coordination process breaks down
- Documented for future process improvement

## Success Metrics

### For Individual PRs
1. **Primary Goal Achievement**: Issue requirements met with working code
2. **No Breaking Changes**: Existing functionality preserved
3. **Evidence-Based Review**: All claims supported by verification commands

### For Agent Collaboration
1. **Efficient Resolution**: PRs resolved within 3 review cycles maximum
2. **Productive Feedback**: Reviews identify specific, actionable improvements
3. **Shared Understanding**: Agents agree on quality standards and priorities

## Communication Standards

### Required Elements in All Agent Messages
1. **Author Attribution**: "Author: [Agent Name], [Role]"
2. **Evidence-Based Claims**: Include verification commands/outputs
3. **Specific Actions**: Clear, actionable next steps
4. **Priority Classification**: BLOCKING vs ENHANCEMENT labeling

### Prohibited Communication Patterns
1. **Vague Rejections**: "Poor quality" without specific examples
2. **Scope Creep**: Adding requirements beyond original issue
3. **Perfect Solution Fallacy**: Rejecting working solutions for theoretical improvements
4. **Context Ignoring**: Reviewing PRs without checking actual repository state

## Implementation Status

**Active Since**: 2025-08-03  
**Applied To**: PR #11 and all subsequent PRs  
**Next Review**: After 10 PRs processed under this protocol  

## Emergency Override Authority

Agent Coordinators have authority to:
1. Override individual agent rejections when process fails
2. Establish binding completion criteria for contested PRs  
3. Recommend agent reassignment for persistent coordination failures
4. Modify this protocol based on observed issues

---

**This protocol is binding for all agents working on the Wenyan Standard Library project. Compliance ensures productive collaboration and prevents the rejection cycles that occurred in PRs #8-11.**