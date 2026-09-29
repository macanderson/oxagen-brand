"use client";
import * as React from "react";
import { Autocomplete as AutocompletePrimitive } from "@base-ui/react/autocomplete";
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { MagnifyingGlassIcon, XIcon } from "@phosphor-icons/react";
import { cn } from "../lib/utils";
import { menuItem, menuLabel, menuPopup } from "./control-styles";

/**
 * The command menu, after `.cmdk` in the mockup's `shared.css` (oxagen-roadmap
 * #244): a dialog drawn on the translucent menu surface, with a search field
 * over grouped commands. Cmd+K or Ctrl+K opens and closes it anywhere on the
 * page. Enter runs the highlighted command, the arrows move the highlight,
 * and Escape or a press on the scrim closes it.
 *
 * On a desktop it has no title bar; the dialog keeps its `aria-label`. A
 * phone has no Escape key, so there the title bar and its close button stay.
 * The scrim dims the page without blurring it, so the menu's own blur has the
 * page to work on.
 *
 * `CommandMenu` builds the whole menu from `groups`. The parts below it build
 * a menu by hand: `CommandMenuPopup` holds a Base UI `Autocomplete.Root` with
 * `inline` and `open` set, and the input, list, groups and items go inside.
 */

/** One command: a page to go to or an action to run. */
export interface CommandMenuCommand {
  /** A stable key for the command. */
  value: string;
  /** The name the row shows and the search matches. */
  label: string;
  /** A 16px glyph, drawn in the muted ink. */
  icon?: React.ReactNode;
  /** A second line in the mono face, such as a path or a count. */
  detail?: string;
  /** More words the search matches, such as "billing" for Spend. */
  keywords?: readonly string[];
  disabled?: boolean;
  /** Runs after the menu closes. */
  onSelect?: () => void;
}

/** A named group of commands, such as "Go to" or "Create". */
export interface CommandMenuCommandGroup {
  label: string;
  items: readonly CommandMenuCommand[];
}

/**
 * The button that opens the menu: a search glyph, a word, and the shortcut
 * as a key cap, after `.kbtn` in the mockup's `v3.css`. It takes the maia
 * field's pill so it reads as a search field in the top bar.
 */
const CommandMenuTrigger = React.forwardRef<
  React.ComponentRef<typeof DialogPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Trigger> & {
    /** The key cap's text. */
    shortcutLabel?: string;
  }
>(({ className, children, shortcutLabel = "⌘K", ...props }, ref) => (
  <DialogPrimitive.Trigger
    ref={ref}
    aria-keyshortcuts="Meta+K Control+K"
    className={cn(
      "inline-flex h-9 min-w-[190px] cursor-pointer items-center gap-2 rounded-4xl border border-border bg-card px-3 text-[12.5px] text-muted-foreground transition-colors outline-none hover:border-rule hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring",
      className,
    )}
    {...props}
  >
    <MagnifyingGlassIcon className="size-3.5 shrink-0" aria-hidden />
    <span>{children ?? "Search"}</span>
    <CommandMenuShortcut className="ml-auto" aria-hidden>
      {shortcutLabel}
    </CommandMenuShortcut>
  </DialogPrimitive.Trigger>
));
CommandMenuTrigger.displayName = "CommandMenuTrigger";

/** A key cap, such as the "⌘K" on the trigger. */
const CommandMenuShortcut = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) => (
  <kbd
    className={cn(
      "rounded-sm border border-border bg-hl px-[5px] py-px font-mono text-[10.5px] leading-normal text-muted-foreground",
      className,
    )}
    {...props}
  />
);
CommandMenuShortcut.displayName = "CommandMenuShortcut";

interface CommandMenuPopupProps
  extends React.ComponentPropsWithoutRef<typeof DialogPrimitive.Popup> {
  /** The dialog's name, and the phone title bar's text. */
  title?: string;
  /** Forwarded to Base UI `Dialog.Portal` (e.g. `keepMounted`, custom `container`). */
  portalProps?: React.ComponentPropsWithoutRef<typeof DialogPrimitive.Portal>;
}

/**
 * The scrim and the floating surface: the popover ground at 70%, blurred and
 * saturated, a faint ring, a 16px corner and a 4px inset. It drops 70px from
 * the top of the page, as a dialog does, and opens with focus in the search
 * field.
 */
const CommandMenuPopup = React.forwardRef<HTMLDivElement, CommandMenuPopupProps>(
  (
    { className, children, title = "Search", portalProps, initialFocus, ...props },
    ref,
  ) => {
    const popupRef = React.useRef<HTMLDivElement>(null);
    React.useImperativeHandle(ref, () => popupRef.current as HTMLDivElement);
    // Focus the search field rather than the phone bar's close button, which
    // comes first in the tab order.
    const focusSearch = React.useCallback(
      () => popupRef.current?.querySelector<HTMLElement>("input") ?? true,
      [],
    );
    return (
      <DialogPrimitive.Portal {...portalProps}>
        <DialogPrimitive.Backdrop
          className={cn(
            // The mockup's rgba(0,0,0,.28): half the scrim token, unblurred.
            "fixed inset-0 z-50 bg-overlay-scrim/50",
            "transition-opacity duration-[var(--motion-overlay)] ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[ending-style]:opacity-0",
          )}
        />
        <DialogPrimitive.Popup
          ref={popupRef}
          aria-label={title}
          initialFocus={initialFocus ?? focusSearch}
          className={cn(
            menuPopup,
            "fixed left-1/2 top-[70px] z-50 flex max-h-[calc(100dvh-86px)] w-[calc(100%-2rem)] max-w-[600px] -translate-x-1/2 flex-col",
            "origin-top transition-[opacity,scale] duration-[var(--motion-overlay)] ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[starting-style]:scale-[0.98] data-[ending-style]:opacity-0 data-[ending-style]:scale-[0.98]",
            className,
          )}
          {...props}
        >
          <div className="flex items-center justify-between gap-3 py-1 pr-1 pl-3 md:hidden">
            <span className="text-sm font-semibold">{title}</span>
            <DialogPrimitive.Close className="inline-flex size-8 cursor-pointer items-center justify-center rounded-lg text-muted-foreground transition-colors outline-none hover:bg-foreground/10 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-input-ring">
              <XIcon className="size-4" aria-hidden />
              <span className="sr-only">Close</span>
            </DialogPrimitive.Close>
          </div>
          {children}
        </DialogPrimitive.Popup>
      </DialogPrimitive.Portal>
    );
  },
);
CommandMenuPopup.displayName = "CommandMenuPopup";

/**
 * `.cmdk-q { font-size:14px; padding:10px 12px; border:1px solid
 * var(--border); border-radius:12px; margin-bottom:8px }`: the search field.
 * It keeps focus while the arrows move the highlight through the list.
 */
const CommandMenuInput = React.forwardRef<
  HTMLInputElement,
  React.ComponentPropsWithoutRef<typeof AutocompletePrimitive.Input>
>(({ className, ...props }, ref) => (
  <AutocompletePrimitive.Input
    ref={ref}
    className={cn(
      "mb-2 block w-full min-w-0 shrink-0 rounded-2xl border border-border bg-input-bg px-3 py-2.5 text-sm text-input-fg outline-none placeholder:text-input-placeholder focus-visible:border-input-border-focus max-md:text-base",
      className,
    )}
    {...props}
  />
));
CommandMenuInput.displayName = "CommandMenuInput";

/** `.cmdk { max-height:min(420px,60vh); overflow-y:auto }`: the scrolling list. */
const CommandMenuList = React.forwardRef<
  HTMLDivElement,
  React.ComponentPropsWithoutRef<typeof AutocompletePrimitive.List>
>(({ className, ...props }, ref) => (
  <AutocompletePrimitive.List
    ref={ref}
    className={cn(
      "max-h-[min(420px,60vh)] min-h-0 overflow-y-auto overflow-x-hidden",
      className,
    )}
    {...props}
  />
));
CommandMenuList.displayName = "CommandMenuList";

/** A group of rows. Pass the group's `items` so its rows filter with the query. */
const CommandMenuGroup = React.forwardRef<
  HTMLDivElement,
  React.ComponentPropsWithoutRef<typeof AutocompletePrimitive.Group>
>(({ className, ...props }, ref) => (
  <AutocompletePrimitive.Group ref={ref} className={cn("pb-1", className)} {...props} />
));
CommandMenuGroup.displayName = "CommandMenuGroup";

/** `.menu-h`: the group's name in caps over its rows. */
const CommandMenuGroupLabel = React.forwardRef<
  HTMLDivElement,
  React.ComponentPropsWithoutRef<typeof AutocompletePrimitive.GroupLabel>
>(({ className, ...props }, ref) => (
  <AutocompletePrimitive.GroupLabel
    ref={ref}
    className={cn(menuLabel, className)}
    {...props}
  />
));
CommandMenuGroupLabel.displayName = "CommandMenuGroupLabel";

/** Maps a group's filtered items to rows. Its child is a function of one item. */
const CommandMenuCollection = AutocompletePrimitive.Collection;

interface CommandMenuItemProps
  extends React.ComponentPropsWithoutRef<typeof AutocompletePrimitive.Item> {
  /** A 16px glyph in a 24px box, drawn in the muted ink. */
  icon?: React.ReactNode;
  /** A second line in the mono face under the name. */
  detail?: React.ReactNode;
}

/**
 * `.menu-i` with `.ic` and `.tx`: one command. The name is 14px at weight
 * 600, and the optional detail sits under it at 11px in the mono face.
 */
const CommandMenuItem = React.forwardRef<HTMLDivElement, CommandMenuItemProps>(
  ({ className, icon, detail, children, ...props }, ref) => (
    <AutocompletePrimitive.Item
      ref={ref}
      className={cn(menuItem, className)}
      {...props}
    >
      {icon ? (
        <span className="flex w-6 flex-none items-center justify-center text-muted-foreground">
          {icon}
        </span>
      ) : null}
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-semibold">{children}</span>
        {detail ? (
          <span className="block truncate font-mono text-[11px] text-muted-foreground">
            {detail}
          </span>
        ) : null}
      </span>
    </AutocompletePrimitive.Item>
  ),
);
CommandMenuItem.displayName = "CommandMenuItem";

/**
 * `.cmdk-none { padding:14px 10px }`: the line shown when nothing matches.
 * It stays mounted and empty while the list has rows, since it is the live
 * region that tells a screen reader the list ran out.
 */
const CommandMenuEmpty = React.forwardRef<
  HTMLDivElement,
  React.ComponentPropsWithoutRef<typeof AutocompletePrimitive.Empty>
>(({ className, ...props }, ref) => (
  <AutocompletePrimitive.Empty
    ref={ref}
    className={cn(
      "text-[12.5px] text-muted-foreground [&:not(:empty)]:px-2.5 [&:not(:empty)]:py-3.5",
      className,
    )}
    {...props}
  />
));
CommandMenuEmpty.displayName = "CommandMenuEmpty";

export interface CommandMenuProps {
  /** The commands, in the order the menu shows their groups. */
  groups: readonly CommandMenuCommandGroup[];
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  /** Runs after the menu closes, before the command's own `onSelect`. */
  onSelect?: (command: CommandMenuCommand) => void;
  /** The query the menu opens with. */
  defaultQuery?: string;
  placeholder?: string;
  /** The search field's accessible name. */
  inputLabel?: string;
  /** The dialog's accessible name. */
  title?: string;
  emptyMessage?: React.ReactNode;
  /** Whether Cmd+K and Ctrl+K open and close the menu. */
  shortcut?: boolean;
  /** Anything that opens the menu, usually a `CommandMenuTrigger`. */
  children?: React.ReactNode;
}

/**
 * The whole command menu from data. The search matches a command's name,
 * its group's name, its detail and its keywords, so "create" lists every
 * command in the Create group, as the mockup's menu does.
 */
function CommandMenu({
  groups,
  open: openProp,
  defaultOpen = false,
  onOpenChange,
  onSelect,
  defaultQuery,
  placeholder = "Go to a page or run an action",
  inputLabel = "Search pages and actions",
  title = "Search",
  emptyMessage = "Nothing matches.",
  shortcut = true,
  children,
}: CommandMenuProps) {
  const [uncontrolledOpen, setUncontrolledOpen] = React.useState(defaultOpen);
  const open = openProp ?? uncontrolledOpen;

  const setOpen = React.useCallback(
    (next: boolean) => {
      if (openProp === undefined) setUncontrolledOpen(next);
      onOpenChange?.(next);
    },
    [openProp, onOpenChange],
  );

  // The shortcut reads the latest state through a ref, so the listener is
  // added once rather than on every open and close.
  const toggleRef = React.useRef(() => setOpen(!open));
  toggleRef.current = () => setOpen(!open);
  React.useEffect(() => {
    if (!shortcut) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        toggleRef.current();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [shortcut]);

  const groupOf = React.useMemo(() => {
    const map = new Map<CommandMenuCommand, string>();
    for (const group of groups) {
      for (const item of group.items) map.set(item, group.label);
    }
    return map;
  }, [groups]);
  // Base UI caches the filter per locale, so this returns the same object on
  // every render.
  const { contains } = AutocompletePrimitive.useFilter();
  const filter = React.useCallback(
    (item: CommandMenuCommand, query: string) =>
      contains(
        [groupOf.get(item), item.label, item.detail, ...(item.keywords ?? [])]
          .filter(Boolean)
          .join(" "),
        query,
      ),
    [contains, groupOf],
  );

  // Base UI drops a press or an Enter on a disabled row before it reaches
  // this handler, so a disabled command never runs.
  const run = (command: CommandMenuCommand) => {
    setOpen(false);
    onSelect?.(command);
    command.onSelect?.();
  };

  return (
    <DialogPrimitive.Root open={open} onOpenChange={(next) => setOpen(next)}>
      {children}
      <CommandMenuPopup title={title}>
        <AutocompletePrimitive.Root
          open
          inline
          items={groups}
          filter={filter}
          defaultValue={defaultQuery}
          autoHighlight="always"
          keepHighlight
        >
          <CommandMenuInput placeholder={placeholder} aria-label={inputLabel} />
          <CommandMenuList aria-label="Commands">
            {(group: CommandMenuCommandGroup) => (
              <CommandMenuGroup key={group.label} items={group.items}>
                <CommandMenuGroupLabel>{group.label}</CommandMenuGroupLabel>
                <CommandMenuCollection>
                  {(command: CommandMenuCommand) => (
                    <CommandMenuItem
                      key={command.value}
                      value={command}
                      icon={command.icon}
                      detail={command.detail}
                      disabled={command.disabled}
                      onClick={() => run(command)}
                    >
                      {command.label}
                    </CommandMenuItem>
                  )}
                </CommandMenuCollection>
              </CommandMenuGroup>
            )}
          </CommandMenuList>
          <CommandMenuEmpty>{emptyMessage}</CommandMenuEmpty>
        </AutocompletePrimitive.Root>
      </CommandMenuPopup>
    </DialogPrimitive.Root>
  );
}
CommandMenu.displayName = "CommandMenu";

/** Base UI `Dialog.Root`, for a menu built from the parts. */
const CommandMenuRoot = DialogPrimitive.Root;
/** Base UI `Autocomplete.Root`, for a menu built from the parts. Set `inline` and `open`. */
const CommandMenuSearch = AutocompletePrimitive.Root;
const CommandMenuClose = DialogPrimitive.Close;

export {
  CommandMenu,
  CommandMenuRoot,
  CommandMenuTrigger,
  CommandMenuShortcut,
  CommandMenuPopup,
  CommandMenuSearch,
  CommandMenuInput,
  CommandMenuList,
  CommandMenuGroup,
  CommandMenuGroupLabel,
  CommandMenuCollection,
  CommandMenuItem,
  CommandMenuEmpty,
  CommandMenuClose,
};
