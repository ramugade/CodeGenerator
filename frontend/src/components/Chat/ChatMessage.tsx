import { CodeBlock } from "./CodeBlock";
import { MessageActions } from "./MessageActions";

interface ChatMessageProps {
  type: "user" | "assistant";
  content: string;
  code?: {
    language: string;
    content: string;
  };
}

export const ChatMessage = ({ type, content, code }: ChatMessageProps) => {
  if (type === "user") {
    return (
      <div className="flex justify-end mb-6 animate-fade-in">
        <div className="max-w-2xl bg-secondary rounded-2xl px-5 py-3">
          <p className="text-foreground">{content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-8 max-w-4xl animate-fade-in">
      {code && <CodeBlock code={code.content} language={code.language} />}
      <MessageActions />
    </div>
  );
};
