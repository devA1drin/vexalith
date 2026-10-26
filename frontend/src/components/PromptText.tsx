/** The question in plain words, with its "Your task:" line set apart so it's easy to spot. */
export function PromptText({ prompt }: { prompt: string }) {
  const [question, ...rest] = prompt.split("\n\n");
  const task = rest.join("\n\n");
  return (
    <div className="space-y-2 border-l-2 border-accent pl-4" data-testid="prompt">
      <p className="text-[17px] font-medium leading-relaxed text-ink-50">{question}</p>
      {task && (
        <p className="text-[15px] leading-relaxed text-ink-200" data-testid="task-line">
          {task.startsWith("Your task:") ? (
            <>
              <span className="font-mono text-[12px] uppercase tracking-wider text-accent">Your task · </span>
              {task.replace(/^Your task:\s*/, "")}
            </>
          ) : (
            task
          )}
        </p>
      )}
    </div>
  );
}
