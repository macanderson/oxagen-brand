"use client";
// Moved from oxagen apps/app/src/ui/hover-card.tsx at ddb85803.
// shadcn's base-maia hover card (ADR-221), written from
// https://ui.shadcn.com/r/styles/base-maia/hover-card.json. Two changes from
// the registry: the popup is the kit's one floating surface (oxagen-roadmap
// #244), the popover fill at 70% over a blur that a menu and a popover share,
// and the content can take an `anchor`, so one card can show beside any
// element without a trigger of its own (features/shell/cell-overflow.tsx).
//
// The registry animated with tw-animate classes that nothing in the kit
// defines. The card now fades and lifts through the Base UI starting and
// ending styles, as every other kit overlay does.
import { PreviewCard as PreviewCardPrimitive } from "@base-ui/react/preview-card";
import { cn } from "../lib/utils";
import { popoverSurface } from "./control-styles";

function HoverCard({ ...props }: PreviewCardPrimitive.Root.Props) {
  return <PreviewCardPrimitive.Root data-slot="hover-card" {...props} />;
}

function HoverCardContent({
  className,
  side = "bottom",
  sideOffset = 4,
  align = "center",
  alignOffset = 4,
  anchor,
  collisionPadding,
  ...props
}: PreviewCardPrimitive.Popup.Props &
  Pick<
    PreviewCardPrimitive.Positioner.Props,
    | "align"
    | "alignOffset"
    | "side"
    | "sideOffset"
    | "anchor"
    | "collisionPadding"
  >) {
  return (
    <PreviewCardPrimitive.Portal data-slot="hover-card-portal">
      <PreviewCardPrimitive.Positioner
        align={align}
        alignOffset={alignOffset}
        side={side}
        sideOffset={sideOffset}
        anchor={anchor}
        collisionPadding={collisionPadding}
        className="isolate z-50"
      >
        <PreviewCardPrimitive.Popup
          data-slot="hover-card-content"
          className={cn(
            popoverSurface,
            // Prose sits 12px by 16px in: the surface's 4px inset plus the
            // 8px by 12px a menu row keeps.
            "z-50 w-72 px-4 py-3 text-base outline-hidden",
            "origin-(--transform-origin) transition-[opacity,transform,translate,scale] duration-[var(--motion-overlay)] ease-[var(--ease-entry)] data-[starting-style]:opacity-0 data-[starting-style]:scale-[0.97] data-[ending-style]:opacity-0 data-[ending-style]:scale-[0.97]",
            className,
          )}
          {...props}
        />
      </PreviewCardPrimitive.Positioner>
    </PreviewCardPrimitive.Portal>
  );
}

export { HoverCard, HoverCardContent };
