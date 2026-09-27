import * as React from "react";
import { type ButtonProps } from "./button";
/**
 * useCopyToClipboard — shared clipboard write + transient "copied" flag.
 * Use directly when the trigger chrome is bespoke; otherwise use <CopyButton>.
 */
export declare function useCopyToClipboard({ timeout, }?: {
    timeout?: number;
}): {
    copied: boolean;
    copy: (text: string) => Promise<boolean>;
};
export interface CopyButtonProps extends Omit<ButtonProps, "value" | "onCopy" | "children"> {
    /** Text written to the clipboard (or a lazy producer for expensive payloads). */
    value: string | (() => string);
    /** Tooltip + accessible name at rest. */
    label?: string;
    /** Tooltip + announcement after a successful copy. */
    copiedLabel?: string;
    /** How long the copied state persists, in ms. */
    timeout?: number;
    /** Called after a successful clipboard write. */
    onCopied?: () => void;
}
declare const CopyButton: React.ForwardRefExoticComponent<CopyButtonProps & React.RefAttributes<HTMLButtonElement>>;
export { CopyButton };
