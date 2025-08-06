"""Core domain types for SDA architecture detection - The Foundation of Type-Driven Development.

PURPOSE:
This module defines the fundamental vocabulary of Semantic Domain Architecture (SDA) analysis.
It demonstrates how to eliminate conditionals by encoding business logic into the type system itself.

SDA PRINCIPLES DEMONSTRATED:
1. **Discriminated Union Dispatch**: Every enum replaces if/elif chains with pure type dispatch
2. **Behavioral Enums**: Enums contain methods that encode their own logic
3. **No Naked Primitives**: Every string/int is wrapped in a semantic type
4. **Immutable Intelligence**: All types are immutable with computed behaviors
5. **Zero Runtime Reflection**: No isinstance/hasattr/getattr in business logic

LEARNING GOALS:
- Understand how discriminated unions eliminate conditionals
- Learn to encode business logic in types, not procedures
- Master behavioral enum patterns that self-organize code
- See how proper type design prevents entire bug categories
- Recognize the difference between boundary code and domain logic

ARCHITECTURE NOTES:
This is the foundation layer - all other domain models build on these types.
Every enum here replaces what would traditionally be if/elif chains scattered
throughout the codebase. By centralizing dispatch logic in behavioral enums,
we achieve "software by subtraction" - less code, more capability.

Teaching Example:
    >>> # Traditional approach (what we're replacing):
    >>> if isinstance(node, ast.FunctionDef):
    >>>     handle_function(node)
    >>> elif isinstance(node, ast.ClassDef):
    >>>     handle_class(node)
    >>> elif isinstance(node, ast.If):
    >>>     handle_conditional(node)
    >>> 
    >>> # SDA approach (what we do instead):
    >>> node_type = ASTNodeType.from_ast(node)  # Pure classification
    >>> findings = node_type.create_analyzer_findings(node, context)  # Behavioral dispatch

Key Insight:
Every enum in this file is a mini-expert system that knows everything about
its domain. This is the opposite of anemic models - our types are rich with
behavior, eliminating the need for external service logic.
"""

import ast
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analysis_domain import Finding
    from .context_domain import AnalysisScope, RichAnalysisContext


class ASTNodeCategory(StrEnum):
    """Domain classification of AST nodes by semantic meaning.
    
    WHAT: Groups AST nodes into categories based on their role in code structure.
    Each category represents a different aspect of program organization.
    
    WHY: Different node categories require different analysis strategies.
    Structural nodes define architecture, behavioral nodes show usage patterns,
    control flow nodes reveal logic patterns, and data nodes show state access.
    
    HOW: This demonstrates SDA's "behavioral enum" pattern - the enum itself
    contains methods that encode domain knowledge about each category.
    
    Teaching Example:
        >>> # Instead of scattered conditionals:
        >>> if node_type in ['class', 'function', 'module']:
        >>>     priority = 1
        >>> elif node_type in ['if', 'try', 'for']:
        >>>     priority = 2
        >>> 
        >>> # We encode this knowledge in the type:
        >>> category = ASTNodeCategory.STRUCTURAL
        >>> priority = category.analysis_priority  # Type knows its own priority
    
    SDA Pattern Demonstrated:
        Behavioral Enums - The enum encapsulates all knowledge about node categories,
        eliminating the need for external classification logic.
    """

    STRUCTURAL = "structural"  # Classes, functions, modules
    BEHAVIORAL = "behavioral"  # Calls, attribute access
    CONTROL_FLOW = "control_flow"  # If, try, loops
    DATA = "data"  # Names, constants, literals

    @property
    def analysis_priority(self) -> int:
        """Domain intelligence: analysis priority by semantic importance.
        
        Teaching Note:
            This property demonstrates "intelligence in types". Instead of having
            a service method like get_priority(category), the category knows its
            own priority. This is fundamental SDA - data and behavior together.
            
            Notice the pure dictionary dispatch - no if/elif chains. The dictionary
            is a compile-time constant, making this both fast and maintainable.
        """
        priorities = {
            ASTNodeCategory.STRUCTURAL: 1,  # High priority - architecture
            ASTNodeCategory.CONTROL_FLOW: 2,  # Medium priority - patterns
            ASTNodeCategory.BEHAVIORAL: 3,  # Medium priority - usage
            ASTNodeCategory.DATA: 4,  # Low priority - data access
        }
        return priorities[self]

    @property
    def creates_scope(self) -> bool:
        """Does this category introduce a new naming scope?
        
        Teaching: Simple boolean properties encode domain knowledge directly
        in the type, eliminating the need for external scope-checking logic.
        """
        return self == self.STRUCTURAL

    @property
    def needs_flow_analysis(self) -> bool:
        """Does this category affect program flow?
        
        Teaching: Set membership is still pure functional programming -
        it's a boolean operation, not a conditional statement.
        """
        return self in {self.CONTROL_FLOW, self.BEHAVIORAL}

    @property
    def can_contain_patterns(self) -> bool:
        """Can this category contain SDA violations?
        
        Teaching: Domain knowledge encoded as computed properties means
        the type system itself understands which nodes to analyze.
        """
        # Data nodes rarely contain patterns we care about
        return self != self.DATA


class ASTNodeType(StrEnum):
    """Discriminated union for AST node classification - The Heart of SDA Pattern Detection.

    WHAT: A discriminated union (tagged union) that classifies Python AST nodes
    into semantic categories. Each value represents a different type of code construct.
    
    WHY: Python's ast module requires isinstance() checks to identify node types,
    which violates SDA principles. This enum wraps that boundary operation once,
    then provides pure type-driven dispatch throughout the rest of the system.
    
    HOW: The from_ast() factory method performs the boundary isinstance checks
    (marked and isolated), then all subsequent operations use pure dispatch
    through behavioral methods on the enum itself.
    
    Teaching Example:
        >>> # What NOT to do (scattered throughout codebase):
        >>> def analyze(node):
        >>>     if isinstance(node, ast.FunctionDef):
        >>>         return analyze_function(node)
        >>>     elif isinstance(node, ast.ClassDef):
        >>>         return analyze_class(node)
        >>>     elif isinstance(node, ast.If):
        >>>         return analyze_conditional(node)
        >>> 
        >>> # What we do instead (SDA pattern):
        >>> def analyze(node):
        >>>     node_type = ASTNodeType.from_ast(node)  # Single boundary conversion
        >>>     return node_type.create_analyzer_findings(node, context)  # Pure dispatch
    
    SDA Pattern Demonstrated:
        Discriminated Union Dispatch - We convert untyped external data (AST nodes)
        into a strongly-typed discriminated union once at the boundary, then use
        pure type dispatch for all logic. This eliminates hundreds of isinstance
        calls throughout the codebase.
        
    Architecture Note:
        This is a "boundary pattern" - it sits at the edge between Python's
        dynamic AST and our type-safe domain. All isinstance operations are
        contained here, marked with comments, and never leak into domain logic.
    """

    FUNCTION_DEF = "function_def"
    CLASS_DEF = "class_def"
    CONDITIONAL = "conditional"
    MATCH_CASE = "match_case"
    CALL = "call"
    ATTRIBUTE = "attribute"
    UNKNOWN = "unknown"

    @classmethod
    def from_ast(cls, node: ast.AST) -> "ASTNodeType":
        """Pure discriminated union classification - replaces isinstance chains.

        Teaching Note: THE BOUNDARY PATTERN IN ACTION
        
        This is the ONLY place we use type() to check AST node types. This is a
        "boundary method" - it converts untyped external data (Python AST) into
        our strongly-typed domain model. Notice:
        
        1. We use type() not isinstance() for exact type matching
        2. We use a dictionary for O(1) lookup instead of if/elif chains  
        3. We provide a sensible default (UNKNOWN) for unrecognized nodes
        4. This is a @classmethod factory - a common pattern for type conversion
        
        After this conversion, the rest of the codebase NEVER needs isinstance.
        This is "software by subtraction" - one boundary method eliminates
        hundreds of conditionals throughout the system.
        
        Implementation Note:
            Using type() instead of isinstance() is intentional - we want exact
            matches, not inheritance checks. This makes our classification
            deterministic and prevents subtle bugs from subclass handling.
        """
        node_classifiers = {
            ast.FunctionDef: ASTNodeType.FUNCTION_DEF,
            ast.AsyncFunctionDef: ASTNodeType.FUNCTION_DEF,
            ast.ClassDef: ASTNodeType.CLASS_DEF,
            ast.If: ASTNodeType.CONDITIONAL,
            ast.Match: ASTNodeType.MATCH_CASE,
            ast.Call: ASTNodeType.CALL,
            ast.Attribute: ASTNodeType.ATTRIBUTE,
        }
        return node_classifiers.get(type(node), ASTNodeType.UNKNOWN)

    def creates_scope(self) -> bool:
        """Behavioral method - node types know if they create analysis scopes.
        
        Teaching Note: BEHAVIORAL ENUMS IN ACTION
        
        Instead of having external code that checks:
            if node_type in ['function', 'class', 'conditional']:
                create_scope()
                
        The enum itself knows this! This is "intelligence in types" - the type
        system carries semantic knowledge that would otherwise be scattered
        across service methods.
        
        Notice the set membership test - this is still pure and functional,
        just expressed as a boolean operation rather than a dictionary lookup.
        Both patterns are valid SDA as long as they're pure and deterministic.
        """
        scope_creators = {ASTNodeType.FUNCTION_DEF, ASTNodeType.CLASS_DEF, ASTNodeType.CONDITIONAL, ASTNodeType.MATCH_CASE}
        return self in scope_creators

    def process_with_scope(
        self, node: ast.AST, current_scopes: list["AnalysisScope"], visit_children: Callable[[ast.AST], None]
    ) -> None:
        """Process node with proper scope handling using pure discriminated union dispatch.

        Teaching Note: ADVANCED BEHAVIORAL DISPATCH
        
        This method is a masterclass in SDA principles. It demonstrates:
        
        1. **Type-Driven Behavior**: The enum value determines processing strategy
        2. **Pure Dictionary Dispatch**: No if/elif chains, just data lookup
        3. **Delegation Pattern**: Complex logic delegated to private methods
        4. **Inversion of Control**: The type controls the flow, not the caller
        
        Traditional approach would have this logic in service.py:
            if creates_scope(node):
                push_scope()
                process_children()
                pop_scope()
            else:
                process_children()
                
        SDA approach: The type itself orchestrates the entire flow!
        This is "Tell, Don't Ask" taken to its logical conclusion.
        """
        # Pure dictionary dispatch for scope handling behavior
        scope_processors = {
            # Scope creators: create scope, visit children with scope, pop scope
            ASTNodeType.FUNCTION_DEF: self._process_with_new_scope,
            ASTNodeType.CLASS_DEF: self._process_with_new_scope,
            ASTNodeType.CONDITIONAL: self._process_with_new_scope,
            ASTNodeType.MATCH_CASE: self._process_with_new_scope,
            # Non-scope creators: just visit children
            ASTNodeType.CALL: self._process_without_scope,
            ASTNodeType.ATTRIBUTE: self._process_without_scope,
            ASTNodeType.UNKNOWN: self._process_without_scope,
        }
        scope_processors[self](node, current_scopes, visit_children)

    def _process_with_new_scope(
        self, node: ast.AST, current_scopes: list["AnalysisScope"], visit_children: Callable[[ast.AST], None]
    ) -> None:
        """Process node that creates a new scope."""
        new_scope = self.create_scope(node)
        current_scopes.append(new_scope)
        visit_children(node)
        current_scopes.pop()

    def _process_without_scope(
        self, node: ast.AST, current_scopes: list["AnalysisScope"], visit_children: Callable[[ast.AST], None]
    ) -> None:
        """Process node that doesn't create a scope."""
        visit_children(node)

    def create_scope(self, node: ast.AST) -> "AnalysisScope":
        """Behavioral method - node types know how to create their own scopes.

        Pure discriminated union dispatch without getattr or conditionals.
        """
        scope_handlers = {
            ASTNodeType.FUNCTION_DEF: self._create_function_scope,
            ASTNodeType.CLASS_DEF: self._create_class_scope,
            ASTNodeType.CONDITIONAL: self._create_conditional_scope,
            ASTNodeType.MATCH_CASE: self._create_match_scope,
            ASTNodeType.CALL: self._create_call_scope,
            ASTNodeType.ATTRIBUTE: self._create_attribute_scope,
            ASTNodeType.UNKNOWN: self._create_unknown_scope,
        }
        return scope_handlers[self](node)

    def create_analyzer_findings(self, node: ast.AST, context: "RichAnalysisContext") -> list["Finding"]:
        """Behavioral method - node types know how to analyze themselves.

        Teaching Note: THE ULTIMATE SDA PATTERN - SELF-ANALYZING TYPES
        
        This method embodies the pinnacle of SDA design. Instead of:
        1. Service asks "what type are you?"
        2. Service decides which analyzer to use
        3. Service calls the analyzer
        
        We have:
        1. Service tells type "analyze yourself"
        2. Type knows exactly how to do that
        
        The dictionary maps enum values to lambda functions that lazily import
        and call the appropriate analyzer. This demonstrates:
        
        - **Lazy Imports**: Analyzers only imported when needed
        - **Pure Dispatch**: No conditionals, just dictionary lookup
        - **Type Safety**: Each analyzer knows what node type it handles
        - **Encapsulation**: Calling code doesn't need to know about analyzers
        
        Critical Insight:
            The lambda functions provide lazy evaluation - analyzers are only
            imported when actually needed. This improves startup time and makes
            the dispatch table a compile-time constant.
        """
        from collections.abc import Callable

        # Import analyzers from the extracted modules
        from .analyzers.attribute_analyzer import AttributeAnalyzer
        from .analyzers.call_analyzer import CallAnalyzer
        from .analyzers.conditional_analyzer import ConditionalAnalyzer

        # Teaching: Pure discriminated union dispatch - trust the classification
        # The from_ast() method GUARANTEES the node type matches what we expect.
        # This is why we can safely pass any node to any analyzer - the type
        # system ensures we only get nodes we can handle
        analyzer_dispatch: dict[ASTNodeType, Callable[[], list[Finding]]] = {
            ASTNodeType.CONDITIONAL: lambda: ConditionalAnalyzer.analyze_node(node, context),
            ASTNodeType.MATCH_CASE: lambda: ConditionalAnalyzer.analyze_node(node, context),  # Match/case is a conditional pattern
            ASTNodeType.CALL: lambda: CallAnalyzer.analyze_node(node, context),
            ASTNodeType.ATTRIBUTE: lambda: AttributeAnalyzer.analyze_node(node, context),
            ASTNodeType.FUNCTION_DEF: lambda: [],
            ASTNodeType.CLASS_DEF: lambda: [],
            ASTNodeType.UNKNOWN: lambda: [],
        }
        return analyzer_dispatch[self]()

    def _create_empty_findings(self) -> list["Finding"]:
        """Temporary method - returns empty findings until analyzers are extracted."""
        return []

    def _create_function_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create function scope using discriminated union pattern.
        
        Teaching: Notice the getattr() calls here - these are BOUNDARY operations.
        We're extracting data from an external system (Python AST). This is acceptable
        at boundaries but would be a violation in domain logic.
        """
        from .context_domain import AnalysisScope, ScopeType

        return AnalysisScope(
            scope_type=ScopeType.FUNCTION,
            name=getattr(node, "name", "unknown_function"),
            line_number=getattr(node, "lineno", 0),
        )

    def _create_class_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create class scope using discriminated union pattern.
        
        Teaching: The getattr() with defaults ('unknown_class', 0) is defensive
        programming at the boundary - we don't trust external data but convert
        it to safe domain values immediately.
        """
        from .context_domain import AnalysisScope, ScopeType

        return AnalysisScope(
            scope_type=ScopeType.CLASS,
            name=getattr(node, "name", "unknown_class"),
            line_number=getattr(node, "lineno", 0),
        )

    def _create_conditional_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create conditional scope using discriminated union pattern.
        
        Teaching: ScopeNaming.CONDITIONAL is another enum - we never use
        raw strings in domain logic. Every string becomes a typed constant.
        """
        from .context_domain import AnalysisScope, ScopeType

        return AnalysisScope(
            scope_type=ScopeType.CONDITIONAL, name=ScopeNaming.CONDITIONAL, line_number=getattr(node, "lineno", 0)
        )

    def _create_match_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create match/case scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        return AnalysisScope(
            scope_type=ScopeType.CONDITIONAL, name="match_case", line_number=getattr(node, "lineno", 0)
        )

    def _create_call_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create call scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        # Calls don't create their own scope type, use FUNCTION as container
        return AnalysisScope(
            scope_type=ScopeType.FUNCTION, name=ScopeNaming.CALL, line_number=getattr(node, "lineno", 0)
        )

    def _create_attribute_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create attribute scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        # Attributes don't create their own scope type, use FUNCTION as container
        return AnalysisScope(
            scope_type=ScopeType.FUNCTION, name=ScopeNaming.ATTRIBUTE, line_number=getattr(node, "lineno", 0)
        )

    def _create_unknown_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create unknown scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        # Unknown nodes don't create their own scope type, use MODULE as default
        return AnalysisScope(
            scope_type=ScopeType.MODULE, name=ScopeNaming.UNKNOWN, line_number=getattr(node, "lineno", 0)
        )


class FileResult(StrEnum):
    """Discriminated union for file operation results - Replacing Exceptions with Types.

    WHAT: Represents the result of file operations as a type rather than using
    exceptions for control flow. Similar to Result<T, E> in Rust or Either in Haskell.
    
    WHY: Using exceptions for control flow is a procedural pattern that makes
    code paths implicit and hard to follow. By encoding success/failure as types,
    we make all code paths explicit and composable.
    
    HOW: Instead of try/except blocks, operations return a FileResult that
    encodes success or failure. The result type has methods to handle each case.
    
    Teaching Example:
        >>> # Traditional approach (hidden control flow):
        >>> try:
        >>>     content = read_file(path)
        >>>     findings = analyze(content)
        >>> except IOError:
        >>>     findings = [error_finding()]
        >>> 
        >>> # SDA approach (explicit control flow):
        >>> result = read_file_safe(path)  # Returns FileResult
        >>> findings = result.to_findings(path, content)  # Type handles both cases
    
    SDA Pattern Demonstrated:
        Result Types - Encoding success/failure in the type system makes error
        handling explicit, composable, and impossible to forget. This pattern
        eliminates entire categories of uncaught exception bugs.
        
    Philosophy Note:
        This is "errors as values" - a functional programming principle that
        makes error handling a first-class concern rather than an afterthought.
    """

    SUCCESS = "success"
    ERROR = "error"

    def to_findings(self, file_path: str, content: str = "") -> list["Finding"]:
        """Behavioral method - results know how to convert themselves to findings.

        Teaching Note: PURE ERROR HANDLING
        
        This method shows how to handle errors without exceptions:
        1. Success returns an empty list (no findings = no problems)
        2. Error creates an error finding
        
        The dictionary dispatch makes both paths explicit and ensures
        we handle all cases. No forgotten error handling!
        
        Implementation Detail:
            The content parameter is unused here but could be used for
            more sophisticated error reporting in the future.
        """
        from .analysis_domain import Finding

        # Pure dictionary dispatch with computed values - no lambdas, no conditionals
        result_handlers = {
            FileResult.SUCCESS: [],
            FileResult.ERROR: [Finding(file_path=file_path, line_number=0, description="file_read_error")],
        }
        return result_handlers[self]

    def _create_success_findings(self) -> list["Finding"]:
        """Success produces no findings - pure discriminated union behavior."""
        return []

    def _create_error_findings(self, file_path: str) -> list["Finding"]:
        """Error creates file read error finding - pure discriminated union behavior."""
        from .analysis_domain import Finding

        return [Finding(file_path=file_path, line_number=0, description="file_read_error")]


class AnalysisResult(StrEnum):
    """Discriminated union for AST parsing results - Type-Safe AST Analysis.

    WHAT: Represents the result of AST parsing operations as explicit types
    rather than relying on exception handling.
    
    WHY: AST parsing can fail for various reasons (syntax errors, encoding issues).
    Instead of scattering try/except blocks, we centralize error handling logic.
    
    HOW: Parse operations return AnalysisResult.SUCCESS or PARSE_ERROR,
    with methods to convert results to appropriate findings.
    
    Teaching Note:
        This is the same pattern as FileResult but for AST operations.
        Consistency in error handling patterns makes code predictable.
    
    SDA Pattern Demonstrated:
        Consistent Error Types - Using the same pattern (Result types) for
        all fallible operations creates a uniform error handling strategy
        across the entire codebase.
    """

    SUCCESS = "success"
    PARSE_ERROR = "parse_error"

    def to_findings(self, file_path: str, findings: list["Finding"] | None = None) -> list["Finding"]:
        """Behavioral method - results know how to handle analysis outcomes."""
        from .analysis_domain import Finding

        # Pure dictionary dispatch with computed values - no lambdas, no conditionals
        result_handlers = {
            AnalysisResult.SUCCESS: findings or [],
            AnalysisResult.PARSE_ERROR: [Finding(file_path=file_path, line_number=0, description="ast_parse_error")],
        }
        return result_handlers[self]

    def _create_parse_error_findings(self, file_path: str) -> list["Finding"]:
        """Parse error creates AST parse error finding."""
        from .analysis_domain import Finding

        return [Finding(file_path=file_path, line_number=0, description="ast_parse_error")]


class PathType(StrEnum):
    """Discriminated union for file system path handling - Making File Systems Type-Safe.

    WHAT: Classifies file system paths into semantic categories (Python files,
    directories, other) to enable type-driven file processing.
    
    WHY: File system operations often involve complex if/elif chains checking
    extensions, whether something is a file or directory, etc. This type
    encapsulates all that logic in one place.
    
    HOW: The from_path() factory method classifies paths, then behavioral
    methods like get_python_files() operate based on the classification.
    
    Teaching Example:
        >>> # Traditional approach (scattered logic):
        >>> if os.path.isfile(path):
        >>>     if path.endswith('.py'):
        >>>         files = [path]
        >>>     else:
        >>>         files = []
        >>> elif os.path.isdir(path):
        >>>     files = glob.glob(os.path.join(path, '*.py'))
        >>> else:
        >>>     files = []
        >>> 
        >>> # SDA approach (centralized intelligence):
        >>> path_type = PathType.from_path(path)
        >>> files = path_type.get_python_files(path)
    
    SDA Pattern Demonstrated:
        Smart Enums - The enum encapsulates all file system classification logic,
        making it reusable and testable. This is "intelligence in types" - the
        type system understands the domain.
        
    Implementation Note:
        The nested dispatch pattern (True/False -> classifier methods) shows
        how to handle multi-level decisions without nested conditionals.
    """

    PYTHON_FILE = "python_file"
    DIRECTORY = "directory"
    OTHER = "other"

    @classmethod
    def from_path(cls, path_str: str) -> "PathType":
        """Factory method to classify path type using discriminated union dispatch."""
        from pathlib import Path

        path = Path(path_str)

        # Pure type dispatch - no conditionals
        path_classifiers = {True: cls._classify_file, False: cls._classify_non_file}

        return path_classifiers[path.is_file()](path)

    @classmethod
    def _classify_file(cls, path: Path) -> "PathType":
        """Classify file paths using suffix dispatch."""
        suffix_types = {
            ".py": cls.PYTHON_FILE,
        }
        return suffix_types.get(path.suffix, cls.OTHER)

    @classmethod
    def _classify_non_file(cls, path: Path) -> "PathType":
        """Classify non-file paths."""
        return cls.DIRECTORY if path.is_dir() else cls.OTHER

    def get_python_files(self, path_str: str) -> list[str]:
        """Get Python files using pure dispatch - no conditionals."""
        path = Path(path_str)

        # Pure dictionary dispatch without lambdas
        file_getters: dict[PathType, list[str]] = {
            PathType.PYTHON_FILE: [str(path)],
            PathType.DIRECTORY: [str(f) for f in path.glob("*.py")],
            PathType.OTHER: [],
        }

        return file_getters[self]


class FindingClassifier(StrEnum):
    """Discriminated union for finding classification - Organizing Analysis Results.

    WHAT: Classifies analysis findings into violations, positive patterns, or unknown
    based on their properties, enabling type-driven report generation.
    
    WHY: Findings need to be organized into different collections for reporting.
    Instead of scattered if/else logic checking properties, this type centralizes
    the classification and collection logic.
    
    HOW: Uses boolean tuple indexing - a powerful pattern for multi-condition
    dispatch without conditionals. The from_finding() method creates a tuple
    of booleans, then uses it as a dictionary key.
    
    Teaching Example:
        >>> # Traditional approach (nested conditionals):
        >>> if finding.pattern_category:
        >>>     if finding.pattern_type:
        >>>         violations.append(finding)  # Has both
        >>>     else:
        >>>         violations.append(finding)  # Just violation
        >>> elif finding.pattern_type:
        >>>     patterns.append(finding)  # Just pattern
        >>> else:
        >>>     pass  # Unknown, ignore
        >>> 
        >>> # SDA approach (pure dispatch):
        >>> classifier = FindingClassifier.from_finding(finding)
        >>> classifier.add_to_collections(finding, violations, patterns)
    
    SDA Pattern Demonstrated:
        Boolean Tuple Dispatch - Using tuples of booleans as dictionary keys
        enables complex multi-condition logic without any conditionals. This
        pattern scales to any number of conditions while remaining pure.
        
    Advanced Technique:
        The (has_violation, has_pattern) tuple creates 4 possible states,
        all handled explicitly in the classification_map. This exhaustive
        handling prevents bugs from unhandled edge cases.
    """

    VIOLATION = "violation"
    PATTERN = "pattern"
    UNKNOWN = "unknown"

    @classmethod
    def from_finding(cls, finding: "Finding") -> "FindingClassifier":
        """Classify finding type using discriminated union dispatch.
        
        Teaching Note: BOOLEAN TUPLE DISPATCH MASTERY
        
        This is an advanced SDA pattern that eliminates complex nested conditionals:
        
        1. Convert conditions to booleans (has_violation, has_pattern)
        2. Create a tuple from the booleans - this becomes our "key"
        3. Map ALL possible combinations (2^n for n booleans)
        4. Look up the result - O(1) operation!
        
        With 2 booleans we have 4 cases. With 3 booleans we'd have 8 cases.
        This scales better than nested if/elif because:
        - All cases are visible in one place
        - Impossible to miss a case (dict would KeyError)
        - Easy to test - just check all tuples
        - Performance is always O(1) regardless of case count
        """
        # Teaching: Pure boolean coercion - no conditionals
        # bool() ensures we get True/False even if values are None
        has_violation = bool(finding.pattern_category)
        has_pattern = bool(finding.pattern_type)

        # Teaching: Boolean tuple becomes dictionary key
        # This maps a 2D decision space to a single lookup
        classification_index = (has_violation, has_pattern)
        classification_map = {
            (True, False): cls.VIOLATION,  # Has violation, no pattern
            (False, True): cls.PATTERN,  # Has pattern, no violation
            (True, True): cls.VIOLATION,  # Both - violation takes precedence
            (False, False): cls.UNKNOWN,  # Neither
        }

        return classification_map[classification_index]

    def add_to_collections(
        self,
        finding: "Finding",
        violations: dict["PatternType", list["Finding"]],
        patterns: dict["PositivePattern", list["Finding"]],
    ) -> None:
        """Add finding to appropriate collection using pure dispatch.
        
        Teaching Note: METHOD DISPATCH PATTERN
        
        Instead of if/elif checking the classifier type, we:
        1. Map each enum value to a method
        2. Look up the method for our value (self)
        3. Call it with the same parameters
        
        This pattern keeps methods small and focused. Each method does
        ONE thing based on ONE enum value. This is Single Responsibility
        at the method level.
        """
        # Teaching: Pure dictionary dispatch - no conditionals
        # Maps enum values to methods that handle each case
        collection_handlers = {
            FindingClassifier.VIOLATION: self._add_violation,
            FindingClassifier.PATTERN: self._add_pattern,
            FindingClassifier.UNKNOWN: self._ignore_finding,
        }

        collection_handlers[self](finding, violations, patterns)

    def _add_violation(
        self,
        finding: "Finding",
        violations: dict["PatternType", list["Finding"]],
        patterns: dict["PositivePattern", list["Finding"]],
    ) -> None:
        """Add violation finding to violations collection."""
        if violation_pattern := finding.pattern_category:
            violations.setdefault(violation_pattern, []).append(finding)

    def _add_pattern(
        self,
        finding: "Finding",
        violations: dict["PatternType", list["Finding"]],
        patterns: dict["PositivePattern", list["Finding"]],
    ) -> None:
        """Add pattern finding to patterns collection."""
        if positive_pattern := finding.pattern_type:
            patterns.setdefault(positive_pattern, []).append(finding)

    def _ignore_finding(
        self,
        finding: "Finding",
        violations: dict["PatternType", list["Finding"]],
        patterns: dict["PositivePattern", list["Finding"]],
    ) -> None:
        """Ignore unknown findings."""
        pass


class CLIArgumentState(StrEnum):
    """Discriminated union for CLI argument validation.

    Eliminates if/else chains in CLI argument handling.
    """

    NO_ARGS = "no_args"
    PATH_ONLY = "path_only"
    PATH_AND_NAME = "path_and_name"

    @classmethod
    def from_argv(cls, argv: list[str]) -> "CLIArgumentState":
        """Classify CLI argument state using pure dispatch."""
        arg_count = len(argv)

        # Pure dictionary dispatch based on argument count
        count_mapping = {
            0: cls.NO_ARGS,
            1: cls.NO_ARGS,  # argv[0] is the script name
            2: cls.PATH_ONLY,
            3: cls.PATH_AND_NAME,
        }

        # For counts > 3, treat as PATH_AND_NAME
        return count_mapping.get(arg_count, cls.PATH_AND_NAME)

    def handle_arguments(self, argv: list[str]) -> tuple[str | None, str | None, bool]:
        """Handle CLI arguments based on state.

        Returns: (module_path, module_name, should_continue)
        """
        handlers = {
            CLIArgumentState.NO_ARGS: self._handle_no_args,
            CLIArgumentState.PATH_ONLY: self._handle_path_only,
            CLIArgumentState.PATH_AND_NAME: self._handle_path_and_name,
        }

        return handlers[self](argv)

    def _handle_no_args(self, argv: list[str]) -> tuple[str | None, str | None, bool]:
        """Handle case with no arguments - print usage."""
        print("Usage: sda-detector <module_path> [module_name]")
        return None, None, False

    def _handle_path_only(self, argv: list[str]) -> tuple[str | None, str | None, bool]:
        """Handle case with path only."""
        return argv[1], None, True

    def _handle_path_and_name(self, argv: list[str]) -> tuple[str | None, str | None, bool]:
        """Handle case with path and name."""
        return argv[1], argv[2], True


class ModuleTypeClassifier(StrEnum):
    """Discriminated union for module type classification.

    Eliminates if/elif chains for module type detection using pure dispatch.
    """

    TEST = "test"
    DOMAIN = "domain"
    MODEL = "model"
    SERVICE = "service"
    API = "api"
    MIXED = "mixed"

    @classmethod
    def from_path(cls, module_path: str) -> "ModuleType":
        """Classify module type from path using pure discriminated union dispatch.

        Pure SDA implementation using priority-based keyword detection.
        """
        path_lower = module_path.lower()

        # Priority-based classification using boolean indexing
        has_test = "test" in path_lower
        has_domain = "model" in path_lower or "domain" in path_lower
        has_service = "service" in path_lower or "api" in path_lower

        # Pure tuple-based dispatch - no conditionals
        classification_key = (has_test, has_domain, has_service)

        # Exhaustive mapping of all combinations
        classification_map = {
            (True, False, False): ModuleType.TOOLING,  # test only
            (True, True, False): ModuleType.TOOLING,  # test + domain
            (True, False, True): ModuleType.TOOLING,  # test + service
            (True, True, True): ModuleType.TOOLING,  # test + all
            (False, True, False): ModuleType.DOMAIN,  # domain only
            (False, True, True): ModuleType.DOMAIN,  # domain + service
            (False, False, True): ModuleType.INFRASTRUCTURE,  # service only
            (False, False, False): ModuleType.MIXED,  # none
        }

        return classification_map[classification_key]


class ModuleType(StrEnum):
    """Types of modules with different architectural patterns and expectations.

    Each module type has different tolerance levels for certain patterns:
    - DOMAIN: Pure business logic, should minimize conditionals and external dependencies
    - INFRASTRUCTURE: Boundary code, may need error handling and external service integration
    - TOOLING: Analysis/development tools, may need runtime reflection and file system access
    - FRAMEWORK: Third-party integration code, follows external library patterns
    - MIXED: Combination of concerns, evaluated with balanced criteria
    """

    DOMAIN = "domain"
    INFRASTRUCTURE = "infrastructure"
    TOOLING = "tooling"
    FRAMEWORK = "framework"
    MIXED = "mixed"

    @property
    def analysis_priority(self) -> int:
        """Self-determining analysis priority using type dispatch."""
        priorities = {
            ModuleType.DOMAIN: 20,  # Highest priority (lowest number) - pure business logic
            ModuleType.INFRASTRUCTURE: 40,  # High priority - critical boundaries
            ModuleType.TOOLING: 60,  # Medium priority - development tools
            ModuleType.FRAMEWORK: 80,  # Lower priority - external integration
            ModuleType.MIXED: 100,  # Lowest priority (highest number) - mixed concerns
        }
        return priorities.get(self, 110)


class PatternType(StrEnum):
    """Neutral classification of architectural patterns detected in code.

    WHAT: Identifies procedural/imperative patterns that SDA seeks to replace
    with type-driven alternatives. These aren't necessarily "bad" - they're
    just different approaches with different tradeoffs.
    
    WHY: To migrate from procedural to type-driven architecture, we must first
    identify where procedural patterns exist. This enum catalogs patterns that
    have type-driven alternatives.
    
    HOW: Each pattern represents a specific coding approach that can be detected
    via AST analysis and potentially replaced with SDA patterns.
    
    Teaching Examples:
        
        BUSINESS_CONDITIONALS - Traditional vs SDA:
        >>> # Traditional:
        >>> if order.status == 'pending':
        >>>     process_pending(order)
        >>> elif order.status == 'shipped':
        >>>     process_shipped(order)
        >>> 
        >>> # SDA alternative (discriminated union):
        >>> handlers = {
        >>>     OrderStatus.PENDING: process_pending,
        >>>     OrderStatus.SHIPPED: process_shipped,
        >>> }
        >>> handlers[order.status](order)
        
        ISINSTANCE_USAGE - Traditional vs SDA:
        >>> # Traditional:
        >>> if isinstance(shape, Circle):
        >>>     return math.pi * shape.radius ** 2
        >>> elif isinstance(shape, Rectangle):
        >>>     return shape.width * shape.height
        >>> 
        >>> # SDA alternative (polymorphic dispatch):
        >>> return shape.calculate_area()  # Each shape knows its formula
        
        TRY_EXCEPT_USAGE - Traditional vs SDA:
        >>> # Traditional:
        >>> try:
        >>>     value = dangerous_operation()
        >>> except ValueError:
        >>>     value = default_value
        >>> 
        >>> # SDA alternative (Result type):
        >>> result = safe_operation()  # Returns Result[Value, Error]
        >>> value = result.unwrap_or(default_value)
    
    SDA Pattern Demonstrated:
        Pattern Catalog - By cataloging procedural patterns, we can systematically
        identify refactoring opportunities. This is "knowledge as data" - the
        enum itself documents what to look for and why.
        
    Philosophy Note:
        These patterns represent different programming paradigms. Procedural
        code asks "what type is this?" and "did this fail?" Type-driven
        code says "you handle yourself" and "success and failure are both values."
    """

    # Teaching: Conditional logic patterns - different approaches to control flow
    BUSINESS_CONDITIONALS = "business_conditionals"  # if/elif for business rules - replace with dispatch tables
    ISINSTANCE_USAGE = "isinstance_usage"  # Runtime type checking - replace with discriminated unions
    HASATTR_USAGE = "hasattr_usage"  # Attribute existence checks - replace with protocols/interfaces
    GETATTR_USAGE = "getattr_usage"  # Dynamic attribute access - replace with typed models
    DICT_GET_USAGE = "dict_get_usage"  # dict.get() instead of typed models - use Pydantic models
    TRY_EXCEPT_USAGE = "try_except_usage"  # Exception handling for control flow - use Result types

    # Teaching: Type system patterns - different approaches to type usage
    ANY_TYPE_USAGE = "any_type_usage"  # Using Any type annotation - loses type safety
    MISSING_FIELD_CONSTRAINTS = "missing_field_constraints"  # Fields without validation - use Field()
    PRIMITIVE_OBSESSION = "primitive_obsession"  # Raw str/int instead of value objects - wrap in types
    ENUM_VALUE_ACCESS = "enum_value_access"  # .value calls on StrEnum/Enum - use enum directly
    MISSING_MODEL_CONFIG = "missing_model_config"  # No model configuration - add ModelConfig
    NO_FORWARD_REFS = "no_forward_refs"  # Missing forward references - use 'ClassName' strings
    MANUAL_VALIDATION = "manual_validation"  # Hand-written validation - use Pydantic validators
    ANEMIC_SERVICES = "anemic_services"  # Services that are just bags of functions - add to models
    MANUAL_JSON_SERIALIZATION = "manual_json_serialization"  # Manual json.dumps/loads - use model_dump()


# FindingClassificationType removed - has broken lambda calls and unused


# ServiceOperationType removed - unused and has broken imports


# PathProcessingType removed - unused and has broken lambda calls


class PositivePattern(StrEnum):
    """Enumeration of architectural patterns that align with SDA principles.

    WHAT: Identifies type-driven patterns that represent SDA best practices.
    These are the patterns we want to see more of in codebases.
    
    WHY: These patterns indicate sophisticated use of Python's type system
    and Pydantic's capabilities to encode business logic into types rather
    than procedural code. They lead to more maintainable, bug-free software.
    
    HOW: Each pattern represents a specific technique for encoding intelligence
    into the type system, detected via AST analysis.
    
    Teaching Examples:
        
        PYDANTIC_MODELS - Domain models with built-in validation:
        >>> class Price(BaseModel):
        >>>     amount: Decimal = Field(ge=0, decimal_places=2)
        >>>     currency: Currency  # Currency is an enum
        >>>     
        >>>     @computed_field
        >>>     @property
        >>>     def display_value(self) -> str:
        >>>         return f"{self.currency.symbol}{self.amount}"
        
        BEHAVIORAL_ENUMS - Enums that encode their own logic:
        >>> class OrderStatus(StrEnum):
        >>>     PENDING = "pending"
        >>>     SHIPPED = "shipped"
        >>>     
        >>>     def can_cancel(self) -> bool:
        >>>         return self == self.PENDING
        >>>     
        >>>     def next_status(self) -> Optional['OrderStatus']:
        >>>         transitions = {
        >>>             self.PENDING: self.SHIPPED,
        >>>             self.SHIPPED: None,
        >>>         }
        >>>         return transitions[self]
        
        TYPE_DISPATCH_TABLES - Replacing conditionals with dictionaries:
        >>> # Instead of if/elif chains:
        >>> processors: dict[EventType, Callable] = {
        >>>     EventType.CREATED: handle_created,
        >>>     EventType.UPDATED: handle_updated,
        >>>     EventType.DELETED: handle_deleted,
        >>> }
        >>> result = processors[event.type](event)
        
        DISCRIMINATED_UNIONS - Type-safe variants:
        >>> class Result(BaseModel):
        >>>     # Tagged union with discriminator
        >>>     kind: Literal["success", "error"] = Field(discriminator="kind")
        >>> 
        >>> class Success(Result):
        >>>     kind: Literal["success"] = "success"
        >>>     value: Any
        >>> 
        >>> class Error(Result):
        >>>     kind: Literal["error"] = "error"
        >>>     message: str
    
    SDA Pattern Demonstrated:
        Best Practices Catalog - This enum documents the patterns that represent
        architectural maturity. Teams can use this as a checklist for code quality.
        
    Higher counts of these patterns suggest more mature architectural design
    that leverages type-driven development. The goal is to maximize these
    patterns while minimizing the PatternType violations.
    
    Philosophy:
        Each pattern here represents a shift from "telling computers what to do"
        to "teaching types how to behave." This is the essence of SDA - intelligence
        in types, not procedures.
    """

    # Teaching: Core SDA patterns - business logic in types
    PYDANTIC_MODELS = "pydantic_models"  # BaseModel classes - domain models with validation
    BEHAVIORAL_ENUMS = "behavioral_enums"  # Enums with methods - logic in the type itself
    COMPUTED_FIELDS = "computed_fields"  # @computed_field properties - derived state
    VALIDATORS = "validators"  # Pydantic validators - business rules as types
    PROTOCOLS = "protocols"  # typing.Protocol interfaces - structural typing
    TYPE_DISPATCH_TABLES = "type_dispatch_tables"  # Dictionary-based dispatch - no conditionals

    # Teaching: Pydantic integration patterns - leveraging the framework
    PYDANTIC_VALIDATION = "pydantic_validation"  # model_validate* calls - type-safe parsing
    PYDANTIC_SERIALIZATION = "pydantic_serialization"  # model_dump* calls - type-safe output
    IMMUTABLE_UPDATES = "immutable_updates"  # model_copy usage - functional updates
    FIELD_CONSTRAINTS = "field_constraints"  # Field() with constraints - validation in types
    MODEL_CONFIG_USAGE = "model_config_usage"  # ModelConfig definitions - model behavior

    # Advanced type system patterns
    UNION_TYPES = "union_types"  # Union type annotations
    LITERAL_TYPES = "literal_types"  # Literal type annotations
    DISCRIMINATED_UNIONS = "discriminated_unions"  # Tagged union patterns
    FORWARD_REFERENCES = "forward_references"  # Self-referential types
    ANNOTATED_TYPES = "annotated_types"  # Annotated type hints
    GENERIC_MODELS = "generic_models"  # Generic Pydantic models
    RECURSIVE_MODELS = "recursive_models"  # Self-referential models

    # Pydantic advanced features
    CUSTOM_VALIDATORS = "custom_validators"  # @field_validator, @model_validator
    CUSTOM_SERIALIZERS = "custom_serializers"  # @field_serializer
    ROOT_VALIDATORS = "root_validators"  # @root_validator (legacy)

    # Code organization patterns
    ENUM_METHODS = "enum_methods"  # Methods on enum classes
    BOUNDARY_CONDITIONS = "boundary_conditions"  # Proper error handling at boundaries
    TYPE_CHECKING_IMPORTS = "type_checking_imports"  # TYPE_CHECKING blocks


class ScopeNaming(StrEnum):
    """Behavioral enum - scope names know their own capabilities."""

    CONDITIONAL = "conditional"
    CALL = "call"
    ATTRIBUTE = "attribute"
    UNKNOWN = "unknown"

    def is_analyzable(self) -> bool:
        """Behavioral method - scope names know if they should be analyzed."""
        analyzable_scopes = {ScopeNaming.CONDITIONAL, ScopeNaming.CALL, ScopeNaming.ATTRIBUTE}
        return self in analyzable_scopes

    def get_display_name(self) -> str:
        """Behavioral method - scope names know how to display themselves."""
        display_names = {
            ScopeNaming.CONDITIONAL: "Conditional Block",
            ScopeNaming.CALL: "Function Call",
            ScopeNaming.ATTRIBUTE: "Attribute Access",
            ScopeNaming.UNKNOWN: "Unknown Scope",
        }
        return display_names[self]

    def create_scope_identifier(self, node_name: str) -> str:
        """Behavioral method - scope names know how to create identifiers."""
        identifier_patterns = {
            ScopeNaming.CONDITIONAL: f"condition_{node_name}",
            ScopeNaming.CALL: f"call_{node_name}",
            ScopeNaming.ATTRIBUTE: f"attr_{node_name}",
            ScopeNaming.UNKNOWN: f"unknown_{node_name}",
        }
        return identifier_patterns[self]
