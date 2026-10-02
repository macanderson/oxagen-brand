import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  Combobox,
  ComboboxTrigger,
  ComboboxValue,
  ComboboxPopup,
  ComboboxItem,
} from "./combobox";

const meta = {
  title: "Forms/Combobox",
  component: Combobox,
  // An open overlay portals to <body>, outside its story. On the Docs page
  // each story draws in its own frame, so the overlay stays with its story.
  parameters: { docs: { story: { inline: false, height: "420px" } } },
} satisfies Meta<typeof Combobox>;
export default meta;
// Combobox's root requires `children`; base the story on the component so
// render-only stories don't have to declare an `args` object.
type Story = StoryObj<typeof Combobox>;

const REPOSITORIES = [
  "oxagen",
  "oxagen-roadmap",
  "oxagen-brand",
  "stella",
  "context-graph",
  "tacho",
  "mcp-studio",
];

function RepositoryPicker({
  defaultOpen,
  defaultSearchValue,
}: {
  defaultOpen?: boolean;
  defaultSearchValue?: string;
}) {
  const [value, setValue] = React.useState<string | null>(
    defaultOpen ? "stella" : null,
  );
  return (
    <div className="min-h-96 w-64">
      <Combobox value={value} onValueChange={setValue} defaultOpen={defaultOpen}>
        <ComboboxTrigger className="w-full" aria-label="Repository">
          <ComboboxValue placeholder="Pick a repository" />
        </ComboboxTrigger>
        <ComboboxPopup
          searchPlaceholder="Search repositories…"
          defaultSearchValue={defaultSearchValue}
        >
          {REPOSITORIES.map((repo) => (
            <ComboboxItem key={repo} value={repo}>
              {repo}
            </ComboboxItem>
          ))}
        </ComboboxPopup>
      </Combobox>
    </div>
  );
}

export const Default: Story = {
  render: () => <RepositoryPicker />,
};

/** Open with the full list and one repository checked. */
export const OpenWithResults: Story = {
  render: () => <RepositoryPicker defaultOpen />,
};

/** Open with a query that matches nothing, so the empty message shows. */
export const Empty: Story = {
  render: () => <RepositoryPicker defaultOpen defaultSearchValue="billing" />,
};
