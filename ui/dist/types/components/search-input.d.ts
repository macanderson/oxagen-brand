import * as React from "react";
import { type InputProps } from "./input";
export interface SearchInputProps extends Omit<InputProps, "type"> {
    /** Shows an X button when there is a value; called on click. */
    onClear?: () => void;
    /** Class for the wrapping element (the Input itself takes `className`). */
    containerClassName?: string;
}
declare const SearchInput: React.ForwardRefExoticComponent<SearchInputProps & React.RefAttributes<HTMLInputElement>>;
export { SearchInput };
