"use client";
import * as React from "react";
import {
  Toast as ToastPrimitive,
  type ToastManagerAddOptions,
  type UseToastManagerReturnValue,
} from "@base-ui/react/toast";
import {
  CheckCircleIcon,
  CircleNotchIcon,
  InfoIcon,
  WarningIcon,
  XCircleIcon,
  XIcon,
  type Icon,
} from "@phosphor-icons/react";
import { cn } from "../lib/utils";

/**
 * Toast is shadcn's base Toast (Base UI) in the maia style. Each toast shows
 * an icon in its tone's status colour, the message, and a close button, on
 * the translucent popover surface.
 *
 * Mount the provider and the viewport once at the app root:
 *   <ToastProvider><App /><ToastViewport /></ToastProvider>
 *
 * Then add toasts from anywhere under the provider:
 *   const toast = useToast();
 *   toast.add({ title: "Policy saved", tone: "success" });
 *
 * The newest toast sits in front and up to two older ones peek 12px behind
 * it. The stack opens on hover or focus. A fourth toast hides the oldest.
 */

/** How long a toast stays up, in milliseconds. The app's TOAST_MS. */
export const TOAST_MS = 4200;

/** How many toasts show at once. Older toasts beyond this fade out. */
const TOAST_LIMIT = 3;

/**
 * The four tones. `warn` and `warning` are the same tone. A toast with no
 * tone, or a tone the kit does not know, reads as success.
 */
export type ToastTone = "success" | "info" | "warn" | "warning" | "error";

type ResolvedTone = "success" | "info" | "warning" | "error" | "loading";

/** The options `useToast().add` takes: Base UI's options plus `tone`. */
export interface ToastAddOptions<Data extends object = object>
  extends ToastManagerAddOptions<Data> {
  /** The tone of the toast. It wins over `type` when both are set. */
  tone?: ToastTone | undefined;
}

/** The manager `useToast` returns. `add` also takes a `tone`. */
export interface ToastApi extends Omit<UseToastManagerReturnValue, "add"> {
  add: <Data extends object = object>(options: ToastAddOptions<Data>) => string;
}

function ToastProvider({
  timeout = TOAST_MS,
  limit = TOAST_LIMIT,
  ...props
}: React.ComponentProps<typeof ToastPrimitive.Provider>) {
  return <ToastPrimitive.Provider timeout={timeout} limit={limit} {...props} />;
}

function toBaseOptions<Data extends object>({
  tone,
  ...rest
}: ToastAddOptions<Data>): ToastManagerAddOptions<Data> {
  return tone === undefined ? rest : { ...rest, type: tone };
}

/** Returns the Base UI toast manager, with an `add` that takes a `tone`. */
function useToast(): ToastApi {
  const manager = ToastPrimitive.useToastManager();
  return React.useMemo<ToastApi>(() => {
    const add = <Data extends object = object>(
      options: ToastAddOptions<Data>,
    ) => manager.add<Data>(toBaseOptions(options));
    return { ...manager, add };
  }, [manager]);
}

/** Maps a toast's `type` to its tone. The old type names still work. */
function resolveTone(type: string | undefined): ResolvedTone {
  switch (type) {
    case "warn":
    case "warning":
      return "warning";
    case "error":
    case "destructive":
      return "error";
    case "info":
      return "info";
    case "loading":
      return "loading";
    default:
      return "success";
  }
}

const TONE_ICON: Record<ResolvedTone, Icon> = {
  success: CheckCircleIcon,
  info: InfoIcon,
  warning: WarningIcon,
  error: XCircleIcon,
  loading: CircleNotchIcon,
};

const TONE_ICON_CLASS: Record<ResolvedTone, string> = {
  success: "text-success",
  info: "text-info",
  warning: "text-warning",
  error: "text-error",
  loading: "animate-spin text-muted-foreground motion-reduce:animate-none",
};

/*
 * The stack follows Base UI's stacking recipe with the mockup's numbers: a
 * 12px peek, each older toast 10% smaller, and a 12px gap when the stack
 * opens. Closed, every toast takes the front toast's height, so the peek is
 * the same whatever an older toast holds.
 */
const ROOT_CLASS = cn(
  "[--gap:12px] [--peek:12px] [--scale:calc(max(0,1-(var(--toast-index)*0.1)))] [--shrink:calc(1-var(--scale))] [--height:var(--toast-frontmost-height,var(--toast-height))] [--offset-y:calc(var(--toast-offset-y)*-1+(var(--toast-index)*var(--gap)*-1)+var(--toast-swipe-movement-y))]",
  "absolute right-0 bottom-0 left-0 z-[calc(10-var(--toast-index))] w-full origin-bottom select-none",
  "h-[var(--height)] data-[expanded]:h-[var(--toast-height)]",
  "[transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--toast-swipe-movement-y)-(var(--toast-index)*var(--peek))-(var(--shrink)*var(--height))))_scale(var(--scale))]",
  "data-[expanded]:[transform:translateX(var(--toast-swipe-movement-x))_translateY(var(--offset-y))]",
  // The translucent popover surface, the same recipe the select popup uses:
  // a 16px corner, the faint ring, and the deep shadow. `glass-pop` hooks it
  // to the glass fallbacks in globals.css, which turn it opaque.
  "glass-pop isolate rounded-3xl bg-menu-popup-bg/70 text-menu-popup-fg shadow-pop ring-1 ring-pop-ring outline-none",
  "before:pointer-events-none before:absolute before:inset-0 before:-z-1 before:rounded-[inherit] before:backdrop-blur-2xl before:backdrop-saturate-150",
  // A bridge under each toast keeps the stack open while the pointer crosses the gap.
  "after:absolute after:top-full after:left-0 after:h-[calc(var(--gap)+1px)] after:w-full after:content-['']",
  // Enter from below, leave by fading and dropping 6px, and hide past the limit.
  "data-[starting-style]:opacity-0 data-[starting-style]:[transform:translateY(100%)]",
  "data-[ending-style]:opacity-0 [&[data-ending-style]:not([data-limited]):not([data-swipe-direction])]:[transform:translateY(6px)]",
  "data-[ending-style]:data-[swipe-direction=down]:[transform:translateY(calc(var(--toast-swipe-movement-y)+150%))]",
  "data-[ending-style]:data-[swipe-direction=right]:[transform:translateX(calc(var(--toast-swipe-movement-x)+150%))_translateY(var(--offset-y))]",
  "data-[limited]:pointer-events-none data-[limited]:opacity-0",
  "[transition:transform_0.5s_cubic-bezier(0.22,1,0.36,1),opacity_0.2s,height_0.15s] motion-reduce:[transition:opacity_0.2s]",
);

function ToastList() {
  const { toasts } = ToastPrimitive.useToastManager();
  return toasts.map((toast) => {
    const tone = resolveTone(toast.type);
    const ToneIcon = TONE_ICON[tone];
    const hasDescription = toast.description != null;
    return (
      <ToastPrimitive.Root
        key={toast.id}
        toast={toast}
        data-tone={tone}
        className={ROOT_CLASS}
      >
        <ToastPrimitive.Content className="flex items-start gap-2.5 py-3.5 pr-3 pl-4 text-[13px] leading-[1.4] transition-opacity duration-[250ms] data-[behind]:pointer-events-none data-[behind]:opacity-0 data-[expanded]:pointer-events-auto data-[expanded]:opacity-100">
          <span
            data-slot="toast-icon"
            className="grid h-[18px] flex-none place-items-center"
          >
            <ToneIcon
              aria-hidden="true"
              className={cn("size-4", TONE_ICON_CLASS[tone])}
            />
          </span>
          <div className="grid min-w-0 flex-1 gap-0.5 [overflow-wrap:anywhere]">
            <ToastPrimitive.Title
              className={cn("text-foreground", hasDescription && "font-medium")}
            />
            <ToastPrimitive.Description className="text-muted-foreground" />
            {toast.actionProps && (
              // ToastAction reads toast.actionProps from context itself (for
              // onClick and children), so do not also spread it here, or its
              // onClick fires twice.
              <ToastPrimitive.Action
                className={cn(
                  "mt-1 w-fit rounded-sm font-medium text-accent-text underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  toast.actionProps.className,
                )}
              />
            )}
          </div>
          <ToastPrimitive.Close
            aria-label="Close"
            className="-mt-0.5 grid size-[22px] flex-none place-items-center rounded-[6px] text-muted-foreground transition-colors hover:bg-hl hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <XIcon aria-hidden="true" className="size-3.5" />
          </ToastPrimitive.Close>
        </ToastPrimitive.Content>
      </ToastPrimitive.Root>
    );
  });
}

/**
 * The fixed stack. It sits bottom right on a desktop and bottom centre below
 * 48rem. Set `--toast-inset-bottom` on a parent, or pass a className, to lift
 * it above a bar that owns the bottom of the screen.
 */
function ToastViewport({ className }: { className?: string }) {
  return (
    <ToastPrimitive.Portal>
      <ToastPrimitive.Viewport
        className={cn(
          "fixed right-4 bottom-[calc(var(--toast-inset-bottom,16px)+env(safe-area-inset-bottom,0px))] z-[100] w-[356px] max-w-[calc(100vw-32px)]",
          "max-md:right-auto max-md:left-1/2 max-md:w-[min(368px,calc(100vw-32px))] max-md:max-w-none max-md:-translate-x-1/2",
          className,
        )}
      >
        <ToastList />
      </ToastPrimitive.Viewport>
    </ToastPrimitive.Portal>
  );
}

export { ToastProvider, ToastViewport, useToast };
