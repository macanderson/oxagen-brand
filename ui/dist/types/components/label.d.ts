import * as React from "react";
/**
 * Label — a styled native `<label>`. Base UI has no standalone label primitive
 * (it exposes `Field.Label` inside a `Field.Root`); for the common standalone
 * case a native element with `htmlFor` is the stock, fully-accessible choice.
 */
declare const Label: React.ForwardRefExoticComponent<React.LabelHTMLAttributes<HTMLLabelElement> & React.RefAttributes<HTMLLabelElement>>;
export { Label };
