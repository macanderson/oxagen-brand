import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { SearchInput } from "./search-input";

/**
 * A search field with a search icon in front and a clear button.
 */
const meta = {
  title: "Primitives/SearchInput",
  component: SearchInput,
} satisfies Meta<typeof SearchInput>;
export default meta;
type Story = StoryObj<typeof meta>;

function Demo() {
  const [value, setValue] = React.useState("graph");
  return (
    <SearchInput
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onClear={() => setValue("")}
      placeholder="Search tools…"
      containerClassName="max-w-xs"
    />
  );
}

export const Default: Story = {
  render: () => <Demo />,
};
