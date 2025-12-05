<!--
Sync Impact Report:
Version Change: Initial → 1.0.0
Principles Added:
  - Code Quality & Maintainability
  - Testing Standards (NON-NEGOTIABLE)
  - User Experience Consistency
  - Performance Requirements
  - Documentation & Knowledge Sharing
Sections Added:
  - Quality Gates & Review Process
  - Development Workflow
  - Governance
Templates Consistency Status:
  ✅ plan-template.md - Constitution Check section aligns with principles
  ✅ spec-template.md - User scenarios and requirements support UX consistency
  ✅ tasks-template.md - Task structure supports test-first and quality gates
Follow-up TODOs:
  - None - all placeholders filled
-->

# Tarot Project Constitution

## Core Principles

### I. Code Quality & Maintainability

**Every line of code MUST be written for long-term maintainability, not short-term convenience.**

- Code MUST be self-documenting with clear naming conventions
- Cyclomatic complexity MUST stay below 10 per function/method
- Functions MUST have single responsibility (SRP)
- Code duplication MUST be eliminated via abstraction when pattern appears 3+ times
- SOLID principles MUST guide all architectural decisions
- Technical debt MUST be tracked and addressed within 2 sprint cycles
- Code smells (long methods, large classes, feature envy) MUST be refactored immediately

**Rationale**: Maintainable code reduces cognitive load, prevents bugs, and enables team velocity. Short-term hacks compound into long-term liabilities.

### II. Testing Standards (NON-NEGOTIABLE)

**Test coverage and test quality are not optional—they are fundamental requirements.**

- Unit test coverage MUST be ≥80% for all business logic
- Integration tests MUST cover all API contracts and service boundaries
- Tests MUST be written BEFORE implementation (Test-Driven Development)
- Red-Green-Refactor cycle MUST be followed:
  1. Write failing test
  2. Get user/stakeholder approval on test scenarios
  3. Implement minimum code to pass
  4. Refactor for quality
- Every bug fix MUST include a regression test
- Tests MUST run in <5 minutes for unit suite, <15 minutes for full suite
- Flaky tests MUST be fixed immediately or disabled with ticket
- Test names MUST clearly describe the scenario being tested

**Rationale**: Tests are executable documentation and safety nets. TDD prevents over-engineering and ensures requirements are met. Fast tests enable rapid feedback loops.

### III. User Experience Consistency

**Users MUST encounter a coherent, predictable, and delightful experience across all touchpoints.**

- UI components MUST follow a documented design system
- Interaction patterns MUST be consistent (e.g., confirmation flows, error handling)
- Response times MUST meet performance SLAs (see Principle IV)
- Error messages MUST be user-friendly and actionable
- Accessibility MUST meet WCAG 2.1 Level AA standards minimum
- User flows MUST be validated with usability testing before release
- Breaking UX changes MUST be communicated with migration guides
- All user-facing text MUST be localization-ready (i18n support)

**Rationale**: Consistency reduces cognitive load and builds user trust. Predictable experiences increase user satisfaction and reduce support burden.

### IV. Performance Requirements

**Performance is a feature, not an afterthought. Every component MUST meet defined performance budgets.**

- API response times MUST be <200ms p95, <500ms p99
- Page load time MUST be <2 seconds on 3G networks
- Time to Interactive (TTI) MUST be <3.5 seconds
- Database queries MUST be indexed; N+1 queries are prohibited
- Memory leaks MUST be identified and fixed before release
- Bundle sizes MUST stay within budget (tracked per PR)
- Performance regression MUST block deployment
- Load testing MUST validate system handles 2x expected peak traffic

**Rationale**: Users abandon slow applications. Performance directly impacts conversion, satisfaction, and operational costs.

### V. Documentation & Knowledge Sharing

**Knowledge MUST be captured, shared, and maintained to enable team autonomy and onboarding.**

- All public APIs MUST have OpenAPI/Swagger documentation
- Architectural decisions MUST be documented in ADRs (Architecture Decision Records)
- README files MUST include: purpose, setup, usage, contributing guidelines
- Complex algorithms MUST include explanatory comments
- Runbooks MUST exist for operational procedures
- Code reviews MUST be educational opportunities, not gatekeeping
- Onboarding documentation MUST be maintained and tested with new hires

**Rationale**: Documentation multiplies team effectiveness. Tribal knowledge creates single points of failure and slows onboarding.

## Quality Gates & Review Process

**Every change MUST pass through quality gates before merging.**

### Pre-Merge Requirements

- [ ] All tests pass (unit, integration, contract)
- [ ] Code coverage threshold met (≥80%)
- [ ] Linting and formatting checks pass
- [ ] Performance benchmarks within budget
- [ ] Security scanning shows no critical vulnerabilities
- [ ] At least one peer review approval
- [ ] All review comments resolved or explicitly deferred

### Code Review Standards

- Reviews MUST focus on: correctness, maintainability, performance, security
- Reviewers MUST verify tests exist and fail before implementation
- Nitpicks (style preferences) SHOULD be handled by automated tooling, not humans
- Review turnaround time SHOULD be <24 hours
- Blocking reviews MUST include clear rationale and actionable feedback
- "LGTM" without substantive review is prohibited

### Deployment Gates

- [ ] All pre-merge requirements met
- [ ] Smoke tests pass in staging environment
- [ ] Rollback plan documented
- [ ] Monitoring/alerting configured for new features
- [ ] Feature flags enabled where appropriate

## Development Workflow

### Feature Development Process

1. **Specification Phase**
   - User stories written in Given-When-Then format
   - Acceptance criteria defined and reviewed
   - UX mockups/wireframes for UI changes
   - Performance budgets allocated

2. **Planning Phase**
   - Technical design reviewed
   - Dependencies identified
   - Complexity justified if violating simplicity principles

3. **Implementation Phase**
   - Write failing tests first
   - Implement minimum viable solution
   - Refactor for quality
   - Update documentation

4. **Review Phase**
   - Self-review using checklist
   - Peer review (constitution compliance verified)
   - Address feedback

5. **Release Phase**
   - Staging validation
   - Production deployment
   - Monitoring and validation

### Branching Strategy

- Main branch MUST always be deployable
- Feature branches MUST be short-lived (<3 days)
- Commits MUST be atomic and reversible
- Commit messages MUST follow Conventional Commits standard

### Emergency Hotfix Process

- Hotfixes MAY bypass full process for critical production issues
- Hotfixes MUST be followed by retrospective and test addition
- Technical debt created MUST be tracked and addressed immediately after

## Governance

### Authority & Compliance

- This constitution supersedes all conflicting practices and guidelines
- All team members MUST understand and follow these principles
- PRs MUST include a constitution compliance checklist
- Violations MUST be discussed in code review, not merged with "we'll fix later"
- Complexity that violates simplicity principles MUST be explicitly justified

### Amendment Process

1. Proposed amendment documented with rationale
2. Team discussion and consensus-building
3. Constitution version incremented per semantic versioning
4. Templates and documentation updated for consistency
5. Team training on changes
6. Adoption date recorded

### Version History & Semantics

**Version Bumping Rules:**
- **MAJOR**: Backward-incompatible governance changes, principle removals, or redefinitions
- **MINOR**: New principles added, sections expanded, materially new guidance
- **PATCH**: Clarifications, wording improvements, typo fixes, non-semantic refinements

### Continuous Improvement

- Constitution effectiveness MUST be reviewed quarterly
- Metrics tracked: test coverage, deployment frequency, incident rate, review turnaround
- Retrospectives MUST identify process improvements
- Principle violations MUST be analyzed for root causes

**Version**: 1.0.0 | **Ratified**: 2025-12-04 | **Last Amended**: 2025-12-04
