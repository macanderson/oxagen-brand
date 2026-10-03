// Moved from oxagen apps/app/src/ui/attachment.tsx at ddb85803.
// A file shown as a chip: its icon or preview, its name, one line about it,
// and an action such as Remove. Ported from shadcn's base-maia `attachment`
// (https://ui.shadcn.com/docs/components/base/attachment) with the same slots
// and data attributes (#4690, ADR-222). The slots merge classes with `cn`, so
// a caller's class replaces the slot's own class for the same property.
//
// The chip sits on the assistant's flyout, a raised surface, so it is drawn
// with the raised tokens, and its action with the app's link tokens.
//
// `AttachmentCard` builds the composer's file card (#246) from these slots:
// a 40px tile for the kind, the name, then the kind and the size.
import type { ComponentProps } from "react";
import {
  FileCodeIcon,
  FileIcon,
  FileImageIcon,
  FilePdfIcon,
  FileTextIcon,
  XIcon,
} from "@phosphor-icons/react/ssr";
import type { Icon, IconProps } from "@phosphor-icons/react";
import { cn } from "../lib/utils";

/** Where a file is on its way to the message. */
export type AttachmentState = "uploading" | "error" | "done";

type AttachmentSize = "default" | "sm" | "xs";

const SIZE: Record<AttachmentSize, string> = {
  default:
    "gap-2 px-2.5 py-2 text-base has-data-[slot=attachment-media]:p-2 has-data-[slot=attachment-media]:pr-2.5",
  sm: "gap-2 px-2 py-1.5 text-sm has-data-[slot=attachment-media]:p-1.5 has-data-[slot=attachment-media]:pr-2",
  xs: "gap-1.5 rounded-lg px-1.5 py-1 text-sm has-data-[slot=attachment-media]:p-1 has-data-[slot=attachment-media]:pr-1.5",
};

/** One file. `state` reaches `data-state`, which every slot reads. */
export function Attachment({
  className,
  state = "done",
  size = "default",
  ...props
}: ComponentProps<"div"> & {
  state?: AttachmentState;
  size?: AttachmentSize;
}) {
  return (
    <div
      data-slot="attachment"
      data-state={state}
      data-size={size}
      aria-busy={state === "uploading" ? true : undefined}
      className={cn(
        "group/attachment relative flex w-fit max-w-full min-w-0 shrink-0 items-center rounded-xl border border-border bg-app-raised-bg text-app-raised-fg transition-colors focus-within:ring-1 focus-within:ring-ring/50 data-[state=error]:border-destructive/40",
        SIZE[size],
        className,
      )}
      {...props}
    />
  );
}

/** The file's icon, or a preview image with `variant="image"`. */
export function AttachmentMedia({
  className,
  variant = "icon",
  ...props
}: ComponentProps<"div"> & { variant?: "icon" | "image" }) {
  return (
    <div
      data-slot="attachment-media"
      data-variant={variant}
      className={cn(
        "relative flex aspect-square w-9 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-muted text-foreground group-data-[size=sm]/attachment:w-8 group-data-[size=xs]/attachment:w-7 group-data-[size=xs]/attachment:rounded-md group-data-[state=error]/attachment:bg-destructive/10 group-data-[state=error]/attachment:text-destructive [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 group-data-[size=xs]/attachment:[&_svg:not([class*='size-'])]:size-3.5",
        variant === "image" &&
          "opacity-60 group-data-[state=done]/attachment:opacity-100 *:[img]:aspect-square *:[img]:w-full *:[img]:object-cover",
        className,
      )}
      {...props}
    />
  );
}

/** The name and the line under it. */
export function AttachmentContent({
  className,
  ...props
}: ComponentProps<"div">) {
  return (
    <div
      data-slot="attachment-content"
      className={cn("max-w-full min-w-0 flex-1 leading-tight", className)}
      {...props}
    />
  );
}

/**
 * The file's name, cut with an ellipsis when it does not fit. It shimmers
 * while the file uploads.
 */
export function AttachmentTitle({
  className,
  ...props
}: ComponentProps<"span">) {
  return (
    <span
      data-slot="attachment-title"
      className={cn(
        "block max-w-48 min-w-0 truncate font-medium group-data-[state=uploading]/attachment:text-shimmer",
        className,
      )}
      {...props}
    />
  );
}

/**
 * One line about the file. Put each fact in its own element and let the gap
 * separate them, rather than joining them with punctuation.
 */
export function AttachmentDescription({
  className,
  ...props
}: ComponentProps<"span">) {
  return (
    <span
      data-slot="attachment-description"
      className={cn(
        "mt-0.5 flex max-w-48 min-w-0 gap-2 truncate text-sm text-muted-foreground group-data-[state=error]/attachment:text-destructive",
        className,
      )}
      {...props}
    />
  );
}

/** Where the chip's buttons sit. */
export function AttachmentActions({
  className,
  ...props
}: ComponentProps<"div">) {
  return (
    <div
      data-slot="attachment-actions"
      className={cn("relative flex shrink-0 items-center", className)}
      {...props}
    />
  );
}

/** An icon button on the chip. The caller names it with `aria-label`. */
export function AttachmentAction({
  className,
  type = "button",
  ...props
}: ComponentProps<"button"> & { "aria-label": string }) {
  return (
    <button
      data-slot="attachment-action"
      type={type}
      className={cn(
        "inline-flex size-6 items-center justify-center rounded-md text-app-link-fg outline-none hover:bg-app-link-hover-bg hover:text-app-link-hover-fg focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-3.5",
        className,
      )}
      {...props}
    />
  );
}

/** A row of chips that scrolls sideways when it runs out of room. */
export function AttachmentGroup({
  className,
  ...props
}: ComponentProps<"div">) {
  return (
    <div
      data-slot="attachment-group"
      className={cn(
        "flex min-w-0 gap-2 overflow-x-auto overscroll-x-contain py-1 *:data-[slot=attachment]:flex-none",
        className,
      )}
      {...props}
    />
  );
}

/*
 * Kinds, sizes and the file card.
 */

/** The file kinds the composer accepts, by extension, with their glyphs. */
const KIND_ICON: Readonly<Record<string, Icon>> = {
  pdf: FilePdfIcon,
  png: FileImageIcon,
  jpg: FileImageIcon,
  jpeg: FileImageIcon,
  gif: FileImageIcon,
  webp: FileImageIcon,
  md: FileTextIcon,
  markdown: FileTextIcon,
  txt: FileTextIcon,
  csv: FileTextIcon,
  json: FileCodeIcon,
  yaml: FileCodeIcon,
  yml: FileCodeIcon,
  js: FileCodeIcon,
  ts: FileCodeIcon,
  py: FileCodeIcon,
  go: FileCodeIcon,
  rs: FileCodeIcon,
  sql: FileCodeIcon,
  sh: FileCodeIcon,
};

/** The `accept` list for a file input: every extension the card has a glyph for. */
export const ATTACHMENT_ACCEPT = Object.keys(KIND_ICON)
  .map((ext) => `.${ext}`)
  .join(",");

const KIND_LABEL: Readonly<Record<string, string>> = {
  md: "Markdown",
  markdown: "Markdown",
  jpg: "JPEG",
  yml: "YAML",
};

function extensionOf(name: string): string {
  const match = /\.([a-z0-9]+)$/i.exec(name);
  return match?.[1]?.toLowerCase() ?? "";
}

/**
 * The kind a person reads under the name: "PDF", "Markdown", "JPEG", "YAML",
 * or the extension in upper case. A name with no extension is a "File".
 */
export function attachmentKind(name: string): string {
  const ext = extensionOf(name);
  return KIND_LABEL[ext] ?? (ext ? ext.toUpperCase() : "File");
}

/** A byte count as "2.4 MB" from 1 MB up, and as whole kilobytes below it. */
export function formatAttachmentSize(bytes: number): string {
  if (bytes >= 1048576) return `${(bytes / 1048576).toFixed(1)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

/** The glyph for a file's kind, or the plain file glyph for any other. */
export function AttachmentKindIcon({
  name,
  ...props
}: IconProps & { name: string }) {
  const KindIcon = KIND_ICON[extensionOf(name)] ?? FileIcon;
  return <KindIcon aria-hidden="true" {...props} />;
}

/** A file the composer holds or a sent turn shows. */
export interface AttachmentFile {
  /** A key that stays the same while the file is attached. */
  id: string;
  name: string;
  /** The size in bytes. The card leaves the size out when it is missing. */
  size?: number | undefined;
  state?: AttachmentState | undefined;
  /** An image to show in the tile in place of the kind glyph. */
  previewUrl?: string | undefined;
}

/**
 * One file as a card: a tile for its kind or its preview, its name, and its
 * kind and size. While the file uploads the name shimmers and the line under
 * it reads "Uploading". Pass `onRemove` to show the remove button.
 */
export function AttachmentCard({
  file,
  onRemove,
  className,
  ...props
}: Omit<ComponentProps<"div">, "children"> & {
  file: AttachmentFile;
  onRemove?: ((file: AttachmentFile) => void) | undefined;
}) {
  const state = file.state ?? "done";
  return (
    <Attachment
      state={state}
      className={cn(
        "w-58 max-w-full gap-2.5 rounded-xl bg-card p-1.5 has-data-[slot=attachment-media]:p-1.5",
        className,
      )}
      {...props}
    >
      <AttachmentMedia
        variant={file.previewUrl ? "image" : "icon"}
        className="w-10 rounded-lg bg-hl text-muted-foreground [&_svg:not([class*='size-'])]:size-[18px]"
      >
        {file.previewUrl ? (
          <img src={file.previewUrl} alt="" />
        ) : (
          <AttachmentKindIcon name={file.name} />
        )}
      </AttachmentMedia>
      <AttachmentContent className="leading-[1.35]">
        <AttachmentTitle
          title={file.name}
          className="max-w-none text-sm text-foreground"
        >
          {file.name}
        </AttachmentTitle>
        <AttachmentDescription className="mt-0 max-w-none text-sm">
          {state === "uploading" ? (
            <span>Uploading</span>
          ) : state === "error" ? (
            <span>Upload failed</span>
          ) : (
            <>
              <span>{attachmentKind(file.name)}</span>
              {file.size != null && (
                <span>{formatAttachmentSize(file.size)}</span>
              )}
            </>
          )}
        </AttachmentDescription>
      </AttachmentContent>
      {onRemove && (
        <AttachmentActions className="self-start">
          <AttachmentAction
            aria-label={`Remove ${file.name}`}
            onClick={() => onRemove(file)}
            className="text-muted-foreground hover:bg-hl hover:text-foreground [&_svg]:size-3"
          >
            <XIcon aria-hidden="true" />
          </AttachmentAction>
        </AttachmentActions>
      )}
    </Attachment>
  );
}
