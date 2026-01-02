import { useState } from "react";
import { Copy, Check } from "lucide-react";

interface CodeBlockProps {
  code: string;
  language?: string;
}

export const CodeBlock = ({ code, language = "python" }: CodeBlockProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Simple syntax highlighting for Python
  const highlightCode = (code: string) => {
    const keywords = ['def', 'return', 'if', 'else', 'elif', 'for', 'while', 'import', 'from', 'class', 'try', 'except', 'raise', 'not', 'or', 'and', 'in', 'is', 'True', 'False', 'None', 'print'];
    const types = ['int', 'str', 'float', 'bool', 'list', 'dict', 'tuple', 'set'];
    
    return code.split('\n').map((line, lineIndex) => {
      const parts: React.ReactNode[] = [];
      let remaining = line;
      let key = 0;

      // Handle comments
      const commentIndex = remaining.indexOf('#');
      let commentPart = '';
      if (commentIndex !== -1) {
        commentPart = remaining.slice(commentIndex);
        remaining = remaining.slice(0, commentIndex);
      }

      // Tokenize and highlight
      const tokens = remaining.split(/(\s+|[(),:.\[\]{}=<>+\-*/%]|""".*?"""|'''.*?'''|".*?"|'.*?')/g);
      
      tokens.forEach((token, i) => {
        if (!token) return;
        
        // String literals
        if ((token.startsWith('"') && token.endsWith('"')) || 
            (token.startsWith("'") && token.endsWith("'"))) {
          parts.push(<span key={key++} className="text-code-string">{token}</span>);
        }
        // Keywords
        else if (keywords.includes(token)) {
          parts.push(<span key={key++} className="text-code-keyword">{token}</span>);
        }
        // Types
        else if (types.includes(token)) {
          parts.push(<span key={key++} className="text-code-type">{token}</span>);
        }
        // Numbers
        else if (/^\d+$/.test(token)) {
          parts.push(<span key={key++} className="text-code-number">{token}</span>);
        }
        // Function names (word followed by open paren in next token)
        else if (/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(token) && tokens[i + 1] === '(') {
          parts.push(<span key={key++} className="text-code-function">{token}</span>);
        }
        // Default
        else {
          parts.push(<span key={key++} className="text-code-foreground">{token}</span>);
        }
      });

      // Add comment
      if (commentPart) {
        parts.push(<span key={key++} className="text-code-comment">{commentPart}</span>);
      }

      return (
        <div key={lineIndex} className="leading-relaxed">
          {parts.length > 0 ? parts : '\u00A0'}
        </div>
      );
    });
  };

  return (
    <div className="rounded-lg overflow-hidden bg-code-background my-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-secondary/50 border-b border-border/50">
        <span className="text-sm text-muted-foreground font-medium">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          {copied ? (
            <>
              <Check size={14} />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Copy size={14} />
              <span>Copy code</span>
            </>
          )}
        </button>
      </div>
      
      {/* Code content */}
      <div className="p-4 overflow-x-auto">
        <pre className="font-mono text-sm">
          <code>{highlightCode(code)}</code>
        </pre>
      </div>
    </div>
  );
};
