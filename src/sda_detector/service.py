"""SDA Detection Service - Pure orchestration with zero business logic.

PURPOSE:
This service demonstrates pure orchestration - coordinating domain models and
boundary operations without making business decisions. It's the conductor of
an orchestra where each instrument (domain model) knows how to play itself.

SDA PRINCIPLES DEMONSTRATED:
1. **Pure Orchestration**: Zero business logic, only coordination
2. **Boundary Isolation**: File I/O and AST parsing isolated with try/except
3. **Delegated Intelligence**: All decisions made by domain models
4. **Immutable Context**: State flows functionally without mutation
5. **Discriminated Dispatch**: All branching via behavioral enums

LEARNING GOALS:
- Understand the difference between orchestration and business logic
- Learn how to isolate boundary operations (I/O, parsing)
- Master immutable context threading through recursive structures
- See how services can be simple when models are smart
- Recognize proper separation of concerns in architecture

ARCHITECTURE NOTES:
This service is intentionally "dumb" - it knows HOW to coordinate but not
WHAT decisions to make. All intelligence lives in domain models that analyze
themselves. The service just connects the pieces.

The service coordinates:
1. File system operations (boundary) - isolated with try/except
2. AST parsing (boundary) - isolated with try/except
3. Domain model analysis (intelligence) - delegated to models
4. Report generation (aggregation) - delegated to report model

Teaching Example:
    >>> # Traditional service (business logic mixed with orchestration):
    >>> class AnalysisService:
    >>>     def analyze(self, path):
    >>>         files = self.get_files(path)
    >>>         for file in files:
    >>>             content = self.read_file(file)
    >>>             if self.is_python_file(file):  # Business decision!
    >>>                 if 'test' in file:  # Business decision!
    >>>                     findings = self.analyze_test(content)
    >>>                 else:
    >>>                     findings = self.analyze_code(content)
    >>> 
    >>> # SDA service (pure orchestration):
    >>> class DetectionService:
    >>>     def analyze(self, path):
    >>>         path_type = PathType.from_path(path)  # Delegate classification
    >>>         files = path_type.get_python_files(path)  # Type knows what to do
    >>>         for file in files:
    >>>             findings = self._analyze_file(file)  # Delegate to domain

Key Insight:
When domain models are intelligent, services become simple coordinators.
This is the inverse of traditional "smart service, dumb model" architecture.
"""

import ast
from pathlib import Path

# ast_domain removed - using direct ASTNodeType dispatch
from .models.analysis_domain import Finding

# Note: Analyzers replaced with pure domain model intelligence
from .models.context_domain import AnalysisScope, RichAnalysisContext
from .models.core_types import ModuleType, PatternType, PositivePattern
from .models.reporting_domain import ArchitectureReport


class DetectionService:
    """Pure orchestration service with zero business logic.
    
    WHAT: Coordinates the analysis pipeline from file discovery to report generation,
    without making any business decisions itself.
    
    WHY: Separating orchestration from business logic makes both simpler. The service
    doesn't need to understand patterns; it just needs to connect components.
    
    HOW: Delegates all decisions to domain models via their behavioral methods,
    using discriminated union dispatch for all control flow.
    
    Teaching Note:
        This service has NO if/elif statements for business logic - only
        try/except for boundary operations. All decisions are delegated
        to domain models that understand themselves.
    
    SDA Pattern Demonstrated:
        Orchestration Without Intelligence - The service is intentionally
        "dumb", delegating all intelligence to self-aware domain models.
    """

    def __init__(self) -> None:
        """Initialize detection service - no state needed.
        
        Teaching: Stateless services! No instance variables, no mutable state.
        Everything is computed functionally from inputs. This makes the service
        trivially testable and thread-safe.
        """
        pass  # Teaching: Explicit pass shows this is intentionally empty

    def analyze_module(self, module_path: str, module_name: str | None = None) -> ArchitectureReport:
        """Analyze a module using adapters + context + analyzers.
        
        Teaching Note: ORCHESTRATION FLOW
        
        This method shows pure orchestration:
        1. Resolve inputs (simple defaults, no logic)
        2. Classify module (delegate to enum)
        3. Get files (delegate to path type)
        4. Analyze files (delegate to analyzers)
        5. Create report (delegate to report model)
        
        No business decisions made here - just coordination!
        """
        # Teaching: Simple defaults without business logic
        resolved_name = module_name or Path(module_path).stem
        module_type = self._classify_module_type(module_path)

        # Get Python files to analyze
        python_files = self._get_python_files(module_path)

        # Analyze each file
        all_findings: list[Finding] = []
        for file_path in python_files:
            file_findings = self._analyze_file(file_path, module_type)
            all_findings.extend(file_findings)

        # Create report using domain model
        return self._create_report(all_findings, resolved_name, module_type, python_files)

    def _classify_module_type(self, module_path: str) -> ModuleType:
        """Module classification using pure discriminated union dispatch.
        
        Teaching: The service doesn't know HOW to classify - it asks
        the enum to do it. This is delegation, not implementation.
        """
        from .models.core_types import ModuleTypeClassifier

        # Teaching: Pure SDA - delegate to enum's behavioral method
        # The enum knows how to classify paths, not the service
        return ModuleTypeClassifier.from_path(module_path)

    def _get_python_files(self, module_path: str) -> list[str]:
        """Get Python files to analyze using pure discriminated union dispatch.
        
        Teaching Note: TWO-STEP DELEGATION PATTERN
        
        1. Ask PathType to classify the path
        2. Ask the classified type what files to return
        
        The service never checks if it's a file or directory - the
        PathType enum handles all that logic internally.
        """
        from .models.core_types import PathType

        # Teaching: Classify path using enum's factory method
        path_type = PathType.from_path(module_path)

        # Teaching: Pure discriminated union dispatch - no conditionals
        # The enum value knows what files to return for its type
        return path_type.get_python_files(module_path)

    def _analyze_file(self, file_path: str, module_type: ModuleType) -> list[Finding]:
        """Analyze a single file using pure immutable SDA approach.
        
        Teaching Note: BOUNDARY OPERATION PATTERN
        
        This method shows the ONLY acceptable use of try/except in SDA:
        isolating boundary operations (file I/O, AST parsing).
        
        Notice:
        1. Try/except ONLY for external operations, not control flow
        2. Immediate conversion to domain types (Finding)
        3. No error details exposed - just fact that error occurred
        4. After boundaries, everything is pure functional
        
        This is the "adapter pattern" - converting external failures
        into domain types that the rest of the system understands.
        """
        # Teaching: Read file with boundary error handling
        # This is I/O - a boundary operation where try/except is acceptable
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:  # Teaching: Catch all - we don't care what went wrong
            return [Finding(file_path=file_path, line_number=0, description="file_read_error")]

        # Teaching: Parse AST with boundary error handling
        # This is parsing external data - another boundary operation
        try:
            tree = ast.parse(content, filename=file_path)
        except Exception:  # Teaching: Convert parse errors to domain types
            return [Finding(file_path=file_path, line_number=0, description="ast_parse_error")]

        # Teaching: Create base immutable context
        # This context will flow through analysis, accumulating information
        base_context = RichAnalysisContext(current_file=file_path, module_type=module_type)

        # Teaching: Pure functional AST analysis - no mutable state!
        # The context is never mutated, only copied with updates
        return self._analyze_ast_pure(tree, base_context)

    def _analyze_ast_pure(self, tree: ast.AST, base_context: RichAnalysisContext) -> list[Finding]:
        """Pure functional AST analysis using immutable context computation.

        Teaching Note: PURE FUNCTIONAL TREE TRAVERSAL
        
        This method demonstrates pure functional programming over trees:
        
        1. Build immutable scope map (pure computation)
        2. For each node, compute its context (pure function)
        3. Analyze node with context (delegation to domain)
        4. Collect findings (pure accumulation)
        
        No mutable state! Each node gets its own computed context.
        This is harder than mutable traversal but eliminates entire
        categories of bugs (race conditions, state corruption).
        
        SDA Principle: No mutable state - compute context per node from AST structure.
        """
        findings = []

        # Build scope map from AST structure (pure function)
        scope_map = self._build_scope_map(tree)

        # Analyze each node with computed context
        for node in ast.walk(tree):
            # Compute immutable context for this specific node
            node_context = self._compute_node_context(node, scope_map, base_context)

            # Teaching: Use discriminated union dispatch for node analysis
            from .models.core_types import ASTNodeType

            # Teaching: Convert AST node to our type system
            node_type = ASTNodeType.from_ast(node)

            # Teaching: Pure SDA - Node types know how to analyze themselves!
            # The service doesn't know what to look for - the type does
            node_findings = node_type.create_analyzer_findings(node, node_context)
            findings.extend(node_findings)

        # Add string literal repetition analysis (runs once per file)
        from .models.analyzers.literal_analyzer import LiteralAnalyzer

        literal_findings = LiteralAnalyzer.analyze_tree(tree, base_context)
        findings.extend(literal_findings)

        return findings

    def _build_scope_map(self, tree: ast.AST) -> dict[ast.AST, list[AnalysisScope]]:
        """Build a map of each AST node to its scope stack.

        Teaching Note: IMMUTABLE TREE ANNOTATION
        
        This is a sophisticated pattern - we're building a map that
        annotates each AST node with its scope context, but doing it
        functionally without mutating the AST itself.
        
        The trick: We use a mutable list (current_scopes) during
        traversal, but we COPY it for each node. This gives us
        efficiency of mutation with safety of immutability.
        
        Pure function that computes scope hierarchy without mutating the AST.
        """
        scope_map = {}
        current_scopes: list[AnalysisScope] = []

        def visit_node(node: ast.AST) -> None:
            # Record current scope stack for this node
            scope_map[node] = current_scopes.copy()

            # Pure discriminated union dispatch - zero conditionals
            from .models.core_types import ASTNodeType

            node_type = ASTNodeType.from_ast(node)

            # Define child visitor for the behavioral method
            def visit_children(n: ast.AST) -> None:
                for child in ast.iter_child_nodes(n):
                    visit_node(child)

            # Teaching: Delegate ALL scope handling to the enum's behavioral method
            # The enum knows whether to push/pop scope based on node type
            # No if/else needed - pure discriminated union dispatch!
            node_type.process_with_scope(node, current_scopes, visit_children)

        visit_node(tree)
        return scope_map

    def _compute_node_context(
        self, node: ast.AST, scope_map: dict[ast.AST, list[AnalysisScope]], base_context: RichAnalysisContext
    ) -> RichAnalysisContext:
        """Compute immutable context for a specific AST node.

        Teaching Note: PURE CONTEXT COMPUTATION
        
        This creates a new context for each node by:
        1. Looking up the node's scope stack from the map
        2. Creating a copy of base context with updated scopes
        
        The model_copy() method is Pydantic's immutable update pattern.
        It creates a new model with some fields changed, leaving the
        original untouched. This is functional programming!
        
        Pure function - no side effects, deterministic output.
        """
        node_scopes = scope_map.get(node, [])
        return base_context.model_copy(update={"scope_stack": node_scopes})

    def _create_report(
        self, findings: list[Finding], module_name: str, module_type: ModuleType, files: list[str]
    ) -> ArchitectureReport:
        """Create architecture report from findings."""
        # Classify findings into violations and patterns
        violations: dict[PatternType, list[Finding]] = {}
        patterns: dict[PositivePattern, list[Finding]] = {}

        # Pure SDA: Use FindingClassifier for discriminated union dispatch
        from .models.core_types import FindingClassifier

        for finding in findings:
            # Classify finding using enum's factory method
            classifier = FindingClassifier.from_finding(finding)

            # Pure discriminated union dispatch - no conditionals
            classifier.add_to_collections(finding, violations, patterns)

        return ArchitectureReport(
            violations=violations,
            patterns=patterns,
        )


# Module-level service instance
service = DetectionService()


def analyze_module(module_path: str, module_name: str | None = None) -> ArchitectureReport:
    """Analyze a module for SDA compliance - clean public API."""
    return service.analyze_module(module_path, module_name)


def main() -> None:
    """CLI entry point using pure discriminated union dispatch.
    
    Teaching Note: ELIMINATING CONDITIONALS IN MAIN
    
    Even the main() function avoids if/else! Instead:
    1. Classify arguments into a state (enum)
    2. Let the state handle the arguments
    3. Use dictionary dispatch for continuation
    
    This shows that SDA principles apply everywhere, even in
    simple CLI handling. No part of the code is "too small"
    to benefit from proper type-driven design.
    """
    import sys

    from .models.core_types import CLIArgumentState

    # Teaching: Pure SDA - classify arguments and handle via dispatch
    arg_state = CLIArgumentState.from_argv(sys.argv)
    module_path, module_name, should_continue = arg_state.handle_arguments(sys.argv)

    # Teaching: Pure dispatch - no conditionals!
    # This replaces:
    #   if should_continue:
    #       run_analysis(module_path, module_name)
    #   else:
    #       return
    #
    # The enum GUARANTEES the invariants:
    # - When should_continue is False, module_path is None
    # - When should_continue is True, module_path is not None
    from collections.abc import Callable

    # Teaching: Dictionary dispatch with lambdas for lazy evaluation
    continuations: dict[bool, Callable[[], None]] = {
        False: lambda: None,  # Do nothing
        True: lambda: _run_analysis_safe(module_path, module_name),  # Run analysis
    }
    continuations[should_continue]()  # Call the selected function


def _run_analysis_safe(module_path: str | None, module_name: str | None) -> None:
    """Run analysis with path that enum guarantees is valid when called.
    
    Teaching Note: TRUSTING TYPE GUARANTEES
    
    The enum's handle_arguments() method guarantees that when
    should_continue is True, module_path is not None. We trust
    this completely - no defensive checks needed!
    
    The `or ""` is ONLY for the static type checker - at runtime,
    module_path is NEVER None when this function is called. This
    is the power of discriminated unions - they encode invariants.
    """
    # Teaching: The discriminated union GUARANTEES module_path is not None
    # We trust the enum dispatch completely - no defensive coding

    # Teaching: Direct call - the enum ensures this is safe
    # The `or ""` is only to satisfy mypy, never executes
    report = analyze_module(module_path or "", module_name)

    _format_report(report)


def _format_report(report: ArchitectureReport) -> None:
    """Format and print the analysis report."""
    # Simple report formatting
    print(f"🧠 SDA ARCHITECTURE ANALYSIS - {report.module_type.upper()}")
    print("=" * 70)

    print("🔍 SDA VIOLATIONS DETECTED:")
    for violation_type, findings in report.violations.items():
        count = len(findings)
        status = "🔍" if count > 0 else "⚪"
        print(f"  {violation_type:30} {count:3} {status}")

    print("\n📊 ARCHITECTURAL FEATURES:")
    for pattern_type, findings in report.patterns.items():
        count = len(findings)
        status = "📊" if count > 0 else "⚪"
        print(f"  {pattern_type:30} {count:3} {status}")

    print(f"\nMODULE TYPE: {report.module_type}")
    print(f"TOTAL VIOLATIONS: {report.total_violations}")
    print(f"TOTAL PATTERNS: {report.total_patterns}")

    dist = report.pattern_distribution
    print(f"DISTRIBUTION: {dist['patterns']:.1%} patterns, {dist['violations']:.1%} violations")


if __name__ == "__main__":
    main()
