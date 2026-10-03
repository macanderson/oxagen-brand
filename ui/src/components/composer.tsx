"use client";
import * as React from "react";
import { PaperPlaneTiltIcon, PaperclipIcon } from "@phosphor-icons/react";
import { cn } from "../lib/utils";
import {
  ATTACHMENT_ACCEPT,
  AttachmentCard,
  type AttachmentFile,
} from "./attachment";
import { Button } from "./button";

/*
 * The question box with file attachments (#246). Files arrive three ways:
 * the attach button, drag and drop onto the composer, and paste. Each file
 * shows as a card above the input.
 *
 * The composer holds no upload logic. It hands new files to `onFilesAdd` and
 * shows whatever `files` the caller passes back, each with its own state. The
 * caller uploads, dedupes, refuses a kind it does not take, and makes preview
 * URLs. Send stays disabled while any file uploads.
 */

export interface ComposerProps
  extends Omit<
    React.ComponentProps<"form">,
    | "children"
    | "defaultValue"
    | "onSubmit"
    | "onDragEnter"
    | "onDragOver"
    | "onDragLeave"
    | "onDrop"
  > {
  /** The attached files, in the order the cards show them. */
  files?: readonly AttachmentFile[] | undefined;
  /** Called with the files a person attached, dropped, or pasted. */
  onFilesAdd?: ((files: File[]) => void) | undefined;
  /** Called when a person removes a card. */
  onFileRemove?: ((file: AttachmentFile) => void) | undefined;
  /** The text in the input. Leave it out to let the composer hold the text. */
  value?: string | undefined;
  defaultValue?: string | undefined;
  onValueChange?: ((value: string) => void) | undefined;
  /** Called with the text when a person sends. The caller clears the files. */
  onSend?: ((value: string) => void) | undefined;
  /** The accessible name of the input. */
  label?: string | undefined;
  placeholder?: string | undefined;
  /** The file types the attach button offers. */
  accept?: string | undefined;
  /** Shows the drop-target state without a drag, for stories and previews. */
  dropActive?: boolean | undefined;
  disabled?: boolean | undefined;
  /** Content between the attach button and Send, such as the model name. */
  toolbar?: React.ReactNode;
}

function isFileDrag(event: React.DragEvent): boolean {
  return Array.from(event.dataTransfer?.types ?? []).includes("Files");
}

function Composer({
  files = [],
  onFilesAdd,
  onFileRemove,
  value,
  defaultValue = "",
  onValueChange,
  onSend,
  label = "Ask Stella",
  placeholder = "Ask about this workspace",
  accept = ATTACHMENT_ACCEPT,
  dropActive = false,
  disabled = false,
  toolbar,
  className,
  ...props
}: ComposerProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [innerValue, setInnerValue] = React.useState(defaultValue);
  const [dragging, setDragging] = React.useState(false);
  const text = value ?? innerValue;
  const uploading = files.some((file) => file.state === "uploading");
  const canSend =
    !disabled && !uploading && (text.trim() !== "" || files.length > 0);
  const over = dropActive || dragging;

  function setText(next: string) {
    if (value === undefined) setInnerValue(next);
    onValueChange?.(next);
  }

  function addFiles(list: FileList | readonly File[] | null | undefined) {
    const added = Array.from(list ?? []);
    if (disabled || added.length === 0) return;
    onFilesAdd?.(added);
  }

  function send() {
    if (!canSend) return;
    onSend?.(text);
    if (value === undefined) setInnerValue("");
  }

  function onDragOver(event: React.DragEvent<HTMLFormElement>) {
    if (!isFileDrag(event)) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = disabled ? "none" : "copy";
    if (!disabled) setDragging(true);
  }

  function onDragLeave(event: React.DragEvent<HTMLFormElement>) {
    // Moving between the composer's own children fires dragleave too. Only a
    // pointer that leaves the composer clears the drop target.
    const next = event.relatedTarget;
    if (next instanceof Node && event.currentTarget.contains(next)) return;
    setDragging(false);
  }

  function onDrop(event: React.DragEvent<HTMLFormElement>) {
    if (!isFileDrag(event)) return;
    event.preventDefault();
    setDragging(false);
    addFiles(event.dataTransfer.files);
  }

  return (
    <form
      data-slot="composer"
      data-dragging={over ? "" : undefined}
      data-uploading={uploading ? "" : undefined}
      className={cn("group/composer flex min-w-0 flex-col gap-2", className)}
      {...props}
      onSubmit={(event) => {
        event.preventDefault();
        send();
      }}
      onDragEnter={onDragOver}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {files.length > 0 && (
        <div
          data-slot="composer-files"
          role="group"
          aria-label="Attached files"
          className="flex min-w-0 flex-wrap gap-2"
        >
          {files.map((file) => (
            <AttachmentCard key={file.id} file={file} onRemove={onFileRemove} />
          ))}
        </div>
      )}
      <textarea
        data-slot="composer-input"
        aria-label={label}
        placeholder={placeholder}
        value={text}
        disabled={disabled}
        onChange={(event) => setText(event.currentTarget.value)}
        onPaste={(event) => {
          const pasted = event.clipboardData?.files;
          if (!pasted || pasted.length === 0) return;
          event.preventDefault();
          addFiles(pasted);
        }}
        onKeyDown={(event) => {
          if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.nativeEvent.isComposing
          ) {
            event.preventDefault();
            send();
          }
        }}
        className={cn(
          "block min-h-[60px] max-h-[180px] w-full resize-none field-sizing-content rounded-[10px] border border-border bg-background px-[11px] py-[9px] text-base leading-[1.5] text-foreground transition-colors placeholder:text-dim focus-visible:border-gold focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 max-md:text-input-touch",
          "group-data-[dragging]/composer:border-dashed group-data-[dragging]/composer:border-gold group-data-[dragging]/composer:bg-hl",
        )}
      />
      <div
        data-slot="composer-bar"
        className="flex min-w-0 items-center gap-2.5"
      >
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="Attach files"
          title="Attach files"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
        >
          <PaperclipIcon aria-hidden="true" />
        </Button>
        <input
          ref={inputRef}
          data-slot="composer-file-input"
          type="file"
          multiple
          hidden
          tabIndex={-1}
          accept={accept}
          onChange={(event) => {
            const picked = Array.from(event.currentTarget.files ?? []);
            // Clear the input so picking the same file again still fires change.
            event.currentTarget.value = "";
            addFiles(picked);
          }}
        />
        <div className="min-w-0 flex-1 truncate text-sm text-dim">
          {toolbar}
        </div>
        <Button
          type="submit"
          size="sm"
          disabled={!canSend}
          disabledTooltip={
            uploading ? "The files are still uploading" : undefined
          }
          startIcon={<PaperPlaneTiltIcon aria-hidden="true" />}
        >
          Send
        </Button>
      </div>
    </form>
  );
}

/**
 * A question a person sent, with its files as cards above the text. The
 * cards have no remove button.
 */
function ComposerSentTurn({
  files = [],
  children,
  className,
  ...props
}: React.ComponentProps<"div"> & {
  files?: readonly AttachmentFile[] | undefined;
}) {
  return (
    <div
      data-slot="composer-sent-turn"
      className={cn(
        "ml-auto flex w-fit max-w-[88%] flex-col gap-1.5 rounded-[12px_12px_4px_12px] border border-border bg-hl px-3 py-2 text-base leading-[1.5] text-foreground [overflow-wrap:anywhere]",
        className,
      )}
      {...props}
    >
      {files.length > 0 && (
        <div className="flex min-w-0 flex-wrap gap-2">
          {files.map((file) => (
            <AttachmentCard key={file.id} file={file} className="bg-background" />
          ))}
        </div>
      )}
      {children != null && children !== "" && <p>{children}</p>}
    </div>
  );
}

export { Composer, ComposerSentTurn };
